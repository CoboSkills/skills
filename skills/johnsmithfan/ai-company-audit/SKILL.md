---
name: "ai-company-audit"
version: 1.0.0
description: "跨Agent审计日志规范（7类日志 + 合规检查点 + 审计追踪标准）"
triggers: ["audit log", "compliance", "audit trail", "logging standard", "审计日志", "合规检查", "审计追踪", "日志规范"]
interface:
  inputs:
    type: "object"
    schema: |
      {
        "log_type": "decision|action|error|security|performance|access|data",
        "agent_id": "string (optional)",
        "date_range": "object (from/to)"
      }
  outputs:
    type: "object"
    schema: |
      {
        "logs": "array of log entries",
        "compliance_status": "object",
        "anomalies": "array"
      }
  errors:
    - code: "AUDIT_001"
      message: "Log entry missing required fields"
      action: "Enforce schema: timestamp/agent/action/result"
dependencies:
  skills: ["ai-company-governance", "ai-company-registry"]
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

# Audit Logging Standard — 审计日志规范

## 7类审计日志

| Log Type | Description | Retention |
|----------|-------------|----------|
| Decision | 战略/战术决策记录 | 2 years |
| Action | Agent 执行的操作 | 90 days |
| Error | 系统异常和错误 | 90 days |
| Security | 认证/授权/安全事件 | 2 years |
| Performance | 延迟/吞吐量/KPI | 30 days |
| Access | 数据访问记录 | 2 years |
| Data | 数据变更历史 | 7 years |

## Log Entry Schema

```yaml
log_entry:
  timestamp: "ISO 8601 format (YYYY-MM-DDTHH:MM:SS.SSSZ)"
  agent_id: "e.g., CFO-001, CEO-001"
  log_type: "decision|action|error|security|performance|access|data"
  action: "string (what happened)"
  target: "string (affected resource/endpoint)"
  result: "success|failure|partial"
  duration_ms: 0
  metadata:
    task_id: "TASK-001"
    confidence: 0.95
    [敏感]: "redacted"
  trace_id: "uuid (for cross-agent correlation)"
```

## Compliance Checkpoints

| Checkpoint | Standard | Enforcement |
|-----------|---------|-------------|
| P0 SLA 达成 | 95% P0 事件在 SLA 内完成 | CQO 监控 |
| 敏感数据标注 | 所有 PII 字段含 `[敏感]` 标注 | CISO 审计 |
| 跨 Agent 审计追踪 | trace_id 贯穿完整调用链 | CTO 技术实现 |
| 审计日志不可篡改 | append-only + hash chain | CTO 技术实现 |
| 审计日志保留期 | 详见上表（7类）| CTO 存储策略 |

## P0 Incident Compliance

| P0 标准 | 响应要求 | 审计要求 |
|---------|---------|---------|
| 响应时间 | 15 分钟内初始响应 | 时间戳记录 |
| CEO 通报 | 立即通报 | 决策日志 |
| 根因分析 | 48 小时内完成 | 分析报告存档 |
| 改进项 | 7 天内入 backlog | 追踪记录 |

## Audit Log Storage Policy

```yaml
storage_policy:
  format: "structured JSON (CloudWatch/Elasticsearch/Splunk compatible)"
  encryption: "AES-256-GCM at rest"
  replication: "3 copies across regions"
  access_control: "CQO + CISO read-only; CTO write-only"
  retention:
    decision: "2 years"
    security: "2 years"
    access: "2 years"
    performance: "30 days"
    action: "90 days"
    error: "90 days"
    data: "7 years"
```

## Natural Language Commands

```
"Audit all decisions this week" → Decision logs filtered by date range
"Check compliance for P0 SLAs" → P0 compliance report
"Review access logs for sensitive data" → Access log audit
"Export audit trail for INC-001" → Trace by trace_id
```
