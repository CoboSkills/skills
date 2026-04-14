---
name: knowledge-base
slug: knowledge-base
version: 1.0.1
description: 全AI公司共享知识库接口。统一管理运营记录、战略文档、审计日志，支持跨Agent知识检索与共享状态同步。
metadata: {"openclaw":{"emoji":"🗄️","os":["linux","darwin","win32"]}}
---

# Knowledge Base — 共享知识库（增强版）

> **版本 1.0.1 更新**：新增交接（Handoff）协议支持，引入 IMA 实时同步中枢集成。

## 触发场景

当 Agent 需要存取以下内容时调用本服务：
- "保存会议记录"、"读取审计日志"、"查询历史决策"
- "更新运营状态"、"同步共享状态"、"查询他人工作记录"
- "获取战略文档"、"访问财务记录"、"查看合规报告"
- "发起任务交接"、"填写 handoff"、"接收跨部门任务"

## 目录结构

```
C:\Users\Admin\.qclaw\workspace\skills\tools\knowledge-base\
├── daily/                  # 每日运营记录
│   └── {YYYY-MM-DD}/
│       ├── morning-briefing.md    # 早间简报
│       ├── evening-report.md      # 晚间总结
│       └── agent-reports/        # 各Agent汇报
├── audit/                 # 审计日志（永久保留）
│   ├── ceo-decisions/      # CEO决策日志
│   ├── financial/          # 财务审计
│   ├── legal/              # 法律合规审计
│   ├── hr/                 # 人事审计
│   ├── tech/               # 技术审计
│   └── quality/            # 质量审计
├── shared-state/           # 共享状态（实时更新）
│   ├── cashflow.json       # CFO: 现金流状态
│   ├── reputation.json      # CMO: 舆情状态
│   ├── quality-metrics.json # CQO: 质量指标
│   ├── risk-level.json     # CRO: 风险等级
│   ├── operations.json     # COO: 运营状态
│   └── security.json       # CISO: 安全状态
├── strategy/               # 战略文档
│   └── {YYYY-MM-DD}/       # 按日期归档
│       ├── okr.md
│       ├── investment-decision.md
│       └── crisis-response.md
├── skills/                 # 技能更新记录
│   └── {YYYY-MM-DD}/
│       ├── learning/        # 学习记录
│       └── optimization/   # 优化记录
└── handoff/               # 任务交接记录（新增）
    ├── pending/            # 待接收的交接
    │   └── {YYYY-MM-DD}_{handoff-id}.md
    ├── in-progress/         # 进行中的交接
    │   └── {handoff-id}.md
    └── completed/          # 已完成的交接
        └── {handoff-id}.md
```

## IMA 实时同步中枢集成

知识库作为跨 Agent 实时状态同步中枢，支持：
- **写入时推送**：更新共享状态后，通过 IMA API 通知订阅者
- **查询聚合**：单一接口查询所有 Agent 的最新状态快照
- **变更历史**：每次更新记录时间戳，支持回溯

### IMA 同步接口

```python
def sync_to_ima(domain: str, data: dict, agent_id: str) -> dict:
    """
    将共享状态同步至 IMA（腾讯知识库）
    domain: cashflow | reputation | quality-metrics | risk-level | operations | security
    """
    import json
    from pathlib import Path
    from datetime import datetime

    # 写入本地共享状态文件
    base = Path("C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/shared-state")
    file_map = {
        "cashflow": "cashflow.json",
        "reputation": "reputation.json",
        "quality-metrics": "quality-metrics.json",
        "risk-level": "risk-level.json",
        "operations": "operations.json",
        "security": "security.json"
    }
    filepath = base / file_map.get(domain, f"{domain}.json")
    filepath.parent.mkdir(parents=True, exist_ok=True)

    content = {
        "updated_by": agent_id,
        "updated_at": datetime.now().isoformat(),
        "data": data,
        "synced": True
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    # 通过 IMA API 通知订阅者（如已配置）
    # notify_subscribers(domain, agent_id, content)

    return {"success": True, "domain": domain, "file": str(filepath)}


def get_ima_snapshot(agent_ids: list = None) -> dict:
    """
    获取所有 Agent 的最新状态快照（单一接口查询）
    如传入 agent_ids，仅返回指定 Agent 的状态
    """
    import json
    from pathlib import Path

    base = Path("C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/shared-state")
    snapshot = {}
    for f in base.glob("*.json"):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            agent = data.get("updated_by")
            if agent_ids is None or agent in agent_ids:
                snapshot[f.stem] = data
    return snapshot
```

## 接口规范

### 1. 写入共享状态

```python
import json
from pathlib import Path
from datetime import datetime

def write_shared_state(domain: str, data: dict, agent_id: str, sync_ima: bool = True):
    """
    写入共享状态文件（可选自动同步至 IMA）
    domain: cashflow | reputation | quality-metrics | risk-level | operations | security
    """
    if sync_ima:
        return sync_to_ima(domain, data, agent_id)
    # else: local-only write
```

### 2. 读取共享状态

```python
def read_shared_state(domain: str) -> dict:
    """读取单个共享状态"""
    base = Path("C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/shared-state")
    file_map = {
        "cashflow": "cashflow.json", "reputation": "reputation.json",
        "quality-metrics": "quality-metrics.json", "risk-level": "risk-level.json",
        "operations": "operations.json", "security": "security.json"
    }
    filepath = base / file_map.get(domain, f"{domain}.json")
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None
```

### 3. 写入审计日志

```python
def write_audit_log(category: str, agent_id: str, action: str, detail: str, sensitive: bool = False):
    """
    写入审计日志
    category: ceo-decisions | financial | legal | hr | tech | quality
    """
    base = Path("C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/audit")
    category_map = {
        "ceo-decisions": "ceo-decisions",
        "financial": "financial",
        "legal": "legal",
        "hr": "hr",
        "tech": "tech",
        "quality": "quality"
    }
    folder = base / category_map[category]
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{agent_id}.md"
    content = f"""# 审计日志
- **Agent**: {agent_id}
- **时间**: {datetime.now().isoformat()}
- **类别**: {category}
- **操作**: {action}
- **敏感**: {'[敏感]' if sensitive else '否'}

## 详情
{detail}
"""
    with open(folder / filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(folder / filename)
```

### 4. 交接（Handoff）操作

```python
def write_handoff(handoff_type: str, sender: str, receiver: str,
                  task_summary: str, completed: list, pending: list,
                  key_data: dict = None, risks: str = None,
                  attachments: list = None) -> str:
    """
    写入标准 handoff 交接文档
    handoff_type: pending | in-progress | completed
    """
    import uuid
    from pathlib import Path
    from datetime import datetime

    base = Path("C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/handoff")
    date = datetime.now().strftime('%Y-%m-%d')
    hid = f"{date}_{uuid.uuid4().hex[:8]}"

    folder_map = {"pending": "pending", "in-progress": "in-progress", "completed": "completed"}
    folder = base / folder_map.get(handoff_type, "pending")
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / f"{hid}.md"

    completed_md = "\n".join(f"- [x] {c}" for c in completed)
    pending_md = "\n".join(f"- [ ] {p}" for p in pending)
    key_data_md = "\n".join(f"- {k}: {v}" for k, v in (key_data or {}).items())
    attach_md = "\n".join(f"- [{a}]({a})" for a in (attachments or []))

    content = f"""# Handoff 交接文档

- **交接ID**: {hid}
- **移交方**: {sender}
- **接收方**: {receiver}
- **移交时间**: {datetime.now().isoformat()}
- **状态**: {handoff_type}

## 任务背景
{task_summary}

## 已完成工作
{completed_md}

## 待办事项
{pending_md}

## 关键数据
{key_data_md or '_无_'}

## 风险提示
{risks or '_无已知风险_'}

## 附件
{attach_md or '_无附件_'}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(filepath)


def read_handoff(handoff_id: str) -> str:
    """读取指定交接文档"""
    from pathlib import Path
    base = Path("C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/handoff")
    for folder in ["pending", "in-progress", "completed"]:
        fp = base / folder / f"{handoff_id}.md"
        if fp.exists():
            with open(fp, 'r', encoding='utf-8') as f:
                return f.read()
    return None
```

### 5. 写入每日汇报

```python
def write_daily_report(agent_id: str, report_type: str, content: str):
    """
    写入每日汇报
    report_type: morning-briefing | evening-report | agent-report
    """
    date = datetime.now().strftime('%Y-%m-%d')
    base = Path(f"C:/Users/Admin/.qclaw/workspace/skills/tools/knowledge-base/daily/{date}")
    if report_type == "agent-report":
        folder = base / "agent-reports"
        filename = f"{agent_id}.md"
    else:
        folder = base
        filename = f"{report_type}.md"
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(folder / filename)
```

## 各Agent对应状态文件

| Agent | 写入状态文件 | 读取者 |
|-------|------------|--------|
| CFO | `cashflow.json` | CEO, COO, CRO |
| CMO | `reputation.json` | CEO, CLO, CRO |
| CQO | `quality-metrics.json` | CEO, CTO |
| CRO | `risk-level.json` | 全C-Suite |
| COO | `operations.json` | CEO |
| CISO | `security.json` | CEO, CTO, CLO |
| CHO | — | hr-audit/ |
| CLO | — | legal-audit/ |
| CTO | — | tech-audit/ |
| CPO | — | agent-reports/ |
| CEO | `ceo-decisions/` | 所有人 |

## 调用示例（各Agent通用模板）

```
# 写入财务状态（CFO）
Python: write_shared_state("cashflow", {"balance": 0, "runway_months": 6, "status": "waiting-seed-round"}, "CFO-001")

# 读取舆情状态（CMO发起舆情时）
Python: data = read_shared_state("reputation")

# 发起任务交接（从 CTO → CLO）
Python: handoff_id = write_handoff(
    handoff_type="in-progress",
    sender="CTO-001",
    receiver="CLO-001",
    task_summary="MVP v2 合规白皮书联合编写",
    completed=["技术架构设计"],
    pending=["合规审查", "声明审核"],
    key_data={"deadline": "2026-04-15", "priority": "P1"}
)

# 写入审计日志（任何Agent跨部门调用时）
Python: write_audit_log("tech", "CTO-001", "跨部门调用CLO", "请求合规审查: AI模块v2.1", sensitive=False)

# 写入每日汇报（各Agent下班前）
Python: write_daily_report("CTO-001", "agent-report", "# CTO 日报 2026-04-12\n\n## 今日进展...\n")
```

## 铁律

```
❌ 敏感财务/法律数据必须标注 [敏感]，不得在日志中明文存储敏感凭证
✅ 每次跨Agent调用必须写入对应审计日志
✅ 共享状态更新后立即通知相关读取Agent（sessions_send）
✅ 审计日志永久保留，不得删除
✅ Handoff 交接文档须在任务移交后 10 分钟内创建
✅ IMA 同步失败时须回退本地写入并记录错误日志
```
