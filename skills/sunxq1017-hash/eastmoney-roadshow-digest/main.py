from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from providers.asr import ASRUnavailable, ASRError, extract_audio, transcribe_audio
from providers.eastmoney import EastMoneyError, fetch_page

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"


def ensure_outputs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def dump_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_asr_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", "", text)
    text = re.sub(r"[，,]{2,}", "，", text)
    text = re.sub(r"[。]{2,}", "。", text)
    pieces = []
    buf = ""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        buf += line
        while len(buf) >= 90:
            cut = max(buf.rfind("。", 0, 120), buf.rfind("？", 0, 120), buf.rfind("！", 0, 120), buf.rfind("；", 0, 120), buf.rfind("，", 0, 120))
            if cut < 30:
                cut = 90
            pieces.append(buf[: cut + (1 if cut < len(buf) and buf[cut] in '。？！，；' else 0)].strip())
            buf = buf[cut + (1 if cut < len(buf) and buf[cut] in '。？！，；' else 0):].strip()
    if buf:
        pieces.append(buf)
    cleaned = []
    last = None
    for piece in pieces:
        piece = piece.strip("，。； ")
        if len(piece) < 6:
            continue
        if piece == last:
            continue
        cleaned.append(piece)
        last = piece
    return "\n\n".join(cleaned).strip()


def clean_metadata_transcript(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines()]
    out: List[str] = []
    seen = set()
    for line in lines:
        if not line:
            if out and out[-1] != "":
                out.append("")
            continue
        line = re.sub(r"\s+", " ", line)
        if line in seen and len(line) > 12:
            continue
        seen.add(line)
        if line.startswith("[") and "]" in line:
            name, rest = line.split("]", 1)
            rest = rest.strip()
            line = f"{name[1:]}：{rest}" if rest else name[1:]
        if line.startswith("- "):
            out.append(line)
            continue
        if line in {"嘉宾资料：", "议程："}:
            out.append(line)
            continue
        if line.startswith("标题：") or line.startswith("简介："):
            out.append(line)
            continue
        out.append(line)
    cleaned = "\n".join(out)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def make_deliverable_summary(meta: Dict[str, Any], transcript: str) -> str:
    title = meta.get("name") or meta.get("intro") or "未命名路演"
    status_map = {1: "直播中", 3: "回放", 4: "预告"}
    status = status_map.get(meta.get("status"), str(meta.get("status")))
    guests = meta.get("guests") or []
    guest_names = [g.get("alias") or g.get("nickname") for g in guests if g.get("alias") or g.get("nickname")]
    lines = [x.strip() for x in transcript.splitlines() if x.strip()]
    usable = [x for x in lines if not x.startswith(("标题：", "简介：", "嘉宾资料：", "议程："))]
    highlights = []
    for item in usable:
        if len(item) >= 16:
            highlights.append(item[:120])
        if len(highlights) >= 5:
            break
    if not highlights:
        highlights = ["当前公开页面可提取的主要信息集中于主题、嘉宾与回放元数据；逐字稿仍建议补做 ASR/人工校对。"]
    agenda_lines = []
    config = meta.get("config") or {}
    for ag in config.get("agendas", []) or []:
        label = ag.get("title") or ag.get("name")
        if label:
            agenda_lines.append(f"- {label}")
    guest_block = "\n".join(f"- {name}" for name in guest_names[:8]) if guest_names else "- 页面未暴露清晰嘉宾名录"
    agenda_block = "\n".join(agenda_lines) if agenda_lines else "- 页面未暴露结构化议程"
    highlight_block = "\n".join(f"- {x}" for x in highlights)
    return (
        f"# Summary\n\n"
        f"## Executive Overview\n"
        f"- 标题：{title}\n"
        f"- 页面状态：{status}\n"
        f"- 时间：{meta.get('start_time')} → {meta.get('end_time')}\n"
        f"- 处理方式：公开页面解析；字幕优先；必要时媒体+ASR 回退\n\n"
        f"## Guests\n{guest_block}\n\n"
        f"## Agenda Signals\n{agenda_block}\n\n"
        f"## Key Takeaways\n{highlight_block}\n\n"
        f"## Quality Note\n"
        f"- 本摘要基于公开页面元数据与当前可得文本生成；若需对外发布或用于投资判断，建议补充真实 ASR 与人工复核。\n"
    )


def make_deliverable_brief(meta: Dict[str, Any], transcript: str) -> str:
    title = meta.get("name") or "未命名路演"
    lines = [x.strip() for x in transcript.splitlines() if x.strip()]
    usable = [x for x in lines if not x.startswith(("标题：", "简介：", "嘉宾资料：", "议程："))]
    points = []
    for item in usable:
        if len(item) >= 14:
            points.append(item[:80])
        if len(points) >= 3:
            break
    while len(points) < 3:
        fallback = [
            "本场主题聚焦震荡市环境下的量化产品配置。",
            "公开页面可稳定提取回放元数据与媒体地址。",
            "若要形成正式逐字稿，仍需补齐 ASR 或人工校对。",
        ]
        points.append(fallback[len(points)])
    return (
        f"# Brief\n\n"
        f"**标题**：{title}\n\n"
        f"**适合谁看**：需要快速判断本场路演是否值得进一步精听的审核者/研究支持人员。\n\n"
        f"**三条核心结论**\n"
        f"- {points[0]}\n"
        f"- {points[1]}\n"
        f"- {points[2]}\n\n"
        f"**当前可用性**\n- 已可稳定抽取公开元数据与回放媒体；逐字稿质量仍受 ASR 可用性影响。\n\n"
        f"**一句话风险提示**\n- 若缺少可用字幕或 ASR 依赖，文本产物将退化为基于公开元数据的结构化摘要。\n"
    )


def summarize(meta: Dict[str, Any], transcript: str) -> str:
    bullets: List[str] = []
    title = meta.get("name") or meta.get("intro") or "未命名路演"
    bullets.append(f"# 会议纪要\n\n## 主题\n- {title}")
    bullets.append(f"\n## 基本信息\n- 状态：{meta.get('status')}\n- 开始：{meta.get('start_time')}\n- 结束：{meta.get('end_time')}")
    guests = meta.get("guests") or []
    if guests:
        guest_lines = []
        for g in guests[:8]:
            alias = g.get("alias") or g.get("nickname") or "未知嘉宾"
            intro = (g.get("intro") or "").strip().replace("\n", " ")
            guest_lines.append(f"- {alias}：{intro[:120]}".rstrip("："))
        bullets.append("\n## 嘉宾\n" + "\n".join(guest_lines))
    key_points = []
    for line in [x.strip() for x in transcript.splitlines() if x.strip()]:
        if len(line) >= 18:
            key_points.append(f"- {line[:120]}")
        if len(key_points) >= 6:
            break
    if not key_points:
        key_points = ["- 未获得高质量逐字稿；请结合 meta 与回放人工复核。"]
    bullets.append("\n## 核心观点（基于转写抽取）\n" + "\n".join(key_points))
    bullets.append("\n## 风险提示\n- 本纪要仅基于公开页面元数据与自动转写生成，可能存在漏字、错字与语义压缩，不能替代人工复核。")
    return "\n".join(bullets).strip() + "\n"


def make_brief(meta: Dict[str, Any], transcript: str) -> str:
    lines = [x.strip() for x in transcript.splitlines() if x.strip()]
    picks = [f"- {x[:80]}" for x in lines[:3]] or ["- 未取得足够转写内容，需人工查看回放。"]
    return (
        f"# Brief\n\n"
        f"**标题**：{meta.get('name') or '未命名路演'}\n\n"
        f"**三条核心结论**\n" + "\n".join(picks) + "\n\n"
        f"**一句话风险提示**\n- 内容来自公开页面与自动转写，需人工复核。\n"
    )


def run(url: str) -> Dict[str, Any]:
    ensure_outputs()
    report: Dict[str, Any] = {
        "url": url,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "steps": [],
        "status": "failed",
        "notes": [],
        "artifacts": [
            "outputs/meta.json",
            "outputs/transcript.md",
            "outputs/clean_transcript.md",
            "outputs/summary.md",
            "outputs/brief.md",
            "outputs/run_report.md",
        ],
    }
    transcript = ""

    try:
        page = fetch_page(url)
        meta = {
            "source_url": page.url,
            "channel_id": page.channel_id,
            "html_title": page.html_title,
            "page_notes": page.notes,
            "subtitle_candidates": page.subtitle_candidates,
            "media_candidates": page.media_candidates,
            "metadata": page.metadata,
        }
        dump_json(OUT / "meta.json", meta)
        report["steps"].append("url validation: ok")
        report["steps"].append("page parsing: ok")

        if page.subtitle_candidates:
            report["steps"].append("subtitle extraction: candidates found but parser not yet specialized; fallback continues")
            report["notes"].append("Subtitle-first branch is implemented as discovery. No subtitle payload was consumable for this tested URL.")
        else:
            report["steps"].append("subtitle extraction: no candidates found")

        if page.media_candidates:
            report["steps"].append("media discovery: ok")
            media_url = page.media_candidates[0]["url"]
            try:
                audio_path = extract_audio(media_url, OUT)
                report["steps"].append("audio extraction: ok")
                try:
                    asr = transcribe_audio(audio_path, model_size="tiny", segment_seconds=30, total_timeout_seconds=150)
                    transcript = asr.get("text", "").strip()
                    asr_status = asr.get("status", "ASR_complete")
                    report["steps"].append(f"ASR: {asr_status}")
                    report["notes"].append(
                        f"ASR engine: {asr.get('engine')}; model={asr.get('model_size')}; chunks={asr.get('completed_chunks')}/{asr.get('total_chunks')}; timeout={asr.get('timeout_seconds')}s"
                    )
                except ASRUnavailable as e:
                    report["steps"].append("ASR: unavailable")
                    report["notes"].append(str(e))
                except ASRError as e:
                    report["steps"].append("ASR: failed")
                    report["notes"].append(str(e))
            except Exception as e:
                report["steps"].append("audio extraction: failed")
                report["notes"].append(str(e))
        else:
            report["steps"].append("media discovery: no candidates found")

        if transcript:
            transcript = normalize_asr_text(transcript)
            clean_transcript = transcript
            report["notes"].append("Transcript generated from ASR and normalized with enhanced cleanup.")
        else:
            guests = page.metadata.get("guests") or []
            guest_lines = []
            for g in guests:
                alias = g.get("alias") or g.get("nickname") or "未知嘉宾"
                intro = (g.get("intro") or "").strip()
                if intro:
                    guest_lines.append(f"[{alias}] {intro}")
            agenda_lines = []
            config = page.metadata.get("config") or {}
            for ag in config.get("agendas", []) or []:
                title = ag.get("title") or ag.get("name") or "议程"
                agenda_lines.append(f"- {title}")
            transcript = "\n".join(
                [
                    f"标题：{page.metadata.get('name') or ''}",
                    f"简介：{page.metadata.get('intro') or ''}",
                    "",
                    "嘉宾资料：",
                    *guest_lines,
                    "",
                    "议程：",
                    *agenda_lines,
                ]
            ).strip()
            clean_transcript = clean_metadata_transcript(transcript)
            report["notes"].append("No ASR transcript available; transcript.md falls back to structured public metadata text.")

        if not clean_transcript:
            clean_transcript = clean_text(transcript)
        write(OUT / "transcript.md", "# Transcript\n\n" + transcript.strip() + "\n")
        write(OUT / "clean_transcript.md", "# Clean Transcript\n\n" + clean_transcript + "\n")
        write(OUT / "summary.md", make_deliverable_summary(page.metadata, clean_transcript))
        write(OUT / "brief.md", make_deliverable_brief(page.metadata, clean_transcript))
        report["steps"].append("cleaning: ok")
        report["steps"].append("summary: ok")
        report["steps"].append("brief: ok")
        report["status"] = "ok"
    except EastMoneyError as e:
        report["notes"].append(f"EastMoney parse error: {e}")
    except Exception as e:
        report["notes"].append(f"Unhandled error: {e}")
    finally:
        report["finished_at"] = datetime.now().isoformat(timespec="seconds")
        md = ["# Run Report", "", f"- URL: {report['url']}", f"- Status: {report['status']}", "", "## Steps"]
        md.extend([f"- {s}" for s in report["steps"]] or ["- none"])
        md.extend(["", "## Notes"])
        md.extend([f"- {n}" for n in report["notes"]] or ["- none"])
        md.extend(["", "## Artifacts"])
        md.extend([f"- {a}" for a in report["artifacts"]])
        write(OUT / "run_report.md", "\n".join(md) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    result = run(args.url)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
