# browser-ops — 浏览器操作标准化方案

[![GitHub](https://img.shields.io/github/license/lanyasheng/browser-ops)](LICENSE)
[![Skill Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/lanyasheng/browser-ops)

> **浏览器操作的统一入口** — 6 层分层架构、路由决策、Session 管理、Jina 内容提取、CDP 状态复用

## 🎯 定位

browser-ops 是一个 **OpenClaw Skill**，为 AI Agent 提供浏览器操作的完整规范：
- 选型指导（6 层分层架构）
- 路由决策（先判断是否需要浏览器渲染）
- 状态管理（CDP Session 复用）
- 反爬策略（Cloudflare 盾绕过）

## 🚀 快速开始

### 安装

```bash
# 从 ClawHub 安装（推荐）
clawhub install browser-ops

# 或手动安装
git clone https://github.com/lanyasheng/browser-ops.git ~/.openclaw/skills/browser-ops
```

### 使用

```markdown
@browser-ops 帮我抓取 https://example.com/article 的正文内容
```

Skill 会自动选择最优方案：
1. 先用 **Jina AI Reader** 提取正文（$0，已验证）
2. 失败则回退到 **web_fetch**
3. 需要交互则升级到 **agent-browser**

## 🏗️ 核心架构

### 6 层分层架构

| Layer | 名称 | 工具 | 成本 | 适用场景 |
|-------|------|------|------|---------|
| L1 | API 优先 | requests / feedparser | $0 | 官方 API / RSS |
| L2 | 轻量抓取 | web_search / web_fetch / Jina | $0 | 静态内容 |
| L3 | 命令化浏览器 | agent-browser + browser-cdp | $0 | 固定流程 |
| L4 | AI 增强浏览器 | Stagehand v3 | ~$0.001/任务 | 动态网站 |
| L5 | 云浏览器 | Zyte > Browserless | $10-30/月 | 大规模并发 |
| L6 | 反检测 | Camoufox / Nodriver | $0 | Cloudflare 盾 |

### 路由决策树

```
收到网页访问任务
├── 有官方 API / RSS？ → 使用 API
├── 只要正文？ → Jina AI Reader（已验证 ✅）
├── 需要交互？ → agent-browser / Stagehand
├── 需要截图？ → Playwright
└── 强反爬？ → Camoufox / Nodriver
```

## 📚 文档

- [SKILL.md](SKILL.md) — Skill 主文档
- [references/architecture.md](references/architecture.md) — 6 层架构详解
- [references/routing.md](references/routing.md) — 路由决策树
- [references/state-management.md](references/state-management.md) — CDP Session 管理
- [references/jina-usage.md](references/jina-usage.md) — Jina 使用指南
- [references/anti-detection.md](references/anti-detection.md) — 反爬策略

## ✅ 已验证能力

| 能力 | 状态 | 说明 |
|------|------|------|
| Jina AI Reader | ✅ 已验证 | Paul Graham 博客、BBC News 实测通过 |
| agent-browser | ✅ 已验证 | 雪球行情、GitHub Trending |
| browser-cdp | ✅ 已验证 | Cookie 持久化/登录态复用 |
| Stagehand | ✅ 已验证 | AI 增强浏览器层 |
| Camoufox | ✅ 已验证 | ~80% Cloudflare bypass |
| Nodriver | ✅ 已验证 | ~90% 反爬 bypass |

## 🔧 配置

### CDP Session 复用

```bash
# 启动带 CDP 的 Chrome（Cookie 永久保留）
bash ~/.openclaw/scripts/browser-cdp.sh start

# 验证
curl http://localhost:9222/json/version
```

### Jina AI Reader

```bash
# 提取网页正文为 Markdown
curl -s "https://r.jina.ai/http://example.com/article" > article.md
```

## 📈 路线图

- [x] v1.0.0 — 初版，6 层架构 + Jina 验证
- [ ] v1.1.0 — Readability 自托管支持
- [ ] v1.2.0 — 统一访问接口封装
- [ ] v2.0.0 — 多站点并发优化

## 🤝 贡献

欢迎提交 Issue 和 PR！

### 开发环境

```bash
git clone https://github.com/lanyasheng/browser-ops.git
cd browser-ops
# 安装依赖（如需要）
```

### 测试

```bash
# 运行 skill-evaluator 评估
python ~/.openclaw/skills/skill-evaluator/scripts/run_eval.py --target ./SKILL.md
```

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 🔗 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [ClawHub](https://clawhub.com)
- [Jina AI Reader](https://jina.ai/reader/)
- [Stagehand](https://github.com/browserbasehq/stagehand)
