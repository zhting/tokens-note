# 雪糕 · AI 额度与订阅提醒

本地运行的 AI 订阅看板：追踪各家工具的**已用额度**、**重置倒计时**和**订阅到期**。

额度和订阅信息默认**手工填写 / 手工刷新**，不做自动联网。提供两种界面，共用同一份数据文件 `ai-tools-data.json`：

- **完整视图** — Windows 原生窗口（pywebview 内嵌 WebView2），管理全部订阅
- **桌面小窗** — Windows 原生 tkinter 贴边小窗，适合日常瞄一眼

想核对实时额度时，在完整视图右上角或小窗右键点 **↻**，按 [CodexBar](https://github.com/steipete/CodexBar) 同一套数据源**手动拉取**一次；拉不到的仍可手工填写。

## 功能

- **手工为主** — 额度、重置、到期都由你填；需要时才手动点 ↻ 拉一次实时额度
- **重置倒计时** — 支持按周 / 按月 / 按日，小窗顶部显示下一次重置
- **到期提醒** — 跟踪订阅到期日，7 天内到期高亮
- **原生完整视图** — pywebview 内嵌 WebView2，无需开浏览器、无需起服务器
- **桌面小窗** — 无边框圆角、右侧贴边（圆角藏到屏外）、双击 logo 收成带阴影的浮动图标
- **品牌图标** — OpenAI、Claude、Cursor、Grok、Kimi 等
- **本地保存** — 数据集中在 `ai-tools-data.json`，不经过云端

## 快速开始

需要 **Python 3**（Windows 官方安装包已带 `tkinter`）。

- 桌面小窗的圆角 / logo / 浮动阴影需要 **Pillow**
- 原生完整视图需要 **pywebview**（依赖系统自带的 WebView2 运行时，Win11 一般已装）

```bash
pip install pillow pywebview
```

### 完整视图（原生窗口）

```bash
pythonw fullview.py
```

直接弹出一个 Windows 窗口，管理全部订阅。数据经 JS 桥接直接读写 `ai-tools-data.json`，**不需要**起 `server.py`、也不需要浏览器。页面右上角 **↻** 手动拉取实时额度。

> 若机器上没有 pywebview，会自动回退到「本地服务器 + 默认浏览器」的旧方式。

### 桌面小窗

双击 `widget.bat`，或：

```bash
pythonw widget.py
```

- 拖动窗口可移动；靠近屏幕右缘会吸附，并把右侧圆角推出屏外
- **双击 logo** 收成圆形浮动图标，再点一下还原
- **右键** 菜单：↻ 刷新额度（手动拉一次）/ 打开完整视图 / 始终置顶 / 退出
- 鼠标移入显示关闭按钮
- 小窗只读盘展示，**不再**每 5 分钟自动联网

### 浏览器版完整视图（可选）

若想用浏览器看，双击 `start.bat`，或：

```bash
python server.py 8080
# 浏览器打开 http://127.0.0.1:8080/index.html
```

`start.bat` 会从 8080 起找空闲端口、启动 `server.py` 并打开浏览器。请不要直接双击 `index.html`（`file://` 下无法读写数据文件）。

## 实时额度（手动）

点 **↻** 时才读取本机已有登录拉一次，不把密钥写进本仓库：

| 工具 | 数据源 |
|------|--------|
| ChatGPT Plus / Codex | `~/.codex/auth.json` → `chatgpt.com/backend-api/wham/usage` |
| Claude Pro | `~/.claude/.credentials.json` → Anthropic OAuth `/api/oauth/usage` |
| Cursor | `quota-secrets.json` 的 Cookie，或 Cursor 本地 token → `cursor.com/api/usage-summary` |
| Grok | `~/.grok/auth.json` → grok.com billing |
| Kimi | Kimi Code CLI 或 API key → `api.kimi.com/coding/v1/usages` |

对应 CLI 过期时，重新 `codex login` / `claude login` / `grok login` 即可。

Cursor 或额外 Key：复制 `quota-secrets.example.json` 为 **`quota-secrets.json`** 后填写。该文件已被 git 忽略。

命令行自检（也会手动拉一次）：

```bash
python quota_fetch.py
```

## 数据

- 主数据：`ai-tools-data.json`（工具列表、重置/到期规则、额度缓存）
- 原生完整视图经 JS 桥接直接读写；浏览器版通过 `POST /api/save` 写入，实时刷新走 `POST /api/refresh-quota`
- 备份或换电脑：复制 `ai-tools-data.json`（以及可选的 `quota-secrets.json`）

## 项目结构

```
start.bat / widget.bat     启动器
index.html                 完整视图页面
fullview.py                完整视图的原生窗口封装（pywebview）
server.py                  浏览器版的静态托管 + 保存 / 刷新额度
widget.py                  桌面小窗
quota_fetch.py             各家用量拉取（手动触发）
ai-tools-data.json         订阅数据
quota-secrets.example.json 可选密钥模板
assets/  logo.png          图标
```

## License

MIT
