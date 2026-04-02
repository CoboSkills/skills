# Browser Operations Architecture — 6 层分层架构

## 分层总览

| Layer | 名称 | 工具 | 成本 | 适用场景 | 状态 |
|-------|------|------|------|---------|------|
| L1 | API 优先 | requests / feedparser | $0 | 官方 API / RSS / Webhook | ✅ |
| L2 | 轻量抓取 | web_search / web_fetch / Jina | $0 | 静态内容 / 公开网页 | ✅ |
| L3 | 命令化浏览器 | agent-browser + browser-cdp | $0 | 固定流程 / 已知 DOM | ✅ 已验证 |
| L4 | AI 增强浏览器 | Stagehand v3 | ~$0.001/任务 | 动态网站 / 复杂多步 | ✅ 已验证 |
| L5 | 云浏览器 | Zyte > Browserless > Hyperbrowser | $10-30/月 | 大规模并发 / 免运维 | ✅ |
| L6 | 反检测 | Camoufox / Nodriver(py3.12) | $0 | Cloudflare 盾 / 强反爬 | ✅ 已验证 |

## 各层详解

### L1: API 优先

**原则**：有官方 API 绝不用爬虫

**工具**：
- `requests` / `urllib` — HTTP 请求
- `feedparser` — RSS/Atom 解析

**适用**：
- 官方 API 可用
- RSS/Atom Feed
- Webhook 推送

### L2: 轻量抓取

**原则**：只要正文，不开浏览器

**工具**：
- `web_search` — 内置搜索
- `web_fetch` — 内置网页抓取
- **Jina AI Reader** — 外部内容提取器（r.jina.ai）

**Jina 使用**：
```bash
curl -s "https://r.jina.ai/http://example.com/article" > article.md
```

**适用**：
- 文章/博客/文档正文提取
- 公开网页内容
- 不需要登录态

**限制**：
- 无登录态支持
- 不执行 JavaScript
- 不适合动态内容

### L3: 命令化浏览器

**原则**：固定流程，命令化操作

**工具**：
- `agent-browser` — 命令化浏览器操作
- `browser-cdp` — CDP Session 复用

**CDP Session 复用**：
```bash
bash ~/.openclaw/scripts/browser-cdp.sh start
agent-browser open https://example.com
```

**适用**：
- 已知 DOM 结构
- 固定交互流程
- 需要登录态的网站

### L4: AI 增强浏览器

**原则**：动态网站，AI 理解页面

**工具**：
- `Stagehand` — AI 增强浏览器层

**适用**：
- 动态网站
- 复杂多步任务
- 需要 AI 理解页面结构

### L5: 云浏览器

**原则**：大规模并发，免运维

**工具**：
- Zyte（首选）
- Browserless（次选）
- Hyperbrowser（第三）

**适用**：
- 大规模并发
- 免运维需求
- 云端托管

### L6: 反检测

**原则**：强反爬场景

**工具**：
- `Camoufox` — Firefox modified，~80% bypass
- `Nodriver(py3.12)` — Chrome/Chromium，~90% bypass

**适用**：
- Cloudflare 盾
- 强指纹检测
- IP 封禁

## 桥接层

**opencli** — 浏览器桥接层（已验证）

## 观察项

- Browser Use（成本高，~$0.01/任务）
- Skyvern（场景有限）

## 暂不投入

- BrowserOS（定位重叠，成熟度不足）
