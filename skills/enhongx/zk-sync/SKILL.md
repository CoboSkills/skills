---
name: zk-sync
description: Sync saved knowledge item to NotebookLM after Feishu save succeeds.
---

# zk-sync

Use this skill only after a knowledge item has been successfully saved and a valid ID is available.

## Inputs
- id
- title_b64
- content_b64

## Action
Run:

```bash
~/.openclaw/skills/zk-sync/run.sh "<id>" "<title_b64>" "<content_b64>"
```
## Expected output

A JSON result:

- `ok=true, status=synced`
- `ok=false, status=failed`

## Rules

- Never call before Feishu save succeeds
- Always use absolute paths
- Never assume sync succeeded without reading the script output