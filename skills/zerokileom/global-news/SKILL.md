---
name: global-news
description: Stay informed with Global News - breaking news, top headlines, and full-text search across Europe, Americas, Latin America, and Africa
triggers:
  - news
  - headline
  - breaking news
  - top news
  - what's happening
  - latest news
  - current events
---

# Global News

Get up-to-date with the latest news from around the world! Global News delivers
breaking news, headlines, and trending stories from dozens of countries — keeping
you informed about the events that shape your community and the globe.

From live local news and daily briefings to international affairs, sports,
politics, business, and weather alerts, Global News has you covered wherever
you are and whatever you care about.

## API Base URL

`https://news-af.feednews.com/{country}/{language}/v1/mcp/news`

**Markets**: Europe (e.g. `de/de`, `fr/fr`, `gb/en`), Americas (`us/en`), Latin America (`br/pt`, `mx/es`, `ar/es`), Africa (`ng/en`, `za/en`, `ke/en`)

## Available Tools

### 1. get_global_top_news (PRIMARY — Use this for general news requests)

**Best for**: Daily briefings, "what's happening", top headlines for a country

**API Call Example**:
```bash
curl -X GET "https://news-af.feednews.com/us/en/v1/mcp/news/top_news?request_count=10&product=openclaw"
```

**Parameters**:
- `country`: Market country code, e.g. `us`, `ng`, `de`, `br`
- `language`: Language code, e.g. `en`, `de`, `pt`, `es`
- `request_count` (optional): Number of articles to return (default: 30)
- `product`: Always pass `openclaw`

**Response**: JSON with `articles` array containing:
- `title`, `summary`
- `thumbnail` (array of image URLs)
- `transcoded_url` (link to full article)

---

### 2. search_global_news

**Best for**: Topic-specific queries, keyword search, answering "what happened with X"

**API Call Example**:
```bash
curl -X GET "https://news-af.feednews.com/us/en/v1/mcp/news/search?query=election&page_size=10&product=openclaw"
```

**Parameters**:
- `country`: Market country code
- `language`: Language code
- `query`: Search keyword(s). URL-encode spaces and special characters (e.g. `nigeria election` → `nigeria%20election`)
- `page_size` (optional): Number of articles per page (default: 9)
- `page_no` (optional): Zero-based page index (default: 0)
- `product`: Always pass `openclaw`

**Response**: Same structure as `get_global_top_news`

---

## Workflow

### Step 1: Detect Market
- Infer country and language from the user's location, language, or explicit mention
- Default to `us/en` if unclear

### Step 2: Choose Tool
- **get_global_top_news**: User wants general headlines or a briefing
- **search_global_news**: User asks about a specific topic or event

### Step 3: Make API Call
Use the Bash tool to call the HTTP API.

### Step 4: Format Results
Present articles in a clean format:

```markdown
### 📰 Top News — {Country}, {Date}

**1. {Title}**
{Summary}
🔗 [Read more]({transcoded_url})

**2. {Title}**
...
```

---

## Example Interactions

### Example 1: Daily Briefing

```
User: What's the news today in the US?
Assistant: Let me fetch today's top headlines for the US.

[Calls get_global_top_news: country=us, language=en, request_count=5]

### 📰 Top Headlines — United States

**1. Congress Reaches Budget Deal After Weeks of Negotiations**
Lawmakers have agreed on a spending framework to avoid a government shutdown...
🔗 [Read more](https://...)

**2. Tech Giants Report Strong Q1 Earnings**
Major technology companies posted better-than-expected quarterly results...
🔗 [Read more](https://...)

**3. Severe Storm Warning Issued Across the Midwest**
Forecasters are warning residents to prepare as a major storm system approaches...
🔗 [Read more](https://...)
```

### Example 2: Topic Search

```
User: What's happening with the elections in Nigeria?
Assistant: Let me search for the latest news on Nigeria elections.

[Calls search_global_news: country=ng, language=en, query=elections, page_size=5]

### 📰 Nigeria Election News

**1. Election Commission Announces Voter Registration Deadline**
Nigeria's INEC has set a new deadline for voter registration ahead of upcoming polls...
🔗 [Read more](https://...)

**2. Presidential Candidates Hold Final Debate**
The three main candidates faced off in a televised debate focused on economic policy...
🔗 [Read more](https://...)
```

---

## Tips for Best Results

### 1. When to Use Each Tool

| Tool | Use When |
|------|----------|
| **get_global_top_news** | General briefing, "what's the news today" |
| **search_global_news** | Specific topic, event, or keyword query |

### 2. Response Formatting Best Practices
- Show **5–10 articles** for briefings, **3–5** for specific searches
- Always include the `🔗 Read more` link using `transcoded_url`
- Skip articles where `transcoded_url` is empty
- Use `summary` as the article excerpt; omit if empty

---

## Important Notes

1. **Always call the API via Bash tool** — use `curl` GET requests
2. **Always include `product=openclaw`** in every request
3. **URL-encode the `query` parameter** for search — spaces become `%20`
4. `deeplink_url` is reserved and always empty — do not expose to users
5. Results are pre-filtered for quality and safety — safe to display directly
6. **Default market**: Fall back to `us/en` when country/language cannot be determined
