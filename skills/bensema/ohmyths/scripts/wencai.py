#!/usr/bin/env python3
"""
wencai.py — 问财自然语言条件选股（wencai_nlp）

用法:
    python wencai.py <条件语句>

示例 — 热度/排行类:
    python wencai.py "热度排名前50只股票"
    python wencai.py "今年以来涨幅最大的前50名，非ST"
    python wencai.py "近一个月涨幅最大的前20只股票"
    python wencai.py "今日换手率最高的前30只股票"
    python wencai.py "近一周资金净流入最多的前20只股票"

示例 — 概念/板块类:
    python wencai.py "脑机接口概念股"
    python wencai.py "低空经济概念股"
    python wencai.py "人工智能概念股，市值大于100亿"
    python wencai.py "半导体行业股票"

示例 — 财务指标类:
    python wencai.py "营业收入增长率>10%;营业利润增长率>10%;加权净资产收益率>15%;总资产报酬率>5%"
    python wencai.py "市盈率小于20且股息率大于3%"
    python wencai.py "连续3年净利润增长且负债率小于50%"
    python wencai.py "ROE大于15%且市净率小于3"
    python wencai.py "近三年每年分红且股息率大于4%"

示例 — 技术形态类:
    python wencai.py "涨停"
    python wencai.py "今日跌停"
    python wencai.py "今日成交量大于昨日成交量的两倍"
    python wencai.py "连续5日上涨"
    python wencai.py "macd金叉且成交量放大"
    python wencai.py "突破60日均线且成交量创近20日新高"

示例 — 综合筛选类:
    python wencai.py "市值小于50亿的次新股，非ST，上市不足2年"
    python wencai.py "科创板股票，净利润同比增长大于30%"
    python wencai.py "北交所股票，市盈率低于20"
"""

import sys
import json
from thsdk import THS


def wencai(condition: str):
    with THS() as ths:
        resp = ths.wencai_nlp(condition)
        if not resp.success:
            print(json.dumps({"error": f"问财查询失败: {resp.error}", "success": False}, ensure_ascii=False))
            sys.exit(1)

        result = {
            "success": True,
            "condition": condition,
            "count": len(resp.data) if isinstance(resp.data, list) else 0,
            "data": resp.data,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python wencai.py <条件语句>")
        sys.exit(1)
    wencai(" ".join(sys.argv[1:]))
