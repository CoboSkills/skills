# Compression Examples / 压缩示例对照

Real-world scenarios for context compression to help you determine the depth of trimming.
真实场景的对照示例，辅助判断裁剪深度。

---

## Ex 1: Tool Output Trimming (L1) / 工具输出裁剪

### Before (3000+ chars)
```
$ git log --oneline -50
a1b2c3d feat: add user authentication
d4e5f6g fix: resolve login redirect bug
... (50 records expanded) ...
```

### After (Bilingual, ~200 chars)
```
[git log clipped] Recent 50 commits. Key entries:
- a1b2c3d feat: add user authentication (3 days ago)
- d4e5f6g fix: resolve login redirect bug (2 days ago)
- [HEAD] feat: context memory optimization
Full log available via `git log --oneline -50`.
```

---

## Ex 2: Conversation Summary (L3) / 对话摘要

### Before (40 turns, 15000+ tokens)
```
User: Analyze this script...
Agent: Reading... analysis: ...
... (Many turns of back-and-forth) ...
User: Write tests now.
```

### After (Bilingual, ~500 tokens)
```
## Conversation Summary / 对话摘要 (Turns 1-40)

**Completed / 已完成:**
- Analyzed performance of scripts/data_processor.py.
- Optimized DB queries (Batching, ~3x speedup).
- Fixed memory leak in Turn 23 (Commit d4e5f6g).

**Current Status / 当前状态:**
- Task: Writing pytest cases for data_processor.py.
- Pending: Choice between pytest and unittest?

**Conventions / 重要约定:**
- Style: PEP8, Type hints required.
- Files: Do NOT modify config.py per client request.
```

---

## Ex 3: Multi-Agent Tasking (De-identified) / 多任务传递

### ❌ Incorrect (Ambiguous)
Agent-A: "Agent-B, check the DB script, tell Agent-C to write tests, don't change config."

### ✅ Correct (Structured YAML/XML)
```xml
<task>
  <from>Coordinator</from>
  <to>Analyst</to>
  <task_id>20260401-003</task_id>
  <type>read_only</type>
  <context>
    Performance optimization finished for data_processor.py.
    Need coverage analysis.
  </context>
  <input>scripts/data_processor.py</input>
  <expected_output>
    List functions to test with:
    1. Priority 2. Mocking needs 3. Edge cases.
  </expected_output>
  <constraints>
    - Read-only analysis.
    - Skip config.py logic.
  </constraints>
</task>
```
