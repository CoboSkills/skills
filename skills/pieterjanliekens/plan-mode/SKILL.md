---
name: plan
description: "Think-first execution: research, plan, approve, execute. For complex multi-step or irreversible tasks. Not for simple edits or quick questions."
---

# 📋 Plan Mode

**Stop your AI agent from yolo-executing complex tasks.**

Every AI coding agent has the same problem: you ask for something complex and it immediately starts hacking away — editing files, running commands, deploying things — before you've even agreed on the approach. Plan Mode fixes this with a simple, battle-tested pattern: **Research → Plan → Approve → Execute.**

Inspired by how 8 tools handle planning (Claude Code, Aider, Codex, Cursor, Windsurf, Roo Code, ExecPlan, claw-superpowers) — distilled into one lightweight, agent-agnostic skill.

## ✨ What Makes This Different

| Feature | Most agents | With Plan Mode |
|---|---|---|
| Complex task lands | Immediately starts editing | 📋 Researches first, presents plan |
| You want changes to the approach | Too late, already done | Revise plan before any action |
| Existing skills/tools | Agent reinvents the wheel | **Toolbox audit** — checks what's already installed |
| Something goes wrong mid-task | Silent fix attempt | Stops, reports, asks what to do |
| Simple quick fix | Same ceremony as big refactor | Auto-skips — no plan needed |

## 🚀 Quick Start

```bash
clawhub install plan-mode
```

After install, `/plan` shows up as a **native slash command** (autocomplete on Discord/Telegram).

**Three modes:**

| Command | What it does |
|---|---|
| `/plan` | Full planning mode — research, plan, approve, execute |
| `/plan light` | Quick inline plan only — minimal ceremony |
| `/plan off` | Disable auto-activation for this session |

**That's it.** Your agent will now stop and think before acting on complex tasks.

## 💡 The Toolbox Audit (unique to this skill)

Before writing a plan, the agent checks:
- ✅ **What skills are already installed** — "I have `pdf-generator`, I'll use it"
- 💡 **What's available on ClawHub** — "There's a `remotion` skill for video. Install it?"
- 🚫 **What NOT to reinvent** — no more hand-rolled solutions when a skill exists

This prevents the #1 waste of AI agent time: rebuilding capabilities that already exist in your toolbox.

## 📖 Example

**You:** "Migrate our auth from sessions to JWT"

**Agent (without Plan Mode):** *immediately starts editing 15 files...*

**Agent (with Plan Mode):**
```
📋 Planning this first...

## Plan: Auth Migration (Sessions → JWT)

**Goal:** Replace session auth with stateless JWT tokens.
**Approach:** Dual-mode first (both work), migrate incrementally, then remove sessions.

**Using:**
- ✅ Already installed: github — for PR creation after migration

**Steps:**
1. Add JWT utils → new `lib/jwt.ts`
2. Create dual-auth middleware → `middleware/auth.ts`
3. Migrate login endpoint → `routes/auth.ts`
4. Update 12 protected routes → `routes/*.ts`
5. ⚠️ Remove session store → irreversible
6. Update tests (23 files)

**Risks:** Active sessions invalidated on deploy → 24h overlap period
**Estimate:** deep (2-3 hours, may use subagents)
```

**You:** "do steps 1-4, hold on 5"

**Agent:** *executes steps 1-4, pauses before the irreversible step*

## 🔧 How It Works

### The Four Phases

**Phase 1: Research** *(internal, no output)*
- Reads relevant files and checks current state
- Audits installed skills and searches ClawHub for relevant tools
- Max 5-10 tool calls — focused, not exhaustive

**Phase 2: Plan** *(presented to you)*
- Format scales: **inline** (1-2 steps) → **standard** (3-7) → **living document** (8+)
- Includes a `Using:` section showing which skills/tools will be leveraged
- Complex plans get saved to file for context compaction survival

**Phase 3: Approve** *(your call)*

| You say | What happens |
|---|---|
| "go" / "do it" / 👍 | Execute full plan |
| "do steps 1-3, hold on 4" | Partial execution |
| "change X" | Revise and re-present |
| "skip plan" / "just do it" | Exit plan mode |
| "cancel" | Abort |

**Phase 4: Execute** *(follows the plan)*
- No scope creep — only what was approved
- Surprises trigger stop → report → wait for your input
- Subagent delegation with full context handoff

### When It Activates (and when it doesn't)

**Auto-activates:** `/plan` command · 3+ files/systems · irreversible actions · architecture decisions

**Stays out of the way:** Quick fixes · single file edits · "just do it" · subagent execution · `/plan off`

### Safety

- **Hard gate:** Agent cannot act until you approve — no exceptions
- **Irreversible steps** flagged with ⚠️
- **Mid-execution surprises** trigger immediate pause
- **No nested planning** — subagents execute directly
- **Context-aware** — uses compact format when context is >80K tokens

## 🤝 Compatibility

Works with **OpenClaw** (native `/plan` command), **Claude Code**, **Codex**, **Cursor**, **Windsurf**, **Roo Code**, and any agent that loads SKILL.md files.

## 📚 Research

This skill was built by analyzing planning patterns across 8 tools. The full comparative analysis (Claude Code permission modes, Aider architect/editor split, Windsurf background planner, Roo Code orchestrator, ExecPlan living documents, claw-superpowers hard gates) is in `references/patterns.md`.

## License

MIT
