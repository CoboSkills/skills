# veroq

Verified intelligence for AI agents from VEROQ — 1,061 tickers, 200+ sources, 18 categories, bias scored, confidence rated. Live prices, trading signals, screener, social sentiment, crypto, forex, commodities, economic data.

## Install

```
openclaw install veroq
```

## Commands

### Ask & Verify

| Command | Description |
|---------|-------------|
| `/ask [question]` | Ask any question — verified answer with trade signals, reasoning, follow-ups |
| `/verify [claim]` | Fact-check a claim — verdict + evidence + confidence score |

### Intelligence

| Command | Description |
|---------|-------------|
| `/news [category] [limit]` | Latest verified briefs (18 categories) |
| `/brief [topic]` | Generate an on-demand intelligence brief |
| `/search [query]` | Full-text search across all briefs |
| `/trending` | Trending stories by engagement |
| `/forecast [topic]` | Structured predictions on any topic |
| `/entities [query]` | Search extracted entities (people, orgs, tickers) |
| `/trending-entities` | Most mentioned entities in last 24h |
| `/events [type] [subject]` | Structured events (acquisitions, funding, launches) |
| `/historical [from] [to]` | Search briefs within a date range |
| `/similar [brief_id]` | Find related briefs by similarity |
| `/clusters [period]` | Automatic story clusters by topic |
| `/data [entity] [type]` | Structured data (money, percentages, metrics) |
| `/timeline [brief_id]` | How a living brief evolved over time |
| `/web-search [query]` | Web search with trust scoring |
| `/crawl [url]` | Extract structured content from a URL |

### Trading & Market Data

| Command | Description |
|---------|-------------|
| `/price [symbol]` | Live price + change for any ticker |
| `/ticker [symbol]` | Ticker overview with sentiment + price |
| `/ticker-score [symbol]` | Composite trading signal (4 components) |
| `/technicals [symbol]` | 20 technical indicators + signal summary |
| `/candles [symbol] [range]` | OHLCV candlestick data |
| `/screener [query]` | AI-powered natural language stock screener |
| `/backtest [strategy]` | Replay strategies with equity curve + Sharpe |
| `/correlation [tickers]` | Pearson correlation matrix (up to 10 tickers) |
| `/alerts [action]` | Price/sentiment alerts with webhook delivery |
| `/market-movers` | Top gainers, losers, most active |
| `/sectors [days]` | All sectors with sentiment overview |
| `/portfolio [tickers]` | Portfolio-aware intelligence feed |
| `/events-calendar [ticker]` | Upcoming earnings, launches, acquisitions |
| `/ipo` | IPO calendar from SEC EDGAR |

### AI Reports

| Command | Description |
|---------|-------------|
| `/report [symbol] [tier]` | Generate AI analysis report (quick/full/deep) |

### Social Sentiment

| Command | Description |
|---------|-------------|
| `/social [symbol]` | Reddit + Twitter sentiment for a ticker |
| `/social-trending` | Trending tickers on social media |

### Alternative Assets

| Command | Description |
|---------|-------------|
| `/crypto [symbol]` | Crypto token data or market overview (200 tokens) |
| `/defi [protocol]` | DeFi TVL overview or protocol detail |
| `/economy [indicator]` | Economic indicators (GDP, CPI, unemployment, yields) |

## Coverage

- **1,061 tickers**: 713 equities (full S&P 500 + international ADRs), 197 crypto, 127 ETFs, 16 commodities, 8 market indices + auto-discovery
- **200+ sources** across 18 verticals
- **20 technical indicators**: SMA, EMA, RSI, MACD, Bollinger, ATR, Stochastic, ADX, OBV, VWAP, Williams %R, CCI, MFI, ROC, and more
- **Multi-provider prices**: Yahoo Finance + Twelve Data + FMP with automatic failover

## Pricing

| Plan | Credits/mo | Rate Limit | Price |
|------|------------|------------|-------|
| Free | 1,000 | 10/min | $0 |
| Builder | 3,000 | 120/min | $24/mo |
| Startup | 10,000 | 300/min | $79/mo |
| Growth | 40,000 | 600/min | $179/mo |
| Scale | 100,000 | 1,200/min | $399/mo |

Free tier requires no API key. Upgrade at [veroq.ai/pricing](https://veroq.ai/pricing).

## Security & Privacy

- **Read-only**: Only fetches public data. Does not write, modify, or delete anything.
- **No credentials**: No API keys or tokens required.
- **No user data**: Queries are not stored or shared.
- **Single domain**: All requests go to `api.veroq.ai` only.

Privacy policy: https://veroq.ai/privacy

## Links

- [VEROQ](https://veroq.ai)
- [API Reference](https://veroq.ai/api-reference)
- [SDKs & Integrations](https://veroq.ai/developers)
