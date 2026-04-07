# self-preserve

Backup readiness and disaster recovery for your OpenClaw agent. Makes sure you don't lose memory, identity, or configuration when your agent crashes or a risky operation goes wrong.

## Install

```bash
npx clawhub@latest install self-preserve
```

## What it does

Self-preserve checks whether your OpenClaw agent's standard state files (config, memory, identity, skills, workspace, cron) are covered by a recent backup. It runs `ls` to check file names and dates, then generates a readiness report showing what's protected and what's at risk.

**New in v0.3.0:** After the assessment, self-preserve can schedule automated backup cron jobs using CronCreate (persistent or session-only). It can also view, update, or remove existing backup schedules using CronList and CronDelete.

It does not read file contents or access credentials. See [SKILL.md](./SKILL.md) for the full assessment steps, safety rules, and scheduling options.

## Positioning

If you use [self-improving-agent](https://clawhub.ai/skills/self-improving-agent) to let your agent learn from its mistakes, self-preserve is the preventive companion: it makes sure you still have a memory to learn with when something goes wrong. These are independent skills — self-preserve has no runtime dependency on self-improving-agent and does not install it.

## License

MIT-0
