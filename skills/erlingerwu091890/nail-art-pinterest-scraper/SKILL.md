---
name: nail-art-pinterest-scraper
description: Pinterest 美甲图片扒取技能。从 Pinterest 搜索页批量采集美甲图片，支持 MD5 排重、自动下载、路径转换（AVIF→JPG）、防封策略。触发场景：用户说"采集 Pinterest 美甲图片"、"扒取美甲图"、"Pinterest 扒图"、"下载美甲图片"。
---

# Nail Art Pinterest Scraper

专注美甲图片的 Pinterest 扒图工作流。

## 工作流程

### 执行前确认
向用户展示完整流程，等待确认后再执行：
1. 打开 Pinterest 搜索页（关键词由用户提供）
2. 滚动加载获取 Pin 列表（最多 30 个/次）
3. 逐个点击 Pin 详情页，等 3 秒后提取图片 URL
4. 下载图片（736x/avif 路径转为 1200x jpg）
5. MD5 哈希排重，与本地哈希库比对
6. 保存为 `F:\cut2\nail3_art_XXX.png`（序号连续）
7. 节奏：每张间隔 3 秒，每 8 张休息 15 秒
8. 完成后展示文件数量和列表

### 关键技术细节

**浏览器**：OpenClaw browser tool（profile=openclaw）

**图片提取 JS**：
```javascript
var b='',w=0;document.querySelectorAll('img').forEach(function(i){if(i.src&&i.src.indexOf('pinimg')>-1&&i.naturalWidth>w){w=i.naturalWidth;b=i.src;}});return b;
```

**下载**：PowerShell `Invoke-WebRequest`，UserAgent=Mozilla/5.0

**路径转换**：将 `i.pinimg.com/736x/HASH.jpg` 替换为 `1200x` 版本下载；AVIF 格式尝试替换为 1200x jpg（约 70% 存在）

**哈希库**：`F:\cut2\hashes.txt`，格式：`MD5HASH,filename`，每行一条

**防封**：每张图间隔 3 秒，每 8 张休息 15-30 秒；浏览器每 5-8 张重启一次

### 异常处理
- 403 → 尝试 `originals` 路径
- AVIF 格式 → 替换为 1200x jpg 版本
- 浏览器超时 → 重启 browser session

### 文件路径
- 图片保存：`F:\cut2\nail3_art_XXX.png`
- 哈希库：`F:\cut2\hashes.txt`
- 已访问 Pin 库：`F:\cut2\visited_pins.txt`

### 排重规则
- 下载前先查哈希库，命中则跳过不下载，不占序号
- 每完成一批，立即将新哈希追加写入哈希库
- 同一图片可能出现在不同 Pin 中，必须以内容哈希而非 Pin ID 排重
