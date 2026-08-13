# 雪糕 · AI 额度与订阅提醒

一个本地运行的 AI 工具额度追踪应用，帮助你管理各种 AI 服务的订阅额度和到期提醒。

## 功能特性

- 📊 **额度追踪** — 记录各 AI 工具的已用额度百分比
- ⏰ **重置提醒** — 支持周重置和月重置，实时倒计时
- 📅 **到期提醒** — 跟踪订阅到期日期，提前预警
- 🔍 **智能搜索** — 按名称或提供商快速筛选
- 🎨 **品牌图标** — 集成 OpenAI、Claude、Cursor、Kimi 等官方矢量图标
- 💾 **自动保存** — 数据保存在固定文件 `ai-tools-data.json`，每次打开自动读取、改动后一键保存

## 使用方法

### 启动完整视图（推荐：使用 start.bat）

直接双击项目根目录下的 `start.bat`：

1. 自动查找一个可用端口（从 8080 起递增）
2. 启动本地服务器 `server.py`（支持读取与写入 `ai-tools-data.json`）
3. 自动打开浏览器访问 `http://127.0.0.1:<端口>/index.html`

> 数据保存在项目根目录的 `ai-tools-data.json`。应用**每次打开都会自动读取该文件**，因此请始终通过 `start.bat` 启动，不要直接双击 `index.html`（浏览器在 `file://` 下会禁止读写数据文件）。

### 打开桌面小窗口（原生 Windows 程序）

双击 `widget.bat`，会以**原生 tkinter 桌面窗口**（非浏览器）在屏幕右上角弹出一个紧凑小窗，展示：

- 顶部统计：总订阅数 / 将到期数 / 快重置数
- 下一个重置倒计时（Hero 卡片）
- 最近到期的工具列表（含额度进度条，颜色随用量变化）
- 底部显示最近更新时间，点击「打开完整视图」会启动本地服务并在浏览器打开主应用

特性：

- **无需浏览器、无需服务器**：小窗直接读取同目录下的 `ai-tools-data.json`，每分钟自动刷新。
- **可拖拽**：按住顶部标题栏移动窗口。
- **右键 ≡ 菜单**：刷新 / 打开完整视图 / 切换「始终置顶」/ 退出。
- 若需手动运行：`pythonw widget.py`（需 Python 3 且含 `tkinter`，Windows 标准 Python 已内置）。

> 小窗与主应用共享同一份 `ai-tools-data.json` 数据，二者显示内容一致。

### 保存数据

在页面内点击「✓ 保存」按钮，即可将当前所有记录写入 `ai-tools-data.json`（通过 `server.py` 的 POST 接口落盘）。无需选择文件，固定保存在同一位置。

### 读取数据

打开应用时自动从 `ai-tools-data.json` 加载。若文件不存在或为空，会载入一组默认示例数据。

### 备份与迁移

`ai-tools-data.json` 即为完整数据文件，直接复制该文件即可备份或在其他设备间迁移。

## 支持的工具

应用内置以下工具的示例数据：

| 工具 | 提供商 | 重置周期 |
|------|--------|----------|
| ChatGPT Plus | OpenAI | 每周 |
| Claude Pro | Anthropic | 每周 |
| Cursor | Cursor | 每月 |
| Grok | xAI | 每周 |
| Kimi | Moonshot AI | 每月 |

## 技术说明

- 纯前端单文件应用（`index.html` 内含全部 HTML/CSS/JS），无需构建步骤
- 数据持久化到固定本地文件 `ai-tools-data.json`
- 依赖 `server.py`（基于 Python 标准库 `http.server` 的轻量服务器）提供静态托管与数据写入接口
- 支持主流现代浏览器（Chrome/Edge/Safari/Firefox）

## 本地运行

### 方式一：使用启动器（推荐）

```bash
# 双击 start.bat，或在命令行中运行
start.bat
```

### 方式二：手动启动服务器

```bash
# 需要 Python 3，端口可自定义（默认 8080）
python server.py 8080

# 然后在浏览器打开
# http://127.0.0.1:8080/index.html
```

> 若未使用 `start.bat`，也可临时用 `python -m http.server`，但该方式**不支持写入**
> 数据文件（保存按钮会失败），仅适合只读预览。建议始终使用 `start.bat` 或 `server.py`。

## License

MIT
