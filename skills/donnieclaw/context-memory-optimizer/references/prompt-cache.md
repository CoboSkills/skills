# Prompt Cache Optimization / 缓存优化参考

Best practices based on LLM caching mechanisms (e.g., Claude API).
基于主流 LLM（如 Claude API）缓存机制的最佳实践。

---

## Core Principle / 核心原则

LLM API Prompt Cache mechanism: In consecutive turns, segments with the same prefix are cached. 
API 缓存机制：连续对话中，相同前缀的内容会被缓存，大幅减少计费并提升响应速度。

Optimization goal: **Keep the static part of the system prompt stable.**
优化目标：**保持静态 System Prompt 稳定，避免破坏前缀缓存。**

---

## Segmentation Strategy / 分段策略

### ✅ Static Area / 静态区 (Cache-friendly / 缓存友好)
Place generic definitions and rules here.
放置通用的角色定义和规则。

```
# Role Definition / 角色定义
You are a [Specialist]...

# Tool Usage Rules / 工具使用规则
## Read/Write/Bash
- Constraints...
- Output trimming rules...
```

### ✅ Dynamic Area / 动态区 (Updates per turn / 每轮更新)
Place context-specific data here at the **end** of the prompt.
将动态变化的内容放在 Prompt **末尾**。

```
--- DYNAMIC BOUNDARY ---

# Active Context / 当前上下文
{Content from MEMORY.md}

# Current Task / 当前任务
{Task description}

# Environment / 环境信息
Time: {Timestamp} | Path: {Working Dir}
```

---

## Implementation Example / 配置示例

```yaml
system_prompt_static: |
  你是 [Agent Role]，负责 [Responsibilities]。
  [Stable rules...]
  
system_prompt_dynamic_template: |
  --- CONTEXT START ---
  {memory_content}
  
  Task: {current_task}
  Time: {timestamp}
```

---

## Common Mistakes / 常见错误

| Error / 错误做法 | Fix / 正确做法 |
|---------|---------|
| Put timestamp at start / 时间戳放开头 | Move to Dynamic Area / 移至动态区末尾 |
| Insert summary in middle / 摘要插在中间 | Keep Static Area intact / 保持静态区连续 |
| Dynamic tool descriptions / 动态增删工具描述 | Use fixed tool list / 工具描述列表固定 |
