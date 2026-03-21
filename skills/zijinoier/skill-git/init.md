---
name: skill-git:init
description: Initialize version tracking for your skills. Creates an independent git repo inside each skill folder and tags it v1.0.0. Run once before using any other skill-git commands. Supports -a <agent> (claude/gemini/codex/openclaw) and --project flags.
---

You are running `skill-git init`. Follow these steps in order.


## Step 1 — Explain what will happen

Tell the user:

> `skill-git init` will set up local version tracking for your AI agent skills:
> 1. Scan `~/.claude/skills/` for subfolders (or the agent directory specified by `-a`)
> 2. For each subfolder, run `git init` + initial commit + tag `v1.0.0`
> 3. Write `~/.skill-git/config.json` to record the agent, base path, and skill versions
> - If a skill folder has a `.git` directory with no commits, that `.git` will be removed and
>   re-initialized. This only affects empty/corrupted repos — any properly versioned skill is left untouched.
>
> All git repos stay on your local machine. Nothing is uploaded anywhere.

## Step 2 — Check git is installed

Run: `git --version`

If the command fails or git is not found, tell the user to install git first (`brew install git` on macOS) and stop.

## Step 3 — Run initialization

Run: `bash "$CLAW_SKILL_DIR/scripts/sg-init.sh" $ARGUMENTS`

Display the full output to the user exactly as printed. If there are errors, explain what went wrong based on the output.

You should output all the plugins and skills detected in the formatted and pretty output to the user.
Also, if there's any [info] or [warn] or [error] in the output, you should explain it to the user.

### `sg-init.sh` Supported Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-a <agent>` | `claude` | Agent to initialize. Supported values: `claude`, `gemini`, `codex`, `openclaw`. Determines the base directory (e.g. `~/.claude/` for claude). |
| `--project` | off | Also scan the project-level skills directory (`./<agent>/skills/` under the current working directory), in addition to the global one. |

Examples:
- `skill-git init` — initialize claude skills at `~/.claude/skills/`
- `skill-git init -a gemini` — initialize gemini skills at `~/.gemini/skills/`
- `skill-git init --project` — initialize both global and project-level claude skills

DO NOT pass unrecognized flags; the script will print an error and exit.
If the user passes unrecognized flags, correct them and run the command again.
