#!/usr/bin/env python3
"""
auction_anomaly.py — 查询竞价异动（涨停试盘、大单封板等）

用法:
    python auction_anomaly.py [--market USHA|USZA]

示例:
    python auction_anomaly.py
    python auction_anomaly.py --market USZA
"""

import sys
import argparse
import json
from thsdk import THS


def auction_anomaly(market: str = "USHA"):
    with THS() as ths:
        resp = ths.call_auction_anomaly(market)
        if not resp.success:
            print(json.dumps({"error": f"竞价异动查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "market": market,
            "count": len(resp.data) if isinstance(resp.data, list) else 0,
            "data": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询竞价异动")
    parser.add_argument("--market", default="USHA", help="市场代码，默认USHA(沪A)，可选USZA(深A)")
    args = parser.parse_args()
    auction_anomaly(args.market)
