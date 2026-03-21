#!/usr/bin/env python3
"""
big_order.py — 查询股票大单数据（search_symbols → big_order_flow）

用法:
    python big_order.py <股票名称或代码>

示例:
    python big_order.py 贵州茅台
"""

import sys
import json
from thsdk import THS


def big_order(name: str):
    with THS() as ths:
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            print(json.dumps({"error": f"未找到证券: {name}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        stock = candidates[0] if candidates else sym_resp.data[0]
        thscode = stock["THSCODE"]

        resp = ths.big_order_flow(thscode)
        if not resp.success:
            print(json.dumps({"error": f"大单数据查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {"name": stock.get("Name"), "thscode": thscode, "market": stock.get("MarketDisplay")},
            "big_orders": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python big_order.py <股票名称或代码>")
        sys.exit(1)
    big_order(sys.argv[1])
