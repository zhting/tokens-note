#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雪糕 · Windows 桌面原生小窗（tkinter 实现，无需浏览器/服务器）。

直接读取同目录下的 ai-tools-data.json，展示订阅统计、下一次重置倒计时、
最近到期工具列表及额度进度条，每分钟自动刷新。
"""
import os
import json
import webbrowser
import subprocess
import socket
from datetime import datetime, timezone, timedelta

try:
    import tkinter as tk
except Exception:
    tk = None

# ---------- 路径 ----------
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "ai-tools-data.json")
LOGO_FILE = os.path.join(HERE, "logo.png")
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
    (["openai", "chatgpt", "gpt"], "#10a37f"),
    (["anthropic", "claude"], "#d97757"),
    (["cursor"], "#1a1a1a"),
    (["grok", "xai"], "#4a4a4a"),
    (["kimi", "moonshot"], "#8b93ff"),
    (["perplexity"], "#20c997"),
]
ICON_MAP = [
    (["kimi", "moonshot"], "kimi"),
    (["chatgpt", "openai", "gpt"], "openai"),
    (["claude", "anthropic"], "claude"),
    (["grok", "xai"], "xai"),
    (["cursor"], "cursor"),
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
        views.append({
            "name": t.get("name", "?"),
            "quotaPct": pct,
            "resetDays": rd, "resetHours": rh,
            "expiryDays": ed, "expiryHours": eh,
            "resetDate": fmt(reset), "expiryDate": fmt(expiry),
            "color": brand_color(t.get("name", "")),
            "bar": quota_color(pct),
        })
    return views


# ---------- 原生 GUI ----------
def round_rect(canvas, x, y, w, h, r, **kw):
    canvas.create_arc(x, y, x + 2 * r, y + 2 * r, start=90, extent=90, style="pieslice", **kw)
    canvas.create_arc(x + w - 2 * r, y, x + w, y + 2 * r, start=0, extent=90, style="pieslice", **kw)
    canvas.create_arc(x, y + h - 2 * r, x + 2 * r, y + h, start=180, extent=90, style="pieslice", **kw)
    canvas.create_arc(x + w - 2 * r, y + h - 2 * r, x + w, y + h, start=270, extent=90, style="pieslice", **kw)
    canvas.create_rectangle(x + r, y, x + w - r, y + h, **kw)
    canvas.create_rectangle(x, y + r, x + w, y + h - r, **kw)


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

        self.W, self.H = 380, 660
        self.R = 22
        try:
            sw = self.root.winfo_screenwidth()
            x = sw - self.W - 24
            y = 24
        except Exception:
            x, y = 200, 200
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#000000", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        round_rect(self.canvas, 1, 1, self.W - 2, self.H - 2, self.R,
                   fill=BG, outline=BG)

        self.content = tk.Frame(self.canvas, bg=BG)
        self.content.place(x=self.R, y=self.R,
                           width=self.W - 2 * self.R, height=self.H - 2 * self.R)

        # 缓存图标，避免被 GC
        self.icons = {}

        self.logo_img = None
        if os.path.exists(LOGO_FILE):
            try:
                raw = tk.PhotoImage(file=LOGO_FILE)
                target = 32
                factor = max(1, int(min(raw.width(), raw.height()) / target))
                self.logo_img = raw.subsample(factor, factor)
            except Exception:
                self.logo_img = None

        self._build_header()
        self.hero = tk.Frame(self.content, bg=HERO_BG)
        self.hero.pack(fill="x", padx=16, pady=(12, 10))
        self.list_area = tk.Frame(self.content, bg=BG)
        self.list_area.pack(fill="both", expand=True, padx=16)
        self._build_footer()

        # 顶部区域（header + hero + 上方空白）均可拖动
        self._dx = self._dy = 0
        self._dragging = False
        self.DRAG_HEIGHT = 200
        self.content.bind("<ButtonPress-1>", self._start_drag)
        self.content.bind("<B1-Motion>", self._on_drag)

        self.menu = tk.Menu(self.root, tearoff=0,
                            bg=SURFACE, fg=TEXT, activebackground=SURFACE2,
                            activeforeground=TEXT, bd=0)
        self.menu.add_command(label="↻ 刷新", command=self.refresh)
        self.menu.add_command(label="🗔 打开完整视图", command=self.open_full_view)
        self.menu.add_checkbutton(label="📌 始终置顶", command=self.toggle_top,
                                  variable=tk.BooleanVar(value=True))
        self.menu.add_separator()
        self.menu.add_command(label="✕ 退出", command=self.root.destroy)

        # 鼠标移入窗口显示关闭按钮，移出隐藏
        self.root.bind("<Enter>", lambda e: self._show_close())
        self.root.bind("<Leave>", lambda e: self._hide_close())
        # 拖拽释放后吸附到就近边缘
        self.root.bind("<ButtonRelease-1>", lambda e: self._snap())

        self.refresh()
        self.root.after(60000, self._tick)

    # ---- 头部 ----
    def _build_header(self):
        self.header = tk.Frame(self.content, bg=BG)
        self.header.pack(fill="x", padx=16, pady=(12, 0))

        self.brand = tk.Frame(self.header, bg=BG)
        self.brand.pack(side="left")
        if self.logo_img:
            tk.Label(self.brand, image=self.logo_img, bg=BG, width=32, height=32).pack(side="left")
        else:
            tk.Label(self.brand, text="🍦", bg=BG, fg=TEXT, font=("Segoe UI", 20)).pack(side="left")
        self.title_lbl = tk.Label(self.brand, text="雪糕", bg=BG, fg=TEXT,
                                  font=("Segoe UI", 15, "bold"))
        self.title_lbl.pack(side="left", padx=(4, 0))

        self.stats = tk.Label(self.header, text="", bg=BG, fg=MUTED,
                              font=("Segoe UI", 10))
        self.stats.pack(side="left", anchor="w", padx=(8, 0))

        # 右上角控制区：菜单 + 关闭；关闭按钮默认隐藏，hover 时显示
        self.topright = tk.Frame(self.content, bg=BG)
        self.topright.place(relx=1.0, x=-6, y=14, anchor="ne")

        self.menu_btn = tk.Label(self.topright, text="▼", bg=BG, fg=MUTED,
                                 font=("Segoe UI", 10), cursor="hand2", width=2)
        self.menu_btn.pack(side="right")
        self.menu_btn.bind("<Button-1>", lambda e: (self.menu.post(e.x_root, e.y_root), "break")[1])

        self.close_btn = tk.Label(self.topright, text="✕", bg=BG, fg=MUTED,
                                  font=("Segoe UI", 11), cursor="hand2", width=2)
        self.close_btn.bind("<Button-1>", lambda e: (self.root.destroy(), "break")[1])
        # 默认隐藏，鼠标移入窗口后显示
        # self.close_btn.pack(side="right")

    # ---- 底部 ----
    def _build_footer(self):
        footer = tk.Frame(self.content, bg=BG)
        footer.pack(fill="x", padx=16, pady=(8, 14))
        tk.Label(footer, text="●", bg=BG, fg=ORANGE, font=("Segoe UI", 8)).pack(side="left")
        self.update_lbl = tk.Label(footer, text="", bg=BG, fg=MUTED,
                                   font=("Segoe UI", 10))
        self.update_lbl.pack(side="left", padx=(4, 0))
        link = tk.Label(footer, text="打开完整视图 ↗", bg=BG, fg=ACCENT,
                        font=("Segoe UI", 10), cursor="hand2")
        link.pack(side="right")
        link.bind("<Button-1>", lambda e: self.open_full_view())

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
        tools = load_tools()
        if not tools:
            self._render_error()
            return
        views = compute_views(tools)
        total = len(views)
        expiring_soon = sum(1 for v in views if v["expiryDays"] <= 7)
        resetting_soon = sum(1 for v in views if v["resetDays"] <= 1)

        self.stats.config(text=f"{total} 个订阅 · {expiring_soon} 个将到期 · {resetting_soon} 个快重置")

        # 按重置时间排序：hero 和列表都基于 reset
        views = sorted(views, key=lambda v: v["resetDays"] * 24 + v["resetHours"])
        hero = views[0]
        self._render_hero(hero)
        self._render_list(views[:6])

        now = datetime.now()
        self.update_lbl.config(text=f"更新于 {now.strftime('%H:%M')}")

    def _render_hero(self, v):
        for w in self.hero.winfo_children():
            w.destroy()
        tk.Label(self.hero, text="下一次重置", bg=HERO_BG, fg=MUTED,
                 font=("Segoe UI", 11)).pack(anchor="w")

        big_row = tk.Frame(self.hero, bg=HERO_BG)
        big_row.pack(fill="x", pady=(0, 8))
        tk.Label(big_row, text=str(v["resetDays"]), bg=HERO_BG, fg=ACCENT,
                 font=("Segoe UI", 48, "bold")).pack(side="left")
        tk.Label(big_row, text=f"天{v['resetHours']}时后重置", bg=HERO_BG, fg=ACCENT,
                 font=("Segoe UI", 14, "bold"), anchor="sw").pack(
                     side="left", padx=(6, 0), pady=(0, 10))

        row = tk.Frame(self.hero, bg=HERO_BG)
        row.pack(fill="x")
        left = tk.Frame(row, bg=HERO_BG)
        left.pack(side="left")
        self._brand_widget(left, v["name"], v["color"], 20)
        tk.Label(left, text=v["name"], bg=HERO_BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=(6, 0))
        tk.Label(row, text=v["resetDate"], bg=HERO_BG, fg=MUTED,
                 font=("Segoe UI", 11)).pack(side="right")

    def _render_list(self, items):
        for w in self.list_area.winfo_children():
            w.destroy()
        for i, v in enumerate(items):
            item = tk.Frame(self.list_area, bg=SURFACE,
                            highlightbackground=BORDER, highlightthickness=1)
            item.pack(fill="x", pady=(0, 8), ipady=6)

            # 首项（最近重置）加金色左边条
            if i == 0:
                bar = tk.Frame(item, bg=ORANGE, width=3)
                bar.pack(side="left", fill="y")
                bar.pack_propagate(False)

            content = tk.Frame(item, bg=SURFACE)
            content.pack(side="left", fill="both", expand=True, padx=12, pady=(8, 0))

            main = tk.Frame(content, bg=SURFACE)
            main.pack(fill="x")
            left = tk.Frame(main, bg=SURFACE)
            left.pack(side="left")
            self._brand_widget(left, v["name"], v["color"], 22)
            tk.Label(left, text=v["name"], bg=SURFACE, fg=TEXT,
                     font=("Segoe UI", 13, "bold")).pack(side="left", padx=(8, 0))

            right = tk.Frame(main, bg=SURFACE)
            right.pack(side="right")
            tk.Label(right, text=f"{v['expiryDays']}天{v['expiryHours']}时",
                     bg=SURFACE, fg=v["bar"], font=("Segoe UI", 14, "bold")).pack(anchor="e")
            tag = "到期" if v["expiryDays"] <= 7 else "续费"
            tk.Label(right, text=f"{tag} {v['expiryDate']}", bg=SURFACE, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="e")

            # 进度条
            track = tk.Frame(content, bg=TRACK, height=5)
            track.pack(fill="x", pady=(8, 0))
            track.pack_propagate(False)
            fill = tk.Frame(track, bg=v["bar"], height=5)
            fill.place(relx=0, rely=0, relheight=1,
                       relwidth=max(0, min(100, v["quotaPct"])) / 100)

            pct = tk.Frame(content, bg=SURFACE)
            pct.pack(fill="x", pady=(5, 8))
            tk.Label(pct, text=f"{v['quotaPct']}%", bg=SURFACE, fg=v["bar"],
                     font=("Segoe UI", 10)).pack(side="right")

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
        if abs(x) <= SNAP:
            x = 0
        elif abs(x + self.W - sw) <= SNAP:
            x = sw - self.W
        if abs(y) <= SNAP:
            y = 0
        elif abs(y + self.H - sh) <= SNAP:
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

    def _start_drag(self, e):
        # 只在窗口顶部区域（含 header、hero 和上方空白）触发拖动
        # 子组件事件会先触发；菜单/关闭按钮已返回 break，不会进入这里
        if e.y > self.DRAG_HEIGHT:
            self._dragging = False
            return
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

    def _tick(self):
        self.refresh()
        self.root.after(60000, self._tick)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    WidgetApp().run()
