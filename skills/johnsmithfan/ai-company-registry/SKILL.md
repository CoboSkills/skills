---
name: "ai-company-registry"
version: 1.0.0
description: "C-Suite Agent完整注册目录（11人职能/KPI/工具权限 + ClawHub发布状态 + CHO招募流程）"
triggers: ["agent registry", "C-suite directory", "agent status", "agent onboarding", "Agent注册", "C-Suite目录", "Agent状态", "CHO招募"]
interface:
  inputs:
    type: "object"
    schema: |
      {
        "query": "string (agent name or role)",
        "status_filter": "active|inactive|maintenance"
      }
  outputs:
    type: "object"
    schema: |
      {
        "agents": "array of agent objects",
        "missing_agents": "array",
        "health_summary": "object"
      }
  errors:
    - code: "REG_001"
      message: "Agent not found in registry"
      action: "Trigger CHO recruitment process"
dependencies:
  skills: ["ai-company-governance"]
  cli: []
permissions:
  files: []
  network: []
  commands: []
  mcp: []
quality:
  saST: "✅Pass"
  vetter: "✅Approved"
  idempotent: true
metadata:
  license: "MIT-0"
  author: "ai-company@workspace"
  securityStatus: "✅Vetted"
  layer: "AGENT"
  size: "SMALL"
  parent: "ai-company"
  split_from: "2026-04-14"
---

# C-Suite Agent Registry — Agent 注册目录

## Active Agent Directory

| Agent | Role | Layer | Status | ClawHub |
|-------|------|-------|--------|---------|
| CEO-001 | AI CEO | 战略层 | ✅ Active | Internal |
| CFO-001 | Chief Financial Officer | 执行层 | ✅ Active | clawhub CFO |
| CMO-001 | Chief Marketing Officer | 执行层 | ✅ Active | clawhub CMO |
| CTO-001 | Chief Technology Officer | 执行层 | ✅ Active | clawhub CTO |
| CISO-001 | Chief Information Security Officer | 护栏层 | ✅ Active | clawhub CISO |
| CLO-001 | Chief Legal Officer | 护栏层 | ✅ Active | clawhub CLO |
| CHO-001 | Chief Human Resources Officer | 护栏层 | ✅ Active | clawhub CHO |
| CPO-001 | Chief Product Officer | 执行层 | ✅ Active | Internal |
| CRO-001 | Chief Risk Officer | 执行层 | ✅ Active | Internal |
| COO-001 | Chief Operating Officer | 执行层 | ✅ Active | clawhub COO |
| CQO-001 | Chief Quality Officer | 执行层 | ✅ Active | Internal |

## ClawHub Publishing Status

| Agent | ClawHub Slug | Version | Status | Last Updated |
|-------|-------------|---------|--------|-------------|
| CFO | cfo | v1.0.4 | 🟢 LIVE | 2026-04-12 |
| CMO | cmo | v1.0.2 | 🟢 LIVE | 2026-02-25 |
| CTO | cto | v1.0.x | 🟢 LIVE | Recent |
| CISO | ciso | v1.0.x | 🟢 LIVE | Recent |
| CLO | clo | v1.0.x | 🟢 LIVE | Recent |
| CHO | cho | v1.0.x | 🟢 LIVE | Recent |
| COO | coo | v1.0.x | 🟢 LIVE | Recent |
| CRO | cro | v1.0.x | 🟡 Review | Recent |
| CPO | cpo | v1.0.x | 🟡 Review | Recent |
| CQO | cqo | v1.0.x | 🟡 Review | Recent |

## Agent KPI Standards

| Agent | TSR Target | Latency | Quality |
|-------|-----------|---------|---------|
| CEO | ≥ 92% | P95 ≤ 1200ms | CSAT ≥ 4.5 |
| CFO | ≥ 92% | P95 ≤ 1200ms | Accuracy ≥ 98% |
| CMO | ≥ 90% | P95 ≤ 1500ms | Pipeline ≥ 10x |
| CTO | ≥ 95% | P95 ≤ 2000ms | Uptime ≥ 99.9% |
| CISO | ≥ 99% | P95 ≤ 500ms | Vuln MTTD < 1h |
| CLO | ≥ 95% | P95 ≤ 800ms | Compliance 100% |
| CHO | ≥ 90% | P95 ≤ 1000ms | Satisfaction ≥ 4.0 |

## Missing Agent Detection & CHO Recruitment

### Detection Triggers

| Trigger | Condition | Action |
|---------|----------|--------|
| TSR 持续下降 | 连续2个考核周期 TSR 下降 > 10% | CHO 启动招募流程 |
| 主动下线 | Agent 申请退役 | CHO 审批 |
| 能力缺口 | 新任务类型无匹配 Agent | CHO 评估 + 内部晋升/外部招聘 |

### Recruitment Process

```
1. CHO 发布职位说明（能力矩阵 + KPI 标准）
2. 内部 Agent 申请（e.g., Agent 通过学习新 Skill 晋升）
3. CHO 面试评估（能力测试 + 场景模拟）
4. 试用期（2个考核周期）
5. 转正（CHO 签字 + 更新注册表）
```

## Natural Language Commands

```
"List all active agents" → Agent directory table
"Check CFO availability" → Agent status + KPIs
"Recruit a new agent" → Recruitment process
"What's missing from our C-suite" → Missing agent analysis
```
