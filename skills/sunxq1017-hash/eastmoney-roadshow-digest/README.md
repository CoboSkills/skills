# EastMoney Roadshow Digest (Transcript + Summary)｜东方财富路演纪要生成

> A reliability-first transcript & summary skill for public EastMoney roadshow replays.

Draft-only skill project for **public EastMoney roadshow replay pages only**.

EastMoney Roadshow Digest (Transcript + Summary) is a reliability-first skill for turning public 东方财富路演回放页面 into structured transcript, clean transcript, summary, brief, and run report outputs.

本技能定位为：面向公开东方财富路演回放页的、以稳定性优先的纪要生成工具，可输出 transcript、clean transcript、summary、brief 与 run report。

## Scope
- Supports only public URLs like `https://roadshow.eastmoney.com/luyan/5149204`
- Validates URL before parsing
- Prefers subtitle discovery first
- Falls back to public replay media discovery + ASR
- Always writes `outputs/run_report.md`
- Writes `outputs/meta.json` whenever page parsing succeeds
- Does **not** require cookies, private credentials, or user-specific paths

## Outputs
- `outputs/meta.json`
- `outputs/transcript.md`
- `outputs/clean_transcript.md`
- `outputs/summary.md`
- `outputs/brief.md`
- `outputs/run_report.md`

## Files
- `SKILL.md` — bilingual skill instructions
- `manifest.json` — project manifest
- `main.py` — orchestration pipeline
- `providers/eastmoney.py` — URL validation, page parsing, subtitle/media discovery only
- `providers/asr.py` — audio extraction + speech-to-text only
- `templates/` — lightweight prompt/reference templates
- `outputs/` — runtime outputs

## Dependencies
Python dependencies are declared in `requirements.txt`.

Runtime notes:
- `requests` is required
- `faster-whisper` is optional but recommended for ASR fallback
- `ffmpeg` must be available on PATH for audio extraction / ASR fallback

Install Python dependencies:
```bash
python3 -m pip install -r requirements.txt
```

Install ffmpeg separately (examples):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get install ffmpeg`

## Run
```bash
python3 main.py --url https://roadshow.eastmoney.com/luyan/5149204
```

## Notes
- If subtitle content is not publicly exposed, the workflow degrades to media discovery + ASR.
- If ASR dependencies are unavailable, the workflow still completes and explains the downgrade in `outputs/run_report.md`.
- The skill is scoped to currently validated public replay pages and does not claim support for private rooms, logged-in experiences, or arbitrary video sources.

## Changelog
### v0.1.0-draft
- Finalized release packaging title and positioning
- Aligned README / SKILL / manifest wording
- Added dependency declaration via `requirements.txt`
- Added bounded, segmented ASR flow for controllable execution
- Verified clean-environment install and end-to-end run completion
- Kept the package in a ready-to-publish state without actually publishing
