# Traffic Lights

Use `🟢 / 🟡 / 🔴` as the standard status and deviation layer in the monthly report.

## Purpose

The traffic light should quickly answer:

- is the item on track
- does it need close attention
- has an actual exception already appeared

Do not introduce a second independent `偏离判断：绿/黄/红` field. The traffic light already expresses that meaning.

## Judgment order

Judge in this order:

1. measure-standard attainment
2. milestone timing
3. owner-authored report evidence
4. exposed risks or blockers
5. action progress as support only

Do not judge the light only from action count.

## Default rules

### 🟢 Green

Use `🟢` when:

- there is no clear deviation from the current milestone
- result evidence supports normal progress
- no major blocker is exposed
- owner-side evidence is sufficient

### 🟡 Yellow

Use `🟡` when:

- milestone pressure exists but is still recoverable
- evidence is incomplete and confidence is not high
- blockers or dependencies need close watching
- the result has not failed yet, but the trend is under pressure

### 🔴 Red

Use `🔴` when:

- a key measure standard is clearly not met
- a milestone is missed or very likely to be missed
- a major issue already affects delivery or business outcome
- no credible owner-side evidence supports a normal judgment

## Confidence adjustment

If evidence is mainly:

- owner-authored manual reports: confidence stays high
- other-authored reports: lower confidence by one level
- AI summaries only: lower confidence by one level and avoid strong green judgments

If evidence is weak, prefer `🟡` over overconfident `🟢`.

## Section usage

- Section 2: each BP subsection should show a traffic-light icon
- Section 3: each result item should show a traffic-light icon
- Section 5 and 6: problems and risks should also carry a traffic-light icon
