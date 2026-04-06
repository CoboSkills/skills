---
name: fix
description: >-
  User behavior correction skill. Triggered by "fix:" prefix feedback (e.g., "fix: why didn't you commit?").
  Analyzes the mistake, improves the relevant rule/skill/hook to prevent recurrence,
  then fixes the current issue. TodoWrite required for all steps.
  Use when "fix:", "fix this", "correct", "why not", "why missing", "behavior fix" is mentioned.
---

# Fix: Behavior Correction Skill

Activated when user gives feedback with "fix:" prefix. Finds the root cause of the mistake, improves rules/skills/hooks, and fixes the current issue.

## Trigger

- Messages with `fix:` prefix
- Behavior correction feedback: "fix this", "correct", "why not", "why missing"

## Procedure

**TodoWrite required** — Track all steps with TodoWrite.

### 1. Root Cause Analysis

- Identify **what went wrong** from user feedback
- Search for the responsible **skill/rule/hook** files (Grep/Glob)

### 2. Root Cause Fix (Prevent Recurrence)

Priority:

| Target | Condition | Example |
|--------|-----------|---------|
| **Skill** (`~/.claude/skills/`, `.claude/skills/`) | Skill is incomplete or has wrong procedure | Core build missing in build.sh |
| **Rule** (`~/.agent/rules/`, `.claude/rules/`) | Behavior rule is missing or insufficient | Add to failed-attempts.md |
| **Hook** (`settings.json` hooks) | Automation needed for repeated mistakes | Add PostToolUse hook |
| **SKILL.md docs** | Documentation doesn't match actual behavior | Update "What it does" section |

When fixing:
- Skill improvements must follow **skill-toolkit upgrade** procedure (direct script/topic file edits allowed)
- Rule location must be confirmed via **AskUserQuestion**
- failed-attempts.md recording is **only for cases not covered by skill/rule/hook** — no duplicate recording if root cause is already reflected in a skill or rule

### 3. Fix Current Issue + Resume Original Work

- After root cause fix, **immediately resolve the current problem**
- Verify fix results (build/test/run)
- **Continue the originally intended work with the corrected approach** — don't just clean up wrong artifacts, complete the original task
- Register the original task with TaskCreate and execute immediately

### 4. Completion Report

```
Fix complete:
- Root cause: {what was missing}
- Improvement: {which file was modified and how}
- Current fix: {result of fixing the current issue}
```

## Anti-patterns

- Repeating "already fixed" without actually fixing the root cause
- Patching only the current issue without improving skills/rules/hooks
- Proceeding without TodoWrite
