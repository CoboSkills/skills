---
name: iran-briefing
description: Real-time Iran crisis intelligence — decision-oriented briefing with situation assessment, active threads, events, social signals, prediction markets, and 700+ tracked entities.
metadata: {"openclaw":{"emoji":"🇮🇷","requires":{},"api_path":"iran"}}
user-invocable: true
---

# Iran Briefing — Decision Support Skill

## When to use

Iran conflict, US-Iran tensions, Israel-Iran, Middle East geopolitics, oil/Hormuz, prediction markets, IRGC, IDF, ceasefire.

## How to think — the decision loop

**Always start from the briefing. Let the data guide your next call.** Do NOT call all endpoints.

### Step 1: Assess — get the big picture

```
curl -s "https://skill.capduck.com/iran"
```

The briefing contains situation assessment (tension 1-10, direction, key deltas), perspective summaries (with evidence strength ◆◇○), active threads (with signals and drill-down hints), and top events. Each section tells you where to look next.

### Step 2: Investigate — follow the scent

- A thread mentions linked events → `/events?category=CONFLICT` to read the evidence chain
- A claim has weak evidence (○) → `/posts?source_type=osint` to see if OSINT confirms
- Mainstream narrative unclear → `/news?region=us` to see how US outlets frame it
- A thread links to prediction markets → `/polymarket` for probability and trend

### Step 3: Cross-reference — triangulate

- Compare official sources vs OSINT vs mainstream: `/posts?source_type=state_media` vs `osint` vs `/news`
- Use `/notable` to understand who a source is and which camp they belong to
- Use `/entities?q=name` to check credibility of an unfamiliar source
- Check `source_count` in events — 1 source = rumor, 5+ sources = confirmed

### Step 4: Project — what happens next

- Look at **Watch** items in Active Threads: likelihood direction (rising/stable/falling), next milestones, decision makers
- Check `/polymarket` for market-implied probabilities and trend direction
- When polymarket diverges from briefing assessment, one of them is wrong — that's where investigation value is highest

## Endpoints

**`/{topic}`** — AI briefing: tension level, 4-perspective summary, active threads with signals, top events. Always start here.

**`/{topic}/events`** — Structured events with impact score, sentiment, confidence, source attribution. Each event has an ID for cross-referencing.
- Params: `impact` (min 1-10), `category`, `hours`, `since` (ISO), `limit`

**`/{topic}/posts`** — Social feed (Twitter + Telegram). Each post has author classification and source_type.
- Params: `source_type`, `category`, `platform`, `event` (event ID → linked posts), `since`, `limit`

**`/{topic}/news`** — Mainstream media articles with region and language metadata.
- Params: `region`, `language`, `event` (event ID → linked articles), `since`, `limit`

**`/{topic}/polymarket`** — Prediction market probabilities, trends, and historical price ranges.

**`/{topic}/notable`** — ~90 curated key entities grouped by role:

| Group | What it represents |
|-------|-------------------|
| Iran Official | Khamenei.ir, IRNA, Fars, Tasnim — the regime's voice |
| Israel & Military | IDF, Netanyahu, Haaretz, Jerusalem Post — Israeli perspective |
| US Government | State Dept, CENTCOM, White House, Trump — US policy signals |
| International Organizations | IAEA, NATO, UN — multilateral stance |
| Key Media (Wire & Global) | Reuters, AP, Bloomberg, NYT, Guardian — baseline narrative |
| Key Media (Regional) | Iran International, Al-Monitor, Bellingcat — specialist depth |
| OSINT & Prediction | Sentdefender, OSINT613, Polymarket — real-time ground truth |
| Think Tanks | Atlantic Council, Brookings, CFR — analytical framing |
| Activists & Opposition | Masih Alinejad, Reza Pahlavi, NCRI — diaspora/opposition voice |

**`/{topic}/entities`** — Full 700+ source directory. Params: `category`, `q` (search), `limit`

## Key dictionaries

**Event category:** `CONFLICT` · `DIPLOMACY` · `POLITICS` · `ECONOMY` · `PROTESTS`

**Event sentiment:** `NEGATIVE` · `POSITIVE` · `NEUTRAL` · `MIXED`

**source_type** (on posts): `news_agency` · `state_media` · `osint` · `gov_military` · `journalist` · `think_tank` · `other`

**News region:** `intl` · `us` · `mideast` · `israel` · `persian`

**Post platform:** `twitter` · `telegram`

## Entity relationships

```
Briefing → thread.signals[].id → Event ID → /posts?event={id} or /news?event={id}
Event → source_details[].entity_slug → /entities or /notable
Post → author_category → source_type mapping
Thread → polymarket_ref → /polymarket
```

**Key investigation paths:**

1. **Briefing → Thread → Event → Sources → Entity**: "This thread claims X" → check linked events → how many sources? → who are they? → what camp?
2. **Event → Posts/News**: use `/posts?event={id}` or `/news?event={id}` to find original content linked to a specific event
3. **Thread → Polymarket**: thread has polymarket_ref → check `/polymarket` → does market probability align with AI assessment?
4. **Weak evidence → Cross-reference**: claim has ○ weak evidence → check `/news` for mainstream coverage → check `/posts?source_type=osint` → if neither confirms, flag as unverified

## Key principle

**The briefing is the map. The other endpoints are the territory.** Don't dump all data on the user — use the briefing to identify what matters, investigate only what's relevant, and synthesize a judgment.

## Notes

- Data from iranmonitor.org (700+ sources), Polymarket CLOB API
- AI analysis hourly, data feeds every 5 minutes
- All responses are Markdown with Chinese translations where available
