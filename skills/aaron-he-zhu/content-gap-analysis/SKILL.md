---
name: content-gap-analysis
description: 'SEO content gap analysis: find topics and keywords competitors rank for that you don''t, with prioritized editorial calendar and opportunity scoring. Part of a 20-skill SEO & GEO suite. 内容差距分析/选题规划/内容机会/内容策略/竞品内容'
version: "6.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when finding content gaps between two domains, discovering missing topics, or identifying coverage holes versus competitors."
argument-hint: "<your domain> <competitor domain>"
metadata:
  author: aaron-he-zhu
  version: "6.0.0"
  geo-relevance: "medium"
  tags:
    - seo
    - geo
    - content-gaps
    - topic-analysis
    - content-strategy
    - editorial-calendar
    - competitive-gap
    - content-opportunities
    - 内容缺口
    - コンテンツギャップ
    - 콘텐츠갭
    - brechas-contenido
  triggers:
    # EN-formal
    - "find content gaps"
    - "content opportunities"
    - "topic analysis"
    - "content strategy gaps"
    - "editorial calendar"
    - "untapped topics"
    # EN-casual
    - "what am I missing"
    - "topics to cover"
    - "what do competitors write about"
    - "what should I cover next"
    - "topics I haven't written about"
    - "they cover this but I don't"
    # EN-question
    - "what topics am I missing"
    - "what content should I create"
    # ZH-pro
    - "内容缺口分析"
    - "选题规划"
    - "内容机会"
    - "竞品话题"
    # ZH-casual
    - "缺什么内容"
    - "竞品写了什么"
    - "还应该写什么"
    # JA
    - "コンテンツギャップ"
    - "コンテンツ機会"
    # KO
    - "콘텐츠 갭 분석"
    - "콘텐츠 기회"
    # ES
    - "brechas de contenido"
    - "oportunidades de contenido"
    # PT
    - "lacunas de conteúdo"
    # Misspellings
    - "content gab analysis"
---

# Content Gap Analysis

**See every topic your competitors rank for that you don't** — this skill compares your content inventory against 3–5 rivals, scores each gap by traffic potential and effort, and delivers a prioritized editorial calendar you can act on immediately.

**Quick example**: `Find content gaps between myblog.com and hubspot.com, drift.com` → get a Tier 1 quick-win list, a Tier 2 strategic build plan, and a 90-day content calendar sorted by ROI.

**System role**: Research layer skill. It turns market signals into reusable strategic inputs for the rest of the library.

> **Part of the [SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills · [ClawHub](https://clawhub.ai/u/aaron-he-zhu) · [skills.sh](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)

## When This Must Trigger

Use this when the conversation involves any of these situations — even if the user does not use SEO terminology:

Use this whenever the task needs reusable market intelligence that should influence strategy, not just an ad hoc answer.

- Planning content strategy and editorial calendar
- Finding quick-win content opportunities
- Understanding where competitors outperform you
- Identifying underserved topics in your niche
- Expanding into adjacent topic areas
- Prioritizing content creation efforts
- Finding GEO opportunities competitors miss

## What This Skill Does

1. **Keyword Gap Analysis**: Finds keywords competitors rank for that you don't
2. **Topic Coverage Mapping**: Identifies topic areas needing more content
3. **Content Format Gaps**: Reveals missing content types (videos, tools, guides)
4. **Audience Need Mapping**: Matches gaps to audience journey stages
5. **GEO Opportunity Detection**: Finds AI-answerable topics you're missing
6. **Priority Scoring**: Ranks gaps by impact and effort
7. **Content Calendar Creation**: Plans gap-filling content schedule

## Quick Start

Start with one of these prompts. Finish with a short handoff summary using the repository format in [Skill Contract](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md).

### Basic Gap Analysis

```
Find content gaps between my site [URL] and [competitor URLs]
```

```
What content am I missing compared to my top 3 competitors?
```

### Topic-Specific Analysis

```
Find content gaps in [topic area] compared to industry leaders
```

```
What [content type] do competitors have that I don't?
```

### Audience-Focused

```
What content gaps exist for [audience segment] in my niche?
```

## Skill Contract

**Expected output**: a prioritized research brief, evidence-backed findings, and a short handoff summary ready for `memory/research/`.

- **Reads**: user goals, target market inputs, available tool data, and prior strategy from [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) and the shared [State Model](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/state-model.md) when available.
- **Writes**: a user-facing research deliverable plus a reusable summary that can be stored under `memory/research/`.
- **Promotes**: durable keyword priorities, competitor facts, entity candidates, and strategic decisions to `CLAUDE.md`, `memory/decisions.md`, and `memory/research/`; hand canonical entity work to `entity-optimizer`.
- **Next handoff**: use the `Next Best Skill` below when the findings are ready to drive action.

## Data Sources

> **Note:** All integrations are optional. This skill works without any API keys — users provide data manually when no tools are connected.

> See [CONNECTORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONNECTORS.md) for tool category placeholders.

**With ~~SEO tool + ~~search console + ~~analytics + ~~AI monitor connected:**
Automatically pull your site's content inventory from ~~search console and ~~analytics (indexed pages, traffic per page, keywords ranking), competitor content data from ~~SEO tool (ranking keywords, top pages, backlink counts), and AI citation patterns from ~~AI monitor. Keyword overlap analysis and gap identification can be automated.

**With manual data only:**
Ask the user to provide:
1. Your site URL and content inventory (list of published content with topics)
2. Competitor URLs (3-5 sites)
3. Your current traffic and keyword performance (if available)
4. Known content strengths and weaknesses
5. Industry context and business goals

Proceed with the full analysis using provided data. Note in the output which metrics are from automated collection vs. user-provided data.

## Instructions

When a user requests content gap analysis:

1. **Define Analysis Scope**

   Clarify parameters:
   
   ```markdown
   ### Analysis Parameters
   
   **Your Site**: [URL]
   **Competitors to Analyze**: [URLs or "identify for me"]
   **Topic Focus**: [specific area or "all"]
   **Content Types**: [blogs, guides, tools, videos, or "all"]
   **Audience**: [target audience]
   **Business Goals**: [traffic, leads, authority, etc.]
   ```

2. **Audit Your Existing Content**

   Document total indexed pages, content by type and topic cluster, top performing content, and content strengths/weaknesses.

3. **Analyze Competitor Content**

   For each competitor: document content volume, monthly traffic, content distribution by type, topic coverage vs. yours, and unique content they have.

4. **Identify Keyword Gaps**

   Find keywords competitors rank for that you do not. Categorize into High Priority (high volume, achievable difficulty), Quick Wins (lower volume, low difficulty), and Long-term (high volume, high difficulty). Include keyword overlap analysis.

5. **Map Topic Gaps**

   Create a topic coverage comparison matrix across all competitors. For each missing topic cluster, document business relevance, competitor coverage, opportunity size, sub-topics, and recommended pillar/cluster approach.

6. **Identify Content Format Gaps**

   Compare format distribution (guides, tutorials, comparisons, case studies, tools, templates, video, infographics, research) against competitors and industry averages. For each gap, assess effort and expected impact.

7. **Analyze GEO/AI Gaps**

   Identify topics where competitors get AI citations but you do not. Document missing Q&A content, definition/explanation content, and comparison content. Score each by traditional SEO value and GEO value.

8. **Map to Audience Journey**

   Compare funnel stage coverage (Awareness, Consideration, Decision, Retention) against competitor averages. Detail specific gaps at each stage.

9. **Prioritize and Create Action Plan**

   Produce a final report with: Executive Summary, Prioritized Gap List (Tier 1 Quick Wins, Tier 2 Strategic Builds, Tier 3 Long-term), Content Calendar, and Success Metrics.

   > **Reference**: See [references/analysis-templates.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/references/analysis-templates.md) for detailed templates for each step.

## Validation Checkpoints

### Input Validation
- [ ] Your content inventory is complete or representative sample provided
- [ ] Competitor URLs identified (minimum 2-3 competitors)
- [ ] Analysis scope defined (specific topics or comprehensive)
- [ ] Business goals and priorities clarified

### Output Validation
- [ ] Every recommendation cites specific data points (not generic advice)
- [ ] Gap analysis compares like-to-like content (topic clusters to topic clusters)
- [ ] Priority scoring based on measurable criteria (volume, difficulty, business fit)
- [ ] Content calendar maps gaps to realistic timeframes
- [ ] Source of each data point clearly stated (~~SEO tool data, ~~analytics data, ~~AI monitor data, user-provided, or estimated)

## Example

> **Reference**: See [references/example-report.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/references/example-report.md) for a complete example analyzing SaaS marketing blog gaps vs. HubSpot and Drift.

## Advanced Analysis

### Competitive Cluster Comparison

```
Compare our topic cluster coverage for [topic] vs top 5 competitors
```

### Temporal Gap Analysis

```
What content have competitors published in the last 6 months that we haven't covered?
```

### Intent-Based Gaps

```
Find gaps in our [commercial/informational] intent content
```

## Tips for Success

1. **Focus on actionable gaps** - Not all gaps are worth filling
2. **Consider your resources** - Prioritize based on ability to execute
3. **Quality over quantity** - Better to fill 5 gaps well than 20 poorly
4. **Track what works** - Measure gap-filling success
5. **Update regularly** - Gaps change as competitors publish
6. **Include GEO opportunities** - Don't just optimize for traditional search



### Save Results

After delivering findings to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to `memory/research/content-gap-analysis/YYYY-MM-DD-<topic>.md` containing:
- One-line headline finding
- Top 3-5 actionable items
- Open loops or blockers
- Source data references

If any findings should influence ongoing strategy, recommend promoting key conclusions to `memory/hot-cache.md`.

## Reference Materials

- [Analysis Templates](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/references/analysis-templates.md) — Detailed templates for each analysis step (inventory, competitor content, keyword gaps, topic gaps, format gaps, GEO gaps, journey, prioritized report)
- [Gap Analysis Frameworks](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/references/gap-analysis-frameworks.md) — Content audit matrices, funnel mapping, and gap prioritization scoring methodologies
- [Example Report](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/research/content-gap-analysis/references/example-report.md) — Complete example analyzing SaaS marketing blog gaps vs. HubSpot and Drift

## Next Best Skill

- **Primary**: [seo-content-writer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/seo-content-writer/SKILL.md) — turn missing topics into a draft or content roadmap.

## Related Skills in This Suite

| Phase | Skills |
|-------|--------|
| **Research** | [keyword-research](../keyword-research/SKILL.md), [competitor-analysis](../competitor-analysis/SKILL.md), [serp-analysis](../serp-analysis/SKILL.md), [content-gap-analysis](../content-gap-analysis/SKILL.md) |
| **Build** | [seo-content-writer](../../build/seo-content-writer/SKILL.md), [geo-content-optimizer](../../build/geo-content-optimizer/SKILL.md), [meta-tags-optimizer](../../build/meta-tags-optimizer/SKILL.md), [schema-markup-generator](../../build/schema-markup-generator/SKILL.md) |
| **Optimize** | [on-page-seo-auditor](../../optimize/on-page-seo-auditor/SKILL.md), [technical-seo-checker](../../optimize/technical-seo-checker/SKILL.md), [internal-linking-optimizer](../../optimize/internal-linking-optimizer/SKILL.md), [content-refresher](../../optimize/content-refresher/SKILL.md) |
| **Monitor** | [rank-tracker](../../monitor/rank-tracker/SKILL.md), [backlink-analyzer](../../monitor/backlink-analyzer/SKILL.md), [performance-reporter](../../monitor/performance-reporter/SKILL.md), [alert-manager](../../monitor/alert-manager/SKILL.md) |
| **Cross-cutting** | [content-quality-auditor](../../cross-cutting/content-quality-auditor/SKILL.md), [domain-authority-auditor](../../cross-cutting/domain-authority-auditor/SKILL.md), [entity-optimizer](../../cross-cutting/entity-optimizer/SKILL.md), [memory-management](../../cross-cutting/memory-management/SKILL.md) |

> **Install the full suite**: See [README](https://github.com/aaron-he-zhu/seo-geo-claude-skills) for one-command install of all 20 skills.
