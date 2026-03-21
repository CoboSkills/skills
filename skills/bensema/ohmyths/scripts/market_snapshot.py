#!/usr/bin/env python3
"""
market_snapshot.py — 查询股票实时行情快照（search_symbols → market_data_cn）

用法:
    python market_snapshot.py <股票名称或代码>

示例:
    python market_snapshot.py 茅台
    python market_snapshot.py 腾讯
"""

import sys
import argparse
import json
from thsdk import THS


def market_snapshot(name: str):
    with THS() as ths:
        # Step 1: 搜索股票代码
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            print(json.dumps({"error": f"未找到证券: {name}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        if not candidates:
            candidates = sym_resp.data

        stock = candidates[0]
        thscode = stock["THSCODE"]
        market_prefix = stock.get("MarketStr", "USZA")

        # Step 2: 根据市场类型选择合适的 market_data 接口
        if market_prefix in ("USZA", "USHA", "UBJA"):
            resp = ths.market_data_cn(thscode)
        elif market_prefix.startswith("UHKA"):
            resp = ths.market_data_cn(thscode)  # 港股也走cn
        elif market_prefix.startswith("UUSA") or market_prefix.startswith("UNASA"):
            resp = ths.market_data_cn(thscode)
        else:
            resp = ths.market_data_cn(thscode)

        if not resp.success:
            print(json.dumps({"error": f"行情查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {
                "name": stock.get("Name"),
                "thscode": thscode,
                "market": stock.get("MarketDisplay"),
            },
            "snapshot": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询股票实时行情")
    parser.add_argument("name", help="股票名称或关键词")
    args = parser.parse_args()
    market_snapshot(args.name)
