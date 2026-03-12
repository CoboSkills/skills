---
name: x-growth-automation
description: Set up a reusable X/Twitter growth automation system with OpenClaw, Bird CLI, X API, optional source branching, optional community CTA, dry-run/live rollout, and niche-specific posting policy. Use when a user wants to build, clone, publish, or customize an autonomous X growth workflow, especially if they ask to install the system from GitHub/ClawHub, configure posting cadence, define niches, add reply automation, localize the system for a specific language, or connect external content feeds into X.
---

# X Growth Automation

Build a **separate, reusable X automation project** for the user. Do not assume their current production project should be modified. Prefer creating a fresh folder unless they explicitly target an existing repo.

## Core workflow

1. **Ask setup questions first** using `references/setup-questionnaire.md`.
2. **Choose safe rollout mode** using `references/rollout-modes.md`.
3. **Scaffold a clean project** with `scripts/scaffold_x_growth_project.py`.
4. **Fill configs** based on the user's answers.
5. **Keep publish disabled by default** unless the user explicitly asks for live publishing.
6. **If enabling live publish**, keep caps, slot scheduling, and fallback rules explicit.

## What this skill should help build

A reusable X automation system with these layers:
- discovery via Bird CLI
- selection/scoring layer
- draft generation layer
- optional LLM-first approval layer
- optional source branching from an external editorial feed
- optional community CTA logic
- slot-based publishing via X API
- dry-run-first rollout

## Non-negotiable safety defaults

- Create the project in a **new folder** unless the user clearly says otherwise.
- Treat Bird as **read/discovery first**.
- Treat X API as **write/publish layer**.
- Default new installs to **dry-run**.
- If the user wants aggressive automation, still keep daily/monthly caps in config.
- Never silently copy private tokens, links, handles, or niche assumptions from another project.
- Treat reply automation as a higher-risk lane than normal posts.
- In live mode, require clear logging for posted / skipped / failed outcomes.

## Ask these questions before scaffolding

Read `references/setup-questionnaire.md` and ask only the missing items.
Do not dump all questions at once if the user already answered some.

Minimum set to unblock setup:
- niche/topic focus
- posting language
- dry-run or live
- daily target range
- monthly hard cap
- Bird available?
- X API available?
- source branching wanted?
- community CTA wanted?

## After answers are clear

Run the scaffold script:

```bash
python3 scripts/scaffold_x_growth_project.py --path <target-dir> --profile-json '<json>'
```

The JSON may include fields like:
- `project_name`
- `language`
- `niche_summary`
- `daily_min`
- `daily_max`
- `monthly_cap`
- `community_enabled`
- `community_link`
- `reply_cta_enabled`
- `reply_cta_style`
- `source_branching_enabled`
- `source_branching_label`
- `bird_enabled`
- `x_api_enabled`
- `live_publish`

## Recommended setup behavior

### If user says “install this system for me”
- Ask the setup questions.
- Scaffold a fresh project.
- Fill the config files.
- Keep publish disabled unless they explicitly approve live mode.
- Explain where they should place credentials.

### If user says “can we adapt this to my niche?”
- Ask for niche, audience, tone, and content pillars.
- Update topic/search/watch-account config.
- Update crosspost/reply policy if needed.

### If user says “make it more aggressive”
- Increase cadence and caps explicitly.
- Keep hard caps documented.
- Confirm whether replies should include CTA or not.
- Do not remove quality gates unless asked.
- Keep reply-specific safeguards even in aggressive mode: target validation, skip-on-failure, and per-day caps.

### If user says “I want community integration”
- Ask whether the external community/feed is:
  - source-of-truth content feed
  - CTA destination only
  - both
- Configure source branching and reply CTA rules separately.
- Never assume the community platform is Telegram unless the user explicitly says so.

## File customization order

After scaffolding, customize in this order:
1. `config/publish-policy.json`
2. `config/topics.json`
3. `config/budget-policy.json`
4. `.env.example`
5. `docs/operator-notes.md`
6. prompts if the user wants a distinct tone

## When to enable live mode

Enable live mode only when all of these are true:
- credentials are present
- the user explicitly wants live publish
- cadence/caps are set
- reply policy is defined
- source branching behavior is defined
- the user understands what will auto-post

## Publish strategy guidance

Recommended live structure:
- 1 daily news/source crosspost if configured
- 1 daily special content crosspost if configured
- 0-1 reply/day with optional CTA
- 0-2 core posts/day from the main drafting pipeline

If the user wants a different mix, encode it in config rather than burying it in prose.

## Resources

### scripts/
- `scaffold_x_growth_project.py` creates a clean generic project scaffold.

### references/
- `setup-questionnaire.md` contains the installation interview.
- `rollout-modes.md` explains dry-run vs live rollout choices.
