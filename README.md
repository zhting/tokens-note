# 雪糕 · AI 额度与订阅提醒

一个本地运行的 AI 工具额度追踪应用，帮助你管理各种 AI 服务的订阅额度和到期提醒。

## 功能特性

- 📊 **额度追踪** — 记录各 AI 工具的已用额度百分比
- ⏰ **重置提醒** — 支持周重置和月重置，实时倒计时
- 📅 **到期提醒** — 跟踪订阅到期日期，提前预警
- 🔍 **智能搜索** — 按名称或提供商快速筛选
- 🎨 **品牌图标** — 集成 OpenAI、Claude、Cursor、Kimi 等官方矢量图标
- 💾 **本地保存** — 支持将数据保存到本地 JSON 文件（Chrome/Edge）
- 📂 **文件导入导出** — 随时备份和恢复数据

## 使用方法

### 首次使用

1. 用浏览器打开 `index.html`
2. 点击「+ 添加工具」添加你的 AI 订阅
3. 填写工具名称、提供商、重置周期和额度信息

### 保存数据

1. 点击「💾 保存」按钮
2. 选择保存位置，文件名为 `ai-tools-data.json`
3. 每次修改后记得重新保存

### 加载数据

1. 点击「📂 加载」按钮
2. 选择之前保存的 JSON 文件
3. 数据将自动导入并显示

> 注意：本地文件保存功能需要 Chrome 或 Edge 浏览器支持 File System Access API。

### 备份与迁移

- **导出**：点击「↓ 导出」生成 JSON 备份文件
- **导入**：点击「↑ 导入」从 JSON 文件恢复数据

## 支持的工具

应用内置以下工具的示例数据：

| 工具 | 提供商 | 重置周期 |
|------|--------|----------|
| ChatGPT Plus | OpenAI | 每周 |
| Claude Pro | Anthropic | 每周 |
| Cursor | Cursor | 每月 |
| Grok | xAI | 每周 |
| Kimi | Moonshot AI | 每周 |
| Perplexity Pro | Perplexity | 每月 |

## 技术说明

- 纯前端应用，无需服务器
- 数据存储在浏览器 localStorage 或本地 JSON 文件
- 支持主流现代浏览器（Chrome/Edge/Safari/Firefox）

## 本地运行

无需任何构建步骤，直接用浏览器打开即可：

```bash
# 使用 Python 启动简单服务器（可选）
python -m http.server 8080

# 或直接打开
open index.html
```

## License

MIT
