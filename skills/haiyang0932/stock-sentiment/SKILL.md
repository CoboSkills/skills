---
name: stock-sentiment
description: "Stock sentiment analysis and financial data for US equity research. Analyze multi-engine AI sentiment (Grok, DeepSeek, GPT-5), SEC EDGAR filings, Seeking Alpha ratings, earnings call transcripts, social media sentiment, news insights, FRED macro indicators, and OHLCV prices for 2000+ stocks. Use when researching stocks, checking sentiment, analyzing SEC filings, or exploring market data."
argument-hint: "[symbol]"
allowed-tools: mcp__alphafactoryx__*
metadata:
  openclaw:
    requires:
      env:
        - name: ALPHAFACTORYX_MCP_TOKEN
          description: "API token for paid tier access (starter/pro/enterprise). Not required for free tier (20 req/day)."
          required: false
      bins: []
    emoji: "📊"
    homepage: "https://alphafactoryx.com"
    mcp:
      server: alphafactoryx
      type: streamable-http
      url: "https://mcp.alphafactoryx.com/mcp"
      headers:
        Authorization: "Bearer $ALPHAFACTORYX_MCP_TOKEN"
---

# Stock Sentiment & Financial Data

Stock sentiment analysis and US equity research tools. Query multi-engine AI sentiment scores, SEC filings, analyst ratings, earnings transcripts, social media sentiment, macro indicators, and price data for 2000+ stocks — all through 27 MCP tools.

## References

- `references/tools.md` — full tool reference with parameters and descriptions
- `references/workflows.md` — step-by-step research workflows (stock analysis, sentiment, macro, deep search)

## Quick Start

No token or registration needed. Free tier: 20 requests/day per IP.

**Check data coverage:**
```
mcp__alphafactoryx__get_archive_stats()
```

**Research a stock:**
```
mcp__alphafactoryx__sa_overview(symbol="AAPL")
mcp__alphafactoryx__edgar_latest(symbol="AAPL", form_type="10-K")
mcp__alphafactoryx__stocknews_articles(symbol="AAPL")
mcp__alphafactoryx__kline(symbol="AAPL")
```

**Search across archives:**
```
mcp__alphafactoryx__edgar_search(query="revenue guidance", symbol="AAPL")
mcp__alphafactoryx__sa_search(query="AI chips")
mcp__alphafactoryx__sa_transcript_search(query="margin expansion")
```

**Check sentiment:**
```
mcp__alphafactoryx__stocknews_articles(symbol="AAPL")
mcp__alphafactoryx__polygon_news_articles(symbol="AAPL")
mcp__alphafactoryx__x_sentiment(symbol="AAPL")
```

**Get macro data:**
```
mcp__alphafactoryx__fred_macro()
```

## Tool Categories

| Category | Tools | Key Capabilities |
|----------|-------|-----------------|
| General | 1 | Archive stats and data coverage |
| SEC EDGAR | 5 | Filings (10-K, 10-Q, 8-K, Form 4), full text, full-text search |
| Seeking Alpha | 10 | Articles, news, earnings transcripts, ratings, financials, comments, search |
| Stock News | 2 | News articles with Grok + DeepSeek + GPT-5 sentiment, search |
| Polygon News | 2 | News with per-ticker AI sentiment insights + reasoning, search |
| X/Twitter | 3 | Tweets by engagement, filtered posts, high-engagement threads |
| FRED Macro | 2 | 25 macro indicators (rates, CPI, GDP, VIX, yield curve), series listing |
| OHLCV | 2 | Daily/hourly/1min price bars, symbol listing |

## Authentication

**Free tier (no setup):** 20 requests/day, 1 req/sec. Just connect and use.

**Paid tiers:** Set `ALPHAFACTORYX_MCP_TOKEN` in your env:

| Tier | Daily | Rate | Price |
|------|-------|------|-------|
| Free | 20 | 1/s | $0 |
| Starter | 200 | 2/s | $29/mo |
| Pro | 2,000 | 5/s | $99/mo |
| Enterprise | 10,000 | 10/s | From $299/mo |

See [alphafactoryx.com/pricing](https://alphafactoryx.com/pricing) for details.

## Best Practices

- **Start with `get_archive_stats`** to check data coverage before querying
- **Cross-reference sources** — combine EDGAR, SA, news, sentiment, and price data
- **Use search tools** — find content across archives by keyword
- **Paginate with `offset`** — most tools support `offset` for paging through results
- **Filing text is truncated** — use search tools to find specific sections in long filings
- **Use `since` for recent data** — date filtering on articles, transcripts, and news

## Error Handling

| Error | Action |
|-------|--------|
| "No data available" / "No filings found" | Check symbol spelling; use `get_archive_stats` for coverage |
| Authentication error | Check `ALPHAFACTORYX_MCP_TOKEN` env var |
| Rate limit (429) | Wait and retry; consider upgrading tier |
| Text truncated | Use search tools to find specific sections |
| Network timeout | Check https://mcp.alphafactoryx.com/mcp is accessible |

## Data Coverage

- ~2,000 US equities (stocks + ETFs)
- SEC EDGAR: 10-K, 10-Q, 8-K filings and Form 4 insider trades (full text)
- Seeking Alpha: articles, earnings call transcripts, ratings, financials, dividends, estimates
- Stock News: articles with Grok + DeepSeek + GPT-5 sentiment
- Polygon News: articles with per-ticker AI sentiment insights and reasoning
- X/Twitter: tweets with engagement metrics for ~50 stocks (not the full 2000)
- FRED: 25 macro series (Fed Funds, CPI, GDP, unemployment, VIX, yield curve, etc.)
- OHLCV: daily, hourly, 1-minute bars for ~2000 stocks + 6 futures (ES, NQ, YM, RTY, GC, CL)