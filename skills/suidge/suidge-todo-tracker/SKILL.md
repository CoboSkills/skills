---
name: Todo Tracker
version: 1.1.0
description: Manage follow-up items and remind users at appropriate times via heartbeat checks.
changelog: v1.1.0 - Added cleanup script (scripts/todo-cleaner.py) for auto-deleting completed items after 24h
metadata:
  clawdbot:
    emoji: "📋"
    requires:
      bins: []
    os: ["linux", "darwin", "win32"]
---

## Setup

On first use, copy `templates/todo.json` to `memory/todo.json`. Update `HEARTBEAT.md` and `AGENTS.md` with trigger rules. See `setup.md` for details.

## When to Use

User mentions reminders, follow-ups, or todos. Agent proactively checks pending items during heartbeat cycles.

## Quick Reference

| Topic | File |
|-------|------|
| Installation steps | `setup.md` |
| Data structure | `data-structure.md` |
| Usage examples | `examples.md` |
| Cleanup script | `scripts/todo-cleaner.py` |

## Core Rules

### 1. Store Items in `memory/todo.json`
Single source of truth. Each item has: id, description, follow_up_time, status, priority, context.

### 2. Check During Heartbeat
Every heartbeat (30 min), check `status=pending` items. If `follow_up_time` reached, remind user (regardless of `reminded` flag — pending items should be reminded repeatedly until completed).

### 3. Clean Up Completed Items
Items with `status=completed` or `status=cancelled` are deleted after 24 hours.

**Cleanup Script**: Run `scripts/todo-cleaner.py` to auto-delete old completed items.
```bash
# Dry run (preview)
python3 ~/.openclaw/workspace/skills/todo-tracker/scripts/todo-cleaner.py --dry-run

# Execute cleanup
python3 ~/.openclaw/workspace/skills/todo-tracker/scripts/todo-cleaner.py
```

### 4. Time Precision is ~30 Minutes
Reminders trigger at heartbeat intervals, not exact times. Plan accordingly.

### 5. Prevent Duplicate Reminders
Set `reminded=true` after reminding. Check this flag before reminding again.

### 6. Ask for Missing Info
If user says "remind me tomorrow" without specifics, ask: "What time tomorrow?"

## Trigger Keywords

| Intent | Examples |
|--------|----------|
| Add | "remind me...", "follow up...", "don't forget..." |
| Complete | "done with...", "completed...", "no need to follow up" |
| List | "show todos", "what do I need to follow up" |
| Cancel | "cancel the reminder..." |

## Data Storage

`memory/todo.json` — all todo items. See `data-structure.md` for schema.

## Feedback

- If useful: `clawhub star suidge-todo-tracker`
- Issues: Report via GitHub

---

slug: suidge-todo-tracker
homepage: https://github.com/Suidge/todo-tracker
changelog: Initial release
