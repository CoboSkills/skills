---
name: eastmoney-roadshow-transcript-summary
description: EastMoney Roadshow Digest (Transcript + Summary)｜东方财富路演纪要生成. A reliability-first transcript & summary skill for public EastMoney roadshow replays, focused on validated public replay URLs and bounded transcript generation with summary outputs.
---

# EastMoney Roadshow Digest (Transcript + Summary)｜东方财富路演纪要生成

## Purpose | 用途

Create a clean, reliability-first workflow for **public EastMoney roadshow replay pages only**.

仅处理**公开可访问的东方财富路演回放页**，不依赖本地 cookie、私有接口凭据或用户路径，强调执行可控与结果留痕。

## Input | 输入

- `url: string`
- Must match `https://roadshow.eastmoney.com/luyan/<id>`

## Output | 输出

Write these files under `outputs/`:
- `meta.json`
- `transcript.md`
- `clean_transcript.md`
- `summary.md`
- `brief.md`
- `run_report.md`

Page parsing succeeds → always write `meta.json`.
Any downstream failure or downgrade → still write `run_report.md`.

## Workflow | 工作流

1. Validate URL
2. Parse page and fetch public metadata
3. Prefer subtitle candidates if available
4. Discover replay media and run ASR fallback if needed
5. Clean transcript
6. Generate summary
7. Generate executive brief
8. Always write run report

## Role boundaries | 模块边界

- `providers/eastmoney.py`: validate URL, parse page, fetch public metadata, discover subtitle/media candidates only
- `providers/asr.py`: convert audio to text only
- `main.py`: orchestration, file writing, cleaning, summary generation, reporting

## Reliability notes | 可靠性说明

- If subtitle is absent, attempt media+ASR fallback
- If ASR dependencies are missing, degrade gracefully and explain in `run_report.md`
- If page parsing succeeds, still write `meta.json` even when downstream steps fail
- Keep outputs deterministic and conservative; do not invent facts
- Keep `README.md`, `SKILL.md`, and `manifest.json` aligned on scope, inputs, outputs, and dependency expectations

## Practical guidance | 实操说明

- Use replay metadata from the public detail API
- Preserve source path in `meta.json`
- Prefer concise summaries grounded in extracted text
- If transcript quality is low, say so explicitly in `run_report.md`

## Dependencies | 依赖

- Python 3.9+
- `requests` required
- `faster-whisper` optional but recommended for ASR fallback
- `ffmpeg` required on PATH for audio extraction / ASR fallback

## Description | 描述

EastMoney Roadshow Digest (Transcript + Summary) is a reliability-first skill for turning public 东方财富路演回放页面 into structured transcript, clean transcript, summary, brief, and run report outputs.

本技能定位为：面向公开东方财富路演回放页的、以稳定性优先的纪要生成工具，可输出 transcript、clean transcript、summary、brief 与 run report。

## Non-goals | 非目标

- Do not handle private/live-only rooms
- Do not log in
- Do not require browser cookies
- Do not publish automatically
