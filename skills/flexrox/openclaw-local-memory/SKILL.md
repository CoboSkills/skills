---
name: Local Memory
description: Local vector memory plugin for OpenClaw — zero-config, stores and searches memories using TF-IDF. No external service, no API key, works out of the box.
---

# Local Memory Plugin

**Zero-config memory for OpenClaw. Install → works. No Ollama, no API key, no external service.**

## Features

- 🧠 **Auto-Recall** — Injects relevant memories before each AI turn
- 💾 **Smart Capture** — Stores conversation exchanges automatically, with significance detection
- 🔍 **Semantic Search** — TF-IDF based full-text similarity search
- 🗑️ **Forgettable** — Delete specific memories by query
- 🏠 **100% Local** — All data stays on your machine
- ⚡ **Zero Config** — Works immediately after install
- 📈 **Auto-Pruning** — Keeps memory size manageable, removes old entries

## Tools

| Tool | Description |
|------|-------------|
| `local_memory_search` | Search memories by natural language query |
| `local_memory_store` | Store a specific piece of information |
| `local_memory_list` | List all memories (newest first) |
| `local_memory_forget` | Remove the most relevant memory for a query |
| `local_memory_wipe` | Delete ALL memories (irreversible) |

## Setup

```bash
# 1. Install
clawhub install openclaw-local-memory

# 2. Enable in OpenClaw config (or use the UI)
# The plugin works with zero configuration!
```

No API keys. No Ollama. No external service. Just works.

## Configuration

```json
{
  "autoRecall": true,
  "autoCapture": true,
  "captureInterval": 10,
  "captureSignificantOnly": true,
  "pruneAfterCapture": true,
  "maxRecallResults": 10,
  "similarityThreshold": 0.1,
  "maxMemories": 500,
  "pruneOlderThanDays": 30,
  "debug": false
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `containerTag` | `openclaw_local_memory` | Memory namespace |
| `autoRecall` | `true` | Inject relevant memories before each turn |
| `autoCapture` | `true` | Store conversation exchanges automatically |
| `captureInterval` | `10` | Capture every N turns (0=disabled) |
| `captureSignificantOnly` | `true` | Only capture significant content (decisions, facts, preferences) |
| `pruneAfterCapture` | `true` | Signal context pruning after memory capture |
| `maxRecallResults` | `10` | Max memories injected per turn |
| `similarityThreshold` | `0.1` | Min similarity to inject (lower = more results) |
| `maxMemories` | `500` | Maximum memories to keep (older pruned first) |
| `pruneOlderThanDays` | `30` | Auto-delete memories older than N days |
| `debug` | `false` | Enable verbose debug logs |

## Smart Capture Logic

The plugin automatically decides what to capture based on:

1. **Significance Detection** — Content matching patterns like:
   - Decisions: "beschlossen", "geplant", "werde"
   - Facts: "ich bin", "mein", "unser Unternehmen"
   - Preferences: "bevorzug", "immer", "nie"
   - Credentials: "api_key", "password", "token"

2. **Periodic Capture** — Every N turns (configurable via `captureInterval`)

3. **Context Pruning** — When memory is captured, signals context can be pruned to keep sessions efficient

## How It Works

Uses **TF-IDF (Term Frequency-Inverse Document Frequency)** to find semantically similar memories. This approach:

- Requires **no external service** — all computation is local
- **No API key** needed
- Works **out of the box** on any machine with Node.js

## Data Storage

All memories are stored locally in:
```
~/.openclaw/memory/<containerTag>.json
```

Default: `~/.openclaw/memory/openclaw_local_memory.json`

## Requirements

- OpenClaw 2026.1.29 or later

## ⚠️ autoCapture Privacy Note

When `autoCapture` is enabled, the plugin automatically stores user + assistant message exchanges after each conversation turn. No data leaves your machine. To disable, set `autoCapture: false` in the plugin config.