# Skill Downloader

> Discover, compare, and review OpenClaw skills from trusted sources, then guide safe installation when the user explicitly approves it.

Skill Downloader helps agents discover candidate OpenClaw skills from trusted sources, compare them using available ranking evidence, and review them carefully before installation.

By default it operates in search-and-review mode. It does not automatically run third-party code, and any download or installation step requires explicit user approval and local source inspection.

## Features

- 🔍 **Search skills**: Discover candidate skills by name, summary, or use case
- 🧾 **Review before install**: Default behavior is discovery and inspection, not automatic installation
- 🛡️ **Security-first workflow**: Emphasizes explicit approval, local source review, and trusted-source preference
- 📦 **Guided installation workflow**: Helps with installation only after explicit user confirmation
- 📁 **Flexible installation targets**:
  - Global install to `~/.openclaw/skills` when the user explicitly asks for global installation
  - Local install to current workspace `./skills` by default
- 📊 **Structured comparisons and recommendations**: Shows available ranking evidence (such as search score, popularity, stars, recency, or source quality), highlights missing fields as `unknown`, and suggests the best match when multiple skills are available
- 🚫 **No symlink installs**: Uses copied source files for transparent fallback installs

## Safety first

This skill is designed to support careful review and reduce installation risk, not bypass it.

- Default mode is discovery and review, not automatic installation
- Never install a skill without explicit user confirmation
- Prefer official ClawHub workflows when available
- Inspect downloaded source files before installation
- Do not automatically execute third-party repositories or package scripts
- If a source looks suspicious, stop and report the risk clearly

## Trusted Sources (by priority)

1. `https://clawhub.ai/` - Official ClawHub skill repository
2. `https://skills.sh/` - Open agent skills ecosystem registry (manual discovery or user-provided links)
3. `https://github.com/anthropics/skills` - Anthropic example skills repository

You can add more trusted sources by editing `SKILL.md`.

## When to use this skill

Use this skill whenever the user:
- Asks to find, search, or look for a skill
- Requests to download, install, or add a skill
- Asks whether a skill exists for a certain task
- Wants to compare candidates before choosing one to install

## Security and runtime model

- This skill may access trusted registries and repositories including `https://clawhub.ai/`, `https://skills.sh/`, and relevant GitHub repositories
- It requires a network connection and the ability to inspect downloaded source files locally
- It may use standard local command-line tools when needed, but should not assume every environment has the same toolchain available
- It does not rely on dynamic package execution as part of the default search or install workflow
- It must not download or install anything without explicit user confirmation
- For ClawHub-hosted skills, prefer the official `clawhub` workflow (`search`, `inspect`, `install`, `update`) when available
- If the official ClawHub workflow is unavailable, use an agent-managed transparent file installation workflow with unique per-run temporary directories
- Reviewed source files should be copied rather than symlinked into the target directory unless the official ClawHub workflow is used

## Workflow

### Mode A: Search Only
1. Detect search intent
2. Search trusted sources in priority order, preferring ClawHub first and using the official `clawhub search` / `clawhub inspect` workflow for ClawHub-hosted skills when available
3. Present results as a comparison table or structured list with available ranking evidence, per-skill best-use-case notes, `unknown` markers for unavailable fields, and a final preferred recommendation
4. Wait for the user's selection

### Mode B: Installation
1. Capture the request and confirm installation intent
2. Find the skill in trusted sources
3. Prefer the official `clawhub` workflow when available
4. Review candidate files for safety
5. Install only after explicit approval
6. Clean up temporary files

## Installation

Recommended installation target for a global install:

```text
~/.openclaw/skills/skill-downloader
```

For ClawHub-hosted skills, prefer the official CLI workflow when available:

```bash
clawhub search "<query>"
clawhub inspect <slug>
clawhub install <slug> --dir ~/.openclaw/skills
```

If `clawhub` is unavailable, use the transparent fallback workflow to review source files and place the approved skill files in the appropriate skills directory.

## Requirements

- network access to trusted registries and repositories
- ability to review downloaded text or source files locally
- standard local command-line tooling when available
- `clawhub` CLI for the preferred ClawHub workflow (when installed)
- `skill-scanner` (optional extra check, when available)
- `skill-vetting` (optional extra check, when available)

## Maintenance note

When updating this skill's behavior or source priority, keep `SKILL.md` and `README.md` in sync.

## License

MIT
