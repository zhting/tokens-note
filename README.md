# 雪糕 · AI 额度与订阅提醒

本地运行的 AI 订阅看板：追踪各家工具的**已用额度**、**重置倒计时**和**订阅到期**。

提供两种界面，共用同一份数据文件 `ai-tools-data.json`：

- **完整视图** — 浏览器里管理全部订阅
- **桌面小窗** — Windows 原生 tkinter 贴边小窗，适合日常瞄一眼

额度优先按 [CodexBar](https://github.com/steipete/CodexBar) 同一套数据源**实时拉取**；拉不到的仍可手工填写。

## 功能

- **实时额度** — 读取本机 CLI / OAuth 登录，定时刷新已用百分比
- **重置倒计时** — 支持按周 / 按月 / 按日，小窗顶部显示下一次重置
- **到期提醒** — 跟踪订阅到期日，7 天内到期高亮
- **桌面小窗** — 无边框圆角、右侧贴边（圆角藏到屏外）、双击 logo 收成带阴影的浮动图标
- **品牌图标** — OpenAI、Claude、Cursor、Grok、Kimi 等
- **本地保存** — 数据集中在 `ai-tools-data.json`，不经过云端

## 快速开始

需要 **Python 3**（Windows 官方安装包已带 `tkinter`）。桌面小窗的圆角 / logo / 浮动阴影需要 **Pillow**：

```bash
pip install pillow
```

### 完整视图

双击 `start.bat`，或：

```bash
python server.py 8080
# 浏览器打开 http://127.0.0.1:8080/index.html
```

`start.bat` 会从 8080 起找空闲端口、启动 `server.py` 并打开浏览器。请不要直接双击 `index.html`（`file://` 下无法读写数据文件）。

网页右上角 **↻** 立即拉取实时额度。

### 桌面小窗

双击 `widget.bat`，或：

```bash
pythonw widget.py
```

- 拖动窗口可移动；靠近屏幕右缘会吸附，并把右侧圆角推出屏外
- **双击 logo** 收成圆形浮动图标，再点一下还原
- **右键** 菜单：刷新额度 / 打开完整视图 / 始终置顶 / 退出
- 鼠标移入显示关闭按钮
- 每 5 分钟自动拉一次额度

## 实时额度

启动后读取本机已有登录，不把密钥写进本仓库：

| 工具 | 数据源 |
|------|--------|
| ChatGPT Plus / Codex | `~/.codex/auth.json` → `chatgpt.com/backend-api/wham/usage` |
| Claude Pro | `~/.claude/.credentials.json` → Anthropic OAuth `/api/oauth/usage` |
| Cursor | `quota-secrets.json` 的 Cookie，或 Cursor 本地 token → `cursor.com/api/usage-summary` |
| Grok | `~/.grok/auth.json` → grok.com billing |
| Kimi | Kimi Code CLI 或 API key → `api.kimi.com/coding/v1/usages` |

对应 CLI 过期时，重新 `codex login` / `claude login` / `grok login` 即可。

Cursor 或额外 Key：复制 `quota-secrets.example.json` 为 **`quota-secrets.json`** 后填写。该文件已被 git 忽略。

命令行自检：

```bash
python quota_fetch.py
```

## 数据

- 主数据：`ai-tools-data.json`（工具列表、重置/到期规则、额度缓存）
- 完整视图通过 `POST /api/save` 写入，实时刷新走 `POST /api/refresh-quota`
- 备份或换电脑：复制 `ai-tools-data.json`（以及可选的 `quota-secrets.json`）

## 项目结构

```
start.bat / widget.bat     启动器
index.html                 完整视图
server.py                  静态托管 + 保存 / 刷新额度
widget.py                  桌面小窗
quota_fetch.py             各家用量拉取
ai-tools-data.json         订阅数据
quota-secrets.example.json 可选密钥模板
assets/  logo.png          图标
```

## License

MIT
