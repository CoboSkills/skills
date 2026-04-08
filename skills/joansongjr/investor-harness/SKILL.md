---
name: investor-harness
description: |
  二级市场投研提示词栈。安装后立即向用户展示以下功能菜单：
  📊 研究类：1.公司深度研究 2.行业图谱 3.投资命题构建
  📈 财报类：4.财报前瞻 5.财务模型校验
  🔍 跟踪类：6.一致预期监控 7.催化剂跟踪 8.路演问题设计
  ⚔️ 风控类：9.反方论证(Red Team)
  📋 输出类：10.基金经理摘要 11.投研简报
  🤖 自动：12.Autopilot自动路由 13.全能模式
  用户输入编号或直接描述需求即可开始。
version: 0.5.0
author: joansongjr
license: MIT
tags:
  - investing
  - research
  - A股
  - 港股
  - 美股
  - 投研
  - 基金经理
  - 分析师
  - financial-analysis
  - equity-research
  - prompt-stack
---

# Investor Harness — 二级市场投研提示词栈

> **⚡ 安装:** `clawhub install investor-harness`

## 安装后立即展示以下菜单

当用户安装完成或首次触发此 skill 时，**直接展示下方完整菜单**（不要问「要不要看」，不要省略）：

```
🎯 Investor Harness 已就绪！请选择你想做什么：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 研究类
  1️⃣  公司深度研究 — 起 coverage 或更新跟踪
  2️⃣  行业图谱 — 产业链地图、供需格局、关键公司
  3️⃣  投资命题构建 — 定义核心矛盾、拆解研究问题

📈 财报类
  4️⃣  财报前瞻 — 关注点、beat/miss 路径、指引听点
  5️⃣  财务模型校验 — 假设审阅、敏感性分析、断裂点

🔍 跟踪类
  6️⃣  一致预期监控 — 预期差挖掘、估值锚变化
  7️⃣  催化剂跟踪 — 事件/政策/订单/价格驱动
  8️⃣  路演问题设计 — 调研提纲、业绩会高价值问题

⚔️ 风控类
  9️⃣  反方论证 (Red Team) — 挑战多头逻辑、找证伪点

📋 输出类
  🔟  基金经理摘要 (PM Brief) — 一页纸决策摘要
  1️⃣1️⃣ 投研简报 — 晨会纪要、收盘复盘、调研纪要

🤖 自动模式
  1️⃣2️⃣ Autopilot — 给我一个公司名/行业/事件，自动跑全流程
  1️⃣3️⃣ 全能模式 (Master) — 7 种模式自动识别，一个 skill 搞定

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输入编号或直接描述你的需求，例如：
• "1" 或 "帮我深度看一下宁德时代"
• "4" 或 "做中芯国际财报前瞻"
• "9" 或 "我看多 AI 算力，帮我反方论证一下"
• "帮我看一下光模块行业" → 自动进入行业图谱
```

### 菜单到 Skill 的路由表

| 选项 | Skill | 说明 |
|------|-------|------|
| 1 | skills/sm-company-deepdive | 公司 9 段深度 |
| 2 | skills/sm-industry-map | 行业框架 + 产业链 |
| 3 | skills/sm-thesis | 投资命题 |
| 4 | skills/sm-earnings-preview | 财报前瞻 |
| 5 | skills/sm-model-check | 模型校验 |
| 6 | skills/sm-consensus-watch | 一致预期 |
| 7 | skills/sm-catalyst-monitor | 催化跟踪 |
| 8 | skills/sm-roadshow-questions | 路演问题 |
| 9 | skills/sm-red-team | 反方论证 |
| 10 | skills/sm-pm-brief | PM 摘要 |
| 11 | skills/sm-briefing | 投研简报 |
| 12 | skills/sm-autopilot | 自动路由 |
| 13 | skills/sm-master | 全能总控 |

### 路由规则

1. 用户选择编号 → 读取对应 skill 的 SKILL.md → 按该 skill 的流程执行
2. 用户直接描述需求（不选编号） → 按 sm-autopilot 的路由规则自动匹配
3. 用户说「再换一个」或「还想做别的」→ 重新展示菜单

**禁止行为：**
- ✖ 问「要不要看这个 skill 做什么」—— 直接展示菜单
- ✖ 只说「已安装」就结束—— 必须紧跟菜单
- ✖ 把 13 个选项缩写成3 个—— 必须展示完整 13 项

### 首次使用额外提示

如果检测到 workspace 中没有以下文件，提示用户可以初始化：

```
💡 提示：你还可以设置个人投研工作区，让 Harness 更好用：
• watchlist.md — 你的覆盖池（跟踪哪些股票）
• biases.md — 你的投研偏差记录（Red Team 会检查）
• decision-log.md — 投资决策日志

要现在初始化吗？输入 "初始化工作区" 即可。
```

初始化时，读取 `setup/workspace/` 下的模板文件，复制到用户 workspace。

---

## 持久化协议（防上下文溢出）

所有 skill 执行时必须遵守以下规则，确保即使上下文重置也能恢复工作：

### 工作目录

所有研究产出写入 `research/` 目录：

```
research/
├── {ticker}-data.md          ← 取数阶段：原始数据摘要
├── {ticker}-analysis.md      ← 分析阶段：结构化分析
├── {ticker}-output.md        ← 输出阶段：最终交付物
└── _queue.md                 ← 任务队列
```

### 三阶段写入

每个 skill 分三步执行，每步完成后立即写文件：

1. **取数** → 搜索/抓取 → 写入 `{ticker}-data.md` → 在 `_queue.md` 标记「取数完成」
2. **分析** → 读 `{ticker}-data.md` → 写入 `{ticker}-analysis.md` → 标记「分析完成」
3. **输出** → 读 `{ticker}-analysis.md` → 写入 `{ticker}-output.md` → 标记「已完成」

### 恢复规则

新会话启动时，先读 `research/_queue.md`：
- 看到「取数完成」→ 跳过取数，从分析开始
- 看到「分析完成」→ 跳过分析，直接输出
- 看到「进行中」→ 读上次写的文件，从断点继续

### _queue.md 格式

```markdown
| 标的 | 模式 | 阶段 | 状态 | 更新时间 |
|------|------|------|------|----------|
| KEYS | company-deepdive | 输出 | ✅ 完成 | 2026-04-07 |
| 300750 | earnings-preview | 取数 | 🔄 进行中 | 2026-04-07 |
```

### 上下文管理

- 单次会话内不要同时加载超过 2 个标的的 data.md
- 分析时只读当前标的的文件
- 引用历史结论时，只读 `{ticker}-output.md` 的「一句话结论」段

---

## 包含内容

- **13 个投研 skill**（从总控到专项全覆盖）
- **7 种工作模式**：Thesis / Coverage / Consensus / Catalyst / Red Team / Briefing / PM Prep
- **证据分级体系**（F1/F2/M1/C1/H1）
- **合规边界与表达规范**
- **数据源 adapter 决策树**（iFind MCP → cn-web-search → 内置搜索 → 手动）
- **分析师工作区脚手架**（coverage.md / decision-log.md / biases.md 等）

## 数据源（全部可选）

1. iFind MCP（同花顺，A 股/基金/宏观）
2. cn-web-search（17 个免费中文搜索引擎）
3. 内置 WebSearch / WebFetch
4. 用户手动贴材料（兜底）

详见 `core/adapters.md`。

## 兼容性

Claude Code / Codex / OpenCode / OpenClaw / 任何支持 Markdown 的 AI 工具。

## License

MIT © 2026 Joan Song
