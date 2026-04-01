---
name: kungfu_finance
description: Mainland China A-share stock and sector analysis tool (中国A股个股与板块分析). Current repo build focuses on stable deterministic products for stock snapshots, basic finance indicators, chip/price levels, sector detail lookup, plus bucket, phase-2 strategy, researcher, bayesian monitor, and preview stock/sector deep research flows.
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"skillKey":"kungfu_finance","always":false,"requires":{"bins":["node"],"env":["KUNGFU_OPENKEY"]},"primaryEnv":"KUNGFU_OPENKEY","install":{"node":{"packageManager":"none","bundledScripts":true}},"runtime":"bundled-node-scripts","networkSurface":["tianshan-api.kungfu-trader.com","push2.eastmoney.com","push2his.eastmoney.com","qt.gtimg.cn","ifzq.gtimg.cn"],"homepage":"https://github.com/kungfu-trader/kungfu-skills","publisher":{"name":"kungfu-trader","contact":"https://github.com/kungfu-trader"}}}
---

# 功夫财经 | KungfuFinance

## Publisher

- **Organization**: [kungfu-trader](https://github.com/kungfu-trader)
- **Source repository**: [github.com/kungfu-trader/kungfu-skills](https://github.com/kungfu-trader/kungfu-skills)
- **Tianshan API operator**: kungfu-trader (same organization)

## Runtime Model

- **Local runtime**: Node.js `.mjs` scripts (bundled executable scripts with zero npm dependencies — no `npm install` needed)
- **Outbound APIs**:
  - `https://tianshan-api.kungfu-trader.com` — deterministic products (snapshot, finance, bucket, strategy, researcher, bayesian monitor)
  - `https://push2.eastmoney.com` / `https://push2his.eastmoney.com` — stock/sector deep research market data (free public API, no key required)
  - `https://ifzq.gtimg.cn` / `https://qt.gtimg.cn` — fallback market data via Tencent Finance (free public API, no key required)
- **Authentication**: `KUNGFU_OPENKEY` environment variable, sent as `Authorization: Bearer <token>` (Tianshan API only; EastMoney/Tencent APIs require no authentication)
- **Platform header**: `KUNGFU_PLATFORM` (optional, defaults to `openclaw`)
- **File I/O**: reads bundled assets only, does not write local files
- **Subprocesses**: none — does not shell out, install dependencies, or fetch code at runtime

All environment variables are read from the host process; none are accepted from user prompts.

### Optional Research Search Surface

When separately configured, stock/sector deep research may call an additional search endpoint.
This surface is **independent** from the Tianshan API and uses its own credential boundary:

| Env Var | Purpose |
|---------|---------|
| `KUNGFU_ENABLE_RESEARCH_SEARCH` | Set to `1` to enable |
| `KUNGFU_RESEARCH_SEARCH_PROVIDER` | Provider name (currently `web_search`) |
| `KUNGFU_RESEARCH_SEARCH_ENDPOINT` | Search service URL |
| `KUNGFU_RESEARCH_SEARCH_API_KEY` | Search service credential |
| `KUNGFU_RESEARCH_SEARCH_TIMEOUT_MS` | Search request timeout (default: 15000) |

When search is enabled, requests are POSTed as JSON to `KUNGFU_RESEARCH_SEARCH_ENDPOINT` with `KUNGFU_RESEARCH_SEARCH_API_KEY` as Bearer token.
`KUNGFU_OPENKEY` is **never** reused for search requests.
If search is enabled but misconfigured, the result returns `misconfigured` status instead of silently failing.

### Non-Secret Tuning Variables

| Env Var | Purpose |
|---------|---------|
| `KUNGFU_ENABLE_EXPERIMENTAL_PRODUCTS` | Set to `1` to enable unreleased products |
| `KUNGFU_RESEARCH_DEFAULT_TARGET_DATE` | Override default research date (YYYYMMDD format, for testing) |

## Rollout Status

- Deterministic products (snapshot, finance, bucket, strategy, researcher, bayesian monitor) use revalidated Tianshan backend routes
- Preview `stock-research` / `sector-research` use public EastMoney/Tencent APIs for market data — no backend dependency for these flows
- Experimental products require `KUNGFU_ENABLE_EXPERIMENTAL_PRODUCTS=1`
- Preview `stock-research` / `sector-research` produce `markdown_svg_preview` with explicit degradation reporting

## Data Handling & Network Surface

- `KUNGFU_OPENKEY` is sent **only** to `tianshan-api.kungfu-trader.com` — never to EastMoney, Tencent, or any other host
- EastMoney and Tencent Finance APIs are public and require **no authentication**
- The code contacts **no other hosts** beyond those listed in the Runtime Model table above
- Do not use this skill with secrets, personal data, or other sensitive user content

## Scope

- Mainland China A-shares only
- Direct market-data lookup stays within one stock or one sector
- No arbitrary whole-market screening
- Not for US stocks
- Not for Hong Kong stocks
- Not for cryptocurrencies
- Not for futures or forex
- No free-form SQL
- No user-facing base URL
- No user-facing runtime credential parameters

## Public Intents

Route the user into the currently enabled intent families below.
Do not expose internal product names unless needed for implementation.

### 1. Stock Snapshot

Use when the user wants one A-share stock's current state, recent走势, K-line window, holders,筹码分布,支撑压力位, or other narrow deterministic data.

Default behavior:

- Prefer the narrowest data product that answers the question
- If the stock code is unknown, prefer `instrument_name`
- If code mode is used, `exchange_id` must be `SSE` or `SZE`

### 2. Finance Analysis

Use when the user wants one A-share stock's基础财务指标或基础财务上下文。

Default behavior:

- Prefer `finance_basic_indicators` for narrow factual questions
- Prefer `finance_context` for lightweight finance context

### 3. Sector Analysis

Use when the user asks about one A-share industry or sector.

Default behavior:

- deterministic sector detail products may still use `sector_name`
- fuzzy sector resolution is not exposed as a standalone public product, but `sector-research` resolves theme words by matching against the full EastMoney concept sector list
- preview `sector-research` accepts `sector_name` or `sector_id` directly; when the local resolver cannot disambiguate, it returns `needs_input` for the user to provide a BK code

### 3C. Sector Deep Research

Use when the user wants one A-share sector's deep research, hype-cycle view, thematic thesis, dragon-head observation, committee-style bull/bear review, or a longer structured report.

Default behavior:

- current runtime only supports one mainland China A-share sector per invocation
- the preview path accepts `sector_name` or `sector_id`; `target_date` is optional and defaults to the current market date in Asia/Shanghai
- the current version is `markdown_svg_preview` and returns explicit degradations for remaining search / adapter gaps
- the result surface now also exposes the migrated orchestration contract from the original `sector-analysis` skill
- the result surface now includes `report_svg` and `quality_gate`
- structured inputs now use public EastMoney APIs: concept sector list resolution, sector constituents, sector index K-line, and per-leader stock quotes and money flow
- the sector resolver matches user input against the full EastMoney concept sector list; if ambiguous, returns `needs_input` for the user to provide a BK code
- when the separate `web_search` runtime is enabled and configured, macro / policy / catalyst / industry-trend / competition / money-flow evidence may be attached as external search evidence (7 search buckets)
- otherwise the report must surface missing search evidence as degraded coverage instead of silently inventing facts

### 3B. Stock Deep Research

Use when the user wants one A-share stock's deep research, investment thesis, catalyst map, committee-style bull/bear review, or a longer structured report.

Default behavior:

- current runtime only supports one mainland China A-share stock per invocation
- the preview path accepts optional `target_date` and defaults it to the current market date in Asia/Shanghai
- the current version is `markdown_svg_preview` and returns explicit degradations for remaining search / adapter gaps
- the result surface now also exposes the migrated orchestration contract from the original `stock-analysis-v2` skill
- the result surface now includes `report_svg` and `quality_gate`
- structured market data now comes from public EastMoney APIs: real-time quote, daily K-line, real weekly K-line (klt=102, not aggregated from daily), and 20-day money flow; Tencent Finance APIs serve as fallback
- financial statements, company profile, and other non-market data are sourced from web search (8 search buckets: macro, catalyst, risk, competition, financials, company profile, governance, sector trend)
- when the separate `web_search` runtime is enabled and configured, these evidence buckets are populated; otherwise the report surfaces explicit degradations

### 4. Bucket Flow

Use when the user wants to:

- view current-user buckets
- choose one existing bucket
- add one or more instruments into that bucket

Default behavior:

- only operate on the current authenticated user's own buckets
- do not create or delete buckets in the current release build
- when adding a batch, resolve instruments first and filter invalid ones before writing
- when required information is missing or ambiguous, return a structured `needs_input` response so the host can continue the dialogue
- if all inputs are invalid, return `needs_input` for corrected instruments instead of calling the write API

### 5. Strategy Flow

Use when the user wants to:

- view public strategies
- view public strategies by market mode
- view current-user private strategies
- query one public or private strategy on one stock
- query one public or private select strategy's whole-market picks for one day or one date range
- count buy signals for one stock across eligible public paid strategies
- batch scan one public paid strategy across multiple stocks

Default behavior:

- strategy module requires runtime auth even when listing public strategies
- public and private strategies both support single-strategy query
- public and private select strategies both support controlled whole-market result query
- private strategies do not support first-stage batch scan
- batch scan only supports public strategies with non-empty `lago_plan`
- `market-select` supports `InstrumentSelect`, `TemplateInstrumentSelect`, `BuySell`, and `TemplateBuySell`
- when `market-select` is used on `BuySell` or `TemplateBuySell`, whole-market results only return buy points
- `market-select` accepts either `target_date`, or `strategy_start_date + strategy_end_date`
- if `market-select` mixes the two date modes, or only provides half of a range, return a structured `needs_input` response
- when strategy selector or stock input is missing or ambiguous, return a structured `needs_input` response so the host can continue the dialogue
- when the selected public paid strategy lacks permission for batch scan, return a structured `blocked` response instead of pretending the scan succeeded

### 6. Researcher Flow

Use when the user wants to:

- view top researchers by score
- view one stock's covered researchers together with report titles
- view one researcher's reports

Default behavior:

- researcher module requires runtime auth
- researcher backend also enforces `Journeyman` membership or above
- `stock-reports` is a composed flow built from researcher score plus researcher report list
- `author-reports` prefers `researcher-author-id`
- if the user only gives `researcher-name`, resolve it conservatively; if not unique, return `needs_input`
- do not pretend the backend supports direct global researcher-name search if it does not

### 7. Bayesian Monitor Flow

Use when the user wants to:

- view current-user bayesian monitor tasks
- choose one existing bayesian monitor task
- inspect that task's initial report and recent monitor records

Default behavior:

- bayesian monitor module requires runtime auth
- only operate on the current authenticated user's own tasks
- current release build is read-only: do not create, delete, or run bayesian monitor tasks
- `list` returns task summaries only and must not expose full `original_report`
- `reports` supports `bayesian-task-id` and conservative `bayesian-topic` resolution
- when task selector is missing or ambiguous, return a structured `needs_input` response so the host can continue the dialogue
- when the current user has no tasks, return a structured `blocked` response instead of pretending the task exists

### Not Yet Enabled In Experience Build

The following capabilities are still under route-contract cleanup and should not be used in the current public rollout:

- full finance-analysis bundles
- unusual movement analysis bundle
- money flow
- fuzzy sector resolution / similar sectors
- market news lookup
- standalone fuzzy sector resolution as a separate public deterministic intent outside `sector-research`

## Intent Routing

Pick one default route from the list below.

- User asks "这只股票现在怎么样 / 最近走势 / 看看价格":
  Route to `Stock Snapshot`
- User asks "分析财报 / 财务怎么样 / 估值怎么看":
  Route to `Finance Analysis`
- User asks "分析白酒 / 算力 / 某个板块 / 某个概念":
  Route to `Sector Analysis`
- User asks "给我做贵州茅台的深度研究 / 做一个投资论题 / 看催化剂和风险 / 写一份个股深度报告":
  Route to `Stock Deep Research`
- User asks "看看我的票池 / 把这些股票加到票池里":
  Route to `Bucket Flow`
- User asks "有哪些策略 / 看看我的私人策略 / 某个策略今天有没有买卖点 / 庐山升龙今天选了哪些股票 / 某个策略最近一周选股结果 / 用某个策略扫一组股票":
  Route to `Strategy Flow`
- User asks "评分最高的研究员有哪些 / 某个股票有哪些研究员和研报 / 某个研究员写过哪些研报":
  Route to `Researcher Flow`
- User asks "看看我的贝叶斯监控 / 某个贝叶斯监控任务的报告 / 某个主题最近的贝叶斯监控记录":
  Route to `Bayesian Monitor Flow`

If the user asks for arbitrary whole-market screening, movement-analysis bundles, or market-news bundles, do not use this skill in the current release build.

## Input Rules

### Stock Identification

For single-stock requests, use exactly one:

- `--instrument-name`
- `--instrument-id` and `--exchange-id`

Never mix both modes.
If the stock code is unknown, prefer `--instrument-name`.
When using code mode, `--exchange-id` must be `SSE` or `SZE`.

### Stock Date Mode

For stock products and flows, use:

- `--target-date`
- optional `--visual-days-len`

### Strategy Date Mode

For strategy actions, use:

- `signal` and `count`: `--target-date` with optional `--visual-days-len`
- `batch-scan`: `--target-date`
- `market-select`: either `--target-date`, or `--strategy-start-date` plus `--strategy-end-date`

Never mix single-day mode and range mode in the same `market-select` request.

### Sector Mode

- For sector detail products, use exactly one:
  - `--sector-name`
  - `--sector-id`

Prefer `--sector-name`.
Only reuse `--sector-id` after the backend has already returned it.
The current release build does not expose fuzzy sector resolution as a standalone public data product, but `sector-research` can resolve theme words via the EastMoney concept sector list.

### Hidden Parameters

Do not generate or expose these from the model side:

- `start_date`
- `end_date`
- `is_realtime`
- `limit`
- `days`
- `periods`

## Internal Building Blocks

The internal deterministic product contract lives here:

- [data_products.md](references/schemas/data_products.md)

Use that file only when you need exact internal product names, allowed parameter shapes, or output keys.
Do not dump that whole catalog into the user-facing reasoning path by default.

Bucket flow contract lives here:

- [bucket_flow.md](references/schemas/bucket_flow.md)

Strategy flow contract lives here:

- [strategy_flow.md](references/schemas/strategy_flow.md)

Researcher flow contract lives here:

- [researcher_flow.md](references/schemas/researcher_flow.md)

Bayesian monitor flow contract lives here:

- [bayesian_monitor_flow.md](references/schemas/bayesian_monitor_flow.md)

## Research Methodologies

Documented research methods live here:

- [README.md](references/research-flows/README.md)
- [runtime_parity.md](references/research-flows/runtime_parity.md)
- [stock-analysis](references/research-flows/stock-analysis)
- [sector-analysis](references/research-flows/sector-analysis)

Use them as methodology references and migration inputs for deep research.
The repo build currently has preview CLI/runtime entrypoints via `stock-research` and `sector-research`.
The sector preview accepts `sector_name` first and uses best-effort EastMoney concept list resolution before falling back to `needs_input`.
Read `runtime_parity.md` before treating any research wrapper or asset as implementation-ready truth.

Prompt assets are flow-specific.
Do not mix finance-analysis formatting requirements into movement-analysis outputs, or vice versa.

## Standard Commands

### Stock Snapshot

```bash
node scripts/flows/run_data_request.mjs --product price_snapshot --instrument-name 贵州茅台 --target-date 20260301
```

### Sector Detail

```bash
node scripts/flows/run_data_request.mjs --product sector_performance --sector-name 白酒 --target-date 20260301
```

### Bucket List

```bash
node scripts/router/run_router.mjs bucket --bucket-action list
```

### Bucket Add

```bash
node scripts/router/run_router.mjs bucket --bucket-action add --bucket-name 观察池 --bucket-instrument 贵州茅台 --bucket-instrument 平安银行
```

### Strategy List

```bash
node scripts/router/run_router.mjs strategy --strategy-action list
```

### Strategy Signal

```bash
node scripts/router/run_router.mjs strategy --strategy-action signal --strategy-name 三分归元 --instrument-name 贵州茅台 --target-date 20260331 --visual-days-len 22
```

### Strategy Batch Scan

```bash
node scripts/router/run_router.mjs strategy --strategy-action batch-scan --strategy-id 900 --strategy-instrument 600519.SSE --strategy-instrument 000001.SZE --target-date 20260331
```

### Strategy Market Select

```bash
node scripts/router/run_router.mjs strategy --strategy-action market-select --strategy-name 庐山升龙 --target-date 20260331
```

### Stock Deep Research

```bash
node scripts/router/run_router.mjs stock-research --instrument-name 贵州茅台 --target-date 20260331 --visual-days-len 120
```

### Sector Deep Research

```bash
node scripts/router/run_router.mjs sector-research --sector-name 机器人 --target-date 20260331 --visual-days-len 780
```

### Researcher Rank

```bash
node scripts/router/run_router.mjs researcher --researcher-action rank --researcher-rank-by 1m --researcher-limit 10
```

### Researcher Stock Reports

```bash
node scripts/router/run_router.mjs researcher --researcher-action stock-reports --instrument-name 贵州茅台
```

### Researcher Author Reports

```bash
node scripts/router/run_router.mjs researcher --researcher-action author-reports --researcher-author-id author-1
```
