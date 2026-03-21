#!/usr/bin/env python3
"""
云瞻威胁情报查询示例
"""

import json
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from hs_ti_plugin import YunzhanThreatIntel

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_ioc.py <ioc_value>")
        return
    
    ioc = sys.argv[1]
    intel = YunzhanThreatIntel()
    
    # 查询单个IOC
    result = intel.query_ioc(ioc)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
