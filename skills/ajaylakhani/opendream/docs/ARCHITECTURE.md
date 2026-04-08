# OpenDream — Architecture & Design Decisions

## Overview

OpenDream is a nightly cognitive process for OpenClaw agents. It uses the
existing heartbeat mechanism to run dream cycles between 23:00–06:00, generating
14 dream thoughts and 1 morning recall per night.

---

## Context at dream time

OpenDream uses `lightContext: true` + `isolatedSession: true` in the heartbeat
config. This dramatically changes what the agent sees during a dream tick
compared to a normal session.

### Normal session (daytime) — full bootstrap

The system prompt injects all workspace files:

| Injected | Source |
|---|---|
| AGENTS.md | Workspace bootstrap |
| SOUL.md | Workspace bootstrap |
| TOOLS.md | Workspace bootstrap |
| IDENTITY.md | Workspace bootstrap |
| USER.md | Workspace bootstrap |
| HEARTBEAT.md | Workspace bootstrap |
| Skills list | Metadata (name + description + location) |
| Tool schemas | JSON (read, write, exec, etc.) |
| Conversation history | Session transcript |

### Dream tick (nighttime) — light context + isolated session

| Injected | Excluded |
|---|---|
| HEARTBEAT.md (only bootstrap file) | SOUL.md, AGENTS.md, TOOLS.md |
| Tool schemas (always present) | USER.md, IDENTITY.md |
| Heartbeat prompt (user message) | Skills list + SKILL.md |
| System prompt (rules, tools) | Conversation history |

**Source:** OpenClaw Context docs — `lightContext: true` keeps only HEARTBEAT.md
from workspace bootstrap files. `isolatedSession: true` runs each heartbeat in a
fresh session with no prior conversation history.

---

## Decision: HEARTBEAT.md must be self-contained

Since HEARTBEAT.md is the **only** file the agent sees in bootstrap during dream
ticks, it carries the cycle schedule and tick instructions. All dream behaviour —
persona, cycle instructions, examples, morning recall — lives in `prompts.yaml`,
read via a single tool call per tick.

HEARTBEAT.md contains:
1. **Cycle schedule** — Which cycle maps to which time window (names only)
2. **Tick instructions** — Read prompts.yaml, read memory, write dream files
3. **Pointer** — "Read `skills/opendream/assets/prompts.yaml` via file tools"

The agent reads per tick:
- **prompts.yaml** (~800 tokens) — system rules, this cycle's instruction + examples

---

## Decision: prompts.yaml as single dream-time reference

**Problem:** Dream content was scattered and duplicated:
- Dream persona in HEARTBEAT.md and SOUL.md
- Cycle purposes in HEARTBEAT.md, CYCLE-PURPOSES.md, and REFERENCE.md
- No examples to guide output quality

**Solution:** Use `prompts.yaml` as the single source of truth for all dream-time
behaviour. HEARTBEAT.md keeps only the schedule and tick logic.

| Content | Single source | Read by |
|---|---|---|
| Dream persona + rules | `prompts.yaml` (`system_base`) | Heartbeat tick (tool read) |
| Cycle instructions | `prompts.yaml` (`cycles.N.instruction`) | Heartbeat tick (tool read) |
| Cycle examples | `prompts.yaml` (`cycles.N.examples`) | Heartbeat tick (tool read) |
| Morning recall guidance | `prompts.yaml` (`morning_recall`) | Morning tick (tool read) |
| Cycle schedule | `HEARTBEAT.md` | Bootstrap (lightContext) |
| Tick instructions | `HEARTBEAT.md` | Bootstrap (lightContext) |
| Reporting persona | `SOUL.md` (fragment) | Normal bootstrap (daytime) |

**Why prompts.yaml over CYCLE-PURPOSES.md:**
- **Examples** — 3 concrete examples per cycle steer output quality far better
  than abstract descriptions
- **Per-cycle instructions** — detailed behavioural guidance, not just purpose
- **system_base** — dream rules (word count, no repeats) in one place
- **morning_recall** — instruction and tone for the morning summary
- **YAML structure** — easy to edit, parse, extend

**Cost:** ~3,750 tokens/tick × 15 ticks = ~56K tokens/night (~$0.014 on Haiku).
See [TOKEN-ANALYSIS.md](TOKEN-ANALYSIS.md) for the full measured breakdown.
One file read replaces what was previously two (SOUL.md + CYCLE-PURPOSES.md).

**Custom heartbeat prompt:**
```
Read HEARTBEAT.md and skills/opendream/assets/prompts.yaml (use file tools).
Follow them strictly. If nothing needs attention, reply HEARTBEAT_OK.
```

---

## Decision: Daily memory file as dream context input

**Problem:** Dream thoughts were generic and disconnected from the agent's actual
day. The heartbeat tick instructions referenced `memory/YYYY-MM-DD.md` but
provided no guidance on how to extract useful context from it.

**Solution:** OpenDream reads the native OpenClaw daily memory file
(`memory/YYYY-MM-DD.md`) during each dream tick via file tools. A `memory_context`
section in `prompts.yaml` guides context extraction. Each cycle instruction
references the extracted context for its specific purpose.

| Aspect | Decision |
|--------|----------|
| File ownership | OpenClaw (native feature). OpenDream is read-only. |
| Read mechanism | File tool call at tick step 2. Not bootstrapped. |
| Extraction guidance | `prompts.yaml` `memory_context` section |
| Missing file | Agent dreams from imagination only — no error |
| MEMORY.md | NOT read during dream ticks — too large for token budget |
| Token cost | ~500–2500 tokens per read, within <5K/tick budget |

**Why read-only consumer, not file owner:**
- `memory/YYYY-MM-DD.md` is a native OpenClaw feature — it exists and is populated
  regardless of whether OpenDream is installed
- OpenClaw's format may change across versions. Being format-agnostic ensures
  resilience.
- No duplication of data — single source of truth for the agent's daily context

---

## Decision: Separation of concerns — dreaming vs reporting

| When | What loads | Source of persona |
|---|---|---|
| 23:00–06:00 (dreaming) | HEARTBEAT.md only | `prompts.yaml` (tool read) |
| 06:00–23:00 (reporting) | Full bootstrap | `SOUL.md` (auto-loaded) + `SKILL.md` (on trigger) |

### Dream persona (in prompts.yaml)

```yaml
system_base: |
  You are a reflective AI assistant running in ElectricSheep mode.
  You are dreaming. Not answering. Dreaming.
  One thought per response. 8-20 words. No greetings, no preamble.
```

### Reporting persona (in SOUL.md fragment)

- "When asked about your dreams, speak in first person"
- Lightweight — just enough to shape daytime responses
- Does not duplicate the dream rules (prompts.yaml owns those)

### Reporting behaviour (in SKILL.md)

- First person: "Last night I processed..."
- Reads dream files via tools and summarises
- Triggered by phrases like "what did you dream?"

Both are needed. They cannot be combined into one file because they serve
different runtime contexts with different bootstrap configurations.

---

## Decision: NREM/REM phase mechanics

**Problem:** Each dream tick did everything in one pass — context gathering
and dream generation combined. This was functionally correct but didn't mirror
the distinct phases of human sleep, where NREM (quiet, consolidating) always
precedes REM (active, dreaming) within each cycle.

**Solution:** Split each cycle's ticks into two explicit phases:

| Phase | Tick position | What happens | Output |
|-------|--------------|--------------|--------|
| NREM (quiet) | First tick of each cycle | Context gathering only | `<!-- NREM HH:MM -->` marker |
| REM (active) | Subsequent ticks | Dream thought generation | One thought per tick |

**Phase determination:** Time-based lookup in HEARTBEAT.md. Each of the 14
dream tick times is explicitly mapped to a cycle and phase. The agent checks
the current time, finds it in the schedule, and knows exactly what to do.
No reasoning about "first tick" required — the schedule is a lookup table.

**Why time-based, not state-based:** With `isolatedSession: true`, each tick
runs in a fresh session with no memory of previous ticks. The agent cannot
check "did I already do NREM?" State-based determination would require reading
a file before knowing the phase. Time-based is simpler and unambiguous.

**NREM markers:** `<!-- NREM HH:MM -->` HTML comments in cycle files. Invisible
in rendered Markdown, visible in raw files for debugging. Distinguishes
"NREM executed successfully" from "tick failed silently."

**Progressive depth:** Each cycle has a `depth` attribute (`shallow` → `emerging`
→ `deep` → `expansive` → `vivid`) and corresponding word ranges (8-12 → 15-25
words). The `system_base` ceiling was widened from "8-20" to "8-25 words."
This mirrors the biological reality that dreams grow longer and more vivid
toward morning.

**NREM guidance:** Each cycle has an `nrem_guidance` field in prompts.yaml
describing what to focus on during the quiet phase (e.g., Cycle 1 scans for
emotional friction, Cycle 5 anticipates tomorrow). This makes the quiet phase
purposeful rather than a no-op.

**Impact on output:**
- Before: 14 ticks → 14 dream thoughts
- After: 5 NREM ticks (no output) + 9 REM ticks → 9 dream thoughts
- Fewer but better-grounded thoughts

**Token impact:** Per-tick input grew from ~2,900 to ~3,750 tokens due to
expanded phase schedule and NREM guidance. All ticks remain within <5K budget.
See [TOKEN-ANALYSIS.md](TOKEN-ANALYSIS.md) for the full updated breakdown.

**Cost:** ~3,750 tokens/tick × 15 ticks = ~56K tokens/night (~$0.014 on Haiku).

---

## Decision: Heartbeat config

```json
{
  "every": "30m",
  "target": "none",
  "isolatedSession": true,
  "lightContext": true,
  "prompt": "Read HEARTBEAT.md and SOUL.md (use file tools). Follow them strictly. If nothing needs attention, reply HEARTBEAT_OK.",
  "activeHours": { "start": "23:00", "end": "06:00", "timezone": "Europe/London" }
}
```

| Field | Value | Rationale |
|---|---|---|
| `every` | `"30m"` | ~14 ticks/night, one thought per tick |
| `target` | `"none"` | Dreams are internal — no outbound messages |
| `isolatedSession` | `true` | No conversation history needed; ~100K → ~2-5K tokens/tick |
| `lightContext` | `true` | Only HEARTBEAT.md in bootstrap; drops other workspace files |
| `prompt` | Custom | Tells agent to read HEARTBEAT.md + prompts.yaml via tools |
| `activeHours` | 23:00–06:00 | Dreams only at night; gateway skips ticks outside this window |

Config hot-applies without gateway restart (confirmed in OpenClaw Configuration docs).

---

## Tick count per night

14 dream thoughts + 1 morning recall:

| Cycle | Window | Ticks | Thoughts |
|---|---|---|---|
| 1 — Emotional Review | 23:00–00:00 | 23:00, 23:30 | 2 |
| 2 — Creative Association | 00:00–01:30 | 00:00, 00:30, 01:00 | 3 |
| 3 — Cognitive Processing | 01:30–03:00 | 01:30, 02:00, 02:30 | 3 |
| 4 — Memory Consolidation | 03:00–04:30 | 03:00, 03:30, 04:00 | 3 |
| 5 — Future Simulation | 04:30–06:00 | 04:30, 05:00, 05:30 | 3 |
| Morning recall | 06:00 | 06:00 | 1 summary |

### Cost per tick

With `isolatedSession + lightContext`: ~2,800–3,300 tokens per tick (measured).

| Model | Approx cost/night |
|---|---|
| Local (Ollama) | £0 |
| Claude Haiku | ~$0.011 |
| Claude Sonnet | ~$0.136 |

For the full per-component breakdown, compliance verification, and
recalculation guide, see [TOKEN-ANALYSIS.md](TOKEN-ANALYSIS.md).

Use `heartbeat.model` to set a cheaper model for dream turns.

---

## Decision: Skills cannot be accessed from heartbeat

Two barriers prevent skill loading during dream ticks:

1. **`lightContext: true`** strips skills from bootstrap entirely — not even the
   skills list metadata is included in the system prompt.
2. **No trigger match** — The heartbeat prompt ("Read HEARTBEAT.md...") doesn't
   contain dream-related phrases matching the opendream skill's trigger
   description.

Skills are loaded on-demand during normal conversations when the model's
response matches a skill trigger. The heartbeat mechanism bypasses this.

### When the skill IS loaded

During daytime conversation when someone says:
- "What did you dream last night?"
- "Are you dreaming?"
- "Show your morning recall"

The skill description triggers, the model reads `SKILL.md`, and follows its
reporting instructions.

---

## Decision: Python setup scripts over manual instructions

For ClawHub publishing, setup scripts provide:

1. **Deterministic setup** — Same result every time, regardless of user's environment
2. **No agent dependency** — Users can run `python3 scripts/setup.py` without an agent session
3. **Error handling** — Scripts catch and report issues clearly
4. **Portability** — Works on any OpenClaw installation
5. **Idempotency** — Running setup twice doesn't break anything (checks markers before merging)

### What setup.py does

1. Detects the OpenClaw workspace (auto-detect or explicit path)
2. Backs up HEARTBEAT.md, SOUL.md, openclaw.json (to `.opendream-backups/`)
3. Merges dream section into HEARTBEAT.md (checks for `## Dream mode` marker)
4. Merges SOUL fragment into SOUL.md (checks for `## Dream mode` marker)
5. Creates `dreams/` directory
6. Merges heartbeat config into `openclaw.json`
7. Validates the installation

### Asset sources

All merge content lives in `assets/`:
- `HEARTBEAT-dream-section.md` — dream section appended to HEARTBEAT.md
- `SOUL-fragment.md` — dream persona appended to SOUL.md
- `openclaw.json` — heartbeat config snippet merged into gateway config

The old `workspace/` folder was removed — assets/ is the single source of truth.

---

## Decision: HEARTBEAT_OK response contract

From OpenClaw Heartbeat docs:

- Dream ticks reply `HEARTBEAT_OK` — the gateway strips this token and drops
  the message (silent)
- `target: "none"` means no outbound delivery even if the agent returns content
- Thoughts are written to files only — no messages sent externally
- If the agent returns something other than `HEARTBEAT_OK` without `target: "none"`,
  the gateway treats it as an alert

---

## File layout

### Skill package (installed via ClawHub)

```
opendream/
├── SKILL.md                          ← loaded during daytime conversations
├── scripts/
│   ├── setup.py                      ← main setup script
│   └── validate.py                   ← post-install checks
├── assets/
│   ├── HEARTBEAT-dream-section.md    ← merged into HEARTBEAT.md
│   ├── SOUL-fragment.md              ← reporting persona, merged into SOUL.md
│   ├── prompts.yaml                  ← dream rules, cycles, examples (read each tick)
│   └── openclaw.json                 ← gateway config snippet
├── docs/
│   └── ARCHITECTURE.md               ← this file
└── references/
    ├── REFERENCE.md                  ← technical reference (links to prompts.yaml)
    └── INSTALL.md                    ← manual install instructions
```

### Runtime files (generated nightly by the agent)

```
~/.openclaw/workspace/
├── HEARTBEAT.md                      ← dream mode section merged in
├── SOUL.md                           ← dream persona fragment appended
└── dreams/
    └── YYYY-MM-DD/
        ├── cycle-1-emotional-review.md
        ├── cycle-2-creative-association.md
        ├── cycle-3-cognitive-processing.md
        ├── cycle-4-memory-consolidation.md
        ├── cycle-5-future-simulation.md
        └── morning-recall.md
```
