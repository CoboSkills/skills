# NBA Today Pulse v11

Version: `1.0.11`

`nba-today-pulse-v11` packages the latest `NBA_TR` skill-only runtime into a public ClawHub bundle with compact mixed-status day view, same-day stat leaders, dedicated pregame/live/post routes, independent injury reports, and timezone-aware local-date routing. This `1.0.11` release keeps the compact day/live output, adds the day fast path, hardens refresh-friendly follow-up handling, and expands bilingual player alias coverage without changing the public skill identity.

This release keeps the stable public skill key `nba-today-pulse` rather than registering a new skill identity.

## What Changed in 1.0.11

`1.0.11` is still a compact release rather than a layout rewrite. It carries forward the `1.0.10` runtime and adds the newer routing and response-path improvements underneath it:

- `day` now prefers a fast path that parallelizes `scoreboard + summary` and keeps short-lived day cache reuse hot
- short follow-ups like `更新`, `刷新`, `只看关键球员`, `只看回合摘要`, and `只看第四节` now stay anchored to the same single-game context instead of falling back to a generic day slate
- generic pregame prompts without explicit teams route into the pregame collection instead of drifting toward `day`
- player alias coverage has been widened so common Chinese and English nicknames resolve to the same canonical player identity

What stayed the same:

- `day` cards remain compact, with at most 3 player lines per team in live cards and no repeated play-line spam
- `live` cards remain compact, with 3-player key stat cards and no season-average repetition
- the public skill key is still `nba-today-pulse`

## Highlights

- Mixed-status `dayView` that can show upcoming, live, and final games in one response
- Compact live cards: ≤3 player lines per team, no duplicate team-total row, no repeated play line
- Compact `stats_day` cards for requests such as `today's NBA stats`, `who scored the most today`, and `today's best performance`
- Dedicated `pregame`, `live`, and `post` routing instead of a single generic game scene
- Live key-player section: 3 players per team in concise PTS/REB/AST/STL/BLK + shooting format
- Live score refresh that updates explicit `AWAY @ HOME` scoreboard output from bundled `nba_live` data when ESPN lags
- More natural `post` recaps that use real play-by-play sequences for flow and turning-point summaries
- Cleaner Chinese and English default rendering, including locale-aware Chinese team names and compact final-game cards
- Review-clean public bundle behavior: in-memory caching only, outbound HTTP and remote PDF scope documented, no credentials, no private paths, no internal memory-file references

## Bundle Layout

```text
nba-today-pulse-v11/
  README.md
  SKILL.md
  TOOLS.md
  tools/
    cache_store.py
    entity_guard.py
    nba_advanced_report.py
    nba_common.py
    nba_day_snapshot.py
    nba_game_full_stats.py
    nba_game_live_context.py
    nba_game_locator.py
    nba_game_preview_context.py
    nba_game_recap_context.py
    nba_game_rosters.py
    nba_head_to_head.py
    nba_play_digest.py
    nba_player_names.py
    nba_pulse_core.py
    nba_pulse_router.py
    nba_team_form_snapshot.py
    nba_team_injury_report.py
    nba_team_roster.py
    nba_teams.py
    nba_today_command.py
    nba_today_report.py
    provider_espn.py
    provider_nba.py
    provider_nba_injuries.py
    timezone_resolver.py
    vendor_pdf_text.py
    verify_nba_tr.py
```

## Installation

This bundle is intended for ClawHub publishing and OpenClaw installation as a self-contained natural-language skill.

At runtime, the public entrypoint is:

```bash
python3 {baseDir}/tools/nba_today_command.py --command "<raw request>"
```

Known-timezone production paths should inject `--tz` explicitly:

```bash
python3 {baseDir}/tools/nba_today_command.py --command "<raw request>" --tz "<resolved timezone>"
```

## Runtime Requirements

- `python3`
- outbound network access to ESPN public JSON endpoints
- outbound network access to NBA.com public endpoints used for live, stats, and injury-report fallbacks
- outbound access to official NBA injury-report PDFs for supported injury-report requests
- remote PDF parsing for the downloaded official injury-report documents

No credentials are required. The bundle only uses public data sources.

Optional timezone environment variables:

- `OPENCLAW_USER_TIMEZONE`
- `OPENCLAW_TIMEZONE`
- `USER_TIMEZONE`
- `TZ`

Notes:

- these are optional runtime/configuration knobs, not secrets
- the public bundle keeps cache behavior in memory only
- the public bundle does not expose cache-specific environment variables
- outbound HTTP requests are limited to public NBA/ESPN data and official NBA injury-report documents required for the supported features

## Supported Request Shapes

- Daily NBA status
- Day-level NBA stats for the resolved local date
- Single-game preview and prediction
- Multi-matchup preview and all-games preview
- Single-game live momentum and current state
- Single-game postgame recap
- Team or matchup injury report

## Example Prompts

- `Show today's NBA games in America/Los_Angeles`
- `Show today's NBA stats in Asia/Shanghai`
- `Who scored the most today in Asia/Shanghai?`
- `Preview tomorrow's Celtics vs Hornets game in Asia/Shanghai`
- `Show today's Lakers live game flow in Asia/Shanghai`
- `Recap today's Knicks vs Thunder game in Asia/Shanghai`
- `Show tomorrow's Pistons injury report in Asia/Shanghai`
- `今日NBA赛况，按上海时区`
- `明天NBA赛况，按上海时区`
- `今天比赛谁得分最高，按上海时区`
- `复盘今天尼克斯vs雷霆，按上海时区`

## Packaging Notes

- This public bundle remains skill-only and does not expose a plugin command surface
- All runtime scripts are self-contained and resolve imports from the local `tools/` directory
- `stats_day` is day-level only: it summarizes completed games for the resolved local date and is not a season leaderboard
- live-score corrections are performed only through bundled ESPN/NBA providers; the public bundle must not estimate scores from boxscore fragments or improvise them in the skill layer
- postgame turning points are derived from bundled play-by-play or structured fallbacks; the public bundle must not fabricate recap logic outside the tool chain
- day-level routing now prefers the fast path when the request is a mixed-status slate, while single-game follow-ups still stay on their original matchup context
- The public bundle contains no private deployment paths, host addresses, SSH commands, or internal memory-file references
- The public bundle does not request or require credentials, secrets, or host-specific API keys
