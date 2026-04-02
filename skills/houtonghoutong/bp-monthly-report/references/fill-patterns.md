# Fill Patterns

This file captures writing conventions inferred from the provided filled sample.

## Structural conventions

- Keep the top-level chapter order identical to the template.
- In section 2, subsection titles may be rewritten from generic labels into the actual BP target statements for the current node.
- Field labels inside each subsection should remain stable even when subsection titles are personalized.

## Section 1 conventions

- `本月总体判断` should be a short conclusion plus a clear status judgment.
- `本月参考工作汇报数` should appear near the top of section 1 and should report both how many original work reports were hit and how many evidence entries were finally adopted into this draft.
- `本月最关键的进展` is best expressed as 1-3 high-value progress lines, not a long paragraph.
- `本月最需要关注的问题` should include problem, impact, and current state.
- `对下月的总体判断` should be concise and directional, such as `可达 / 承压 / 需决策`.

Recommended rendering pattern:

```text
- **本月参考工作汇报数：**
  命中原始工作汇报 X 份，经批量通知归并后最终采纳 X 份，其中本人主证据 X 份、他人手动汇报 X 份、AI 汇报 X 份。
```

## Section 2 conventions

Each subsection should clearly contain:

- BP anchor names, not raw IDs, in user-facing report text
- the month-specific focus inherited from the BP
- current status, preferably with metrics
- result-level judgment against `衡量标准`
- `🟢 / 🟡 / 🔴` judgment

Recommended rendering pattern:

```text
### 2.x [actual BP target statement]
**对标BP：** personal / org
**本月承接重点：** ...
**当前状态：**
- 量化指标：...
- 三灯判断：🟢 / 🟡 / 🔴
```

## Style conventions

- Prefer short factual sentences over abstract summaries.
- Prefer metric-bearing statements when available.
- Prefer result-and-standard language over action-and-process language.
- Use one traffic-light language consistently across chapters.
- Prefer explicit progress wording such as “已完成… / 已进入… / 已形成… / 正在推进… / 待拍板…”.
- Avoid introducing facts in section 1 that do not already appear in later sections.

## Usage

Read this file when the user provides both:

- a blank template
- a filled sample or fill-in specification

The sample is not just content. It is also a formatting and reasoning guide.
