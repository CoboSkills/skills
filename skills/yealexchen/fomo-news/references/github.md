# GitHub Trending

Fetches trending repositories from the past 7 days using the GitHub Search API.

## Command

```bash
node fetch.mjs github [--limit <n>] [--json]
```

## Queries

Three parallel queries are executed and deduplicated:

| Query | Focus | Max Results |
|-------|-------|-------------|
| `stars:>50 created:>{7d ago}` | General trending | 15 |
| `topic:ai stars:>20 created:>{7d ago}` | AI repos | 10 |
| `topic:llm stars:>10 created:>{7d ago}` | LLM repos | 10 |

Results are sorted by star count (descending) and deduplicated by repo ID.

## Output Fields

| Field | Description |
|-------|-------------|
| `name` | Full repo name (owner/repo) |
| `description` | Repo description (max 150 chars) |
| `stars` | Star count |
| `forks` | Fork count |
| `language` | Primary language |
| `url` | GitHub URL |
| `topics` | Top 5 topics |
| `created` | Creation date |

## Authentication

Set `GITHUB_TOKEN` env var for higher rate limits (5000/hr vs 60/hr unauthenticated).
