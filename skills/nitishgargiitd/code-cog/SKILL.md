---
name: code-cog
description: "The first coding agent designed for agents, not just humans. Code generation, debugging, refactoring, codebase exploration, terminal operations — directly on your machine via CellCog Desktop. Use for coding, development workflows, or any task requiring direct machine access. Outputs: code files. Powered by CellCog."
metadata:
  openclaw:
    emoji: "💻"
    os: [darwin, linux]
author: CellCog
homepage: https://cellcog.ai
dependencies: [cellcog]
---

# Code Cog - The First Coding Agent Designed for Agents

A coding sub-agent that works directly on your machine — understands the codebase, plans changes, and iterates until the code works.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls, plus CellCog Desktop (Co-work) for machine access.

```bash
clawhub install cellcog
clawhub install cowork-cog  # Setup guide for CellCog Desktop
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**OpenClaw agents (fire-and-forget — recommended for long tasks):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    notify_session_key="agent:main:main",
    task_label="my-task",
    chat_mode="agent core",  # Lightweight context for coding
    enable_cowork=True,
    cowork_working_directory="/path/to/project",
)
```

**All other agents (blocks until done):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    task_label="my-task",
    chat_mode="agent core",
    enable_cowork=True,
    cowork_working_directory="/path/to/project",
)
```

See the **cellcog** mothership skill for complete SDK API reference.

---

## What CellCog Has Internally

1. **Direct Machine Access** — Terminal commands and file operations executed on the user's actual machine via CellCog Desktop bridge.
2. **Codebase Understanding** — Reads project structure, AGENTS.md/README.md, and explores files before making changes.
3. **Iterative Execution** — Plans multi-file changes, executes, tests, and self-corrects through agent threads.
4. **Multimedia On-Demand** — Starts lightweight for coding, loads image/video/audio tools only when needed.

---

## What You Can Do

- Code generation and implementation
- Bug debugging and fixing
- Code refactoring and optimization
- Codebase exploration and documentation
- Terminal operations (build, test, deploy)
- Multi-file changes across a project
- Development workflow automation

---

## Requirements

- **CellCog Desktop** must be installed and connected (see `cowork-cog` for setup)
- **Chat mode**: `"agent core"` (lightweight, coding-optimized)
- **Co-work enabled**: `enable_cowork=True` with `cowork_working_directory`

---

## Related Skills

- **cowork-cog** — Setup guide for CellCog Desktop
- **project-cog** — Knowledge workspaces for project context
