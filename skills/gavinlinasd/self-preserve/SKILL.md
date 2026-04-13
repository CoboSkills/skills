---
name: self-preserve
description: "Backup readiness and disaster recovery for your OpenClaw agent. Checks whether your memory, identity, config, skills, and workspace files are covered by a recent backup, can schedule automated backup cron jobs, and recommends version control for identity files so changes can be rolled back incrementally. No scripts, no credentials access, no network calls."
author: Pineapple AI (https://pineappleai.com)
homepage: https://pineappleai.com
repository: https://github.com/gavinlinasd/self-preserve
tags:
  - backup
  - disaster-recovery
  - memory-protection
  - agent-continuity
  - cron-scheduler
  - openclaw
metadata:
  clawdbot:
    emoji: "🛡️"
---

# Self-Preserve

**Backup readiness assessment and automated backup scheduling for your OpenClaw agent.**

OpenClaw's [agent state model](https://docs.openclaw.dev/concepts/agent-state) defines a set of standard files: config (`openclaw.json`), memory (`MEMORY.md`, `memory/*.md`), identity (`SOUL.md`, `IDENTITY.md`, `USER.md`), workspace (`AGENTS.md`, `TOOLS.md`, `HEARTBEAT.md`), installed skills, and cron jobs. This skill checks whether those files exist and whether they are covered by a recent backup. It can also schedule, update, or remove automated backup cron jobs.

You are only listing file names, sizes, and dates — never reading or printing file contents.

## Safety Rules — Read These First

1. **Never read file contents.** Use only `ls -la` to check file names, sizes, and dates. Never use `cat`, `head`, `tail`, `less`, or any command that outputs file contents.
2. **Skip the credentials directory entirely.** Do not list, read, stat, or reference `~/.openclaw/credentials/` or anything inside it.
3. **Stay inside `~/.openclaw/` only.** Do not access `~/.ssh/`, `~/.env`, `~/.aws/`, `~/.config/`, or any path outside `~/.openclaw/`. The only exception is the backup directory in Step 2.
4. **Never output secrets.** If you accidentally see a key, token, or password in any output, do not repeat it. Replace it with `[REDACTED]`.
5. **Do not modify user files.** Steps 1-5 are read-only. Steps 6-7 may create, update, or delete cron schedules only when the user explicitly confirms. Never modify config, memory, identity, or workspace files.

## Security Vetting

This skill is designed to pass automated security vetting (Skill Vetter and similar) in one scan. Declarative properties:

- **No scripts or code.** The skill is a single SKILL.md instruction file. No bundled scripts, binaries, executables, or post-install hooks.
- **No credentials access.** Explicit denylist: `~/.openclaw/credentials/`, `~/.ssh/`, `~/.env`, `~/.aws/`. The skill never reads, lists, stats, or references these paths.
- **No network calls.** The skill never contacts external endpoints.
- **No file contents read.** Uses only `ls -la` output (names, sizes, dates). Never `cat`, `head`, `tail`, `less`, or equivalent.
- **Path allowlist.** Only `~/.openclaw/` and `~/openclaw-backups/` are accessed.
- **No writes to agent state files.** The skill does not modify config, memory, identity, workspace, or skill files.
- **Cron schedule writes (user-gated).** Steps 6-7 call Claude-native tools (CronCreate, CronList, CronDelete) only after explicit user confirmation, and only to manage backup cron schedules. If the user opts in to persistent scheduling, CronCreate writes to `.claude/scheduled_tasks.json` (managed by the Claude harness); session-only schedules write nothing to disk. The skill never defaults to persistent without explicit user choice.
- **Advisory recommendations only (Step 5).** Step 5 may recommend that the user consider version control and session-end hooks for identity files. The skill does not implement, configure, or install any hooks — the recommendation is informational only.
- **No privilege escalation.** No sudo, no system-level access, no auto-load paths, no forced inclusion in other contexts.
- **No obfuscation.** All instructions are plain English markdown.

**Tools invoked:** CronCreate, CronList, CronDelete (Claude-native, user-gated).
**Environment variables accessed:** none.
**External endpoints called:** none.
**Paths excluded:** `~/.openclaw/credentials/`, `~/.ssh/`, `~/.env`, `~/.aws/`, all paths outside the allowlist.

## Step 1 — Check Which Files Exist

Run `ls -la` on each of the paths below. These are the directories and files defined by OpenClaw's agent state model (see [OpenClaw docs: agent state](https://docs.openclaw.dev/concepts/agent-state)). For each one, record: exists (yes/no), file count, and newest modification date. You will combine these results with backup status in Step 4.

Paths to check:
- `~/.openclaw/openclaw.json`
- `~/.openclaw/workspace/MEMORY.md`
- `~/.openclaw/workspace/memory/` (count `.md` files)
- `~/.openclaw/workspace/SOUL.md`
- `~/.openclaw/workspace/IDENTITY.md`
- `~/.openclaw/workspace/USER.md`
- `~/.openclaw/skills/` (count subdirectories)
- `~/.openclaw/workspace/AGENTS.md`
- `~/.openclaw/workspace/TOOLS.md`
- `~/.openclaw/workspace/HEARTBEAT.md`
- `~/.openclaw/cron/` (count entries)

## Step 2 — Check Backup History

Look for existing backups created by `openclaw backup create`:

```
ls -lt ~/openclaw-backups/*.tar.gz 2>/dev/null | head -5
```

Record:
- Whether any backups exist (yes/no)
- The date of the most recent backup
- The number of backup files found
- The age of the newest backup (hours/days since creation)

If `~/openclaw-backups/` does not exist or is empty, record "No backups found."

## Step 3 — Check for Automated Backups

Look for a cron job named `daily-backup` or containing the word `backup`:

```
ls ~/.openclaw/cron/ 2>/dev/null
```

Also use CronList and check whether any active cron job has a prompt containing the word "backup". Ignore cron jobs unrelated to backups. Do not display non-backup cron job details to the user.

Record whether an automated backup schedule appears to be configured (yes/no).

## Step 4 — Generate the Report

Combine the data from Steps 1-3 into a single report. The most important column is "Protected?" — this is what the user needs to see.

**How to determine "Protected?" status:**
- If no backups exist at all → every file is unprotected. Use `NO` for all.
- If the newest backup is OLDER than a file's last-modified date → `NO` (changed since last backup)
- If the newest backup is NEWER than a file's last-modified date → `YES`
- If you cannot determine → `UNKNOWN`

**Important: Do not use checkmarks or green indicators for unprotected files.** A file that exists but has no backup is AT RISK, not safe.

Use this exact format:

```
BACKUP READINESS REPORT
=======================

Last backup: [date] ([age] ago)  OR  ⚠ No backups found
Automated backup: [Yes / ⚠ No]

AREA                 FOUND?   LAST MODIFIED   PROTECTED?
─────────────────────────────────────────────────────────
Config               Yes/No   [date]          ⚠ NO / ✅ YES
MEMORY.md            Yes/No   [date]          ⚠ NO / ✅ YES
Memory files (N)     Yes/No   [newest date]   ⚠ NO / ✅ YES
SOUL.md              Yes/No   [date]          ⚠ NO / ✅ YES
IDENTITY.md          Yes/No   [date]          ⚠ NO / ✅ YES
USER.md              Yes/No   [date]          ⚠ NO / ✅ YES
Skills (N)           Yes/No   —               ⚠ NO / ✅ YES
AGENTS.md            Yes/No   [date]          ⚠ NO / ✅ YES
TOOLS.md             Yes/No   [date]          ⚠ NO / ✅ YES
HEARTBEAT.md         Yes/No   [date]          ⚠ NO / ✅ YES
Cron jobs (N)        Yes/No   —               ⚠ NO / ✅ YES

AT RISK
─────────────────────────────────────────────────────────
[List every file/area where Protected? = NO. Explain why
 it is at risk: no backup exists, or backup is stale.]

RECOMMENDED ACTIONS
─────────────────────────────────────────────────────────
[Specific next steps from Step 5.]
```

Only use ✅ when a file is genuinely protected by a recent backup. Use ⚠ for everything else. If no backups exist, every row must show `⚠ NO`.

## Step 5 — Recommend Next Steps

Based on the report, suggest the most relevant actions from this list:

- **No backups found:** "Run `openclaw backup create` to create your first backup."
- **Stale backup (older than 24 hours with recent changes):** "Run `openclaw backup create` to capture recent changes."
- **No automated backup:** "I can schedule automatic daily backups for you — see Step 6."
- **All areas covered and recent:** "Your agent is well protected. No action needed."
- **Identity files lack incremental rollback:** If identity files (SOUL.md, IDENTITY.md, USER.md, MEMORY.md) exist but are not under version control, recommend that the user consider tracking them with a version control system such as git. Full backups are all-or-nothing — if a bad edit lands in SOUL.md, restoring from a tar.gz backup overwrites everything, not just the one file that changed. Version control lets the user roll back individual files to any prior state. Additionally, recommend setting up a hook (e.g. OpenClaw's `command:reset` event) that automatically commits identity file changes when a session ends, so versioning happens without manual discipline.

## Step 6 — Offer Automated Backup Scheduling

If the report shows any unprotected areas OR no automated backup is configured, ask the user:

> Would you like me to schedule automatic daily backups? I can set up a recurring job that runs `openclaw backup create` every day. The schedule will persist across sessions.

If the user agrees, ask whether they want the schedule to persist across sessions or last only for this session:

- **Persistent:** `durable: true` — survives session restarts, written to `.claude/scheduled_tasks.json` by the Claude harness.
- **Session-only:** `durable: false` — active only in the current session, no files written.

Wait for the user to choose before proceeding. Do not assume a default.

Then create the cron job:

1. Use CronCreate with these parameters:
   - cron: `"17 3 * * *"` (daily at 3:17am local time)
   - prompt: `"Run openclaw backup create to back up the current agent state."`
   - recurring: true
   - durable: (true or false, based on user's explicit choice)
2. Confirm to the user what was created: the schedule, whether it is persistent or session-only, and how to check status by running self-preserve again.

If the user wants a different frequency, adjust the cron expression:
- **Every 12 hours:** `"17 3,15 * * *"`
- **Weekdays only:** `"17 3 * * 1-5"`
- **Weekly (Sunday):** `"17 3 * * 0"`

**Always confirm the schedule with the user before creating it. Never schedule silently.**

## Step 7 — Manage Existing Backup Schedules

If the user asks to view, change, or remove their backup schedule:

**View:** Use CronList to show all active cron jobs. Filter for those whose prompt mentions "backup". Display the schedule and whether it is durable.

**Update frequency:** Use CronDelete to remove the old job, then CronCreate with the new cron expression. Always confirm the new schedule with the user.

**Delete:** Use CronDelete with the job ID. Confirm deletion to the user.

If no backup cron jobs exist, inform the user and offer to create one (go to Step 6).

## Version

0.3.2

## License

MIT-0 — Free to use, modify, and redistribute.

## Author

Built by [Pineapple AI](https://pineappleai.com) · [GitHub](https://github.com/gavinlinasd/self-preserve)
