#!/usr/bin/env python3
"""
depth_quote.py — 查询股票5档深度行情（search_symbols → depth）

用法:
    python depth_quote.py <股票名称或代码>

示例:
    python depth_quote.py 宁德时代
"""

import sys
import argparse
import json
from thsdk import THS


def depth_quote(name: str):
    with THS() as ths:
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            print(json.dumps({"error": f"未找到证券: {name}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        stock = candidates[0] if candidates else sym_resp.data[0]
        thscode = stock["THSCODE"]

        resp = ths.depth(thscode)
        if not resp.success:
            print(json.dumps({"error": f"深度数据查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {"name": stock.get("Name"), "thscode": thscode, "market": stock.get("MarketDisplay")},
            "depth": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询5档深度行情")
    parser.add_argument("name", help="股票名称或关键词")
    args = parser.parse_args()
    depth_quote(args.name)
