#!/usr/bin/env python3
"""
query_stock.py — 查询股票近日K线数据（核心流程：search_symbols → klines）

用法:
    python query_stock.py <股票名称或代码> [--count N] [--interval day] [--adjust forward]

示例:
    python query_stock.py 茅台
    python query_stock.py 比亚迪 --count 20
    python query_stock.py 同花顺 --interval week --count 10
"""

import sys
import argparse
import json
from thsdk import THS


def query_stock(name: str, count: int = 10, interval: str = "day", adjust: str = ""):
    with THS() as ths:
        # Step 1: 模糊搜索股票代码
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            print(json.dumps({"error": f"未找到证券: {name}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        # 优先匹配A股（USZA/USHA），过滤掉指数/板块
        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        if not candidates:
            candidates = sym_resp.data  # fallback：直接用第一个

        stock = candidates[0]
        thscode = stock["THSCODE"]

        # Step 2: 查询K线数据
        kline_resp = ths.klines(thscode, count=count, interval=interval, adjust=adjust)
        if not kline_resp.success:
            print(json.dumps({"error": f"K线查询失败: {kline_resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {
                "name": stock.get("Name"),
                "code": stock.get("Code"),
                "thscode": thscode,
                "market": stock.get("MarketDisplay"),
            },
            "params": {"count": count, "interval": interval, "adjust": adjust or "不复权"},
            "klines": kline_resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询股票K线数据")
    parser.add_argument("name", help="股票名称或关键词")
    parser.add_argument("--count", type=int, default=10, help="K线条数，默认10")
    parser.add_argument("--interval", default="day", help="周期：1m/5m/15m/30m/60m/day/week/month，默认day")
    parser.add_argument("--adjust", default="", help="复权：forward/backward/（空=不复权）")
    args = parser.parse_args()
    query_stock(args.name, args.count, args.interval, args.adjust)
