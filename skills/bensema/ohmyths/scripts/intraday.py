#!/usr/bin/env python3
"""
intraday.py — 查询股票日内分时数据（search_symbols → intraday_data）

用法:
    python intraday.py <股票名称或代码>

示例:
    python intraday.py 比亚迪
"""

import sys
import argparse
import json
from thsdk import THS


def intraday(name: str):
    with THS() as ths:
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            print(json.dumps({"error": f"未找到证券: {name}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        stock = candidates[0] if candidates else sym_resp.data[0]
        thscode = stock["THSCODE"]

        resp = ths.intraday_data(thscode)
        if not resp.success:
            print(json.dumps({"error": f"分时数据查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {"name": stock.get("Name"), "thscode": thscode, "market": stock.get("MarketDisplay")},
            "intraday": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询股票日内分时数据")
    parser.add_argument("name", help="股票名称或关键词")
    args = parser.parse_args()
    intraday(args.name)
