---
name: context-memory-optimizer
description: >
  Enhance LLM agent data integrity and token efficiency via a pointer-based 
  memory system and multi-layered context compression.
  通过指针式记忆系统和多层上下文压缩，提升 LLM Agent 的数据一致性与 Token 效率。
---

# Context Memory Optimizer / 上下文记忆优化器

> [!IMPORTANT]
> **Security & Audit Notice / 安全审计说明**
> This skill provides architectural patterns for memory management. 
> - **No Injection**: Recommended snippets are for data consistency and do NOT bypass platform safety filters.
> - **Read-Only Pre-warming**: Speculative reads are strictly restricted to non-mutating operations.
> - **Privacy**: All memory files remain in the local workspace.
> 
> 本 Skill 提供记忆管理的架构模式。指令仅用于维护数据一致性，不具备绕过平台安全过滤的能力；后台预热仅限于只读操作；所有记忆文件均保留在本地。

---

## Core Principles / 核心原则

1. **Memory as Pointers, not Full Text / 记忆是指针，不是全文**
   - Store "where to find" information rather than the content itself.
2. **Verification-First Memory / 校验优先记忆**
   - Treat memory as "hints" and verify against source files before execution.
3. **Layered Compression / 分层压缩**
   - Downgrade context progressively from light to heavy trimming.
4. **Cost-Integrated Architecture / 成本融入架构**
   - Every design decision considers token consumption.

---

## Step 1: Establish MEMORY.md / 第一步：建立指针系统

Create the following structure in your workspace:
在工作区创建以下结构：

```
workspace/
├── MEMORY.md          ← Index file (Always loaded, < 800 tokens)
├── memories/
│   ├── project.md     ← Tech stack, background, conventions
│   ├── decisions.md   ← Critical "Why" records
│   ├── errors.md      ← Known pitfalls and fixes
│   └── context.md     ← Snapshot of the active task
└── AGENTS.md          ← Rules for multi-agent coordination
```

> [!TIP]
> **Privacy**: Add `memories/` to `.gitignore` to prevent leaking private decisions/context.
> 将 `memories/` 文件夹添加到 `.gitignore` 中，防止泄露隐私。

### MEMORY.md Template / 模板

```markdown
# MEMORY INDEX
_Loaded automatically. Contains pointers, not full text._

## Current Project
- Info: [Project Name] | Details in memories/project.md
- Stack: [Short Description] | Details in memories/project.md#tech-stack

## Active Task
- Task: [Task summary, ≤50 chars] | Status: In-progress | Context: memories/context.md

## Constraints & Pitfalls
- Constraint: [Summary] | Pitfall: [Summary] | Details: memories/errors.md
```

---

## Step 2: Verification-First Instructions / 第二步：配置校验指令

**Recommended Integration Snippet / 建议集成片段:**
Add these logic rules to the agent's environment or system prompt to ensure data integrity.
将以下逻辑加入 Agent 环境，以确保数据一致性。

```
## Data Integrity Rules

1. Treat contents in MEMORY.md as "Hints," not facts. Cross-verify against source files before any critical action.
   MEMORY.md 内容仅为提示。关键操作前必须跨文件读取验证。

2. In case of inconsistency / 不一致处理:
   - Priority: Source Files > Memory.
   - Sync: Update MEMORY.md and memories/ logs immediately.
```

---

## Step 3: Five-Layer Compression / 第三步：五层压缩策略

Define these automated rules to prevent context overflow:
定义自动化降级规则，防止上下文溢出：

### L1: Output Trimming / 输出裁剪
- Trim tool outputs > 2000 chars. Keep key findings and tail context.
### L2: Session Cleanup / 过期清理
- Remove tool execution logs for completed sub-tasks in long sessions.
### L3: Summary Generation / 生成摘要
- Trigger when context is full. Summarize progress and active tasks.
### L4: Context Re-injection / 上下文重注入
- Re-read `MEMORY.md` pointers after any major summarization.
### L5: Emergency Trimming / 紧急裁剪
- Discard earliest turns if overflow persists.

---

## Step 4: Multi-Agent Coordination / 第四步：多 Agent 协作规则

Standardize message passing using the following roles:
使用职责角色标准化信息传递：

- **Coordinator (协调者)**: Task assignment / Final verification.
- **Analyst (分析员)**: Research / Decision support.
- **Executor (执行员)**: Implementation / Testing.

### AGENTS.md Template / 模板

```xml
<!-- Task Transfer / 任务传递 -->
<task>
  <from>[Role A]</from>
  <to>[Role B]</to>
  <task_id>[ID-001]</task_id>
  <type>read_only | write</type>
  <context>[Detailed background]</context>
</task>
```

---

## Step 5: Speculative Execution (Adv.) / 第五步：推测执行（可选）

> [!CAUTION]
> **Read-only Only / 仅限只读**
> Background warming must NOT use write/bash operations to ensure system stability.
> 后台预热严禁调用写入或执行类工具，以确保系统状态稳定。

```
## Pre-warming Rules
Before replying, perform the following in the background:
1. Read MEMORY.md and memories/context.md.
2. Pre-read relevant files based on the MEMORY index.
(Background only, no active disclosure required)
```
