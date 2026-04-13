#!/usr/bin/env python3
"""
Install skill bundles from skills.csv.
"""
import argparse
import csv
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set


BUNDLE_INFO: List[Dict[str, str]] = [
    {
        "id": "thinktank-core",
        "name": "智库研究核心包",
        "purpose": "覆盖信息获取、文档处理、分析和基础交付，是默认主力技能包。",
    },
    {
        "id": "academic-research-plus",
        "name": "学术研究增强包",
        "purpose": "用于补强 arXiv、Google Scholar 和论文对比等学术研究场景。",
    },
    {
        "id": "field-research-plus",
        "name": "调研执行增强包",
        "purpose": "用于补强问卷设计发布、访谈提纲、访谈分析和调研材料整理等调研执行场景。",
    },
    {
        "id": "monitoring-and-insight",
        "name": "动态监测增强包",
        "purpose": "用于新闻跟踪、趋势观察，以及补充搜索与网页抓取等持续监测类任务。",
    },
    {
        "id": "analysis-modeling-plus",
        "name": "分析建模增强包",
        "purpose": "用于市场分析、商业分析框架、SWOT 和数据分析等研究建模任务。",
    },
    {
        "id": "delivery-plus",
        "name": "材料转换与展示增强包",
        "purpose": "用于处理非常规输入材料和展示化输出，比如扫描版 PDF 转 Word、文章转信息图。",
    },
]


def load_skills(csv_file: Path) -> List[dict]:
    """Load and parse the skills.csv configuration."""
    if not csv_file.exists():
        print(f"Error: {csv_file} not found", file=sys.stderr)
        sys.exit(1)

    with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def is_keep(row: dict) -> bool:
    return row.get("keep", "").strip().lower() in {"yes", "true", "1"}


def bundle_meta(bundle_id: str) -> Dict[str, str] | None:
    for bundle in BUNDLE_INFO:
        if bundle["id"] == bundle_id:
            return bundle
    return None


def list_bundles(rows: List[dict]) -> None:
    """Print available bundles with their descriptions."""
    print("Available bundles:")
    for bundle in BUNDLE_INFO:
        bundle_id = bundle["id"]
        skill_count = sum(
            1
            for row in rows
            if is_keep(row) and row.get("bundle_id", "").strip() == bundle_id
        )
        print(f"  - {bundle_id} | {bundle['name']} ({skill_count})")
        print(f"    {bundle['purpose']}")


def get_bundle_skills(rows: List[dict], bundle_id: str) -> List[str]:
    """Get keep=yes skill slugs for a specific bundle."""
    return [
        row["slug"].strip()
        for row in rows
        if is_keep(row) and row.get("bundle_id", "").strip() == bundle_id and row.get("slug")
    ]


def bundle_exists(bundle_id: str) -> bool:
    return bundle_meta(bundle_id) is not None


def collect_skills(rows: List[dict], bundle_ids: List[str]) -> List[str]:
    """Collect and deduplicate skills from multiple bundles."""
    seen: Set[str] = set()
    skills: List[str] = []

    for bundle_id in bundle_ids:
        if not bundle_exists(bundle_id):
            print(f"Error: Unknown bundle: {bundle_id}", file=sys.stderr)
            print(file=sys.stderr)
            list_bundles(rows)
            sys.exit(1)

        for slug in get_bundle_skills(rows, bundle_id):
            if slug not in seen:
                seen.add(slug)
                skills.append(slug)

    return skills


def install_skills(skills: List[str], registry: str) -> None:
    """Install skills using clawdhub CLI."""
    if not skills:
        print("Error: No skill slugs found for the selected bundle(s).", file=sys.stderr)
        sys.exit(1)

    print("Skills to install:")
    for slug in skills:
        print(f"  - {slug}")
    print()

    for slug in skills:
        print(f"Installing {slug}...")
        try:
            subprocess.run(
                ["clawdhub", "install", slug, "--no-input", f"--registry={registry}"],
                check=True,
                shell=True,  # Windows compatibility
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing {slug}: {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: clawdhub command not found. Please install clawdhub CLI.", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install skill bundles from skills.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("bundles", nargs="*", help="Bundle IDs to install")
    parser.add_argument("--list", action="store_true", help="List available bundles")
    parser.add_argument("--registry", default="https://cn.clawhub-mirror.com", help="Registry URL")

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    csv_file = skill_dir / "skills.csv"
    rows = load_skills(csv_file)

    if args.list:
        list_bundles(rows)
        return

    if not args.bundles:
        parser.print_help()
        print()
        list_bundles(rows)
        sys.exit(1)

    print(f"Selected bundles: {' '.join(args.bundles)}")
    skills = collect_skills(rows, args.bundles)
    install_skills(skills, args.registry)


if __name__ == "__main__":
    main()
