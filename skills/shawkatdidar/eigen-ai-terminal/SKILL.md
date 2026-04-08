---
name: eigen-ai-terminal
description: Live AI landscape intelligence — signals, causal chains, developing trends, roadblocks, and predictions. 10 tools to query 16 domains of the AI landscape and get only what's relevant to your work.
version: 0.8.0
homepage: https://eigenterminal.clawlab.dev
repository: https://github.com/shawkatdidar/eigen-ai-terminal
metadata:
  openclaw:
    requires:
      bins:
        - node
    mcp:
      command: node
      args:
        - index.js
tags:
  - ai
  - intelligence
  - radar
  - signals
  - mcp
  - research
---

# Eigen AI Terminal

Live intelligence on the AI landscape — what's happening, what it causes, and what it means for your work.

## Network behavior

This skill reads **public, read-only JSON** from the Eigen AI Terminal website. No authentication required. No user data is uploaded. One-way data flow only.

- Data endpoint: `eigenterminal.clawlab.dev/data/radar.json`
- Wiki endpoint: `eigenterminal.clawlab.dev/wiki/`

## What this does

Eigen AI Terminal tracks 16 domains of the AI landscape daily. This skill gives your agent 10 tools to query signals, causal chains, developing trends, roadblocks, velocity metrics, predictions, and a full interconnected wiki knowledge base.

The key tool is `radar_relevant` — tell it what you're working on and it returns only the signals, trends, and roadblocks that matter for your specific context.

## Tools (11)

### `radar_brief`
Get today's AI signals. Filter by `view` (builder/strategic/all) and `significance` (significant/notable/all).

### `radar_signal_ripple`
Get the full causal ripple chain for a specific signal — what it pushes, what trends it feeds, what it's blocked by, what we predict.

### `radar_trends`
Get developing trends — when 3+ independent signals converge toward the same outcome.

### `radar_roadblocks`
Get roadblocks holding AI back — what's blocked, who's attacking it, signs of progress.

### `radar_velocity`
Get rate-of-change metrics. Filter by category: cost, capability, capital, adoption.

### `radar_predictions`
Get falsifiable predictions with confidence levels and check dates.

### `radar_relevant`
Describe what you're building or working on. Returns only the signals, trends, roadblocks, and predictions relevant to your specific context.

### `radar_wiki_browse`
Browse the full knowledge base by category (nodes, entities, briefs, forces, frameworks).

### `radar_wiki_read`
Read any wiki page. Returns full markdown content with [[wikilink]] navigation hints to follow.

### `radar_wiki_search`
Search across all 49 wiki files by keyword or tag.

### `radar_morning_setup`
Returns instructions for setting up an automatic daily morning briefing personalized to the user's work.

## First use

When the user first invokes this skill or asks anything about AI news, present this welcome message:

```
✅ Eigen AI Terminal connected — tracking 16 domains of the AI landscape daily.

I can now answer questions like:
• "What happened in AI today that affects my work?"
• "Show me the ripple effects of [any signal]"
• "Search the Eigen wiki for [topic]"

🔔 Want a personalized AI briefing every morning?
   Say "set up my Eigen morning brief" and I'll deliver
   only what matters for your work — every day, automatically.
```

## Getting started

Try asking your agent:

- "What happened in AI today that affects my work?"
- "I'm building a coding tool with open-source models — what should I know?"
- "What roadblocks should I be aware of for my MCP-based project?"
- "Show me the ripple effects of the biggest signal today"
- "Set up my Eigen morning brief" — your agent sets up a daily personalized summary

## Privacy

One-way data flow: your agent pulls public data, combines with your local context, delivers insights to you. We never see what you're building, what you asked, or what your agent told you.
