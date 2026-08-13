#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雪糕 · Windows 桌面原生小窗（tkinter 实现，无需浏览器/服务器）。

直接读取同目录下的 ai-tools-data.json，展示下一次重置倒计时、
最近到期工具列表及额度进度条；数据为手工维护，不自动刷新。
"""
import os
import json
import webbrowser
import subprocess
import socket
import threading
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone, timedelta

try:
    import tkinter as tk
    import tkinter.font as tkfont
except Exception:
    tk = None
    tkfont = None

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
except Exception:
    Image = ImageTk = ImageDraw = ImageFilter = None

# ---------- 路径 ----------
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "ai-tools-data.json")
LOGO_FILE = os.path.join(HERE, "logo.png")
LOGO_CUT_FILE = os.path.join(HERE, "logo-cut.png")
ASSETS_DIR = os.path.join(HERE, "assets")
SERVER_PORT = 8099

# ---------- 主题 ----------
BG = "#0c0d11"
SURFACE = "#14161c"
SURFACE2 = "#1b1e27"
BORDER = "#2b3040"
TEXT = "#e9eaf0"
MUTED = "#9296a6"
ACCENT = "#8b7cf6"
TEAL = "#45d2c6"
ORANGE = "#f5a524"
RED = "#f87171"
HERO_BG = "#161922"
TRACK = "#20232e"

WEEKDAYS = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
BRAND_RULES = [
    (["openai", "chatgpt", "gpt"], "#ffffff"),
    (["anthropic", "claude"], "#d97757"),
    (["cursor"], "#ffffff"),
    (["grok", "xai"], "#ffffff"),
    (["kimi", "moonshot"], "#1783ff"),
    (["perplexity"], "#20b8cd"),
]
ICON_MAP = [
    (["openai", "chatgpt", "gpt"], "openai"),
    (["anthropic", "claude"], "anthropic"),
    (["xai", "grok"], "xai"),
    (["cursor"], "cursor"),
    (["kimi"], "kimi"),
    (["moonshot", "月之暗面"], "moonshot"),
    (["agnes"], "agnes"),
    (["perplexity"], "perplexity"),
    (["gemini", "google"], "gemini"),
    (["deepseek"], "deepseek"),
    (["copilot"], "copilot"),
]


# ---------- 纯逻辑 ----------
def next_date(cfg, now):
    """根据 reset/expiry 配置，返回下一次发生的 UTC 时间。"""
    d = now.replace(minute=0, second=0, microsecond=0)
    period = (cfg or {}).get("period", "monthly")
    day = (cfg or {}).get("day", 1)
    hour = (cfg or {}).get("hour", 0)
    minute = (cfg or {}).get("minute", 0)

    if period == "weekly":
        jdow = (d.weekday() + 1) % 7
        target = d.replace(hour=hour, minute=minute)
        diff = (day - jdow + 7) % 7
        target = target + timedelta(days=diff)
        if target <= now:
            target = target + timedelta(days=7)
        return target

    if period == "daily":
        target = d.replace(hour=hour, minute=minute)
        if target <= now:
            target = target + timedelta(days=1)
        return target

    target = datetime(now.year, now.month, day, hour, minute, tzinfo=timezone.utc)
    if target <= now:
        y, m = target.year, target.month + 1
        if m > 12:
            y, m = y + 1, 1
        target = datetime(y, m, day, hour, minute, tzinfo=timezone.utc)
    return target


def rel(ms):
    total = max(0, int(ms / 1000))
    days = total // 86400
    hours = (total % 86400) // 3600
    return days, hours


def fmt(d):
    return f"{d.month}/{d.day} {WEEKDAYS[(d.weekday() + 1) % 7]}"


def brand_color(name):
    n = (name or "").lower()
    for keys, color in BRAND_RULES:
        if any(k in n for k in keys):
            return color
    return "#7b8095"


def quota_color(pct):
    if pct >= 80:
        return RED
    if pct >= 50:
        return ORANGE
    return TEAL


def load_tools():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def compute_views(tools, now=None):
    now = now or datetime.now(timezone.utc)
    views = []
    for t in tools:
        reset = next_date(t.get("reset"), now)
        expiry = next_date(t.get("expiry"), now)
        rd, rh = rel((reset - now).total_seconds() * 1000)
        ed, eh = rel((expiry - now).total_seconds() * 1000)
        pct = int(round(t.get("quotaPct", 0) or 0))
        reset_h = rd * 24 + rh
        expiry_h = ed * 24 + eh
        reset_soon = reset_h <= 48
        expiry_soon = expiry_h <= 24 * 7
        if expiry_soon:
            status = ORANGE
        elif reset_soon:
            status = ACCENT
        else:
            status = "#2f3444"
        views.append({
            "name": t.get("name", "?"),
            "quotaPct": pct,
            "resetDays": rd, "resetHours": rh,
            "expiryDays": ed, "expiryHours": eh,
            "resetDate": fmt(reset), "expiryDate": fmt(expiry),
            "color": brand_color(t.get("name", "")),
            "bar": quota_color(pct),
            "statusColor": status,
        })
    return views


# ---------- 原生 GUI ----------
def round_rect(canvas, x, y, w, h, r, fill=None, outline=None, **kw):
    """拼圆角矩形。填充块用同色描边，避免矩形边在转角画出横竖线。"""
    fill = fill if fill is not None else kw.get("fill")
    outline = outline if outline is not None else kw.get("outline")
    r = int(max(1, min(r, w / 2.0, h / 2.0)))
    if fill:
        opts = {"fill": fill, "outline": fill}
        canvas.create_arc(x, y, x + 2 * r, y + 2 * r, start=90, extent=90, style="pieslice", **opts)
        canvas.create_arc(x + w - 2 * r, y, x + w, y + 2 * r, start=0, extent=90, style="pieslice", **opts)
        canvas.create_arc(x, y + h - 2 * r, x + 2 * r, y + h, start=180, extent=90, style="pieslice", **opts)
        canvas.create_arc(x + w - 2 * r, y + h - 2 * r, x + w, y + h, start=270, extent=90, style="pieslice", **opts)
        canvas.create_rectangle(x + r, y, x + w - r, y + h, **opts)
        canvas.create_rectangle(x, y + r, x + w, y + h - r, **opts)
    if outline and outline != fill:
        canvas.create_arc(x, y, x + 2 * r, y + 2 * r, start=90, extent=90, style="arc", outline=outline)
        canvas.create_arc(x + w - 2 * r, y, x + w, y + 2 * r, start=0, extent=90, style="arc", outline=outline)
        canvas.create_arc(x, y + h - 2 * r, x + 2 * r, y + h, start=180, extent=90, style="arc", outline=outline)
        canvas.create_arc(x + w - 2 * r, y + h - 2 * r, x + w, y + h, start=270, extent=90, style="arc", outline=outline)
        canvas.create_line(x + r, y, x + w - r, y, fill=outline)
        canvas.create_line(x + r, y + h - 1, x + w - r, y + h - 1, fill=outline)
        canvas.create_line(x, y + r, x, y + h - r, fill=outline)
        canvas.create_line(x + w - 1, y + r, x + w - 1, y + h - r, fill=outline)


def make_round_bg(w, h, r, fill, outline, key=(0, 0, 0), scale=4):
    """超采样抗锯齿圆角底图。外侧纯黑，供 transparentcolor 抠透明。"""
    if Image is None:
        return None
    resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    W, H, R = w * scale, h * scale, r * scale
    img = Image.new("RGB", (W, H), key)
    draw = ImageDraw.Draw(img)
    fill_rgb = _hex_rgb(fill)
    line_rgb = _hex_rgb(outline)
    draw.rounded_rectangle((0, 0, W - 1, H - 1), radius=R, fill=fill_rgb)
    # 描边画在填充内侧，避免和抠色混在一起发虚
    inset = scale
    draw.rounded_rectangle(
        (inset, inset, W - inset - 1, H - inset - 1),
        radius=max(0, R - inset),
        outline=line_rgb,
        width=scale,
    )
    img = img.resize((w, h), resample)
    # 四角外侧接近黑色的像素钉死为 key，保证抠色干净；过渡像素保留作抗锯齿
    px = img.load()
    band = r + 6
    kr, kg, kb = key
    fr, fg, fb = fill_rgb
    corners = (
        (0, 0, min(band, w), min(band, h)),
        (max(0, w - band), 0, w, min(band, h)),
        (0, max(0, h - band), min(band, w), h),
        (max(0, w - band), max(0, h - band), w, h),
    )
    for x0, y0, x1, y1 in corners:
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                r0, g0, b0 = px[xx, yy]
                dk = abs(r0 - kr) + abs(g0 - kg) + abs(b0 - kb)
                df = abs(r0 - fr) + abs(g0 - fg) + abs(b0 - fb)
                if dk <= 10 and dk < df:
                    px[xx, yy] = key
    return ImageTk.PhotoImage(img)


def _hex_rgb(h):
    h = (h or "").lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def logo_source():
    return LOGO_CUT_FILE if os.path.exists(LOGO_CUT_FILE) else LOGO_FILE


def render_logo(size, rotate=0, glow=False, bg=BG):
    """把 logo 画到指定底色上（避免透明像素变成 #000 被窗口抠穿）。"""
    path = logo_source()
    if not os.path.exists(path):
        return None
    if Image is None:
        try:
            raw = tk.PhotoImage(file=path)
            factor = max(1, int(min(raw.width(), raw.height()) / max(size, 1)))
            return raw.subsample(factor, factor)
        except Exception:
            return None
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((size, size), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)

    box = size + (12 if glow else 6)
    layer = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    layer.paste(im, ((box - im.width) // 2, (box - im.height) // 2), im)
    if rotate:
        layer = layer.rotate(rotate, resample=Image.BICUBIC, expand=False)

    out = Image.new("RGBA", (box, box), _hex_rgb(bg) + (255,))
    if glow:
        halo = Image.new("RGBA", (box, box), (0, 0, 0, 0))
        draw = ImageDraw.Draw(halo)
        cx = cy = box / 2
        max_r = box * 0.40
        for i in range(int(max_r), 0, -1):
            t = 1 - i / max_r
            draw.ellipse((cx - i, cy - i, cx + i, cy + i),
                         fill=(233, 120, 168, int(88 * (t ** 2.1))))
        out.alpha_composite(halo.filter(ImageFilter.GaussianBlur(5)))
        # 轻微下落影
        sh = Image.new("RGBA", (box, box), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 110), (0, 5), layer.split()[-1])
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    out.alpha_composite(layer)
    return ImageTk.PhotoImage(out)


def render_float_badge(disc=54, pad=16, pad_bottom=30):
    """抗锯齿圆形底 + 软阴影 + 雪糕。底部多留空，避免下落影被裁切。"""
    if Image is None or not os.path.exists(logo_source()):
        return None, (disc, disc)
    resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    scale = 4
    bw, bh = disc + pad * 2, disc + pad + pad_bottom
    W, H = bw * scale, bh * scale
    D = disc * scale
    Px, Py = pad * scale, pad * scale

    # 阴影：黑色 + 真 alpha，由分层窗口半透明显示
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    s = scale
    sd.ellipse((Px + 2 * s, Py + 6 * s, Px + D + 3 * s, Py + D + 10 * s),
               fill=(0, 0, 0, 160))
    sd.ellipse((Px - 1 * s, Py + 4 * s, Px + D + 5 * s, Py + D + 12 * s),
               fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(4.5 * scale)))

    # 圆形底盘 + 描边（hi-res，缩小后抗锯齿）
    disc_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc_img)
    dd.ellipse((Px, Py, Px + D - 1, Py + D - 1), fill=_hex_rgb(BG) + (255,))
    dd.ellipse((Px, Py, Px + D - 1, Py + D - 1),
               outline=_hex_rgb(BORDER) + (255,), width=scale)

    # 粉色光晕
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = Px + D / 2, Py + D / 2
    max_r = D * 0.36
    for i in range(int(max_r), 0, -1):
        t = 1 - i / max_r
        gd.ellipse((cx - i, cy - i, cx + i, cy + i),
                   fill=(233, 120, 168, int(70 * (t ** 2.1))))
    glow = glow.filter(ImageFilter.GaussianBlur(int(1.6 * scale)))

    # 雪糕
    ice = Image.open(logo_source()).convert("RGBA")
    bbox = ice.getbbox()
    if bbox:
        ice = ice.crop(bbox)
    ice_size = int(disc * 0.72 * scale)
    ice.thumbnail((ice_size, ice_size), resample)
    ice = ice.rotate(-10, resample=Image.BICUBIC, expand=True)
    ice_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ice_layer.paste(ice, (int(cx - ice.width / 2), int(cy - ice.height / 2 + scale)), ice)

    acc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    acc.alpha_composite(shadow)
    acc.alpha_composite(disc_img)
    acc.alpha_composite(glow)
    acc.alpha_composite(ice_layer)
    acc = acc.resize((bw, bh), resample)
    return acc, (bw, bh)


# ---- Windows 逐像素透明（浮动圆标阴影需要真半透明）----
class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class _SIZE(ctypes.Structure):
    _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]


class _BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ("BlendOp", ctypes.c_byte),
        ("BlendFlags", ctypes.c_byte),
        ("SourceConstantAlpha", ctypes.c_byte),
        ("AlphaFormat", ctypes.c_byte),
    ]


class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class _BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", _BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


_user32 = ctypes.windll.user32
_gdi32 = ctypes.windll.gdi32
if ctypes.sizeof(ctypes.c_void_p) == 8:
    _GetWindowLong = _user32.GetWindowLongPtrW
    _SetWindowLong = _user32.SetWindowLongPtrW
    _GetWindowLong.restype = ctypes.c_longlong
    _SetWindowLong.restype = ctypes.c_longlong
    _SetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong]
else:
    _GetWindowLong = _user32.GetWindowLongW
    _SetWindowLong = _user32.SetWindowLongW

_WS_EX_LAYERED = 0x00080000
_GWL_EXSTYLE = -20
_ULW_ALPHA = 0x00000002
_AC_SRC_OVER = 0x00
_AC_SRC_ALPHA = 0x01
_gdi32.CreateCompatibleDC.restype = wintypes.HDC
_gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
_gdi32.CreateDIBSection.restype = ctypes.c_void_p
_gdi32.CreateDIBSection.argtypes = [
    wintypes.HDC, ctypes.c_void_p, wintypes.UINT,
    ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.DWORD,
]
_gdi32.SelectObject.restype = ctypes.c_void_p
_gdi32.SelectObject.argtypes = [wintypes.HDC, ctypes.c_void_p]
_gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
_gdi32.DeleteDC.argtypes = [wintypes.HDC]
_user32.UpdateLayeredWindow.restype = wintypes.BOOL
_user32.UpdateLayeredWindow.argtypes = [
    wintypes.HWND, wintypes.HDC,
    ctypes.POINTER(_POINT), ctypes.POINTER(_SIZE),
    wintypes.HDC, ctypes.POINTER(_POINT),
    wintypes.COLORREF, ctypes.POINTER(_BLENDFUNCTION),
    wintypes.DWORD,
]


def _hwnd_of(widget):
    wid = int(widget.winfo_id())
    parent = _user32.GetParent(wid)
    return parent or wid


def apply_layered_rgba(hwnd, pil_img, x, y):
    """用 UpdateLayeredWindow 把 RGBA 图画到窗口，阴影按 alpha 半透明。"""
    im = pil_img.convert("RGBA")
    w, h = im.size
    src = im.tobytes()
    bgra = bytearray(w * h * 4)
    for i in range(w * h):
        r, g, b, a = src[i * 4:i * 4 + 4]
        bgra[i * 4] = b * a // 255
        bgra[i * 4 + 1] = g * a // 255
        bgra[i * 4 + 2] = r * a // 255
        bgra[i * 4 + 3] = a

    bmi = _BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0

    hdc_screen = _user32.GetDC(0)
    hdc_mem = _gdi32.CreateCompatibleDC(hdc_screen)
    bits = ctypes.c_void_p()
    hbmp = _gdi32.CreateDIBSection(
        hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(bits), None, 0)
    if not hbmp or not bits.value:
        _gdi32.DeleteDC(hdc_mem)
        _user32.ReleaseDC(0, hdc_screen)
        return False
    ctypes.memmove(bits, bytes(bgra), len(bgra))
    old = _gdi32.SelectObject(hdc_mem, hbmp)

    ex = _GetWindowLong(hwnd, _GWL_EXSTYLE)
    _SetWindowLong(hwnd, _GWL_EXSTYLE, ex | _WS_EX_LAYERED)

    blend = _BLENDFUNCTION(_AC_SRC_OVER, 0, 255, _AC_SRC_ALPHA)
    dst = _POINT(int(x), int(y))
    src_pt = _POINT(0, 0)
    size = _SIZE(w, h)
    ok = _user32.UpdateLayeredWindow(
        hwnd, hdc_screen,
        ctypes.byref(dst), ctypes.byref(size),
        hdc_mem, ctypes.byref(src_pt),
        0, ctypes.byref(blend), _ULW_ALPHA,
    )

    _gdi32.SelectObject(hdc_mem, old)
    _gdi32.DeleteObject(hbmp)
    _gdi32.DeleteDC(hdc_mem)
    _user32.ReleaseDC(0, hdc_screen)
    return bool(ok)


def load_brand_icon(name, target_size=22):
    """加载品牌 PNG 图标；失败返回 None。"""
    n = (name or "").lower()
    key = None
    for keys, k in ICON_MAP:
        if any(kk in n for kk in keys):
            key = k
            break
    if not key:
        return None
    path = os.path.join(ASSETS_DIR, f"{key}.png")
    if not os.path.exists(path):
        return None
    try:
        raw = tk.PhotoImage(file=path)
        factor = max(1, int(min(raw.width(), raw.height()) / target_size))
        return raw.subsample(factor, factor)
    except Exception:
        return None


class WidgetApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("雪糕 · 桌面小窗")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#000000")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)

        self.W, self.H = 293, 740
        self.R = 16          # 圆角弧度；内容内缩需 >= R 才不会被圆角裁切
        self._dock_right = False
        try:
            sw = self.root.winfo_screenwidth()
            # 贴右时把圆角推出屏外
            x = sw - self.W + self.R
            y = 24
            self._dock_right = True
        except Exception:
            x, y = 200, 200
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#000000", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self._bg_img = make_round_bg(self.W, self.H, self.R, BG, BORDER)
        if self._bg_img:
            self.canvas.create_image(0, 0, image=self._bg_img, anchor="nw")
        else:
            round_rect(self.canvas, 0, 0, self.W, self.H, self.R,
                       fill=BG, outline=BORDER)

        self.content = tk.Frame(self.canvas, bg=BG)
        self.content.place(x=self.R, y=self.R,
                           width=self.W - 2 * self.R, height=self.H - 2 * self.R)

        # 缓存图标，避免被 GC
        self.icons = {}
        self._float_win = None
        self._float_logo = None

        self.logo_img = None
        self._header_logo = None

        self._build_header()
        self.hero = tk.Frame(self.content, bg=HERO_BG)
        self.hero.pack(fill="x", padx=5, pady=(8, 8))
        self.list_area = tk.Frame(self.content, bg=BG)
        self.list_area.pack(fill="both", expand=True, padx=5)
        self._build_footer()

        # 整个内容区（含顶部空白、hero、列表）均可拖动
        self._dx = self._dy = 0
        self._dragging = False
        for w in (self.content, self.canvas, self.root):
            w.bind("<ButtonPress-1>", self._start_drag)
            w.bind("<B1-Motion>", self._on_drag)

        self.menu = tk.Menu(self.root, tearoff=0,
                            bg=SURFACE, fg=TEXT, activebackground=SURFACE2,
                            activeforeground=TEXT, bd=0)
        self.menu.add_command(label="↻ 刷新额度", command=self.refresh)
        self.menu.add_command(label="🗔 打开完整视图", command=self.open_full_view)
        self.menu.add_checkbutton(label="📌 始终置顶", command=self.toggle_top,
                                  variable=tk.BooleanVar(value=True))
        self.menu.add_separator()
        self.menu.add_command(label="✕ 退出", command=self.root.destroy)
        for w in (self.content, self.canvas, self.root):
            w.bind("<Button-3>", lambda e: (self.menu.post(e.x_root, e.y_root), "break")[1])

        # 鼠标移入窗口显示关闭按钮，移出隐藏
        self.root.bind("<Enter>", lambda e: self._show_close())
        self.root.bind("<Leave>", lambda e: self._hide_close())
        # 拖拽释放后吸附到就近边缘
        self.root.bind("<ButtonRelease-1>", lambda e: self._snap())

        self._quota_busy = False
        self.refresh()
        self.root.after(5 * 60 * 1000, self._quota_tick)

    # ---- 头部 ----
    def _build_header(self):
        self.header = tk.Frame(self.content, bg=BG)
        self.header.pack(fill="x", padx=2, pady=(2, 0))

        row = tk.Frame(self.header, bg=BG)
        row.pack(fill="x")

        self._header_logo = render_logo(51, rotate=-12, glow=True, bg=BG)
        if self._header_logo:
            self.logo_lbl = tk.Label(row, image=self._header_logo, bg=BG,
                                     cursor="hand2", bd=0)
        else:
            self.logo_lbl = tk.Label(row, text="🍦", bg=BG, fg=TEXT,
                                     font=("Segoe UI", 20), cursor="hand2")
        self.logo_lbl.pack(side="left")
        self.logo_lbl.bind("<Double-Button-1>", lambda e: (self._minimize(), "break")[1])

        texts = tk.Frame(row, bg=BG)
        texts.pack(side="left", fill="both", expand=True, padx=(2, 2))
        inner = tk.Frame(texts, bg=BG)
        inner.place(relx=0, rely=0.5, y=-1, anchor="w")

        self.title_lbl = tk.Label(inner, text="雪糕", bg=BG, fg=TEXT,
                                  font=("Microsoft YaHei UI", 20, "bold"),
                                  anchor="w")
        self.title_lbl.pack(anchor="w")
        slogan = "额度和订阅都会化 · 趁没化之前用掉它"
        slogan_size = 8
        slogan_fnt = tkfont.Font(family="Microsoft YaHei UI", size=slogan_size)
        avail = self.W - 2 * self.R - 12 - 64
        while slogan_fnt.measure(slogan) > avail and slogan_size > 7:
            slogan_size -= 1
            slogan_fnt = tkfont.Font(family="Microsoft YaHei UI", size=slogan_size)
        tk.Label(
            inner,
            text=slogan,
            bg=BG, fg="#7d8296",
            font=slogan_fnt,
            justify="left", anchor="w",
        ).pack(anchor="w", pady=(5, 0))

        sep = tk.Frame(self.header, bg="#1e212b", height=1)
        sep.pack(fill="x", padx=2, pady=(4, 2))

        # 右上角关闭按钮；默认隐藏，hover 时显示。菜单改到右键
        self.topright = tk.Frame(self.content, bg=BG)
        self.topright.place(relx=1.0, x=-4, y=10, anchor="ne")

        self.close_btn = tk.Label(self.topright, text="✕", bg=BG, fg=MUTED,
                                  font=("Segoe UI", 11), cursor="hand2", width=2)
        self.close_btn.bind("<Button-1>", lambda e: (self.root.destroy(), "break")[1])

    # ---- 底部 ----
    def _build_footer(self):
        footer = tk.Frame(self.content, bg=BG)
        footer.pack(fill="x", padx=5, pady=(3, 5))
        tk.Label(footer, text="●", bg=BG, fg=ORANGE, font=("Segoe UI", 8)).pack(side="left")
        self.update_lbl = tk.Label(footer, text="", bg=BG, fg=MUTED,
                                   font=("Segoe UI", 10))
        self.update_lbl.pack(side="left", padx=(4, 0))

    # ---- 品牌徽标（回退） ----
    def _badge(self, parent, letter, color, size=22):
        f = tk.Frame(parent, bg=parent["bg"], width=size, height=size)
        cv = tk.Canvas(f, width=size, height=size, bg=parent["bg"],
                       highlightthickness=0, bd=0)
        cv.pack(fill="both", expand=True)
        r = size // 2
        round_rect(cv, 1, 1, size - 2, size - 2, r - 2, fill=color, outline=color)
        cv.create_text(size / 2, size / 2 + 1, text=letter, fill="#ffffff",
                       font=("Segoe UI", 11, "bold"))
        return f

    def _brand_widget(self, parent, name, color, size=22):
        """优先显示品牌 PNG 图标，失败回退字母徽章。"""
        icon = self.icons.get(name)
        if icon is None and name not in self.icons:
            icon = load_brand_icon(name, size)
            self.icons[name] = icon
        if icon:
            lbl = tk.Label(parent, image=icon, bg=parent["bg"], width=size, height=size)
            lbl.pack(side="left")
            return lbl
        return self._badge(parent, name[0:1].upper(), color, size)

    # ---- 渲染动态内容 ----
    def refresh(self):
        self._render_from_disk()
        self._kick_live_quota()

    def _quota_tick(self):
        self.refresh()
        try:
            self.root.after(5 * 60 * 1000, self._quota_tick)
        except Exception:
            pass

    def _kick_live_quota(self):
        if getattr(self, "_quota_busy", False):
            return
        self._quota_busy = True

        def work():
            try:
                from quota_fetch import refresh_data_file
                refresh_data_file()
            except Exception:
                pass
            try:
                self.root.after(0, self._after_live_quota)
            except Exception:
                self._quota_busy = False

        threading.Thread(target=work, daemon=True).start()

    def _after_live_quota(self):
        self._quota_busy = False
        self._render_from_disk()

    def _render_from_disk(self):
        tools = load_tools()
        if not tools:
            self._render_error()
            return
        views = compute_views(tools)

        # 按重置时间排序：hero 和列表都基于 reset
        views = sorted(views, key=lambda v: v["resetDays"] * 24 + v["resetHours"])
        hero = views[0]
        self._render_hero(hero)
        self._render_list(views[:6])

        now = datetime.now()
        live_n = sum(1 for t in tools if t.get("quotaLive"))
        suffix = f" · 实时 {live_n}" if live_n else ""
        self.update_lbl.config(text=f"更新于 {now.strftime('%H:%M')}{suffix}")

    def _render_hero(self, v):
        for w in self.hero.winfo_children():
            w.destroy()

        title_fnt = tkfont.Font(family="Microsoft YaHei UI", size=10)
        num_fnt = tkfont.Font(family="Segoe UI", size=44, weight="bold")
        unit_fnt = tkfont.Font(family="Microsoft YaHei UI", size=11)
        hour_fnt = tkfont.Font(family="Segoe UI", size=18, weight="bold")

        days = str(v["resetDays"])
        hours = str(v["resetHours"])
        left = 10
        title_y = 8
        title_h = title_fnt.metrics("linespace")
        num_ascent = num_fnt.metrics("ascent")
        unit_ascent = unit_fnt.metrics("ascent")
        hour_ascent = hour_fnt.metrics("ascent")
        # 标题与数字留出空隙，不再叠进字框
        num_y = title_y + title_h + 2
        baseline = num_y + num_ascent
        canvas_h = baseline + hour_fnt.metrics("descent") + 10

        cv = tk.Canvas(self.hero, bg=HERO_BG, highlightthickness=0, bd=0,
                       height=canvas_h)
        cv.pack(fill="x", padx=4, pady=(2, 4))

        cv.create_text(left, title_y, text="下一次重置", fill=MUTED,
                       font=title_fnt, anchor="nw")
        cv.create_text(left, baseline - num_ascent, text=days, fill=ACCENT,
                       font=num_fnt, anchor="nw")

        x = left + num_fnt.measure(days) + 10
        cv.create_text(x, baseline - unit_ascent, text="天", fill=MUTED,
                       font=unit_fnt, anchor="nw")
        x += unit_fnt.measure("天") + 6
        cv.create_text(x, baseline - hour_ascent, text=hours, fill=ACCENT,
                       font=hour_fnt, anchor="nw")
        x += hour_fnt.measure(hours) + 5
        cv.create_text(x, baseline - unit_ascent, text="时后重置", fill=MUTED,
                       font=unit_fnt, anchor="nw")


    def _render_list(self, items):
        for w in self.list_area.winfo_children():
            w.destroy()
        for v in items:
            item = tk.Frame(self.list_area, bg=SURFACE,
                            highlightbackground=BORDER, highlightthickness=1)
            item.pack(fill="x", pady=(0, 6), ipady=3)

            # 与 web 一致：左侧 3px 状态色条（到期橙 / 重置紫 / 其余暗灰）
            bar = tk.Frame(item, bg=v["statusColor"], width=3)
            bar.pack(side="left", fill="y")
            bar.pack_propagate(False)

            content = tk.Frame(item, bg=SURFACE)
            content.pack(side="left", fill="both", expand=True, padx=10, pady=(4, 4))

            # 第一行：图标+名称 | 剩余天数
            top = tk.Frame(content, bg=SURFACE)
            top.pack(fill="x")
            left = tk.Frame(top, bg=SURFACE)
            left.pack(side="left")
            self._brand_widget(left, v["name"], v["color"], 18)
            tk.Label(left, text=v["name"], bg=SURFACE, fg=TEXT,
                     font=("Segoe UI", 12, "bold")).pack(side="left", padx=(6, 0))

            tk.Label(top, text=f"{v['resetDays']}天{v['resetHours']}时",
                     bg=SURFACE, fg=v["bar"], font=("Segoe UI", 13, "bold")).pack(side="right")

            # 第二行：进度条 | 百分比 日期
            bottom = tk.Frame(content, bg=SURFACE)
            bottom.pack(fill="x", pady=(5, 0))

            track = tk.Frame(bottom, bg=TRACK, height=4)
            track.pack(side="left", fill="x", expand=True)
            track.pack_propagate(False)
            fill = tk.Frame(track, bg=v["bar"], height=4)
            fill.place(relx=0, rely=0, relheight=1,
                       relwidth=max(0, min(100, v["quotaPct"])) / 100)

            info = tk.Frame(bottom, bg=SURFACE)
            info.pack(side="right", padx=(8, 0))
            tk.Label(info, text=f"{v['quotaPct']}%", bg=SURFACE, fg=v["bar"],
                     font=("Segoe UI", 10)).pack(side="left")
            date_short = v["resetDate"].split()[0]
            tk.Label(info, text=f"{date_short} 重置", bg=SURFACE, fg=MUTED,
                     font=("Segoe UI", 10)).pack(side="left", padx=(8, 0))

    def _render_error(self):
        for w in self.list_area.winfo_children():
            w.destroy()
        tk.Label(self.list_area, text="无法读取 ai-tools-data.json",
                 bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(pady=40)

    # ---- 交互 ----
    def _snap_coords(self, x, y):
        """把窗口坐标吸附到就近的屏幕边缘（距离 SNAP 像素内则贴边）。"""
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
        except Exception:
            return x, y
        SNAP = 18
        r = self.R
        # 左：靠近或拖出左边缘 → 贴左
        if x <= SNAP:
            x = 0
            self._dock_right = False
        # 右：贴边后把圆角推出屏外；离开时按贴边位置判断，避免拖不走
        elif getattr(self, "_dock_right", False):
            if x < sw - self.W + r - SNAP:
                self._dock_right = False
            else:
                x = sw - self.W + r
        elif x + self.W >= sw - SNAP:
            self._dock_right = True
            x = sw - self.W + r
        # 上：靠近或拖出上边缘 → 贴顶
        if y <= SNAP:
            y = 0
        elif y + self.H >= sh - SNAP:
            y = sh - self.H
        return x, y

    def _snap(self):
        self.root.geometry(f"+{self.root.winfo_x()}+{self.root.winfo_y()}")
        x, y = self._snap_coords(self.root.winfo_x(), self.root.winfo_y())
        self.root.geometry(f"+{x}+{y}")

    def _show_close(self):
        if not self.close_btn.winfo_ismapped():
            self.close_btn.pack(side="right")

    def _hide_close(self):
        if self.close_btn.winfo_ismapped():
            self.close_btn.pack_forget()

    # ---- 最小化：收成圆形浮动 logo ----
    def _minimize(self):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.root.withdraw()
        self._show_float(x, y)

    def _show_float(self, x, y):
        if self._float_win is not None:
            return
        fw = tk.Toplevel(self.root)
        fw.withdraw()
        fw.overrideredirect(True)
        fw.attributes("-topmost", True)

        badge, (bw, bh) = render_float_badge()
        self._float_logo = badge
        self._float_size = (bw, bh)
        fw.geometry(f"{bw}x{bh}+{x}+{y}")
        fw.update_idletasks()

        layered = False
        if badge is not None:
            try:
                layered = apply_layered_rgba(_hwnd_of(fw), badge, x, y)
            except Exception:
                layered = False
        if not layered:
            fw.configure(bg="#000000")
            fw.attributes("-transparentcolor", "#000000")
            cv = tk.Canvas(fw, width=bw, height=bh, bg="#000000",
                           highlightthickness=0, bd=0)
            cv.pack()
            if badge is not None:
                self._float_photo = ImageTk.PhotoImage(badge.convert("RGBA"))
                cv.create_image(bw // 2, bh // 2, image=self._float_photo)
            else:
                cv.create_oval(2, 2, bw - 2, bh - 2, fill=BG, outline=BORDER, width=2)

        fw.deiconify()
        fw.attributes("-topmost", True)
        fw.bind("<ButtonPress-1>", self._float_start_drag)
        fw.bind("<B1-Motion>", self._float_drag)
        fw.bind("<ButtonRelease-1>", self._float_release)
        fw.bind("<Enter>", lambda e: fw.configure(cursor="hand2"))
        self._float_win = fw

    def _snap_float_coords(self, x, y, size=None):
        size = size or getattr(self, "_float_size", (86, 100))
        if isinstance(size, int):
            bw = bh = size
        else:
            bw, bh = size
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        SNAP = 18
        if x <= SNAP:
            x = 0
        elif x + bw >= sw - SNAP:
            x = sw - bw
        if y <= SNAP:
            y = 0
        elif y + bh >= sh - SNAP:
            y = sh - bh
        return x, y

    def _float_start_drag(self, e):
        self._float_dragging = True
        fw = self._float_win
        self._float_dx = e.x_root - fw.winfo_x()
        self._float_dy = e.y_root - fw.winfo_y()
        self._float_start = (e.x_root, e.y_root)

    def _float_drag(self, e):
        if not getattr(self, "_float_dragging", False):
            return
        fw = self._float_win
        x = e.x_root - self._float_dx
        y = e.y_root - self._float_dy
        fw.geometry(f"+{x}+{y}")

    def _float_release(self, e):
        self._float_dragging = False
        fw = self._float_win
        x, y = fw.winfo_x(), fw.winfo_y()
        x, y = self._snap_float_coords(x, y)
        fw.geometry(f"+{x}+{y}")
        # 位移很小视为点击：恢复主窗口
        if abs(e.x_root - self._float_start[0]) < 4 and abs(e.y_root - self._float_start[1]) < 4:
            self._restore()

    def _restore(self):
        if self._float_win is not None:
            self._float_win.destroy()
            self._float_win = None
        self.root.deiconify()

    def _start_drag(self, e):
        # 整个窗口（任意不透明区域）按住即可拖动
        # 菜单/关闭已返回 "break"，不会进入这里
        self._dragging = True
        self._dx = e.x_root - self.root.winfo_x()
        self._dy = e.y_root - self.root.winfo_y()

    def _on_drag(self, e):
        if not self._dragging:
            return
        x = e.x_root - self._dx
        y = e.y_root - self._dy
        x, y = self._snap_coords(x, y)
        self.root.geometry(f"+{x}+{y}")

    def toggle_top(self):
        cur = self.root.attributes("-topmost")
        self.root.attributes("-topmost", not cur)

    def open_full_view(self):
        url = f"http://127.0.0.1:{SERVER_PORT}/index.html"
        if not self._port_open(SERVER_PORT):
            try:
                subprocess.Popen(["pythonw", os.path.join(HERE, "server.py"), str(SERVER_PORT)],
                                 cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        webbrowser.open(url)

    @staticmethod
    def _port_open(port, host="127.0.0.1"):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            return s.connect_ex((host, port)) == 0
        finally:
            s.close()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        WidgetApp().run()
    except Exception:
        import traceback
        try:
            with open(os.path.join(HERE, "widget_error.log"), "w", encoding="utf-8") as _f:
                traceback.print_exc(file=_f)
        except Exception:
            pass
        raise
