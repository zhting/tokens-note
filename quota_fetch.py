#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 CodexBar 同一套数据源，实时拉取各家额度（只读本地凭证，不写回登录文件）。"""
from __future__ import annotations

import json
import os
import socket
import sqlite3
import struct
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "ai-tools-data.json"
SECRETS_FILE = HERE / "quota-secrets.json"
HOME = Path.home()
APPDATA = Path(os.environ.get("APPDATA") or "")

UA = "XueGaoQuota/1.0 (CodexBar-compatible)"


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _secrets():
    data = _load_json(SECRETS_FILE)
    return data if isinstance(data, dict) else {}


def _http_json(url, headers=None, method="GET", body=None, timeout=18, raw=False):
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if raw:
                return resp.status, data
            text = data.decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(text) if text else {}
            except json.JSONDecodeError:
                return resp.status, {"_raw": text[:400]}
    except urllib.error.HTTPError as e:
        blob = e.read() if hasattr(e, "read") else b""
        if raw:
            return e.code, blob
        try:
            return e.code, json.loads(blob.decode("utf-8", errors="replace") or "{}")
        except Exception:
            return e.code, {"_raw": blob[:400].decode("utf-8", errors="replace")}
    except Exception as e:
        raise RuntimeError(str(e)) from e


def _pct(used, limit):
    try:
        u, lim = float(used), float(limit)
        if lim <= 0:
            return None
        return max(0.0, min(100.0, u / lim * 100.0))
    except Exception:
        return None


def _as_pct(value):
    if value is None:
        return None
    try:
        v = float(value)
    except Exception:
        return None
    if v < 0:
        return None
    # 0–1 比例（排除已经是 0.36% 这种小百分比的情况：调用方自己保证）
    return max(0.0, min(100.0, v))


def _iso_to_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value > 1e12:
            value = value / 1000.0
        if 1_700_000_000 <= value <= 2_100_000_000:
            return int(value)
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        if s.isdigit():
            return _iso_to_ts(int(s))
        s = s.replace("Z", "+00:00")
        return int(datetime.fromisoformat(s).timestamp())
    except Exception:
        return None


def _ok(provider, pct, source, detail="", reset_at=None):
    return {
        "ok": True,
        "provider": provider,
        "quotaPct": round(float(pct), 1),
        "source": source,
        "detail": detail,
        "resetAt": reset_at,
        "error": None,
    }


def _err(provider, msg, source=""):
    return {
        "ok": False,
        "provider": provider,
        "quotaPct": None,
        "source": source,
        "detail": "",
        "resetAt": None,
        "error": msg,
    }


# ---------- ChatGPT / Codex（~/.codex/auth.json → chatgpt.com wham/usage）----------
def fetch_chatgpt():
    auth = _load_json(HOME / ".codex" / "auth.json") or {}
    tokens = auth.get("tokens") or {}
    token = tokens.get("access_token")
    account = tokens.get("account_id")
    if not token:
        return _err("openai", "未找到 ~/.codex/auth.json 的 access_token")
    headers = {"Authorization": f"Bearer {token}"}
    if account:
        headers["ChatGPT-Account-Id"] = str(account)
    status, data = _http_json("https://chatgpt.com/backend-api/wham/usage", headers=headers)
    if status in (401, 403):
        return _err("openai", "Codex 登录已过期，请重新运行 codex login")
    if status != 200 or not isinstance(data, dict):
        return _err("openai", f"HTTP {status}")
    rate = data.get("rate_limit") or {}
    weekly = rate.get("secondary_window") or {}
    session = rate.get("primary_window") or {}
    win = weekly if weekly.get("used_percent") is not None else session
    pct = _as_pct(win.get("used_percent"))
    if pct is None:
        lim = data.get("individual_limit") or rate.get("individual_limit") or {}
        if lim.get("remaining_percent") is not None:
            pct = _as_pct(100 - float(lim["remaining_percent"]))
        elif lim.get("limit") and lim.get("used") is not None:
            pct = _pct(lim["used"], lim["limit"])
    if pct is None:
        return _err("openai", "响应里没有额度百分比")
    reset_at = _iso_to_ts(win.get("reset_at") or win.get("resets_at"))
    which = "周额度" if win is weekly and weekly else "5 小时窗口"
    return _ok("openai", pct, "codex-oauth", f"{which} {pct:.1f}%", reset_at)


# ---------- Claude（~/.claude/.credentials.json → OAuth usage）----------
def fetch_claude():
    creds = _load_json(HOME / ".claude" / ".credentials.json") or {}
    oauth = creds.get("claudeAiOauth") or {}
    token = oauth.get("accessToken") or oauth.get("access_token")
    if not token:
        return _err("anthropic", "Claude 凭证为空或已失效，请重新 claude login")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "anthropic-beta": "oauth-2025-04-20",
    }
    status, data = _http_json("https://api.anthropic.com/api/oauth/usage", headers=headers)
    if status in (401, 403):
        return _err("anthropic", "Claude 登录已过期，请重新 claude login")
    if status == 429:
        return _err("anthropic", "Claude 用量接口被限流，稍后再试")
    if status != 200 or not isinstance(data, dict):
        return _err("anthropic", f"HTTP {status}")
    week = data.get("seven_day") or {}
    five = data.get("five_hour") or {}
    win = week if week.get("utilization") is not None else five
    pct = _as_pct(win.get("utilization"))
    if pct is None:
        return _err("anthropic", "响应里没有 utilization")
    reset_at = _iso_to_ts(win.get("resets_at") or win.get("reset_at"))
    which = "周额度" if win is week and week else "5 小时窗口"
    return _ok("anthropic", pct, "claude-oauth", f"{which} {pct:.1f}%", reset_at)


# ---------- Kimi Code（~/.kimi-code/credentials → coding/v1/usages）----------
def fetch_kimi():
    secrets = _secrets()
    token = secrets.get("kimi_api_key") or secrets.get("kimi_token")
    source = "kimi-api-key"
    if not token:
        creds = _load_json(HOME / ".kimi-code" / "credentials" / "kimi-code.json") or {}
        token = creds.get("access_token")
        source = "kimi-code-cli"
    if not token:
        return _err("kimi", "未找到 Kimi Code 凭证或 quota-secrets.json 里的 kimi_api_key")
    headers = {"Authorization": f"Bearer {token}"}
    device = HOME / ".kimi-code" / "device_id"
    if device.exists():
        headers["X-Kimi-Device-Id"] = device.read_text(encoding="utf-8").strip()
    headers.setdefault("X-Kimi-Hostname", socket.gethostname())
    status, data = _http_json("https://api.kimi.com/coding/v1/usages", headers=headers)
    if status in (401, 403):
        return _err("kimi", "Kimi 凭证无效，请重新登录 Kimi Code CLI 或填写 API key")
    if status != 200:
        return _err("kimi", f"HTTP {status}")

    detail = None
    if isinstance(data, dict):
        if isinstance(data.get("usage"), dict):
            detail = data["usage"]
        elif isinstance(data.get("usages"), list):
            coding = next((u for u in data["usages"] if str(u.get("scope", "")).upper() == "FEATURE_CODING"), None)
            if coding:
                detail = coding.get("detail") or coding
            elif data["usages"]:
                detail = data["usages"][0].get("detail") or data["usages"][0]
    if not isinstance(detail, dict):
        return _err("kimi", "响应里没有 usage.detail")
    pct = _pct(detail.get("used"), detail.get("limit"))
    if pct is None and detail.get("remaining") is not None and detail.get("limit"):
        try:
            remaining, limit = float(detail["remaining"]), float(detail["limit"])
            pct = max(0.0, min(100.0, (limit - remaining) / limit * 100.0))
        except Exception:
            pct = None
    if pct is None:
        return _err("kimi", "无法从 used/limit 算出百分比")
    reset_at = _iso_to_ts(detail.get("resetTime") or detail.get("reset_time") or detail.get("reset_at"))
    return _ok("kimi", pct, source, f"已用 {detail.get('used')}/{detail.get('limit')}", reset_at)


# ---------- Grok（~/.grok/auth.json → grok.com gRPC-web billing）----------
def _scan_protobuf(buf, path=(), depth=0):
    """极简 protobuf 扫描：抽出 fixed32（可能是百分比）和 varint（可能是重置时间）。"""
    fixed32, varints = [], []
    i, n = 0, len(buf)
    order = 0
    while i < n and depth < 6:
        key = 0
        shift = 0
        while i < n:
            b = buf[i]
            i += 1
            key |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
            if shift > 35:
                return fixed32, varints
        field, wire = key >> 3, key & 7
        here = path + (field,)
        if wire == 0:  # varint
            val = 0
            shift = 0
            while i < n:
                b = buf[i]
                i += 1
                val |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
            varints.append((here, val, order))
            order += 1
        elif wire == 1:  # 64-bit
            i += 8
        elif wire == 2:  # length-delimited
            ln = 0
            shift = 0
            while i < n:
                b = buf[i]
                i += 1
                ln |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
            chunk = buf[i:i + ln]
            i += ln
            sub_f, sub_v = _scan_protobuf(chunk, here, depth + 1)
            fixed32.extend(sub_f)
            varints.extend(sub_v)
        elif wire == 5:  # 32-bit
            if i + 4 <= n:
                (val,) = struct.unpack_from("<f", buf, i)
                fixed32.append((here, val, order))
                order += 1
            i += 4
        else:
            break
    return fixed32, varints


def _grpc_frames(data: bytes):
    frames = []
    i, n = 0, len(data)
    while i + 5 <= n:
        flags = data[i]
        length = int.from_bytes(data[i + 1:i + 5], "big")
        start, end = i + 5, i + 5 + length
        if length < 0 or end > n:
            return []
        if (flags & 0x80) == 0:
            frames.append(data[start:end])
        i = end
    return frames


def fetch_grok():
    auth = _load_json(HOME / ".grok" / "auth.json") or {}
    token = None
    for _k, v in auth.items():
        if isinstance(v, dict) and v.get("key"):
            token = v["key"]
            break
    if not token:
        return _err("xai", "未找到 ~/.grok/auth.json 的 key")
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": "https://grok.com",
        "Referer": "https://grok.com/?_s=usage",
        "Accept": "*/*",
        "Content-Type": "application/grpc-web+proto",
        "x-grpc-web": "1",
        "x-user-agent": "connect-es/2.1.1",
    }
    body = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    status, raw = _http_json(
        "https://grok.com/grok_api_v2.GrokBuildBilling/GetGrokCreditsConfig",
        headers=headers, method="POST", body=body, raw=True)
    if status in (401, 403):
        return _err("xai", "Grok 登录已过期，请重新 grok login")
    if status != 200 or not isinstance(raw, (bytes, bytearray)):
        return _err("xai", f"HTTP {status}")
    payloads = _grpc_frames(raw) or ([raw] if raw else [])
    fixed32, varints = [], []
    for p in payloads:
        f, v = _scan_protobuf(p)
        fixed32.extend(f)
        varints.extend(v)
    now = datetime.now(timezone.utc).timestamp()
    cands = [f for f in fixed32 if f[0] and f[0][-1] == 1 and 0 <= f[1] <= 100]
    cands.sort(key=lambda x: (len(x[0]), x[2]))
    pct = cands[0][1] if cands else None
    resets = [v[1] for v in varints if 1_700_000_000 <= v[1] <= 2_100_000_000 and v[1] > now]
    reset_at = min(resets) if resets else None
    if pct is None and reset_at:
        pct = 0.0
    if pct is None:
        return _err("xai", "未能从 Grok billing 响应解析出百分比")
    return _ok("xai", pct, "grok-billing", f"Grok 额度 {pct:.1f}%", reset_at)


# ---------- Cursor（cookie / 本地 token → cursor.com/api/usage-summary）----------
def _cursor_token_from_vscdb():
    cands = [
        APPDATA / "Cursor" / "User" / "globalStorage" / "state.vscdb",
        HOME / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "state.vscdb",
    ]
    for path in cands:
        if not path.exists():
            continue
        try:
            con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            cur = con.cursor()
            cur.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%cursorAuth%' OR key LIKE '%accessToken%'")
            rows = cur.fetchall()
            con.close()
            for key, val in rows:
                text = val.decode("utf-8", errors="ignore") if isinstance(val, (bytes, bytearray)) else str(val)
                if text.startswith("{"):
                    try:
                        obj = json.loads(text)
                    except Exception:
                        continue
                    for k in ("accessToken", "token", "cachedAccessToken"):
                        if obj.get(k):
                            return obj[k]
                if 20 < len(text) < 4000 and " " not in text:
                    return text
        except Exception:
            continue
    return None


def fetch_cursor():
    secrets = _secrets()
    cookie = secrets.get("cursor_cookie")
    token = secrets.get("cursor_token") or _cursor_token_from_vscdb()
    headers = {}
    if cookie:
        headers["Cookie"] = cookie if cookie.lower().startswith("cookie:") is False else cookie.split(":", 1)[1].strip()
        source = "cursor-cookie"
    elif token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Cookie"] = f"WorkosCursorSessionToken={token}"
        source = "cursor-token"
    else:
        return _err("cursor", "未找到 Cursor 登录。把 Cookie 写到 quota-secrets.json 的 cursor_cookie，或安装并登录 Cursor")
    status, data = _http_json("https://cursor.com/api/usage-summary", headers=headers)
    if status in (401, 403):
        return _err("cursor", "Cursor 会话无效，请更新 cookie")
    if status != 200 or not isinstance(data, dict):
        return _err("cursor", f"HTTP {status}")
    plan = ((data.get("individualUsage") or {}).get("plan") or {})
    pct = plan.get("totalPercentUsed")
    if pct is None:
        auto, api = plan.get("autoPercentUsed"), plan.get("apiPercentUsed")
        if auto is not None and api is not None:
            pct = (float(auto) + float(api)) / 2
        else:
            pct = api if api is not None else auto
    if pct is None:
        pct = _pct(plan.get("used"), plan.get("limit"))
    if pct is None:
        overall = (data.get("individualUsage") or {}).get("overall") or {}
        pct = _pct(overall.get("used"), overall.get("limit"))
    if pct is None:
        return _err("cursor", "usage-summary 里没有百分比")
    reset_at = _iso_to_ts(data.get("billingCycleEnd"))
    return _ok("cursor", float(pct), source, f"Cursor 计划 {float(pct):.1f}%", reset_at)


# ---------- 路由 ----------
def detect_kind(tool: dict) -> str | None:
    hay = f"{tool.get('name', '')} {tool.get('provider', '')}".lower()
    rules = [
        ("chatgpt", ["chatgpt", "openai", "gpt", "codex"]),
        ("claude", ["claude", "anthropic"]),
        ("cursor", ["cursor"]),
        ("grok", ["grok", "xai"]),
        ("kimi", ["kimi", "moonshot", "月之暗面"]),
    ]
    for kind, keys in rules:
        if any(k in hay for k in keys):
            return kind
    return None


FETCHERS = {
    "chatgpt": fetch_chatgpt,
    "claude": fetch_claude,
    "kimi": fetch_kimi,
    "grok": fetch_grok,
    "cursor": fetch_cursor,
}


def fetch_one(tool: dict) -> dict:
    kind = detect_kind(tool)
    if not kind:
        return {**_err("unknown", "暂不支持自动拉取"), "id": tool.get("id"), "name": tool.get("name")}
    try:
        result = FETCHERS[kind]()
    except Exception as e:
        result = _err(kind, str(e))
    result["id"] = tool.get("id")
    result["name"] = tool.get("name")
    result["kind"] = kind
    return result


def fetch_all(tools: list, max_workers=5) -> list:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(fetch_one, t): t for t in tools}
        for fut in as_completed(futs):
            results.append(fut.result())
    order = {t.get("id"): i for i, t in enumerate(tools)}
    results.sort(key=lambda r: order.get(r.get("id"), 999))
    return results


def apply_results(tools: list, results: list) -> list:
    by_id = {r.get("id"): r for r in results}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for t in tools:
        item = dict(t)
        r = by_id.get(t.get("id"))
        if r and r.get("ok") and r.get("quotaPct") is not None:
            item["quotaPct"] = r["quotaPct"]
            item["quotaLive"] = True
            item["quotaSource"] = r.get("source")
            item["quotaDetail"] = r.get("detail")
            item["quotaFetchedAt"] = now
            item["quotaError"] = None
            if r.get("resetAt"):
                item["quotaResetAt"] = r["resetAt"]
        elif r:
            item["quotaLive"] = False
            item["quotaError"] = r.get("error")
            item["quotaFetchedAt"] = now
        out.append(item)
    return out


def refresh_data_file(path=None):
    path = Path(path or DATA_FILE)
    tools = _load_json(path)
    if not isinstance(tools, list):
        return [], []
    results = fetch_all(tools)
    updated = apply_results(tools, results)
    path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return updated, results


if __name__ == "__main__":
    tools = _load_json(DATA_FILE) or []
    for r in fetch_all(tools):
        if r.get("ok"):
            print(f"OK  {r.get('name')}: {r.get('quotaPct')}%  ({r.get('source')}) {r.get('detail')}")
        else:
            print(f"ERR {r.get('name')}: {r.get('error')}")
