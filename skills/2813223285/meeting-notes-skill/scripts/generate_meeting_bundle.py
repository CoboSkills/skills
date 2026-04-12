#!/usr/bin/env python3
"""
Generate a complete meeting bundle from text minutes:
- structured minutes doc
- spoken script
- brief audio (mp3)
- full-text audio (mp3)
- mindmap (.mindmap.json/.html/.xmind)

Fails fast if any required artifact is missing.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def parse_kv_lines(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for ln in text.splitlines():
        if "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def ensure_file(path_str: str | None, label: str) -> Path:
    if not path_str:
        raise RuntimeError(f"missing {label} in script output")
    p = Path(path_str).expanduser().resolve()
    if not p.exists() or p.stat().st_size <= 0:
        raise RuntimeError(f"{label} missing: {p}")
    return p


def publish_quick_access(paths: dict[str, Path]) -> dict[str, Path]:
    """
    Copy generated files to shared public root so users can open them directly
    without entering subdirectories.
    """
    public_root = Path.home() / "clawdhome_shared" / "public"
    out: dict[str, Path] = {}
    try:
        public_root.mkdir(parents=True, exist_ok=True)
    except Exception:
        return out

    for k, src in paths.items():
        dst = public_root / src.name
        try:
            shutil.copy2(src, dst)
            out[k] = dst
        except Exception:
            # Best-effort shortcut publishing; keep primary artifacts unchanged.
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Text minutes file")
    ap.add_argument("--topic", required=True, help="Meeting topic")
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    bridge = script_dir / "audio_bridge.py"
    mindmap = script_dir / "generate_meeting_mindmap.py"

    inp = Path(args.input).expanduser().resolve()
    if not inp.exists():
        print(f"Error: input not found: {inp}", file=sys.stderr)
        return 1

    tts_cmd = [sys.executable, str(bridge), "tts", "--input", str(inp), "--topic", args.topic, "--provider", "auto"]
    tts = run(tts_cmd)
    if tts.returncode != 0:
        print(tts.stdout, end="")
        print(tts.stderr, end="", file=sys.stderr)
        return tts.returncode
    info = parse_kv_lines(tts.stdout)

    doc = ensure_file(info.get("doc"), "doc")
    spoken = ensure_file(info.get("spoken_script"), "spoken_script")
    brief_audio = ensure_file(info.get("audio"), "audio")
    full_audio = ensure_file(info.get("audio_full"), "audio_full")

    # Hard gate: must be mp3 for both tracks
    if brief_audio.suffix.lower() != ".mp3":
        raise RuntimeError(f"brief audio is not mp3: {brief_audio.name}")
    if full_audio.suffix.lower() != ".mp3":
        raise RuntimeError(f"full audio is not mp3: {full_audio.name}")

    map_cmd = [
        sys.executable,
        str(mindmap),
        "--minutes",
        str(doc),
        "--topic",
        args.topic,
        "--formats",
        "html,xmind",
    ]
    mp = run(map_cmd)
    if mp.returncode != 0:
        print(mp.stdout, end="")
        print(mp.stderr, end="", file=sys.stderr)
        return mp.returncode
    minfo = parse_kv_lines(mp.stdout)
    data = ensure_file(minfo.get("data"), "mindmap data")
    html = ensure_file(minfo.get("html"), "mindmap html")
    xmind = ensure_file(minfo.get("xmind"), "mindmap xmind")

    print(f"doc={doc}")
    print(f"spoken_script={spoken}")
    print(f"audio={brief_audio}")
    print(f"audio_full={full_audio}")
    print(f"mindmap_data={data}")
    print(f"mindmap_html={html}")
    print(f"mindmap_xmind={xmind}")

    quick = publish_quick_access(
        {
            "doc": doc,
            "spoken_script": spoken,
            "audio": brief_audio,
            "audio_full": full_audio,
            "mindmap_data": data,
            "mindmap_html": html,
            "mindmap_xmind": xmind,
        }
    )
    if quick:
        print(f"quick_root={Path.home() / 'clawdhome_shared' / 'public'}")
        for k, v in quick.items():
            print(f"quick_{k}={v}")

    print("status=SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
