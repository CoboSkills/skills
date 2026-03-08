# MCP Tool Reference

27 tools available, all prefixed with `mcp__alphafactoryx__`.

## General (1 tool)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_archive_stats` | _(none)_ | Database statistics: article/filing counts, symbol counts, date ranges |

## SEC EDGAR (5 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `edgar_overview` | `symbol`, `offset?` (default 0) | List all filings grouped by form type (10-K, 10-Q, 8-K, Form 4) |
| `edgar_filing` | `symbol`, `form_type`, `accession` | Full text of a specific filing by accession number (50K char limit) |
| `edgar_search` | `query`, `symbol?`, `form?`, `offset?` (default 0) | Full-text search across filings (up to 25 results) |
| `edgar_latest` | `symbol`, `form_type` | Most recent filing of a given form type (50K char limit) |
| `edgar_filings` | `symbol`, `form_type?`, `limit?` (default 10, max 50), `offset?` (default 0) | List filings with accession numbers for use with edgar_filing |

## Seeking Alpha (11 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `sa_overview` | `symbol`, `offset?` (default 0) | Overview: summary, ratings, financials, recent articles |
| `sa_article` | `symbol`, `article_id` | Full article text (10K char limit) |
| `sa_articles` | `symbol`, `limit?` (default/max 20), `since?` (date string, e.g. "2025-01-01"), `offset?` (default 0) | List articles with titles, authors, dates, IDs |
| `sa_search` | `query`, `symbol?`, `offset?` (default 0) | Full-text search across articles (up to 25 results) |
| `sa_transcript` | `symbol`, `transcript_id` | Earnings call transcript full text (30K char limit) |
| `sa_transcripts` | `symbol`, `limit?` (default 10, max 20), `since?` (date string, e.g. "2025-01-01"), `offset?` (default 0) | List earnings call transcripts with dates, IDs |
| `sa_transcript_search` | `query`, `symbol?`, `offset?` (default 0) | Full-text search across earnings call transcripts (up to 25 results) |
| `sa_financials` | `symbol` | Financials + dividends + estimates + peer companies |
| `sa_comments` | `symbol`, `article_id` | Comments on a Seeking Alpha article |
| `sa_news` | `symbol`, `limit?` (default 10, max 20), `since?` (date string, e.g. "2025-01-01"), `offset?` (default 0) | Seeking Alpha news items for a symbol |

## Stock News (2 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `stocknews_articles` | `symbol`, `limit?` (default/max 20), `sentiment?` (Positive/Negative/Neutral), `offset?` (default 0) | Recent news with multi-engine AI sentiment (Grok, DeepSeek, GPT-5) |
| `stocknews_search` | `query`, `symbol?`, `offset?` (default 0) | Full-text search across news articles |

## Polygon News (2 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `polygon_news_articles` | `symbol`, `limit?` (default/max 20), `since?` (date string, e.g. "2025-01-01"), `offset?` (default 0) | Polygon news with per-ticker AI sentiment insights and reasoning |
| `polygon_news_search` | `query`, `symbol?`, `offset?` (default 0) | Full-text search across Polygon news |

## X/Twitter Sentiment (3 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `x_sentiment` | `symbol`, `limit?` (default 20, max 50), `sort?` (views/date/favorites), `offset?` (default 0) | Tweets sorted by engagement |
| `x_sentiment_posts` | `symbol`, `limit?` (default 50), `since?`, `until?`, `min_views?`, `min_followers?`, `screen_name?`, `sort?` (default: date), `offset?` (default 0) | Filtered posts with date range, engagement thresholds, user filters |
| `x_sentiment_threads` | `symbol`, `limit?` (default 10, max 20), `offset?` (default 0) | High-engagement threads with reply chains |

## FRED Macro (2 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `fred_macro` | `series_id?`, `start?` (date string), `end?` (date string) | Without series_id: all 25 latest macro indicators. With series_id: time series (60 points); use start/end to filter by date range |
| `fred_series_list` | _(none)_ | List all available FRED series with title, frequency, and units |

## OHLCV Price Data (2 tools)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `kline` | `symbol`, `timeframe?` (daily/hourly/1min), `limit?` (default 60, max 200), `offset?` (default 0) | OHLCV price bars (offset skips N most recent bars) |
| `kline_symbols` | _(none)_ | List all symbols with available OHLCV data |

Parameters marked with `?` are optional.

## Pagination

Most list and search tools support an `offset` parameter (default 0). To get the next page of results, set `offset` to the number of results already retrieved. For example, after getting 20 articles with `sa_articles(symbol="AAPL", limit=20)`, get the next 20 with `sa_articles(symbol="AAPL", limit=20, offset=20)`.
