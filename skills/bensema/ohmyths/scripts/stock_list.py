#!/usr/bin/env python3
"""
stock_list.py — 获取各市场股票列表

用法:
    python stock_list.py --market cn|us|hk|bj|etf|futures|forex|bond

示例:
    python stock_list.py --market cn      # A股列表
    python stock_list.py --market hk      # 港股列表
    python stock_list.py --market us      # 美股列表
    python stock_list.py --market etf     # ETF基金
    python stock_list.py --market forex   # 外汇
"""

import sys
import argparse
import json
from thsdk import THS

MARKET_MAP = {
    "cn": ("stock_cn_lists", "A股"),
    "us": ("stock_us_lists", "美股"),
    "hk": ("stock_hk_lists", "港股"),
    "bj": ("stock_bj_lists", "北交所"),
    "etf": ("fund_etf_lists", "ETF基金"),
    "futures": ("futures_lists", "期货"),
    "forex": ("forex_list", "外汇"),
    "bond": ("bond_lists", "债券"),
    "nasdaq": ("nasdaq_lists", "纳斯达克"),
}


def stock_list(market: str = "cn"):
    method_name, label = MARKET_MAP.get(market, ("stock_cn_lists", "A股"))
    with THS() as ths:
        method = getattr(ths, method_name)
        resp = method()
        if not resp.success:
            print(json.dumps({"error": f"列表查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "market": label,
            "count": resp.extra.get("total_count", len(resp.data) if isinstance(resp.data, list) else 0),
            "data": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取市场股票列表")
    parser.add_argument("--market", choices=list(MARKET_MAP.keys()), default="cn", help="市场类型")
    args = parser.parse_args()
    stock_list(args.market)
