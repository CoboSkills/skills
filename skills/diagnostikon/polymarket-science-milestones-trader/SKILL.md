---
name: polymarket-science-milestones-trader
description: Trades Polymarket prediction markets on scientific breakthroughs, Nobel Prizes, physics discoveries, climate science milestones, and research paper impact.
metadata:
  author: Diagnostikon
  version: "1.0"
  displayName: Science Milestones & Research Trader
  difficulty: advanced
---

# Science Milestones & Research Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Preprint server velocity signal: arXiv/bioRxiv papers citing breakthrough keywords spike 3–7 days before mainstream coverage, before markets reprice.

## Edge Thesis

Scientific breakthrough markets are priced by non-experts following journalist headlines. The actual scientific community publishes on preprint servers 2–4 weeks before journal publication. A high-citation preprint on arXiv predicts a major Nature/Science paper with ~70% accuracy — and Polymarket markets on the underlying topic take 5–10 days to fully reprice after the preprint drops. Nobel Prize markets are uniquely predictable: Thomson Reuters/Clarivate Citation Laureates correctly predicted ~40% of Nobel winners in advance using citation impact data.

### Remix Signal Ideas
- **arXiv API**: https://arxiv.org/help/api/ — New preprint velocity per topic — leading indicator for breakthrough markets
- **Clarivate Citation Laureates**: https://clarivate.com/the-link/clarivate-citation-laureates/ — Nobel Prize predictions from citation impact analysis
- **Semantic Scholar API**: https://api.semanticscholar.org/ — Real-time citation graph — detect breakout papers early

## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only with `--live` flag.**

| Scenario | Mode | Financial risk |
|---|---|---|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

`autostart: false` and `cron: null` — nothing runs automatically until you configure it in Simmer UI.

## Required Credentials

| Variable | Required | Notes |
|---|---|---|
| `SIMMER_API_KEY` | Yes | Trading authority. Treat as high-value credential. |

## Tunables (Risk Parameters)

All declared as `tunables` in `clawhub.json` and adjustable from the Simmer UI.

| Variable | Default | Purpose |
|---|---|---|
| `SIMMER_MAX_POSITION` | See clawhub.json | Max USDC per trade |
| `SIMMER_MIN_VOLUME` | See clawhub.json | Min market volume filter |
| `SIMMER_MAX_SPREAD` | See clawhub.json | Max bid-ask spread |
| `SIMMER_MIN_DAYS` | See clawhub.json | Min days until resolution |
| `SIMMER_MAX_POSITIONS` | See clawhub.json | Max concurrent open positions |

## Dependency

`simmer-sdk` by Simmer Markets (SpartanLabsXyz)
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
