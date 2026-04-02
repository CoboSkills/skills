---
name: browser-ops
version: 1.0.0
description: "浏览器操作统一入口。6 层分层架构 (API/轻量抓取/命令化浏览器/AI 增强/云浏览器/反检测)、路由决策、Session 管理、Jina 内容提取、CDP 状态复用。Use when: 访问网页/抓取内容/浏览器自动化/登录态复用/反爬绕过/截图调试。"
---

# Browser Operations — 浏览器操作统一入口

## 🎯 定位

浏览器操作的统一标准入口，提供选型/分层/路由/状态管理的完整规范。

## 📋 快速开始

### 默认主链路

```
API 优先 → 轻量抓取 → agent-browser → Stagehand → Playwright (调试/特殊场景)
```

**关键路由原则**：拿到 URL 后，**先判断是否需要浏览器渲染**。
- 只要正文 / 静态内容 → 优先 L2，**不开浏览器**
- 需要登录态 / 交互 / 动态渲染 → 升级到 L3+

### 工具选择决策树

```
收到网页访问任务
├── 有官方 API / RSS？ → 使用 API（0 Browser）
├── 只要正文（文章/博客/文档）？
│   ├── Jina AI Reader（r.jina.ai）— $0，已验证 ✅
│   └── web_fetch + 本地提取 — $0
├── 需要交互（点击/填表）？
│   ├── 固定流程 → agent-browser（$0，首选）⭐
│   └── 动态网站 → Stagehand（~$0.001/任务）⭐
├── 需要截图/渲染/调试？ → Playwright CLI / MCP
├── 大规模并发？ → Zyte > Browserless > Hyperbrowser
└── 强反爬？ → Camoufox / Nodriver(py3.12)
```

**升级/回退规则**：
- L2 失败（403/内容空）→ 升级到 L3/L4
- 需要登录态 → 直接走 browser-cdp
- 只要正文 → 不开浏览器，优先 L2

## 🏗️ 核心架构

### 6 层分层架构

| Layer | 名称 | 工具 | 成本 | 适用场景 | 状态 |
|-------|------|------|------|---------|------|
| L1 | API 优先 | requests / feedparser | $0 | 官方 API / RSS | ✅ |
| L2 | 轻量抓取 | web_search / web_fetch / Jina | $0 | 静态内容 | ✅ |
| L3 | 命令化浏览器 | agent-browser + browser-cdp | $0 | 固定流程 | ✅ 已验证 |
| L4 | AI 增强浏览器 | Stagehand v3 | ~$0.001/任务 | 动态网站 | ✅ 已验证 |
| L5 | 云浏览器 | Zyte > Browserless > Hyperbrowser | $10-30/月 | 大规模并发 | ✅ |
| L6 | 反检测 | Camoufox / Nodriver | $0 | Cloudflare 盾 | ✅ 已验证 |

**详细说明**: 见 `references/architecture.md`

## 🔑 状态管理

### CDP Session 复用

```bash
# 启动带 CDP 的 Chrome（Cookie 永久保留）
bash ~/.openclaw/scripts/browser-cdp.sh start

# 验证
curl http://localhost:9222/json/version
```

**位置**: `~/.openclaw/browser-profile`

### 两种模式

| 模式 | 登录态 | 适用场景 |
|------|--------|---------|
| Persistent | ✅ 保留 | 需要登录的网站 |
| Isolated | ❌ 不保留 | 公开内容/测试 |

**详细说明**: 见 `references/state-management.md`

## 🛠️ 常用命令

### Jina AI Reader

```bash
# 提取网页正文为 Markdown
curl -s "https://r.jina.ai/http://example.com/article" > article.md
```

### agent-browser

```bash
# 导航
agent-browser open <url>

# 查看可交互元素
agent-browser snapshot -i

# 交互
agent-browser click @e1
agent-browser fill @e2 "text"
```

### Stagehand

```javascript
import { Stagehand } from '@browserbasehq/stagehand';
const stagehand = new Stagehand({ apiKey, env: "LOCAL" });
await stagehand.init();
const page = stagehand.page;
await page.act("点击登录按钮");
```

## 📚 References

- `references/architecture.md` — 分层架构详解
- `references/routing.md` — 路由决策树
- `references/state-management.md` — CDP + Session 管理
- `references/jina-usage.md` — Jina 使用指南
- `references/anti-detection.md` — 反爬策略

## 版本历史

- **1.0.0**（2026-04-02）：初版 — 整合 browser-ops-standard v1.1.0
  - 6 层分层架构
  - Jina AI Reader 已验证纳入 L2
  - CDP Session 复用规范
  - 反爬策略整合

## Operator Notes

- This skill is advisory/planning-oriented. It does not connect to external delivery platforms, schedule sends, or manage subscribers directly.
- When answering requests, keep the strategy inside the skill and explicitly call out when execution, analytics, or platform operations require a separate automation or operator workflow.
