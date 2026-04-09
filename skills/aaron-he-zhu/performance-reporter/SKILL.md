---
name: performance-reporter
description: 'SEO and GEO performance reporter: generate dashboards with rankings, organic traffic, backlink metrics, and AI visibility trends for stakeholder reporting. Part of a 20-skill SEO & GEO workflow suite. SEO报告/数据看板/网站流量分析/SEO数据/流量报告'
version: "6.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when generating SEO performance reports, traffic summaries, ranking reports, or stakeholder-facing dashboards."
argument-hint: "<domain> [date range]"
metadata:
  author: aaron-he-zhu
  version: "6.0.0"
  geo-relevance: "medium"
  tags:
    - seo
    - geo
    - seo-reporting
    - performance-report
    - kpi-dashboard
    - traffic-report
    - monthly-report
    - stakeholder-report
    - SEO报告
    - SEOレポート
    - SEO리포트
    - informe-seo
  triggers:
    # EN-formal
    - "generate SEO report"
    - "performance report"
    - "traffic report"
    - "SEO dashboard"
    - "SEO analytics"
    - "monthly report"
    # EN-casual
    - "report to stakeholders"
    - "monthly SEO report"
    - "show me my SEO results"
    - "present SEO results to my boss"
    - "report to my boss"
    - "monthly SEO summary"
    # EN-question
    - "how are my SEO metrics"
    - "how is my SEO performing"
    # ZH-pro
    - "SEO报告"
    - "绩效仪表盘"
    - "流量报告"
    - "数据看板"
    # ZH-casual
    - "出SEO报告"
    - "汇报给老板"
    - "看看数据"
    - "月报"
    - "出月报"
    - "周报"
    # JA
    - "SEOレポート"
    - "パフォーマンスレポート"
    # KO
    - "SEO 리포트"
    - "성과 보고서"
    # ES
    - "informe SEO"
    - "reporte de rendimiento"
    # PT
    - "relatório SEO"
    # Misspellings
    - "SEO repoort"
---

# Performance Reporter

**Turn your SEO data into executive-ready reports and actionable insights** — this skill aggregates organic traffic, keyword rankings, backlinks, and AI citation metrics into a single cohesive report with ROI calculations and a prioritized recommendation list for any audience.

**How to start**: `Create an SEO performance report for [domain] for [time period]` or `Generate an executive summary of SEO performance for [month/quarter]`

**System role**: Monitoring layer skill. It turns performance changes into deltas, alerts, and next actions.

> **[SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)

## When This Must Trigger

Use this when the conversation involves any of these situations — even if the user does not use SEO terminology:

Use this whenever the task needs time-aware change detection, escalation, or stakeholder-ready visibility.

- Monthly/quarterly SEO reporting
- Executive stakeholder updates
- Client reporting for agencies
- Tracking campaign performance
- Combining multiple SEO metrics
- Creating GEO visibility reports
- Documenting ROI from SEO efforts

## What This Skill Does

1. **Data Aggregation**: Combines multiple SEO data sources
2. **Trend Analysis**: Identifies patterns across metrics
3. **Executive Summaries**: Creates high-level overviews
4. **Visual Reports**: Presents data in clear formats
5. **Benchmark Comparison**: Tracks against goals and competitors
6. **Content Quality Tracking**: Integrates CORE-EEAT scores across audited pages
7. **ROI Calculation**: Measures SEO investment returns
8. **Recommendations**: Suggests actions based on data

## Quick Start

Start with one of these prompts. Finish with a short handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Generate Performance Report

```
Create an SEO performance report for [domain] for [time period]
```

### Executive Summary

```
Generate an executive summary of SEO performance for [month/quarter]
```

### Specific Report Types

```
Create a GEO visibility report for [domain]
```

```
Generate a content performance report
```

## Skill Contract

**Expected output**: a delta summary, alert/report output, and a short handoff summary ready for `memory/monitoring/`.

- **Reads**: current metrics, previous baselines, alert thresholds, and reporting context from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available.
- **Writes**: a user-facing monitoring deliverable plus a reusable summary that can be stored under `memory/monitoring/`.
- **Promotes**: significant changes, confirmed anomalies, and follow-up actions to `memory/open-loops.md` and `memory/decisions.md`.
- **Next handoff**: use the `Next Best Skill` below when a change needs action.

## Data Sources

> **Note:** All integrations are optional. This skill works without any API keys — users provide data manually when no tools are connected.

> See [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) for tool category placeholders.

**With ~~analytics + ~~search console + ~~SEO tool + ~~AI monitor connected:**
Automatically aggregate traffic metrics from ~~analytics, search performance data from ~~search console, ranking and backlink data from ~~SEO tool, and GEO visibility metrics from ~~AI monitor. Creates comprehensive multi-source reports with historical trends.

**With manual data only:**
Ask the user to provide:
1. Analytics screenshots or traffic data export (sessions, users, conversions)
2. Search Console data (impressions, clicks, average position)
3. Keyword ranking data for the reporting period
4. Backlink metrics (referring domains, new/lost links)
5. Key performance indicators and goals for comparison
6. AI citation data if tracking GEO metrics

Proceed with the full analysis using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests a performance report:

1. **Define Report Parameters** -- Domain, report period, comparison period, report type (Monthly/Quarterly/Annual), audience (Executive/Technical/Client), focus areas.

2. **Create Executive Summary** -- Overall performance rating, key wins/watch areas/action required, metrics at a glance table (traffic, rankings, conversions, DA, AI citations), SEO ROI calculation.

3. **Report Organic Traffic Performance** -- Traffic overview (sessions, users, pageviews, bounce rate), traffic trend visualization, traffic by source/device, top performing pages.

4. **Report Keyword Rankings** -- Rankings overview by position range, distribution change visualization, top improvements and declines, SERP feature performance.

5. **Report GEO/AI Performance** -- AI citation overview, citations by topic, GEO wins, optimization opportunities.

6. **Report Domain Authority (CITE Score)** -- If a CITE audit has been run, include CITE dimension scores (C/I/T/E) with period-over-period trends and veto status. If no audit exists, note as "Not yet evaluated."

7. **Content Quality (CORE-EEAT Score)** -- If content-quality-auditor has been run, include average scores across all 8 CORE-EEAT dimensions with trends. If no audit exists, note as "Not yet evaluated."

8. **Report Backlink Performance** -- Link profile summary, weekly link acquisition, notable new links, competitive position.

9. **Report Content Performance** -- Publishing summary, top performing content, content needing attention, content ROI.

10. **Generate Recommendations** -- Immediate/short-term/long-term actions with priority, expected impact, and owner. Goals for next period.

11. **Compile Full Report** -- Combine all sections with table of contents, appendix (data sources, methodology, glossary).

   > **Reference**: See [references/report-output-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/references/report-output-templates.md) for complete output templates for all 11 report sections.

## Validation Checkpoints

### Input Validation
- [ ] Reporting period clearly defined with comparison period
- [ ] All required data sources available or alternatives noted
- [ ] Target audience identified (executive/technical/client)
- [ ] Performance goals and KPIs established for benchmarking

### Output Validation
- [ ] Every metric cites its data source and collection date
- [ ] Trends include period-over-period comparisons
- [ ] Recommendations are specific, prioritized, and actionable
- [ ] Source of each data point clearly stated (~~analytics data, ~~search console data, ~~SEO tool data, user-provided, or estimated)

## Example

**User**: "Create a monthly SEO report for cloudhosting.com for January 2025"

**Output** (abbreviated -- full report uses templates from all 11 steps):

```markdown
# CloudHosting SEO & GEO Performance Report — January 2025

## Executive Summary — Overall Performance: Good

| Metric | Jan 2025 | Dec 2024 | Change | Target | Status |
|--------|----------|----------|--------|--------|--------|
| Organic Traffic | 52,100 | 45,200 | +15.3% | 50,000 | On track |
| Keywords Top 10 | 87 | 79 | +8 | 90 | Watch |
| Organic Conversions | 684 | 612 | +11.8% | 700 | Watch |
| Domain Rating | 54 | 53 | +1 | 55 | Watch |
| AI Citations | 18 | 12 | +50.0% | 20 | Watch |

**SEO ROI**: $8,200 invested / $41,040 organic revenue = 400%

**Immediate**: Fix 37 crawl errors on /pricing/ pages
**This Month**: Optimize mobile LCP; publish 3 AI Overview comparison pages
**This Quarter**: Build Wikidata entry for CloudHost Inc.
```

## Tips for Success

1. **Lead with insights** - Start with what matters, not raw data
2. **Visualize data** - Charts and graphs improve comprehension
3. **Compare periods** - Context makes data meaningful
4. **Include actions** - Every report should drive decisions
5. **Customize for audience** - Executives need different info than technical teams
6. **Track GEO metrics** - AI visibility is increasingly important


### Save Results

After delivering monitoring data or reports to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to `memory/monitoring/YYYY-MM-DD-<topic>.md` containing:
- One-line headline finding or status change
- Top 3-5 actionable items
- Open loops or anomalies requiring follow-up
- Source data references

If any findings should influence ongoing strategy, recommend promoting key conclusions to `memory/hot-cache.md`.

## Reference Materials

- [Report Output Templates](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/references/report-output-templates.md) — Complete output templates for all 11 report sections
- [KPI Definitions](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/references/kpi-definitions.md) — SEO/GEO metric definitions with benchmarks, good ranges, warning thresholds, trend analysis, and attribution guidance
- [Report Templates by Audience](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/references/report-templates.md) — Copy-ready templates for executive, marketing, technical, and client audiences

## Next Best Skill

- **Primary**: [alert-manager](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/alert-manager/SKILL.md) — turn reporting insights into ongoing monitoring rules.

## Related Skills in This Suite

| Phase | Skills |
|-------|--------|
| **Research** | [keyword-research](../../research/keyword-research/SKILL.md), [competitor-analysis](../../research/competitor-analysis/SKILL.md), [serp-analysis](../../research/serp-analysis/SKILL.md), [content-gap-analysis](../../research/content-gap-analysis/SKILL.md) |
| **Build** | [seo-content-writer](../../build/seo-content-writer/SKILL.md), [geo-content-optimizer](../../build/geo-content-optimizer/SKILL.md), [meta-tags-optimizer](../../build/meta-tags-optimizer/SKILL.md), [schema-markup-generator](../../build/schema-markup-generator/SKILL.md) |
| **Optimize** | [on-page-seo-auditor](../../optimize/on-page-seo-auditor/SKILL.md), [technical-seo-checker](../../optimize/technical-seo-checker/SKILL.md), [internal-linking-optimizer](../../optimize/internal-linking-optimizer/SKILL.md), [content-refresher](../../optimize/content-refresher/SKILL.md) |
| **Monitor** | [rank-tracker](../rank-tracker/SKILL.md), [backlink-analyzer](../backlink-analyzer/SKILL.md), [performance-reporter](../performance-reporter/SKILL.md), [alert-manager](../alert-manager/SKILL.md) |
| **Cross-cutting** | [content-quality-auditor](../../cross-cutting/content-quality-auditor/SKILL.md), [domain-authority-auditor](../../cross-cutting/domain-authority-auditor/SKILL.md), [entity-optimizer](../../cross-cutting/entity-optimizer/SKILL.md), [memory-management](../../cross-cutting/memory-management/SKILL.md) |

> **Install the full suite**: See [README](https://github.com/aaron-he-zhu/seo-geo-claude-skills) for one-command install of all 20 skills.
