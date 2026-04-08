---
name: nba_games
description: Gets upcoming and/or recent NBA game results for a specified team. Use this skill when asked about scheduled, upcoming, or past games for any NBA team.
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---
# NBA Games Skill

Fetch NBA schedule and results for a team using the ESPN API.

## Script
<!-- Setup: get the python program from https://github.com/highdeserthacker/nba-schedule -->

```
/home/node/python/nba-schedule/nba-schedule.py
```

> Note: `/home/node/python` is a bind-mounted host directory. Replace with the actual container path once the mount is configured.

## Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--team-id <id>` | Yes | - | ESPN team ID |
| `--days-future <n>` | No | 3 | Upcoming days to include (0 = none) |
| `--days-past <n>` | No | 0 | Past days to include (0 = none) |

## Team ID Lookup

If the team ID is unknown, run:
```bash
python3 /home/node/python/nba-schedule/nba-schedule.py --list
```
This prints all 30 teams with their IDs. Common IDs: Golden State Warriors = 9.

## Usage Examples

```bash
# Next 3 upcoming Warriors games (default)
python3 /home/node/python/nba-schedule/nba-schedule.py --team-id 9

# Warriors games in the next 2 days only
python3 /home/node/python/nba-schedule/nba-schedule.py --team-id 9 --days-future 2

# Warriors games in the next 2 days plus yesterday's result
python3 /home/node/python/nba-schedule/nba-schedule.py --team-id 9 --days-future 2 --days-past 1

# Lakers: next 5 days
python3 /home/node/python/nba-schedule/nba-schedule.py --team-id 13 --days-future 5
```

## Output Format

Returns a JSON array of game objects sorted by date ascending. Empty array `[]` means no games in the requested window.

```json
[
  {
    "team":     "Golden State Warriors",
    "opponent": "Los Angeles Lakers",
    "location": "home",
    "datetime": "Fri Mar 28, 7:30 PM PDT",
    "result":   ""
  }
]
```

| Field | Description |
|---|---|
| `team` | Full display name of the requested team |
| `opponent` | Full display name of the opposing team |
| `location` | `"home"` or `"away"` |
| `datetime` | Game time in the container's local timezone |
| `result` | Empty string for upcoming games; score string for completed games (e.g. `"Golden State Warriors (W) 112, Los Angeles Lakers 98"`) |

## Presentation Guidelines

- For **upcoming games**: state opponent, home/away, and tip-off date/time.
- For **completed games**: state opponent, final score, and win/loss.
- If the result array is empty, no games fall in the requested window - do not fabricate or guess.
- Present results conversationally unless the caller context requires structured output.

## Trigger Examples

- "When is the next Warriors game?"
- "Did the Bulls win last night?"
- "Show me the Lakers schedule for the next week."
- "What are the upcoming Celtics games?"
