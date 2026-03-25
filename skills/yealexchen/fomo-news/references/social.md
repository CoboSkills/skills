# Social Posts

Tracks influential tech/AI figures via Google News RSS feeds.

## Command

```bash
node fetch.mjs social [--limit <n>] [--json]
```

## Tracked Figures

| Name | Category |
|------|----------|
| Sam Altman | AI |
| Elon Musk | Tech |
| Jensen Huang | AI |
| Dario Amodei | AI |
| Satya Nadella | Tech |
| Sundar Pichai | Tech |
| Mark Zuckerberg | Tech |
| Tim Cook | Tech |
| Demis Hassabis | AI |
| Ilya Sutskever | AI |
| Andrej Karpathy | AI |
| Yann LeCun | AI |

Each person is searched via Google News RSS with a `when:3d` filter (last 3 days). Max 3 items per person.

## Output Fields

| Field | Description |
|-------|-------------|
| `author` | Person's name |
| `handle` | Social media handle |
| `category` | ai or tech |
| `title` | Headline |
| `link` | Article URL |
| `pubDate` | Publication date |
| `snippet` | Brief excerpt (max 200 chars) |
