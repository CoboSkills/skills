---
name: agent-session-state
description: Per-channel session isolation, Write-Ahead Log (WAL) protocol, and working buffer management. Prevents cross-session interference, captures decisions and facts reliably, and provides context recovery for long or complex sessions. Designed to work with hierarchical-agent-memory and agent-provenance.
---

# Agent Session State

Agents often serve multiple channels (Discord servers, group chats, etc.) from a single workspace. Without isolation, concurrent sessions can clobber each other's memory writes. This skill provides per-channel session state files, a Write-Ahead Log (WAL) protocol for reliable fact capture, and a working buffer for context recovery during long sessions.

## The Problem

When multiple sessions write to the same memory files simultaneously, content gets duplicated, overwritten, or interleaved. The "lost in the middle" effect is exacerbated by concurrent writes. Important decisions and facts can be lost. Long sessions lose continuity when the agent restarts.

## Architecture

### Per-Channel Session Files

Each Discord channel (or other conversation context) gets its own session state file:

```
memory/sessions/
├── channel:<id>.md  # Channel name
├── channel:<id>.md  # Channel name
└── ...
```

These files store:
- Recent context from that channel
- WAL entries specific to that conversation
- Working buffer status
- Channel-specific preferences

### Write-Ahead Log (WAL) Protocol

The WAL protocol ensures that important information (decisions, facts, preferences) is captured reliably, even in the face of concurrent writes or session restarts.

**Trigger:** Scan every message for:
- ✏️ Corrections — "It's X, not Y" / "Actually..." / "No, I meant..."
- 📍 Proper nouns — Names, places, companies, products (new ones)
- 🎨 Preferences — "I like/don't like X", style choices
- 📋 Decisions — "Let's do X" / "Go with Y"
- 🔢 Specific values — Numbers, dates, IDs, URLs

**The protocol:** If ANY of these appear — write to the session state file FIRST, then respond. The urge to respond is the enemy. Context vanishes. Write it down.

### Working Buffer

During long or complex sessions where compaction is likely, activate the working buffer:
- Update `memory/working-buffer.md` status to ACTIVE
- Log every exchange: User's message + 1-2 sentence summary of the AI's response
- After compaction: read working-buffer.md FIRST to recover context — don't ask "where were we?"
- After compaction: clear and restart the buffer at the start of the next long session

**Note:** There's no precise context meter. This is a judgment call based on session length, conversation density, and complexity. Be honest about that — don't pretend the trigger is mechanical.

## Setup

Create the sessions directory:

```bash
mkdir -p memory/sessions
```

Ensure the agent has write access to this directory. Each channel's session state file is only written by that channel's session, so no cross-session conflicts.

## Session Startup

Before doing anything else in a new session:

1. Read `memory/sessions/{channel}.md` for recent context from this channel
2. Read `memory/working-buffer.md` if active (context recovery)
3. Clear and reset the working buffer if the session is starting fresh

This ensures continuity without loading irrelevant history from other channels.

## WAL Protocol in Practice

When you receive a message that contains a decision, correction, preference, or important fact:

1. **Write to session state file FIRST** (before thinking about your response)
2. Include: timestamp, channel, decision/fact, reasoning if relevant
3. Then respond to the user

Example WAL entry:
```
- [Time] — [Channel] — Decision: [Project] will be deployed with [feature]. Reasoning: [justification].
```

## Working Buffer Protocol

Activate the working buffer during long sessions (judgment call based on complexity):

1. Set `memory/working-buffer.md` status to ACTIVE
2. After each exchange, append: `[timestamp] User: [summary], AI: [1-2 sentence summary]`
3. Keep it concise but meaningful
4. When compaction is triggered (session restart, manual clear), read this file first to recover context
5. After recovery, clear the working buffer and restart if the session continues

## Compaction Recovery

If a session starts mid-task or you should know something but don't:

1. Read `memory/working-buffer.md` first (raw danger-zone exchanges)
2. Read your session state file (`memory/sessions/{channel}.md`)
3. Read today's + yesterday's daily notes
4. If still missing context, `memory_search`
5. Let the user know context was recovered and what you picked up — use natural phrasing, but make it clear you're working from reconstructed context, not continuous memory.

Never ask "what were we discussing?" — the buffer has it.

## Integration with Other Skills

- **hierarchical-agent-memory**: Each channel writes only its own daily note, preventing cross-channel contamination. Use together.
- **agent-provenance**: Session state files include provenance headers tracking when they were created and last modified.

## Best Practices

### For Daily Notes
- Keep channel-specific context in the session state file, not the daily note
- Cross-reference between files as needed
- Use the WAL protocol for important facts

### For Working Buffer
- Don't activate for short, simple sessions
- Do activate for complex problem-solving, coding, or multi-step tasks
- Review and clear periodically to avoid bloat

### For Session State
- Treat this as active working memory, not long-term storage
- Move important decisions to daily notes or MEMORY.md during distillation
- Prune old entries during maintenance routines

## Maintenance

During heartbeat and cron routines:
- Check WAL for completeness
- Flag old entries for distillation to daily notes
- Clean up expired working buffer entries
- Verify session state file integrity

## Further Reading

- [Agent Session State](https://github.com/openclaw/openclaw/tree/main/skills/agent-session-state) — Per-channel isolation
- [Hierarchical Agent Memory](https://github.com/openclaw/openclaw/tree/main/skills/hierarchical-agent-memory) — Memory architecture
- [Agent Provenance](https://github.com/openclaw/openclaw/tree/main/skills/agent-provenance) — Tracking and governance