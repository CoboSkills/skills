#!/usr/bin/env python3
"""
sector.py — 查询板块数据（行业板块 / 概念板块 / 板块成分股）

用法:
    python sector.py --type industry          # 行业板块列表
    python sector.py --type concept           # 概念板块列表
    python sector.py --type index             # 指数列表
    python sector.py --constituents <板块代码>  # 板块成分股

示例:
    python sector.py --type industry
    python sector.py --type concept
    python sector.py --constituents URFI883404
"""

import sys
import argparse
import json
from thsdk import THS


def sector(type_: str = "industry", constituents: str = None):
    with THS() as ths:
        if constituents:
            resp = ths.block_constituents(constituents)
            label = f"板块成分股({constituents})"
        elif type_ == "concept":
            resp = ths.ths_concept()
            label = "概念板块"
        elif type_ == "index":
            resp = ths.index_list()
            label = "指数列表"
        else:
            resp = ths.ths_industry()
            label = "行业板块"

        if not resp.success:
            print(json.dumps({"error": f"板块数据查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "type": label,
            "count": resp.extra.get("total_count", len(resp.data) if isinstance(resp.data, list) else 0),
            "data": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询板块数据")
    parser.add_argument("--type", choices=["industry", "concept", "index"], default="industry")
    parser.add_argument("--constituents", help="板块代码，查询成分股", default=None)
    args = parser.parse_args()
    sector(args.type, args.constituents)
