---
name: toolroute
description: "Route agent tasks through ToolRoute for optimal MCP server and model selection. Scores tools on real execution data — quality, reliability, efficiency, cost, and trust. Free, no API key needed."
homepage: https://toolroute.io
metadata:
  openclaw:
    emoji: "🔀"
    requires:
      bins: ["curl"]
    env: []
---

# ToolRoute — Intelligent Routing for Agent Tasks

ToolRoute tells your agent which MCP server or model to use for a specific task, based on real execution data from thousands of agent runs. Not GitHub stars. Not vibes. Actual outcomes.

Free. No API key needed.

## When to use this skill

Use ToolRoute before any task where you need to pick which MCP server to use for a job, or which model tier to use (stop paying GPT-4o prices for simple tasks).

## Route a task
```bash
curl -s "https://toolroute.io/api/route?task=YOUR_TASK_DESCRIPTION"
```

Or with constraints:
```bash
curl -s -X POST "https://toolroute.io/api/route" \
  -H "Content-Type: application/json" \
  -d '{"task": "scrape product prices", "constraints": {"priority": "best_value"}}'
```

Response: `recommended_skill`, `confidence`, `fallback_chain`, `cost_estimate`, `alternatives`.

## Priority options

- `best_value` (default) — best quality/cost tradeoff
- `best_quality` — highest output quality
- `best_efficiency` — lowest latency
- `lowest_cost` — cheapest option
- `highest_trust` — most verified tools only

## Report outcomes (earn credits)
```bash
curl -s -X POST "https://toolroute.io/api/report" \
  -H "Content-Type: application/json" \
  -d '{"skill_slug": "firecrawl-mcp", "outcome": "success", "latency_ms": 1240, "quality_rating": 8}'
```

Report any MCP server you use. Every report improves routing for all agents.

## Add as MCP server
```json
{
  "mcpServers": {
    "toolroute": {
      "url": "https://toolroute.io/api/mcp",
      "transport": "http"
    }
  }
}
```

MCP tools: `toolroute_route`, `toolroute_report`, `toolroute_search`, `toolroute_compare`

## Scoring model

Value Score = 0.35×Quality + 0.25×Reliability + 0.15×Efficiency + 0.15×Cost + 0.10×Trust

Full docs: https://toolroute.io/api/route
