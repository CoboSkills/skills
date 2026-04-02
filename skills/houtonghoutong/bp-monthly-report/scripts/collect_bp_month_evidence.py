#!/usr/bin/env python3
"""Collect month-relevant BP-linked reports into a lightweight manifest.

This script no longer writes one JSON snapshot per report. The evidence object
for drafting is the report itself, referenced by title and, when available,
its online `reportId` link.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import requests


BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api"
PRIORITY_RANK = {"summary_only": 0, "auxiliary": 1, "secondary": 2, "primary": 3}


def api_post(app_key: str, endpoint: str, payload: dict) -> dict:
    resp = requests.post(
        f"{BASE_URL}{endpoint}",
        json=payload,
        headers={"appKey": app_key, "Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def month_pattern(report_month: str) -> re.Pattern[str]:
    year, month = report_month.split("-")
    month_no_zero = str(int(month))
    return re.compile(
        rf"({year}年{month_no_zero}月|{year}-{month}|{month_no_zero}月|{int(month)}月)",
        re.IGNORECASE,
    )


def sanitize(name: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", name.strip())
    return cleaned[:80].strip("_") or "report"


def extract_report_id(item: dict) -> str:
    for key in ("reportId", "id", "bizId", "sourceId", "relationId"):
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def report_link_md(title: str, report_id: str) -> str:
    if report_id:
        safe_title = title.replace("[", "\\[").replace("]", "\\]")
        return f"[{safe_title}](reportId={report_id}&linkType=report)"
    return title


def normalize_batch_title(title: str) -> str:
    title = (title or "").strip()
    if not title:
        return title

    stripped = re.sub(r"^【[^】]+】(?=关于)", "", title)
    stripped = re.sub(r"^[^-【】\s]{1,40}-(?=关于)", "", stripped)

    batch_markers = {
        "关于启动2026年度薪酬调整工作及《薪酬调整与职级晋升管理办法》意见征询的通知（请勿转发）",
        "关于启动2026年1月薪酬调整工作及《薪酬调整与职级晋升管理办法》意见征询的通知（请勿转发）",
        "关于确认2026年1月调薪方案（V3.0版）的通知",
    }
    if stripped in batch_markers:
        return stripped
    return title


def cluster_rows(rows: list[dict]) -> tuple[list[dict], int]:
    raw_hit_count = len(rows)
    grouped: dict[tuple[str, str, str], dict] = {}

    for row in rows:
        canonical_title = normalize_batch_title(row["report_title"])
        key = (row["task_id"], row["report_type"], canonical_title)
        existing = grouped.get(key)
        if existing is None:
            cloned = dict(row)
            cloned["canonical_title"] = canonical_title
            cloned["raw_hit_count"] = 1
            cloned["raw_titles"] = [row["report_title"]]
            grouped[key] = cloned
            continue

        existing["raw_hit_count"] += 1
        if row["report_title"] not in existing["raw_titles"]:
            existing["raw_titles"].append(row["report_title"])
        if PRIORITY_RANK.get(row["author_priority"], -1) > PRIORITY_RANK.get(existing["author_priority"], -1):
            existing["author_priority"] = row["author_priority"]
            existing["write_emp_name"] = row["write_emp_name"]
            existing["report_id"] = row["report_id"]
            existing["report_link_md"] = row["report_link_md"]
            existing["report_link_status"] = row["report_link_status"]

    clustered = list(grouped.values())
    clustered.sort(key=lambda row: row["evidence_id"])
    for idx, row in enumerate(clustered, start=1):
        row["evidence_id"] = f"R{idx:03d}"
    return clustered, raw_hit_count


def split_progress(content: str) -> dict:
    text = re.sub(r"\s+", " ", content or "").strip()
    progress_facts = []
    completed_items = []
    in_flight_items = []
    blockers = []
    next_steps = []

    clauses = re.split(r"[；;。]\s*", text)
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        if any(tag in clause for tag in ["已完成", "完成了", "形成", "已形成", "已进入", "已推进", "已修复", "已优化"]):
            completed_items.append(clause)
            progress_facts.append(clause)
            continue
        if any(tag in clause for tag in ["正在", "推进", "开展", "组织", "测试", "试点", "沟通", "评估", "待", "拟", "计划"]):
            in_flight_items.append(clause)
            progress_facts.append(clause)
            continue
        if any(tag in clause for tag in ["问题", "风险", "不足", "漏洞", "卡点", "延迟", "待评估", "需关注", "缺乏"]):
            blockers.append(clause)
            progress_facts.append(clause)
            continue
        if any(tag in clause for tag in ["下一步", "后续", "下周", "下月", "将", "拟于"]):
            next_steps.append(clause)
            progress_facts.append(clause)

    return {
        "progress_facts": dedupe(progress_facts),
        "completed_items": dedupe(completed_items),
        "in_flight_items": dedupe(in_flight_items),
        "blockers": dedupe(blockers),
        "next_steps": dedupe(next_steps),
    }


def dedupe(items: list[str]) -> list[str]:
    out = []
    seen = set()
    for item in items:
        item = item.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def priority(author: str, report_type: str, owner_name: str) -> str:
    if author == owner_name and report_type == "manual":
        return "primary"
    if report_type == "manual":
        return "auxiliary"
    return "summary_only"


def collect_attachments(item: dict) -> tuple[list, str]:
    attachment_keys = [
        "attachments",
        "attachmentList",
        "attachList",
        "fileList",
        "files",
        "annexList",
        "accessoryList",
    ]
    attachments = []
    for key in attachment_keys:
        val = item.get(key)
        if isinstance(val, list) and val:
            attachments.extend(val)
    if attachments:
        return attachments, "exposed_in_pageAllReports"
    return [], "not_exposed_in_pageAllReports"


def write_manifest_md(path: Path, rows: list[dict], report_month: str, owner_name: str, raw_hit_count: int) -> None:
    total = len(rows)
    primary = sum(1 for row in rows if row["author_priority"] == "primary")
    auxiliary_manual = sum(
        1
        for row in rows
        if row["report_type"] == "manual" and row["author_priority"] != "primary"
    )
    ai_count = sum(1 for row in rows if row["report_type"] == "ai")
    lines = [
        "# Report Manifest",
        "",
        f"> report_month: {report_month}",
        f"> owner_name: {owner_name}",
        "> note: 主证据对象为在线汇报链接；当前接口若未返回 `reportId`，则仅保留标题与最小元数据，不再落本地原文快照。",
        f"> raw_report_hit_count: {raw_hit_count}",
        f"> adopted_report_count: {total}",
        f"> adopted_primary_report_count: {primary}",
        f"> adopted_other_manual_report_count: {auxiliary_manual}",
        f"> adopted_ai_report_count: {ai_count}",
        "> batch_collapse_rule: 批量分发且正文模板一致的通知/确认类汇报，按同一动作模板归并，不按分发对象重复计数。",
        "",
        "| ref | title | raw_hits | author | priority | link_status | task_id | attachment_status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {ref} | {title} | {raw_hits} | {author} | {priority} | {link_status} | {task_id} | {attachment_status} |".format(
                ref=row["evidence_id"],
                title=row["canonical_title"].replace("|", "\\|"),
                raw_hits=row["raw_hit_count"],
                author=row["write_emp_name"] or "",
                priority=row["author_priority"],
                link_status=row["report_link_status"],
                task_id=row["task_id"],
                attachment_status=row["attachment_fetch_status"],
            )
        )

    for row in rows:
        lines.extend(
            [
                "",
                f"## {row['evidence_id']}",
                "",
                f"- 标题：{row['canonical_title']}",
                f"- 原始命中数：`{row['raw_hit_count']}`",
                f"- 作者：{row['write_emp_name'] or ''}",
                f"- 类型：{row['report_type'] or ''}",
                f"- 任务ID：`{row['task_id']}`",
                f"- 优先级：{row['author_priority']}",
                f"- report_id：`{row['report_id'] or 'missing'}`",
                f"- report_link_status：`{row['report_link_status']}`",
                f"- attachment_fetch_status：`{row['attachment_fetch_status']}`",
                "- 归并标题：",
            ]
        )
        for raw_title in row["raw_titles"]:
            lines.append(f"  - {raw_title}")
        lines.extend(
            [
                "- 进展事实：",
            ]
        )
        facts = row["progress"]["progress_facts"] or ["未从正文中抽出稳定进展事实"]
        for fact in facts:
            lines.append(f"  - {fact}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-key", required=True)
    parser.add_argument("--report-month", required=True, help="YYYY-MM")
    parser.add_argument("--owner-name", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--task-id", action="append", required=True)
    parser.add_argument("--include-main", action="append", default=[])
    parser.add_argument("--exclude-ai", action="store_true")
    parser.add_argument("--size", type=int, default=100)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    patt = month_pattern(args.report_month)
    include_main = set(args.include_main or [])
    seen = set()
    exported = []

    for task_id in args.task_id:
        page_index = 1
        while True:
            data = api_post(
                args.app_key,
                "/bp/task/relation/pageAllReports",
                {
                    "taskId": task_id,
                    "pageIndex": page_index,
                    "pageSize": args.size,
                    "sortBy": "relation_time",
                    "sortOrder": "desc",
                },
            ).get("data") or {}
            items = data.get("records") or data.get("list") or data.get("rows") or []
            if not items:
                break
            for item in items:
                main = (item.get("main") or "").strip()
                content = item.get("content") or ""
                if args.exclude_ai and (item.get("type") or "") == "ai":
                    continue
                if include_main:
                    if main not in include_main:
                        continue
                elif not patt.search(main + "\n" + content):
                    continue
                key = (
                    task_id,
                    item.get("writeEmpName"),
                    item.get("type"),
                    main,
                )
                if key in seen:
                    continue
                seen.add(key)
                attachments, attachment_status = collect_attachments(item)
                report_id = extract_report_id(item)
                row = {
                    "evidence_id": f"R{len(exported)+1:03d}",
                    "task_id": task_id,
                    "report_month": args.report_month,
                    "report_title": main,
                    "write_emp_name": item.get("writeEmpName"),
                    "report_type": item.get("type"),
                    "author_priority": priority(item.get("writeEmpName") or "", item.get("type") or "", args.owner_name),
                    "report_id": report_id,
                    "report_link_md": report_link_md(main, report_id),
                    "report_link_status": "ready" if report_id else "missing_report_id",
                    "progress": split_progress(content),
                    "attachments": attachments,
                    "attachment_fetch_status": attachment_status,
                }
                exported.append(row)
            total = int(data.get("total") or 0)
            page_size = int(data.get("pageSize") or data.get("size") or args.size or 0)
            if page_size <= 0 or page_index * page_size >= total:
                break
            page_index += 1

    clustered_rows, raw_hit_count = cluster_rows(exported)
    manifest = out_dir / "manifest.md"
    write_manifest_md(manifest, clustered_rows, args.report_month, args.owner_name, raw_hit_count)
    print(manifest)


if __name__ == "__main__":
    main()
