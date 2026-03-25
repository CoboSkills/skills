---
name: ai-headshot-skill
description: Generate ai headshot images using the Neta AI API. Returns a direct image URL.
tools: Bash
---

# AI Professional Headshot Generator

Generate stunning ai professional headshot generator images from a text description. Get back a direct image URL instantly.

## When to use
Use when someone asks to generate or create ai professional headshot generator images.

## Quick start
```bash
node aiheadshot.js "your description here"
```

## Options
- `--size` — `portrait`, `landscape`, `square`, `tall` (default: `portrait`)


## Token

Requires a Neta API token via `NETA_TOKEN` env var or `--token` flag.
- Global: <https://www.neta.art/open/>
- China:  <https://app.nieta.art/security>

```bash
export NETA_TOKEN=your_token_here
```

## Install
```bash
npx skills add blammectrappora/ai-headshot-skill
```
