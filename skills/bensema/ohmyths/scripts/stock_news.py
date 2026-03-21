#!/usr/bin/env python3
"""
stock_news.py — 查询股票相关资讯新闻（search_symbols → news）

用法:
    python stock_news.py <股票名称或代码>

示例:
    python stock_news.py 华为
    python stock_news.py 沪深市场
"""

import sys
import argparse
import json
from thsdk import THS


def stock_news(name: str):
    with THS() as ths:
        sym_resp = ths.search_symbols(name)
        if not sym_resp.success or not sym_resp.data:
            # 没找到具体股票，查市场整体资讯
            resp = ths.news()
            result = {
                "success": True,
                "stock": {"name": "市场整体", "thscode": "1A0001"},
                "news": resp.data if resp.success else [],
            }
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return

        candidates = [d for d in sym_resp.data if d.get("MarketStr", "").startswith(("USZA", "USHA", "UBJA"))]
        stock = candidates[0] if candidates else sym_resp.data[0]
        thscode = stock["THSCODE"]
        code = stock.get("Code", "1A0001")
        market = stock.get("MarketStr", "USHI")[:4]

        resp = ths.news(code=code, market=market)
        if not resp.success:
            print(json.dumps({"error": f"资讯查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "stock": {"name": stock.get("Name"), "thscode": thscode, "market": stock.get("MarketDisplay")},
            "news": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询股票资讯新闻")
    parser.add_argument("name", help="股票名称或关键词")
    args = parser.parse_args()
    stock_news(args.name)
