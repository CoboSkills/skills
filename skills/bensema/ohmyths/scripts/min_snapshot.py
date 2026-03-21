#!/usr/bin/env python3
"""
min_snapshot.py — 查询历史某日分时数据（search_symbols → min_snapshot）

用法:
    python min_snapshot.py <股票名称或代码> [--date YYYYMMDD]

示例:
    python min_snapshot.py 比亚迪 --date 20240315
    python min_snapshot.py 同花顺
"""

import sys
import argparse
import json
from thsdk import THS


def min_snapshot(name: str, date: str = None):
    with THS() as ths:
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            print(json.dumps({"error": f"未找到证券: {name}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        stock = candidates[0] if candidates else sym_resp.data[0]
        thscode = stock["THSCODE"]

        resp = ths.min_snapshot(thscode, date=date)
        if not resp.success:
            print(json.dumps({"error": f"历史分时查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {"name": stock.get("Name"), "thscode": thscode, "market": stock.get("MarketDisplay")},
            "date": date or "今日",
            "data": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询历史分时数据")
    parser.add_argument("name", help="股票名称或关键词")
    parser.add_argument("--date", default=None, help="日期，格式YYYYMMDD，默认今日")
    args = parser.parse_args()
    min_snapshot(args.name, args.date)
