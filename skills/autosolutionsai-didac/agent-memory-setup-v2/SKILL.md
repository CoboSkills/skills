---
name: agent-memory-setup-v2
description: Set up the full OpenClaw agent memory system with 3-tier memory (HOT/WARM/COLD), daily logs, Google Gemini Embeddings 2 for semantic search, and lossless context management (Lossless Claw). Use when onboarding a new agent, setting up memory for a fresh OpenClaw instance, or when asked to install the memory system on a new agent. Triggers on "set up memory", "install memory system", "onboard new agent memory", "memory setup", "agent onboarding", "gemini embeddings".
---

# Agent Memory Setup v2 (Gemini Embeddings 2)

Set up a complete 3-tier memory system for any OpenClaw agent, powered by **Google Gemini Embeddings 2** for semantic search. No local model downloads required.

## What Gets Installed

1. **3-tier memory structure** (HOT → WARM → COLD)
2. **Gemini Embeddings 2** (`gemini-embedding-2-preview`) — cloud-native semantic search via the built-in `memory-core` plugin
3. **Lossless Claw** — compacts old conversation into expandable summaries (prevents amnesia)
4. **AGENTS.md** — instructions the agent reads every session to use the memory system
5. **openclaw.json config** — enables memorySearch (Gemini), compaction, context pruning, heartbeats

## Prerequisites

- **Gemini API key** — free at https://aistudio.google.com/apikey
- Set via `GEMINI_API_KEY` environment variable or in `openclaw.json` under `models.providers.google.apiKey`

## Setup Steps

### Step 1: Run the setup script

```bash
bash scripts/setup_memory_v2.sh /path/to/agent/workspace
```

This creates:
- `memory/`, `memory/hot/`, `memory/warm/` directories
- `memory/hot/HOT_MEMORY.md` (active session state)
- `memory/warm/WARM_MEMORY.md` (stable config & preferences)
- `MEMORY.md` (long-term archive)
- `memory/YYYY-MM-DD.md` (today's daily log)
- `memory/heartbeat-state.json` (heartbeat tracking)

It also checks for the Gemini API key and Lossless Claw plugin.

### Step 2: Copy the AGENTS.md template

Read `references/AGENTS_TEMPLATE.md` and write it to the agent's workspace as `AGENTS.md`. Adapt the heartbeat section to the agent's domain if needed (e.g., a CFO agent checks costs, a marketing agent checks social metrics).

### Step 3: Configure openclaw.json

Add to `agents.defaults` (or the specific agent config):

```json
"memorySearch": { "provider": "gemini" },
"compaction": { "mode": "safeguard" },
"contextPruning": { "mode": "cache-ttl", "ttl": "1h" },
"heartbeat": { "every": "1h" }
```

Make sure your Gemini API key is available:
- Option A: `export GEMINI_API_KEY=your-key`
- Option B: add to `openclaw.json` → `models.providers.google.apiKey`

Enable plugins:

```json
"lossless-claw": { "enabled": true }
```

### Step 4: Restart and verify

```bash
openclaw gateway restart
```

Verify:
- `openclaw status` shows memory search as enabled
- `memory_search` returns results when queried
- All memory directories and files exist

## How the Tiers Work

| Tier | File | Purpose | Update Frequency |
|------|------|---------|-----------------|
| 🔥 HOT | `memory/hot/HOT_MEMORY.md` | Current task, pending actions | Every few turns |
| 🌡️ WARM | `memory/warm/WARM_MEMORY.md` | Stable preferences, API refs, gotchas | When things change |
| ❄️ COLD | `MEMORY.md` | Milestones, decisions, distilled lessons | Weekly/monthly |

Daily logs (`memory/YYYY-MM-DD.md`) capture raw session events. Periodically, the agent reviews daily logs and promotes important items up to COLD.

## v2 vs v1 Differences

| | v1 (agent-memory-setup) | v2 (this skill) |
|---|---|---|
| Semantic search | QMD (local, requires Python + model downloads) | Gemini Embeddings 2 (cloud, API key only) |
| Dependencies | Python, pip, qmd CLI | Just a Gemini API key |
| Embedding model | Local GGUF via QMD | `gemini-embedding-2-preview` |
| Setup complexity | Medium (pip install, model download) | Low (API key + config) |
| Cross-modal search | No | Yes (text, images, video, audio, docs) |

## Plugin Details

- **Gemini Embeddings 2**: Google's latest multimodal embedding model. Maps text, images, video, audio, and documents into a unified embedding space. Uses the built-in `memory-core` plugin's `gemini` adapter — no extra installation needed. Free tier available.
- **Lossless Claw** (`@martian-engineering/lossless-claw`): Instead of losing old messages when context fills up, compacts them into summaries that can be expanded back. Install: `openclaw plugins install @martian-engineering/lossless-claw`
