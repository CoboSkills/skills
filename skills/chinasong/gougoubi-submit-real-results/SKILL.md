---
name: gougoubi-submit-real-results
description: Submit real-world outcomes for Gougoubi proposal conditions using deterministic mapping from condition skills (Polymarket marketId/event slug). Supports resolved-only mode and forced fallback mode, one submission per condition.
metadata: {"clawdbot":{"emoji":"✅","os":["darwin","linux","win32"]}}
---

# Gougoubi Submit Real Results

Submit condition results for a proposal with deterministic evidence and safe guards.

## When To Use

- User asks to submit real outcomes for all conditions under a proposal.
- User asks to submit only officially resolved conditions first.
- User asks to force-submit remaining conditions as YES/NO.

## Input

```json
{
  "proposalAddress": "0x...",
  "mode": "resolved-only|all|force",
  "forceResult": "yes|no (required when mode=force)",
  "evidenceNote": "optional"
}
```

Defaults:

- `mode=resolved-only`
- `evidenceNote` auto-generated with timestamp

## Deterministic Flow

1. Validate proposal address and chain (BSC 56).
2. Enumerate all conditions from proposal.
3. Read each condition `skills` payload and extract `event slug` + `conditionMarketId`.
4. Fetch event data from `gamma-api.polymarket.com`.
5. Build result map:
   - `resolved-only`: only markets with official resolved marker.
   - `all`: infer all markets with clear winner.
   - `force`: use same forced side for pending conditions.
6. For each target condition:
   - skip if `status != ACTIVE` or already has result (`result != 0`).
   - submit exactly one result vote per condition.
   - auto switch voter if creator/insufficient.
7. Return structured summary and tx hashes.

## Output

```json
{
  "ok": true,
  "proposalAddress": "0x...",
  "mode": "resolved-only|all|force",
  "submittedCount": 0,
  "skippedCount": 0,
  "failedCount": 0,
  "submitted": [
    {
      "index": 0,
      "conditionAddress": "0x...",
      "conditionName": "",
      "result": 1,
      "txHash": "0x..."
    }
  ],
  "skipped": [],
  "failed": []
}
```

Failure:

```json
{
  "ok": false,
  "stage": "validation|fetch-evidence|submit|confirm",
  "error": "reason",
  "retryable": true
}
```

## Script Mapping In This Project

- Generic submit: `scripts/pbft-submit-all-condition-results.mjs`
- Existing deterministic examples:
  - `scripts/pbft-submit-real-results-1605.mjs`
  - `scripts/pbft-submit-real-results-c427-confirmed.mjs`
  - `scripts/pbft-submit-real-results-ba0c-resolved-only.mjs`
  - `scripts/pbft-submit-remaining-no-ba0c.mjs`

## Boundaries

- Never submit duplicated votes for the same condition by default.
- Prefer `resolved-only` unless user explicitly asks to force.
- Always keep evidence text and tx hashes in result.

