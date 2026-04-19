# ERRORS.md — 命令 / 集成错误记录

> 由 self-improvement-loop skill 管理。

---

## 模板格式

```markdown
## [ERR-YYYYMMDD-NNN] error
**Logged**: ISO-8601
**Status**: pending | resolved
**Pattern-Key**: <source>.error.<identifier>

### Error
```
错误信息
```

### Root Cause
...

### Fix
...

*---*
```

---

## 示例（可删除）

## [ERR-20260401-001] error
**Logged**: 2026-04-01T00:00:00+08:00
**Status**: pending
**Pattern-Key**: tool.hook.keyword.missing

### Error
Hook 未检测到 "能不能" 关键词

### Root Cause
handler.js ERROR_KEYWORDS 中不应包含 "能不能"（功能请求，非错误）

### Fix
已修复，详见 handler.js

*---*
