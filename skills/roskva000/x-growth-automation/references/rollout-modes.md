# Rollout Modes

## Mode 1 — Scaffold only
Use when the user wants the project structure and config but is not ready for testing.

## Mode 2 — Dry-run
Use when credentials may exist but the user wants safe validation first.
Build plans, drafts, approval packs, and distribution schedules without publishing.

## Mode 3 — Live with caps
Use only when the user explicitly asks for live publishing.
Required:
- clear daily range
- clear monthly cap
- explicit reply policy
- explicit CTA policy
- explicit source branching rules

## Recommended progression
1. scaffold
2. dry-run validation
3. live with conservative caps
4. increase aggression only after observing results

## Good default live shape
- 1 source crosspost/day if source branching is enabled
- 1 special content crosspost/day if the user wants a second recurring content lane
- 0-1 reply/day
- 0-2 core posts/day

These are defaults, not hardcoded rules. The user may choose a different mix.

## Reply-lane guidance
- Prefer reply-safe targets first (mentions or clearly open discussions)
- Validate reply targets where possible
- If a reply fails permanently, skip that slot and continue
- Always record whether the reply was posted, skipped, or failed

## If the user wants aggressive mode
Still encode:
- daily max
- monthly hard cap
- reply max/day
- slot timing
- fallback behavior when weak content appears
