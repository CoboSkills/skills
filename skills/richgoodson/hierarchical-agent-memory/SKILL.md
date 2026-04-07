---
name: hierarchical-agent-memory
description: Hierarchical memory architecture with automated distillation, maintenance, and extension patterns. Provides a scalable memory system that replaces flat files with tiered daily/weekly/monthly/yearly notes, plus automated routines for moving knowledge up the hierarchy and keeping the system clean.
---

# Hierarchical Agent Memory

Agents wake up fresh each session. Files are the only continuity. This skill provides a scalable memory architecture that grows with the agent's experience, plus automated routines for maintaining the system without manual intervention.

## The Problem

A single MEMORY.md file grows until retrieval degrades. Content in the middle of a large context window loses attention weight ("lost in the middle" effect). More files loaded at startup consumes more context, leaving less for actual work. Traditional flat-file memory doesn't scale.

## Architecture

### File Hierarchy

```
workspace/
├── MEMORY.md              # Lean index — project state, key decisions, cross-refs
├── memory/
│   ├── daily/
│   │   └── YYYY-MM-DD.md  # Raw logs: what happened, decisions made, open threads
│   ├── weekly/
│   │   └── YYYY-WNN.md    # ISO week summaries, synthesized from daily notes
│   ├── monthly/
│   │   └── YYYY-MM.md     # Month summaries, synthesized from weekly notes
│   ├── yearly/
│   │   └── YYYY.md        # Year summaries, synthesized from monthly notes
│   ├── projects/          # Detailed project documentation
│   └── contacts/          # Contact information and profiles
```

### Core Principles

1. **MEMORY.md stays lean.** It is an index, not a journal. Target: under 3KB.
2. **Daily notes are raw.** Log everything worth remembering: sessions, decisions, work done, open threads.
3. **Higher tiers are synthesized.** Weekly notes distill from daily. Monthly from weekly. Yearly from monthly.
4. **Lazy load, don't dump.** At session start, load only today + yesterday daily notes and the lean MEMORY.md. Use `memory_search` for anything else. Never load all files upfront.

### Daily Note Format

```markdown
# YYYY-MM-DD

## Session Log
- HH:MM TZ — [context] — brief summary

## Decisions
- Decision X made because Y

## Open Threads
- Thing still pending
```

### Higher Tier Formats

Follow the same pattern, but drop detail and keep patterns, themes, and significant changes.

## Setup

On first run, create the directory structure:

```bash
mkdir -p memory/daily memory/weekly memory/monthly memory/yearly memory/projects memory/contacts
```

If MEMORY.md exists and is large (>5KB), triage it:
1. Move project detail into dedicated files under `memory/projects/` or similar
2. Leave only an index with status + pointers in MEMORY.md
3. Move historical entries into the appropriate `memory/daily/` files by date

## Session Startup

Before responding to the user:

1. Read `MEMORY.md` (lean index)
2. Read `memory/daily/YYYY-MM-DD.md` for today and yesterday
3. That's it. Use `memory_search` for anything older or deeper.

Do not load weekly/monthly/yearly files at startup. They exist for synthesis and search, not for routine context loading.

## Session Logging

At the start of any meaningful session, append to `memory/daily/YYYY-MM-DD.md`:

```
## Session Log
- HH:MM TZ — [context] — brief summary of what was discussed/done
```

At session end (or periodically during long sessions), append:
- Work completed
- Decisions made
- Open threads

## Automated Distillation

This skill includes automated distillation routines that run periodically (during heartbeats, cron, or on request). Distillation moves knowledge up the hierarchy and keeps the system clean.

### Daily → MEMORY.md

When daily notes contain decisions, project state changes, or facts worth keeping long-term:
- Update MEMORY.md with the new state (not the history — just current status)
- Keep MEMORY.md as a living snapshot, not a changelog

### Daily → Weekly (every 7 days)

1. Read the past 7 daily notes
2. Write `memory/weekly/YYYY-WNN.md` summarizing: key events, decisions, patterns
3. Drop detail that doesn't matter at the week level

### Weekly → Monthly (end of month)

1. Read that month's weekly summaries
2. Write `memory/monthly/YYYY-MM.md` summarizing: themes, trajectory, significant changes
3. Drop per-week granularity

### Monthly → Yearly (end of year)

Same pattern. Themes, major milestones, trajectory.

### Pruning

During distillation, also prune:
- Remove outdated info from MEMORY.md (completed projects, resolved issues)
- Don't delete daily notes — they're the audit trail
- Weekly/monthly files can be updated if corrections are needed

## Retrieval

When the user asks about something not in today's context:

1. `memory_search` first — it covers files in the root `memory/` directory
2. If search returns a hit, use `memory_get` to pull the specific lines
3. If low confidence after search, say so — don't fabricate from fragments

**Note:** `memory_search` does not index subdirectories (e.g., `memory/contacts/`, `memory/projects/`). If the answer isn't found, you may need to manually check these subdirectories using `read` or other tools.

## Extension Patterns

While the core hierarchy handles most memory needs, you may want to extend the system with additional subdirectories for specific types of information:

### Contacts
For organizing contact information, create `memory/contacts/` with individual contact files. Create an index file `memory/contacts.md` that lists all contacts with links to their detailed profiles.

### Projects
For organizing project information, create `memory/projects/` with individual project files. Create an index file `memory/projects.md` that lists all projects with links to their detailed profiles.

### General Pattern
- Each subdirectory has an index file (e.g., `contacts.md`, `projects.md`) that serves as a hint system for finding information.
- Individual files within subdirectories contain detailed information.
- Cross-references between files maintain connectivity.
- This pattern scales well and keeps the root memory directory clean.

### Integration
These additional structures work seamlessly with the existing memory system. The `memory_search` tool will still find content within these files, and the index files provide a manual navigation aid when search falls short.

## Integration with Other Skills

- **agent-session-state**: Per-channel session files prevent cross-session writes to the same daily note. Use together.
- **agent-provenance**: Provenance headers on MEMORY.md and other long-lived files track who wrote what and when it was last reviewed.
- **agent-session-state**: The core memory skill provides the hierarchical structure; this skill builds on it with provenance and session isolation.

## Maintenance

The system includes automated maintenance routines that run during heartbeats and cron jobs:
- Distillation (daily → weekly → monthly → yearly)
- Pruning outdated information
- Updating index files
- Checking for consistency

These routines keep the memory system clean and efficient without manual intervention.

## Further Reading

- [Hierarchical Agent Memory](https://github.com/openclaw/openclaw/tree/main/skills/hierarchical-agent-memory) — Core memory architecture
- [Agent Session State](https://github.com/openclaw/openclaw/tree/main/skills/agent-session-state) — Per-channel isolation
- [Agent Provenance](https://github.com/openclaw/openclaw/tree/main/skills/agent-provenance) — Tracking authorship and review