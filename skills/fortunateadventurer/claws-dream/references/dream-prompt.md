# Nightly Dream — Memory Consolidation Prompt

Detect user's preferred language. All output in that language.
Working directory: the workspace root.

## Step 0: Smart Skip

```bash
ls memory/????-??-??.md 2>/dev/null | head -10
```

Check each file's end for `<!-- consolidated -->`. If all processed or no files → go to Step 0-B.

## Step 0-B: Skip With Value

Even when skipping, send a useful message:
- Read memory/dream-log.md → count past dreams (streak)
- Scan MEMORY.md for oldest uncompleted Open Thread
- Surface one old memory

```
🌙 No new content — skipped

💭 From {N} days ago: {one-line memory}
📈 Memory: {total} entries · Health {score}/100 · Streak: {N} dreams
```

END. Do not proceed.

## Step 0.5: Snapshot BEFORE

```bash
wc -l MEMORY.md
grep -c "^## " MEMORY.md
grep "^### " memory/index.json 2>/dev/null | wc -l
```

Read memory/index.json to get current stats.

## Step 1: Collect

Read all unconsolidated daily logs (last 7 days). Extract:
- Decisions (choices, direction changes)
- Key facts (metrics, technical details)
- Progress (milestones, blockers)
- Lessons (failures, wins)
- Todos (unfinished items)

## Step 2: Consolidate

Read MEMORY.md. For each extracted item:
- **New** → append to right section
- **Updated** → update in place
- **Duplicate** → skip (semantic dedup)
- **Procedures** → append to memory/procedures.md

Update `index.json` with new entries. Mark processed logs with `<!-- consolidated -->`.

## Step 2.5: Compute Health Score

Read references/scoring.md for algorithm. Calculate:
- freshness, coverage, coherence, efficiency, reachability
- Combine into 0-100 health score

Update memory/index.json with new stats and healthHistory entry.

## Step 2.8: Stale Detection

Scan Open Threads for items not marked [x]. Flag items stale >14 days. Top 3 for notification.

## Step 3: Generate Report

Append to memory/dream-log.md:

```markdown
## 🌙 Dream #{N} — YYYY-MM-DD

**Scanned**: {N} files | **New**: {N} | **Updated**: {N} | **Total**: {N} entries

### Changes
- [New/Updated] Describe each change

### Insights
- 1-2 cross-memory observations

### Health
- Score: {X}/100
- Freshness: {X}% | Coverage: {X}% | Coherence: {X}% | Efficiency: {X}% | Reachability: {X}%

### Stale Threads
- {item} — stale for {N} days

### Suggestions
- Actionable suggestions
```

## Step 4: Notify

Check milestones:
- DREAM_COUNT == 1 → "🎉 First dream!"
- DREAM_COUNT == 7 → "🏅 Week streak!"
- DREAM_COUNT == 30 → "🏆 Month streak!"
- Entries cross 100/200/500 → "📊 {N} entries!"

Is today Sunday? Add weekly summary.

```
🌙 Dream #{N} complete

📥 Today: +{NEW} new, ~{UPDATED} updated
📈 Total: {BEFORE} → {AFTER} ({percent}%)
   Running for {N} days

🧠 Highlights:
   • {change_1}
   • {change_2}
   (max 3-5)

🔮 Insight: {one valuable observation}

⏳ Stale: {item} ({N} days), {item} ({N} days)

{milestone if any}

💬 Let me know if anything was missed
```

## Safety Rules
- Never delete daily logs (mark only)
- Never remove ⚠️ PERMANENT items
- If MEMORY.md changes >30% → save .bak first
- Scope: only memory/ directory and MEMORY.md
