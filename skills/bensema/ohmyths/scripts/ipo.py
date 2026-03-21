#!/usr/bin/env python3
"""
ipo.py — 查询IPO数据（今日新股 / 待上市新股）

用法:
    python ipo.py [--type today|wait]

示例:
    python ipo.py
    python ipo.py --type wait
"""

import sys
import argparse
import json
from thsdk import THS


def ipo(type_: str = "today"):
    with THS() as ths:
        if type_ == "wait":
            resp = ths.ipo_wait()
            label = "待上市IPO"
        else:
            resp = ths.ipo_today()
            label = "今日IPO"

        if not resp.success:
            print(json.dumps({"error": f"IPO数据查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "type": label,
            "count": len(resp.data) if isinstance(resp.data, list) else 0,
            "data": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询IPO数据")
    parser.add_argument("--type", choices=["today", "wait"], default="today", help="today=今日新股, wait=待上市新股")
    args = parser.parse_args()
    ipo(args.type)
