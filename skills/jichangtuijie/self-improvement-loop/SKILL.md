---
name: self-improvement-loop
version: 4.3.2
description: |
  openclaw self-evolution loop — Hook captures feedback, distill detects patterns,
  threshold triggers notification, user decides A/B/C, AI creates/updates skills.
  Auto-detects the first available channel from openclaw.json (Telegram, Discord, ...).
  Architecture: skill package + install.sh → canonical scripts → Cron scheduler.
---

# self-improvement-loop v4.3.2

Automated experience → pattern → skill evolution loop.

---

## Architecture

```
openclaw.json ──→ install.sh ──→ Auto-detect first available channel
                              └─→ (Telegram / Discord / ...)
                                    ↓
User message ──→ Hook (handler.js) ──→ .learnings/*.md

self-improvement-check Cron (every 30min, bound to main session)
  ├─→ distill.sh --check-only → distill_json.py → JSON
  ├─→ Semantic understanding + write notified state
  ├─→ Write .pending_notifications/<ts>_<pattern>.json
  └─→ Cron AI (current session)
        └─→ Send A/B/C notification to auto-detected channel
              ↑
User replies A / B / C on that channel
        ↓
    Main session receives message
        ↓
    Detects A/B/C → reads pending_notifications/ → executes skill-creator
```

**Design principle**: Scripts do mechanics, AI does semantics.

---

## Components

| Component | Trigger | Role |
|----------|---------|------|
| `handler.js` | Real-time | Detect CORRECTION/ERROR/FEATURE keywords, write to learnings |
| `distill.sh` | Cron | Mechanical scan, extract fields, output raw data |
| `distill_json.py` | Cron | Python JSON generator |
| `write_notified.py` | Cron | Write Notified state back to MD |
| `reflect_self.py` | distill | Self-check mechanism |
| `archive.sh` | Cron | Archive resolved/promoted entries |
| `match-existing-skill.sh` | Cron | Match existing skills (mechanical, outputs candidates) |

---

## Notification Trigger

```
count >= 2 + (notified == null OR notified == false OR notification_count < count)
```

| Condition | Behavior |
|-----------|----------|
| count = 1 | Silent |
| count >= 2 + never notified | ✅ Send A/B/C |
| count >= 2 + count grew | ✅ Re-notify |
| count >= 2 + no growth | Silent |
| User picks C | dormant, skip |

---

## A/B/C Response Handling

When the Cron sends a notification to the auto-detected channel and the user replies A / B / C:

1. Cron writes context to `~/.openclaw/workspace/.learnings/.pending_notifications/<ts>_<pattern>.json`
2. User replies on Telegram
3. Main session receives and processes the reply
4. A/B/C handler: reads pending JSON → executes skill-creator (A/B) or marks dormant (C)

## Installation

```bash
bash ~/.openclaw/workspace/skills/self-improvement-loop/install.sh
openclaw gateway restart
bash ~/.openclaw/workspace/scripts/self-improvement/distill.sh --check-only
```

---

## Usage

1. **Auto-capture** — Hook detects keywords in real-time, writes to learnings
2. **Cron detection** — Every 30min, distill runs, count >= 2 triggers A/B/C
3. **User decision** — Reply A/B/C to create/optimize/skip
4. **Auto-close loop** — On A/B, calls skill-creator to execute

---

## File Locations

```
~/.openclaw/workspace/
├── scripts/self-improvement/   ← Canonical Source
│   ├── distill.sh / distill_json.py / write_notified.py
│   ├── archive.sh / match-existing-skill.sh / reflect_self.py
├── .learnings/                ← Experience storage
│   ├── LEARNINGS.md / ERRORS.md / FEATURE_REQUESTS.md
│   └── DISTILL-SELF.md
$HOME/.openclaw/hooks/self-improvement/
└── handler.js
```

---

## Dependencies

| Dependency | Note |
|-----------|------|
| OpenClaw | Base platform |
| Python3 | distill_json.py / write_notified.py / reflect_self.py |
| Node.js | OpenClaw + handler.js |
| skill-creator | Executes skill create/optimize on A/B |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| v4.3 | 2026-04-20 | distill_json.py (Python JSON), write_notified.py (write-back-first) |
| v4.3.2 | 2026-04-20 | Channel auto-detection: install.sh scans openclaw.json for available channels |
| v4.2 | 2026-04-20 | pending_only, reflect_self, self-check mechanism |
| v4.0 | 2026-04-19 | Script/AI split, match-existing-skill mechanical-only, archive silent |
