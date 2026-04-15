---
name: "sms-rpg"
description: "Runs the full bundled SMS RPG runtime. Invoke when the user wants complete one-turn chat gameplay after installing the skill from ClawHub."
version: "1.2.2"
metadata:
  openclaw:
    skillKey: "sms-rpg"
    emoji: "🎮"
    requires:
      env:
        - MOONSHOT_API_KEY
      bins:
        - node
    primaryEnv: "MOONSHOT_API_KEY"
---

# SMS RPG

## Overview

This package contains the full SMS RPG runtime, including the dialog engine, prompts, and compiled JavaScript files.

Users who install this skill from ClawHub receive the bundled game files, not only a thin instruction wrapper.

Critical rule:

- never improvise game content from `SKILL.md`
- always execute the bundled runtime and return its real output
- if the runtime is available, do not replace it with manual storytelling

## When To Invoke

Invoke this skill when the user wants to:

- start a full SMS RPG session from chat
- continue an existing save
- send one action and receive one story turn
- use the built-in unlock and license flow

## Included Runtime

Bundled files:

- `dist/` compiled runtime for direct execution with Node.js
- `code/` TypeScript source for audit and modification
- `prompts/` prompt templates used by the engine
- `package.json` for standard `npm run dialog` usage

Primary command:

```bash
node dist/dialog_engine.js --user <user-id> --input "<message>"
```

Optional npm wrapper:

```bash
npm run dialog -- --user <user-id> --input "<message>"
```

## Requirements

Required:

- `node`
- `MOONSHOT_API_KEY`

Optional environment variables:

```bash
MOONSHOT_BASE_URL
MOONSHOT_MODEL
MOONSHOT_TIMEOUT_MS
MOONSHOT_ENABLE_CANON_GUARDIAN
MOONSHOT_MAX_TOKENS
SMS_LICENSE_VERIFY_URL
SMS_PRODUCT_URL
SMS_DATA_DIR
```

Notes:

- The compiled runtime is already bundled, so `npm install` is not required for normal play.
- `node dist/dialog_engine.js` is the preferred entry because it avoids any script-resolution ambiguity.
- `SMS_DATA_DIR` can override the local save/config directory.
- For safest use, set `MOONSHOT_API_KEY` in the environment before the first run.

## Data And Network Scope

Local files written by the game:

- saves
- dialog session state
- local config
- local license state

External network calls:

- Moonshot / Kimi generation API
- optional license verification endpoint
- optional purchase link display

Operational boundary:

- only game prompts, world state, and player input are sent to the model API
- unrelated local files are not part of the model payload

## Quick Start

```bash
node dist/dialog_engine.js --user demo-user --input "开始新游戏"
```

Typical setup flow:

- `开始新游戏`
- `主角名 云游子`
- `武侠修仙，江湖门派与朝廷暗斗`
- `默认`
- `1`

Useful commands:

- `继续游戏`
- `存档列表`
- `授权状态`
- `解锁`
- `解锁 WUXIA-XXXX-XXXX`

## Execution Contract

For every gameplay turn:

1. keep one stable `user-id` for the same player session
2. run the bundled runtime with the latest user message
3. return the runtime output directly
4. do not summarize away setup prompts, world state, opening text, or options

If the runtime is working correctly, the onboarding flow must include:

- API key step when no valid key is configured
- player name step
- world setup step
- narrative style step

Expected markers from the real runtime:

- `最后一步，请告诉我你要的叙事风格`
- `【新游戏已创建：存档 1】`
- `【开场引子】`
- `【可选行动】`

If these markers are missing and a generic story is produced instead, the runtime was not actually executed. In that case, retry with the direct Node command instead of inventing a reply.

## Content Expectations

The bundled runtime already enforces:

- opening narrative around 200-300 Chinese characters
- per-turn narrative around 300 Chinese characters
- user-selectable narrative style with `默认` or a custom style sentence
- dialog-first onboarding instead of jumping straight into round one

## Expected Behavior

- creates a structured initial world
- returns one story turn per message
- persists saves locally
- supports dialog-first onboarding
- supports free and full-version slot rules
