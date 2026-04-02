---
name: claws-dream
description: "World-class cognitive memory consolidation for OpenClaw — periodic dream cycles inspired by the KAIROS dream mechanism system. Consolidates daily logs into structured long-term memory with importance scoring, health metrics, smart skip, and rich notifications. Use when: user asks to 'dream', 'consolidate memory', 'run auto memory', or 'memory status'. Features: 5-metric health scoring, importance-based forgetting curve, milestone tracking, streak counting, and HTML dashboard generation. Version 2.2."
---

# 🦐 Nightly Dream — Memory Consolidation System

> "While you sleep, your memories consolidate. Now your AI does too."

A biologically-inspired memory consolidation system. Every night, fragments of your interactions are distilled into structured long-term knowledge — duplicates merged, insights captured, stale memories gracefully archived.

## Features

- 🌙 **Four-Stage Dream Cycle**: Orient → Gather → Consolidate → Prune
- 📊 **5-Metric Health Score**: Freshness, Coverage, Coherence, Efficiency, Reachability
- 🎯 **Importance Scoring**: Base weight × recency × reference boost
- 🗑️ **Forgetting Curve**: Automatic archival of stale, low-importance entries
- 🔗 **Knowledge Graph**: Related entries tracked via index.json
- 📈 **Milestones**: First dream, streaks, entry count milestones
- 🏥 **Smart Skip**: No new content? Still delivers value with memory recall
- 📊 **Dashboard**: Auto-generated HTML health dashboard
- 🔔 **Rich Notifications**: Growth metrics, highlights, insights, stale threads

## Memory Architecture

```
workspace/
├── MEMORY.md              # Structured long-term knowledge
└── memory/
    ├── index.json         # Entry metadata + health stats
    ├── procedures.md       # Workflow preferences
    ├── archive.md         # Archived entries (faded)
    ├── dream-log.md       # Consolidation reports
    ├── dashboard.html     # Generated health dashboard
    ├── YYYY-MM-DD.md      # Daily interaction logs
    └── episodes/          # Project narratives
```

## Quick Start

### Manual Trigger
```
"Run dream" / "Consolidate memory" / "Dream now"
```

### Automatic (Cron)
Pre-configured cron job runs at 03:00 daily.

## Dream Cycle Flow

### Step 0: Smart Skip
Checks for unconsolidated logs. If none → still delivers value via memory recall.

### Step 1: Collect
Reads unconsolidated daily logs. Extracts decisions, facts, lessons, todos.

### Step 2: Consolidate
Compares with MEMORY.md. Semantic dedup. New → append, Updated → modify, Duplicate → skip.

### Step 3: Score & Prune
Computes health score (5 metrics). Archives stale entries below importance threshold.

### Step 4: Notify
Sends rich notification with growth metrics, highlights, insights, and suggestions.

## Health Metrics

| Metric | Weight | Description |
|--------|--------|-------------|
| Freshness | 25% | Entries referenced in last 30 days |
| Coverage | 25% | Sections updated in last 14 days |
| Coherence | 20% | Entries with relation links |
| Efficiency | 15% | MEMORY.md line count (concise) |
| Reachability | 15% | Connected components in graph |

## Importance Markers

| Marker | Effect |
|--------|--------|
| 🔥 HIGH | 2x importance weight |
| 📌 PIN | Exempt from archival |
| ⚠️ PERMANENT | Never archive or modify |

## Archival Rules

Entry archived when ALL true:
- 90+ days since last referenced
- Importance < 0.3
- Not marked PIN or PERMANENT
- Not in episodes/

## Manual Commands

| Command | Action |
|---------|--------|
| "Dream now" | Run full consolidation |
| "Memory status" | Show health score + stats |
| "Memory dashboard" | Generate dashboard.html |
| "Memory export" | Export memories to JSON |

## ⚠️ Timeout Configuration (Critical!)

**This skill requires a longer timeout to run properly.** Add this to your `openclaw.json` under `agents.defaults`:

```json
"agents": {
  "defaults": {
    "timeoutSeconds": 300
  }
}
```

Without this, the dream consolidation will timeout and fail. The skill scans many files and needs time to read, analyze, and write memory.

## Cron Configuration

```json
{
  "name": "claws-dream",
  "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run auto memory consolidation. Read skills/claws-dream/references/dream-prompt.md and follow every step strictly.",
    "timeoutSeconds": 300
  }
}
```

## Reference Files

- `references/dream-prompt.md` — Full consolidation prompt

- `references/first-dream-prompt.md` — First run initialization
- `references/scoring.md` — Health score algorithms
- `references/memory-template.md` — File templates
- `references/dashboard-template.md` — HTML dashboard template

## Safety Rules

1. **Never delete daily logs** — only mark with `<!-- consolidated -->`
2. **Never remove ⚠️ PERMANENT items** — user-protected
3. **Safe changes** — if MEMORY.md changes >30%, save .bak first
4. **Scope** — only read/write memory/ directory and MEMORY.md

---

_Version 2.2 — Built with 🦐 by Crayfish Liu_
