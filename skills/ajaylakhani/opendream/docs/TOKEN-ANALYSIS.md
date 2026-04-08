# OpenDream — Token Analysis

> Standalone token-cost breakdown for OpenDream's nightly operation.
> All estimates use measured file sizes with the ~4 characters/token
> approximation for English Markdown/YAML content.

**Last updated**: 2026-04-07
**Pricing date**: 2026-04-07 (see [Recalculation Guide](#recalculation-guide) when prices change)

---

## Methodology

Token counts are estimated using **~4 characters per token**, the standard
approximation for GPT/Claude-family tokenisers on English text. OpenDream's
content is Markdown + YAML — primarily English prose with light formatting.

This heuristic converges within ±15% of exact tokeniser counts for English
content. For budget planning purposes, this precision is sufficient — exact
counts vary by model tokeniser anyway.

**Formula**: `tokens ≈ file_size_bytes ÷ 4`

### Measured File Sizes

| File | Bytes | Est. Tokens |
|------|------:|------------:|
| `assets/HEARTBEAT-dream-section.md` | 3,761 | ~940 |
| `assets/prompts.yaml` | 9,482 | ~2,371 |
| `assets/SOUL-fragment.md` | 401 | ~100 |
| `SKILL.md` | 8,677 | ~2,169 |
| `assets/openclaw.json` | 465 | ~116 |

### Memory File Density Fixtures

| Fixture | Bytes | Est. Tokens | Description |
|---------|------:|------------:|-------------|
| `tests/fixtures/memory-sparse.md` | 89 | ~22 | 1 entry |
| `tests/fixtures/memory-medium.md` | 406 | ~102 | 5 entries |
| `tests/fixtures/memory-dense.md` | 1,211 | ~303 | 15 entries, mixed format |

---

## Dream Tick Input Breakdown

Each dream tick (23:00–05:30) runs in an isolated session with light context.
The input consists of these components:

| # | Component | Source | Tokens | Notes |
|---|-----------|--------|-------:|-------|
| 1 | System prompt overhead | Gateway (tool schemas, rules) | ~300 | Not under OpenDream's control |
| 2 | HEARTBEAT.md bootstrap | `lightContext: true` injection | ~940 | Only bootstrap file loaded (grew with phase schedule) |
| 3 | Heartbeat prompt | `openclaw.json` prompt string | ~30 | Fixed custom prompt |
| 4 | prompts.yaml read | File tool call | ~2,371 | Single source of truth (grew with depth + nrem_guidance) |
| 5 | Memory file read | File tool call | 0–303+ | Depends on density; skipped if missing |
| 6 | Cycle file read | File tool call | 0–200 | Grows during the night as thoughts accumulate |
| | **Total input** | | **~3,641–4,144** | |

**Component 1** (system overhead) is estimated. The gateway injects tool schemas
and system rules that are not part of OpenDream's files. ~300 tokens is a
conservative mid-range estimate (200–400 range observed).

**Component 5** (memory file) varies by day:
- No memory file → 0 tokens (agent dreams from imagination only)
- Sparse day → ~22 tokens
- Typical day → ~102 tokens
- Busy day → ~303+ tokens

**Component 6** (cycle file) grows from 0 at the first tick of a cycle to
~100-200 tokens at the last tick. At mid-night (typical), ~100 tokens.

---

## Morning Recall Tick Input Breakdown

The morning recall tick (06:00) has a different input profile — it reads ALL
five cycle files from the night plus optionally the memory file.

| # | Component | Source | Tokens | Notes |
|---|-----------|--------|-------:|-------|
| 1 | System prompt overhead | Gateway | ~300 | Same as dream tick |
| 2 | HEARTBEAT.md bootstrap | `lightContext: true` injection | ~940 | Same as dream tick |
| 3 | Heartbeat prompt | `openclaw.json` prompt string | ~30 | Same as dream tick |
| 4 | prompts.yaml read | File tool call | ~2,371 | Reads `morning_recall` section |
| 5 | All 5 cycle files | File tool calls (×5) | ~160–280 | 9 dream thoughts + 5 NREM markers |
| 6 | Memory file read (optional) | File tool call | 0–303+ | Only if natural connection exists |
| | **Total input** | | **~3,801–4,224** | |

The morning recall tick is ~160–280 tokens heavier than a dream tick due to
reading all five cycle outputs (9 thoughts + 5 NREM markers).

---

## Output Token Estimates

| Tick Type | Output | Tokens |
|-----------|--------|-------:|
| NREM tick | `<!-- NREM HH:MM -->` marker only | ~5 |
| REM tick | One thought, 8–25 words (progressive by depth) | ~10–30 |
| Morning recall | 2–3 sentence summary | ~60–90 |

Output tokens vary by tick type. NREM ticks produce only a silent HTML comment
marker. REM tick output scales progressively: Cycle 1 (shallow, 8–12 words) to
Cycle 5 (vivid, 15–25 words).

---

## Per-Night Totals

5 NREM ticks + 9 REM ticks + 1 morning recall = 15 ticks per night.

| Category | Calculation | Typical Total |
|----------|-------------|-------------:|
| NREM tick input (×5) | 5 × ~3,750 (mid-range) | ~18,750 |
| REM tick input (×9) | 9 × ~3,750 (mid-range) | ~33,750 |
| Morning recall input (×1) | 1 × ~3,950 (mid-range) | ~3,950 |
| **Total input tokens** | | **~56,450** |
| NREM tick output (×5) | 5 × ~5 (marker only) | ~25 |
| REM tick output (×9) | 9 × ~18 (mid-range) | ~162 |
| Morning recall output (×1) | 1 × ~75 (mid-range) | ~75 |
| **Total output tokens** | | **~262** |
| **Grand total** | | **~56,712** |

> **Note on nightly totals**: The addition of `depth`, `nrem_guidance`, and the
> expanded phase schedule increased per-tick input from ~2,900 to ~3,750 tokens.
> The nightly input total grew from ~44K to ~56K. Output dropped from ~327 to
> ~262 tokens (9 REM thoughts instead of 14). All individual ticks remain well
> within the <5K constitutional budget.

---

## Cost by Model Tier

Pricing as of 2026-04-07. Use the formula below to recalculate when
prices change.

| Tier | Model Example | Input Rate | Output Rate | Nightly Input Cost | Nightly Output Cost | **Total/Night** |
|------|---------------|------------|-------------|-------------------:|--------------------:|----------------:|
| Local | Ollama (any) | £0 | £0 | £0.000 | £0.000 | **£0.000** |
| Budget | Claude Haiku | $0.25/M in | $1.25/M out | ~$0.014 | ~$0.0003 | **~$0.014** |
| Standard | Claude Sonnet | $3.00/M in | $15.00/M out | ~$0.169 | ~$0.004 | **~$0.173** |

### Monthly Cost (30 nights)

| Tier | Per Night | **Per Month** |
|------|----------:|--------------:|
| Local | £0.000 | **£0.00** |
| Budget (Haiku) | ~$0.014 | **~$0.42** |
| Standard (Sonnet) | ~$0.173 | **~$5.19** |

**Cost formula**:
```
nightly_cost = (total_input_tokens × input_rate_per_token)
             + (total_output_tokens × output_rate_per_token)
```

---

## Component Budget Breakdown

How each component contributes to the constitutional <5,000 token/tick budget
(dream tick, typical medium-memory scenario):

| Component | Min | Typical | Max | % of 5K Budget |
|-----------|----:|--------:|----:|---------------:|
| System prompt overhead | 200 | 300 | 400 | 6% |
| HEARTBEAT.md bootstrap | 940 | 940 | 940 | 19% |
| Heartbeat prompt | 30 | 30 | 30 | <1% |
| prompts.yaml read | 2,371 | 2,371 | 2,371 | 47% |
| Memory file read | 0 | 102 | 303+ | 2–6% |
| Cycle file read | 0 | 100 | 200 | 2–4% |
| **Total input** | **3,541** | **3,843** | **4,244+** | **71–85%** |

### Key Observations

- **prompts.yaml dominates** at 47% of the budget — it is the single largest
  input component. The addition of `depth`, `nrem_guidance`, and word-range
  guidance grew it from ~2,015 to ~2,371 tokens.
- **HEARTBEAT.md** grew from 9% to 19% of the budget due to the expanded
  14-slot phase schedule (was 5-line range-based).
- **Memory file** adds 0–6% depending on the day's density. Even a dense day
  adds only ~303 tokens.
- **Headroom**: 15–29% of the 5K budget is unused. This gives ~756–1,459
  tokens of space for future growth. Less headroom than before the NREM/REM
  changes (~32–46%), but still comfortably within budget.

---

## Recalculation Guide

If you change a file that contributes to tick input, recalculate as follows:

### Worked Example: prompts.yaml grows by 500 bytes

1. **Measure the new file size**:
   ```
   wc -c assets/prompts.yaml
   # e.g., 9982 bytes (was 9482)
   ```

2. **Estimate new token count**:
   ```
   9982 ÷ 4 ≈ 2,496 tokens (was ~2,371)
   ```

3. **Calculate new per-tick total** (typical medium-memory):
   ```
   300 + 940 + 30 + 2,496 + 102 + 100 = 3,968 tokens
   ```

4. **Check constitutional compliance**:
   ```
   3,968 < 5,000 → ✓ PASS (headroom: 1,032 tokens)
   ```

5. **Recalculate nightly cost** (Haiku):
   ```
   Input:  14 × 3,968 + 1 × 4,268 = 59,820 tokens
   Output: 5 × 5 + 9 × 18 + 1 × 75 = 262 tokens
   Cost:   (59,820 × $0.00000025) + (262 × $0.00000125) ≈ $0.015
   ```

The same method applies if HEARTBEAT.md changes, memory files grow, or cycle
output length increases.

---

## Constitutional Compliance Verification

The constitution mandates **<5,000 tokens per tick**. Tested across 4 memory
density scenarios (dream tick at mid-night, typical cycle file size ~100 tokens):

| Scenario | Memory Tokens | Tick Input Total | Budget (5K) | Headroom | Status |
|----------|-------------:|----------------:|------------:|---------:|--------|
| No memory file | 0 | ~3,641 | 5,000 | 1,359 | **✓ PASS** |
| Sparse memory | ~22 | ~3,663 | 5,000 | 1,337 | **✓ PASS** |
| Medium memory | ~102 | ~3,743 | 5,000 | 1,257 | **✓ PASS** |
| Dense memory | ~303 | ~3,944 | 5,000 | 1,056 | **✓ PASS** |

All 4 scenarios pass with adequate headroom (21–27% of budget unused).

### Morning recall tick compliance

| Scenario | Memory Tokens | Tick Input Total | Budget (5K) | Headroom | Status |
|----------|-------------:|----------------:|------------:|---------:|--------|
| No memory file | 0 | ~3,851 | 5,000 | 1,149 | **✓ PASS** |
| Dense memory | ~303 | ~4,294 | 5,000 | 706 | **✓ PASS** |

The morning recall tick is heavier but still passes. Even in the worst case
(dense memory + all 9 dream thoughts + 5 NREM markers read), the headroom
is ~700 tokens.

### Nightly Total

The constitution specifies **<5K tokens per tick**. The measured nightly
input total is **~56K tokens** across 15 ticks (up from ~44K due to expanded
phase schedule and NREM guidance). Each individual tick remains within <5K.

| Metric | Value | Limit | Status |
|--------|------:|------:|--------|
| Per-tick input (typical) | ~3,843 | 5,000 | **✓ PASS** |
| Per-tick input (dense) | ~4,244 | 5,000 | **✓ PASS** |
| Nightly input tokens | ~56,450 | — | — |
| Nightly output tokens | ~262 | — | — |
| Nightly total tokens | ~56,712 | — | — |

> **Note**: The constitutional ~44K nightly figure was based on pre-NREM/REM
> file sizes. The per-tick budget (<5K) is the binding constraint, and all
> ticks pass comfortably. The nightly total grew because HEARTBEAT.md and
> prompts.yaml expanded to accommodate the phase schedule and NREM guidance.

---

## Appendix: Tick Count Schedule

| Cycle | Window | Ticks | Phase | Thoughts |
|-------|--------|-------|-------|----------|
| 1 — Emotional Review | 23:00–00:00 | 23:00 | NREM | 0 |
| | | 23:30 | REM | 1 |
| 2 — Creative Association | 00:00–01:30 | 00:00 | NREM | 0 |
| | | 00:30 | REM | 1 |
| | | 01:00 | REM | 1 |
| 3 — Cognitive Processing | 01:30–03:00 | 01:30 | NREM | 0 |
| | | 02:00 | REM | 1 |
| | | 02:30 | REM | 1 |
| 4 — Memory Consolidation | 03:00–04:30 | 03:00 | NREM | 0 |
| | | 03:30 | REM | 1 |
| | | 04:00 | REM | 1 |
| 5 — Future Simulation | 04:30–06:00 | 04:30 | NREM | 0 |
| | | 05:00 | REM | 1 |
| | | 05:30 | REM | 1 |
| Morning recall | 06:00 | 06:00 | — | 1 summary |
| **Total** | | **15 ticks** | **5 NREM + 9 REM + 1 recall** | **9 dreams + 1 recall** |
