---
name: sniplink
description: OpenClaw skill. One-shot URL saver for tools and services discovered on X, GitHub, or anywhere. Drop a link, get it categorized, tagged, and stored — no friction, no multi-step forms. Built for ADHD brains and anyone who keeps losing track of tools they saved across bookmarks, notes, and chats.
---

# SnipLink — The ADHD-Friendly URL Saver

## Who It's For

You found something cool. You want it saved **now** — before you forget, before you lose the tab, before the momentum dies.

SnipLink saves it instantly: title, description, category, tags, social links. Done in seconds. No multi-step forms, no "where should I put this" paralysis.

## Trigger
Use this skill when:
1. User shares a URL and wants it saved — "save this", "remember this", "add to my stash"
2. User asks "what tools do I have for X" or wants to search their saved links
3. User is brainstorming and needs quick tool suggestions by tag or category

> **Zero friction.** One URL in, clean record out. Confirm once, forget about it.

## Workflow

### 1. Saving a Link (One-Shot)

**Step 1: Detect source type**
- **GitHub.com repo URL** → use `gh api` (structured data, no scraping)
- **All other URLs** → use `web_fetch`

**Step 2: Extract info**

For GitHub repos, extract:
- Repo name, description, primary language, star count, license, topics/tags, last updated, owner

For all other pages:
- `web_fetch` → title, meta description, pricing, features
- Skip if behind login, paywall, or CAPTCHA

**Step 3: Auto-categorize**
- **AI/ML** — AI services, LLMs, machine learning
- **Development** — Coding tools, APIs, frameworks, testing
- **Productivity** — Task management, notes, workflow automation
- **Marketing** — SEO, social media, ads, content
- **Design** — Graphics, UI/UX, video, prototyping
- **Finance** — Billing, accounting, payments
- **Communication** — Messaging, email, calls, CRM
- **Data** — Analytics, databases, visualization
- **Other** — Anything else

**Step 4: Auto-generate tags**
- Extract from description, GitHub topics, or page keywords
- Common: free, paid, api, no-code, open-source, mobile, cloud, etc.

**Step 5: Social media lookup**
- `web_search` tool name + "LinkedIn" / "Twitter"
- Store URLs if found

**Step 6: Confirm and save**
- Present one-line summary: "Saved: [title] ([category])"
- Save to database after confirmation

### 2. Retrieving Saved Links

- By category: "Show me all AI tools"
- By search: "Find something for PDF editing"
- By tag: "Show me everything tagged free"
- Full list: "List all my saved tools"

### 3. Tool Suggestions (Opt-In)

When user asks for project help, search by relevant tags/categories and suggest.

## GitHub Integration

GitHub URLs get treated specially via `gh api`:

```bash
# Repo metadata example
gh api repos/{owner}/{repo}
```

Extracted fields: name, description, language, stargazers_count, topics, license, updated_at, homepage, html_url

No web scraping needed for GitHub — clean, fast, accurate.

## Content Boundaries

**Never scrape:**
- Pages behind login, paywall, or CAPTCHA
- Pages blocked by robots.txt
- URLs containing personal data (iCloud, Google Drive shared links, etc.)

**Sanitization:**
- Strip tracking params from URLs before saving (utm_*, fbclid, etc.)
- Never store OAuth tokens, API keys, or session IDs

## Database Location

`/workspace/skills/sniplink/references/database.json`

## Record Format

```json
{
  "tools": [
    {
      "url": "https://example.com",
      "title": "Tool Name",
      "description": "What it does",
      "category": "Development",
      "tags": ["python", "api", "free"],
      "use_case": "For building APIs",
      "notes": "Good alternatives to X",
      "saved_date": "2026-04-04",
      "price": "Free / $X/mo",
      "social_media": {
        "linkedin": "...",
        "twitter": "..."
      },
      "contact": {
        "email": "..."
      }
    }
  ]
}
```
