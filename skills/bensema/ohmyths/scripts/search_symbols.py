#!/usr/bin/env python3
"""
search_symbols.py — 模糊搜索证券代码（search_symbols）

用法:
    python search_symbols.py <关键词>

示例:
    python search_symbols.py 茅台
    python search_symbols.py 300033
"""

import sys
import json
from thsdk import THS


def search(pattern: str):
    with THS() as ths:
        resp = ths.search_symbols(pattern)
        if not resp.success:
            print(json.dumps({"error": resp.error, "success": False}, ensure_ascii=False))
            sys.exit(1)
        print(json.dumps({"success": True, "results": resp.data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python search_symbols.py <关键词>")
        sys.exit(1)
    search(sys.argv[1])
