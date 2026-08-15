#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雪糕 · 完整视图（pywebview 原生窗口）。

把 index.html 包进本机 WebView2 窗口，数据经 JS API 直接读写
ai-tools-data.json（与桌面小窗、浏览器版共用同一份文件）。
实时额度仍需在页面右上角手动点 ↻ 拉取。
"""
import ctypes
import json
import os
import sys
import time
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "ai-tools-data.json")
INDEX = os.path.join(HERE, "index.html")
ICON = os.path.join(HERE, "logo.png")
ICON_ICO = os.path.join(HERE, "logo.ico")

try:
    import webview
except Exception as e:  # noqa: BLE001
    webview = None
    _IMPORT_ERR = e
else:
    _IMPORT_ERR = None


class Api:
    """暴露给前端 window.pywebview.api。"""

    def __init__(self):
        self._window = None
        self._ready = False  # pywebview 就绪后设为 True

    # ---- 窗口控制（frameless 下供自定义标题栏调用） ----
    def win_minimize(self):
        if self._window:
            self._window.minimize()

    def win_close(self):
        if self._window:
            self._window.destroy()

    def win_start_drag(self):
        """从当前鼠标位置开始原生拖动，窗口不会跳到别处。"""
        hwnd = self._hwnd()
        if not hwnd:
            return False

        def _drag():
            user32 = ctypes.windll.user32
            user32.ReleaseCapture()
            # WM_NCLBUTTONDOWN + HTCAPTION：按住左键从点击处拖窗口
            user32.SendMessageW(hwnd, 0x00A1, 2, 0)

        native = getattr(self._window, "native", None)
        try:
            if native is not None and getattr(native, "InvokeRequired", False):
                from System import Action
                native.BeginInvoke(Action(_drag))
                return True
        except Exception:
            pass
        _drag()
        return True

    def win_move(self, x, y):
        """JS 回退拖动：传入的是屏幕坐标（screenX - clientX）。"""
        if self._window:
            self._window.move(int(x), int(y))

    def win_get_pos(self):
        """返回 [x, y]，供 JS 拖动时取当前窗口位置。"""
        if self._window:
            return (self._window.x, self._window.y)
        return (0, 0)

    def _hwnd(self):
        native = getattr(self._window, "native", None) if self._window else None
        if native is not None:
            handle = getattr(native, "Handle", None)
            if handle is not None:
                try:
                    return int(handle.ToInt64())
                except Exception:
                    try:
                        return int(handle)
                    except Exception:
                        pass
        return ctypes.windll.user32.GetForegroundWindow() or 0

    # ---- 数据 ----
    def get_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:  # noqa: BLE001
            pass
        return []

    def save_data(self, tools):
        try:
            if not isinstance(tools, list):
                return {"ok": False, "error": "顶层必须是数组"}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(tools, f, ensure_ascii=False, indent=2)
            return {"ok": True}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def refresh_quota(self):
        try:
            from quota_fetch import refresh_data_file
            tools, results = refresh_data_file()
            return {
                "ok": True,
                "tools": tools,
                "results": [
                    {
                        "id": r.get("id"),
                        "name": r.get("name"),
                        "ok": r.get("ok"),
                        "quotaPct": r.get("quotaPct"),
                        "source": r.get("source"),
                        "detail": r.get("detail"),
                        "error": r.get("error"),
                    }
                    for r in results
                ],
            }
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}


def main():
    # 在 pywebview 启动前给进程设独立 AppUserModelID，让任务栏显示成“雪糕”而非 pythonw
    _set_app_user_model_id()
    if webview is None:
        # 没有 pywebview 时回退到浏览器 + 本地服务器
        import subprocess
        import webbrowser
        py = sys.executable
        if py.lower().endswith("python.exe"):
            alt = py[:-10] + "pythonw.exe"
            if os.path.exists(alt):
                py = alt
        subprocess.Popen(
            [py, os.path.join(HERE, "server.py"), "8099"],
            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        webbrowser.open("http://127.0.0.1:8099/index.html")
        return

    api = Api()
    api._ready = True  # API 立即可用，JS 拖动无需等待

    def on_started():
        # 窗口已启动，后台设置图标
        threading.Thread(target=_icon_thread, daemon=True).start()

    window = webview.create_window(
        "雪糕 · AI 额度与订阅提醒",
        INDEX,
        js_api=api,
        width=1032,
        height=880,
        min_size=(760, 560),
        background_color="#0c0d11",
        text_select=True,
        frameless=True,
        easy_drag=False,
        draggable=False,
        shadow=True,
    )
    api._window = window
    webview.start(on_started)


def _icon_thread():
    """后台线程：等窗口就绪后设置图标。"""
    for _ in range(20):
        time.sleep(0.25)
        if _set_window_icon_once():
            break


_set_icon_done = False


def _set_window_icon_once():
    global _set_icon_done
    if _set_icon_done:
        return True
    if not os.path.exists(ICON_ICO):
        return True
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # 枚举本进程的可见顶层窗口（frameless 下即 WebView2 宿主窗口）
    pid = kernel32.GetCurrentProcessId()
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _enum(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid and not user32.GetWindow(hwnd, 4):  # GW_OWNER=4，只取无主顶层窗
            found.append(hwnd)
        return True

    user32.EnumWindows(_enum, 0)
    hwnd = found[0] if found else (user32.GetForegroundWindow() or user32.GetActiveWindow())
    if not hwnd:
        return False
    try:
        LR_LOADFROMFILE = 0x00000010
        IMAGE_ICON = 1
        WM_SETICON = 0x0080
        ICON_SMALL, ICON_BIG = 0, 1
        hicon_big = user32.LoadImageW(None, ICON_ICO, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
        hicon_small = user32.LoadImageW(None, ICON_ICO, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
        if hicon_big:
            user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
        if hicon_small:
            user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        if hicon_big or hicon_small:
            _set_icon_done = True
            return True
    except Exception:  # noqa: BLE001
        return True
    return False


def _set_app_user_model_id():
    """给进程设独立 AppUserModelID，让任务栏把它当独立应用（雪糕）而非 pythonw.exe。"""
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("XueGao.QuotaTracker")
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    main()
