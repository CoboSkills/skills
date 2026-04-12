#!/usr/bin/env python3
"""
Generate meeting mindmap from minutes markdown using ClawHub mindmap engine (safe mode).

Safe-mode constraints:
- Allow formats: html, svg, xmind only
- Block png/jpg/pdf paths that may trigger Pillow auto-install logic
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ALLOWED_FORMATS = {"html", "svg", "xmind"}
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
SKILL_SLUG = SKILL_ROOT.name
WORKSPACE_ROOT = SKILL_ROOT.parent.parent if SKILL_ROOT.parent.name == "skills" else SKILL_ROOT.parent
DEFAULT_OUTPUT_DIR = WORKSPACE_ROOT / f"{SKILL_SLUG}-data"
PUBLIC_OUTPUT_DIR = Path.home() / "clawdhome_shared" / "public" / f"{SKILL_SLUG}-data"
VAULT_OUTPUT_DIR = Path.home() / "clawdhome_shared" / "vault" / f"{SKILL_SLUG}-data"


def ts_now() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_name(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s.strip())
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "meeting"


def section(text: str, heading: str) -> str:
    pat = rf"(?:^|\n)##\s*{re.escape(heading)}\s*\n(.*?)(?=\n##\s+|\Z)"
    m = re.search(pat, text, flags=re.S)
    return m.group(1).strip() if m else ""


def numbered_items(sec: str) -> list[str]:
    out = []
    for ln in sec.splitlines():
        m = re.match(r"^\s*\d+\.\s*(.+?)\s*$", ln)
        if m:
            out.append(m.group(1))
    return out


def bullet_items(sec: str) -> list[str]:
    out = []
    for ln in sec.splitlines():
        m = re.match(r"^\s*[-*]\s*(.+?)\s*$", ln)
        if m:
            out.append(m.group(1))
    return out


def action_items(sec: str) -> list[str]:
    rows = [ln.strip() for ln in sec.splitlines() if ln.strip().startswith("|")]
    out: list[str] = []
    if len(rows) < 3:
        return out
    for row in rows[2:]:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) < 4:
            continue
        task, owner, due, _note = cols[:4]
        if not any([task, owner, due]):
            continue
        out.append(f"{task}（{owner} / {due}）")
    return out


def infer_topic(minutes_text: str, fallback: str) -> str:
    for ln in minutes_text.splitlines():
        m = re.match(r"^\s*#\s*(.+?)\s*$", ln)
        if m:
            return m.group(1).strip()
    return fallback


def build_mindmap_data(minutes_text: str, topic: str) -> dict:
    decisions = numbered_items(section(minutes_text, "核心决议清单"))[:6]
    actions = action_items(section(minutes_text, "Action Items"))[:8]
    risks = bullet_items(section(minutes_text, "风险提示"))[:6]
    agenda = bullet_items(section(minutes_text, "议题重构 (Double Diamond)"))[:6]

    branches = []
    if decisions:
        branches.append({"label": "✅ 核心决议", "color": "#27AE60", "children": decisions})
    if actions:
        branches.append({"label": "📌 待办事项", "color": "#4A90D9", "children": actions})
    if risks:
        branches.append({"label": "⚠️ 风险提示", "color": "#E67E22", "children": risks})
    if agenda:
        branches.append({"label": "🧭 议题脉络", "color": "#9B59B6", "children": agenda})

    if not branches:
        branches = [
            {"label": "📄 会议文本", "color": "#4A90D9", "children": [minutes_text[:120] + ("..." if len(minutes_text) > 120 else "")]}
        ]

    return {"central": topic, "branches": branches}


def run_vendor(vendor_py: Path, title: str, out_path: Path, fmt: str, data_obj: dict) -> None:
    data = json.dumps(data_obj, ensure_ascii=False)
    cmd = [
        sys.executable,
        str(vendor_py),
        "--title",
        title,
        "--format",
        fmt,
        "--output",
        str(out_path),
        "--data",
        data,
    ]
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or "vendor mindmap failed").strip())


def is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test = path / ".write_test"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def resolve_output_dir(user_outdir: str | None = None) -> Path:
    candidates: list[Path] = []
    candidates.append(PUBLIC_OUTPUT_DIR.expanduser().resolve())
    candidates.append(VAULT_OUTPUT_DIR.expanduser().resolve())
    if user_outdir:
        candidates.append(Path(user_outdir).expanduser().resolve())
    env_out = os.getenv("MEETING_OUTPUT_DIR")
    if env_out:
        candidates.append(Path(env_out).expanduser().resolve())
    candidates.append(DEFAULT_OUTPUT_DIR)
    candidates.append(Path.cwd() / f"{SKILL_SLUG}-data")

    for c in candidates:
        if is_writable_dir(c):
            return c
    raise RuntimeError("no writable output directory found")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", required=True, help="Meeting minutes markdown/txt file")
    ap.add_argument("--topic", default=None, help="Mindmap central topic; auto-infer if omitted")
    ap.add_argument("--outdir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory (fixed to skill outputs)")
    ap.add_argument("--formats", default="html,xmind", help="Comma-separated: html,svg,xmind")
    args = ap.parse_args()

    minutes = Path(args.minutes).expanduser().resolve()
    if not minutes.exists():
        print(f"Error: minutes file not found: {minutes}", file=sys.stderr)
        return 1

    vendor_py = Path(__file__).resolve().parent / "vendor" / "generate_mindmap_clawhub.py"
    if not vendor_py.exists():
        print(f"Error: vendor engine missing: {vendor_py}", file=sys.stderr)
        return 1

    requested = [x.strip().lower() for x in args.formats.split(",") if x.strip()]
    invalid = [x for x in requested if x not in ALLOWED_FORMATS]
    if invalid:
        print(f"Error: unsupported formats in safe mode: {invalid}. Allowed: {sorted(ALLOWED_FORMATS)}", file=sys.stderr)
        return 1
    if not requested:
        requested = ["html", "xmind"]

    text = minutes.read_text(encoding="utf-8")
    topic = args.topic or infer_topic(text, "会议纪要导图")
    topic = topic.strip() or "会议纪要导图"
    data_obj = build_mindmap_data(text, topic)

    outdir = resolve_output_dir(args.outdir)
    print(f"output_dir={outdir}")
    prefix = f"{safe_name(topic)}-{ts_now()}"

    data_out = outdir / f"{prefix}.mindmap.json"
    data_out.write_text(json.dumps(data_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"data={data_out}")

    for fmt in requested:
        out_path = outdir / f"{prefix}.{fmt}"
        run_vendor(vendor_py, topic, out_path, fmt, data_obj)
        print(f"{fmt}={out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
