---
name: count
version: "2.0.0"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
license: MIT-0
tags: [count, tool, utility]
description: "Count words, lines, and characters with frequency analysis tools. Use when counting frequencies, analyzing text length, aggregating file stats."
---

# Count

Count v2.0.0 — a versatile data toolkit for ingesting, transforming, querying, filtering, aggregating, and exporting structured data entries. Each command logs timestamped records locally, making Count ideal for lightweight data pipelines, tracking workflows, and auditing activity.

## Commands

| Command | Description |
|---------|-------------|
| `count ingest <input>` | Ingest a data entry (or view recent ingests with no args) |
| `count transform <input>` | Log a transform operation (or view recent transforms) |
| `count query <input>` | Record a query (or view recent queries) |
| `count filter <input>` | Record a filter operation (or view recent filters) |
| `count aggregate <input>` | Record an aggregation (or view recent aggregations) |
| `count visualize <input>` | Log a visualization task (or view recent visualizations) |
| `count export <input>` | Log an export entry (or view recent exports) |
| `count sample <input>` | Record a sampling operation (or view recent samples) |
| `count schema <input>` | Log a schema definition (or view recent schemas) |
| `count validate <input>` | Record a validation check (or view recent validations) |
| `count pipeline <input>` | Log a pipeline step (or view recent pipeline entries) |
| `count profile <input>` | Record a profiling run (or view recent profiles) |
| `count stats` | Show summary statistics across all log files |
| `count search <term>` | Search all entries for a keyword (case-insensitive) |
| `count recent` | Show the 20 most recent activity entries |
| `count status` | Health check — version, entry count, disk usage, last activity |
| `count help` | Display all available commands |
| `count version` | Print version string |

Each data command (ingest, transform, query, filter, aggregate, visualize, export, sample, schema, validate, pipeline, profile) works the same way:

- **With arguments:** saves a timestamped entry to `~/.local/share/count/<command>.log` and logs to `history.log`
- **Without arguments:** displays the 20 most recent entries from that command's log file

## Data Storage

All data is stored locally in `~/.local/share/count/`:

| File | Contents |
|------|----------|
| `ingest.log` | Timestamped ingest records |
| `transform.log` | Transform operation records |
| `query.log` | Query records |
| `filter.log` | Filter operation records |
| `aggregate.log` | Aggregation records |
| `visualize.log` | Visualization task records |
| `export.log` | Export entry records |
| `sample.log` | Sampling records |
| `schema.log` | Schema definition records |
| `validate.log` | Validation check records |
| `pipeline.log` | Pipeline step records |
| `profile.log` | Profiling records |
| `history.log` | Unified activity log for all commands |

The `stats` command reads all `.log` files and reports line counts per file, total entries, data directory size, and the timestamp of the first recorded activity.

The `export` utility function (called internally via `_export`) can produce **JSON**, **CSV**, or **TXT** output files under the data directory.

## Requirements

- **Bash** (4.0+)
- **coreutils** — `date`, `wc`, `du`, `head`, `tail`, `grep`, `basename`, `cat`
- No external dependencies, API keys, or network access required
- Works on Linux and macOS

## When to Use

1. **Tracking data pipeline steps** — use `ingest`, `transform`, `filter`, `aggregate`, and `export` to log each stage of a data workflow with timestamps for auditing
2. **Lightweight activity journaling** — record queries, validations, or schema changes over time without setting up a database
3. **Profiling and sampling logs** — use `profile` and `sample` to keep a running record of profiling and sampling activities across projects
4. **Searching historical entries** — use `search <term>` to grep across all logged data for a specific keyword or pattern
5. **Quick health checks and statistics** — run `status` for a system overview or `stats` for a detailed breakdown of entries per command category

## Examples

```bash
# Ingest a new data point
count ingest "user_signups 2024-03-15 count=142"

# View recent ingest entries
count ingest

# Record a transform step
count transform "normalize email addresses to lowercase"

# Filter and log the operation
count filter "remove records where age < 18"

# Aggregate results
count aggregate "sum revenue by region Q1-2024"

# Search across all logs for a keyword
count search "revenue"

# View summary statistics
count stats

# Check system health
count status

# View the 20 most recent activities across all commands
count recent
```

## How It Works

Count uses a simple append-only log architecture. Every command writes a pipe-delimited record (`timestamp|value`) to its dedicated log file. The `history.log` file captures a unified timeline of all operations with the format `MM-DD HH:MM command: value`.

This design makes Count:
- **Fast** — pure bash, no database overhead
- **Transparent** — all data is human-readable plain text
- **Portable** — works anywhere bash runs, no install needed
- **Auditable** — every action is timestamped and traceable

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
