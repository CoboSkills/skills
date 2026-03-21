---
name: ohmyths
description: 使用 thsdk 查询A股/港股/美股等金融市场数据的技能。Stop and use this skill whenever the user asks anything about stocks, markets, or financial data in Chinese or English. 必须触发的场景包括：【单股查询】「XXX股票近日走势」「XXX怎么样」「帮我看看XXX」「查一下XXX的K线」「XXX今天涨了多少」「XXX最近表现」「XXX的分时图」「XXX的盘口深度」「XXX的资讯」「XXX大单情况」「XXX分红历史」；【选股筛股】「涨停的股票」「今日成交量放大的股票」「市盈率低于20的股票」「问财选股」任何条件筛选类问题；【市场概览】「今日新股」「待上市IPO」「竞价异动」「涨停试盘」「今天有什么行情」；【板块数据】「XX行业板块」「XX概念股有哪些」「XX指数成分股」「沪深300成分股」；【列表查询】「A股有哪些股票」「港股列表」「ETF基金列表」「期货列表」。所有查询统一通过 scripts/ 下封装脚本调用，核心流程：先 search_symbols 查代码，再调用对应数据接口。
---

# THSDK 股票数据技能

## 快速决策：用哪个脚本？

| 用户意图 | 脚本 | 核心接口 |
|---|---|---|
| 近日走势、K线、历史行情 | `query_stock.py` | search_symbols → klines |
| 当前价格、今日涨跌、实时行情 | `market_snapshot.py` | search_symbols → market_data_cn |
| 今日分时图、日内走势 | `intraday.py` | search_symbols → intraday_data |
| 历史某日分时 | `min_snapshot.py` | search_symbols → min_snapshot |
| 买卖盘口、五档深度 | `depth_quote.py` | search_symbols → depth |
| 新闻资讯、最新动态 | `stock_news.py` | search_symbols → news |
| 大单、主力资金流向 | `big_order.py` | search_symbols → big_order_flow |
| 分红送股、权息历史 | `corporate_action.py` | search_symbols → corporate_action |
| 条件选股、问财查询 | `wencai.py` | wencai_nlp |
| 今日新股、待上市IPO | `ipo.py` | ipo_today / ipo_wait |
| 行业/概念/指数板块 | `sector.py` | ths_industry / ths_concept / index_list |
| 板块成分股 | `sector.py --constituents` | block_constituents |
| 竞价异动、涨停试盘 | `auction_anomaly.py` | call_auction_anomaly |
| 各市场股票列表 | `stock_list.py` | stock_cn/us/hk_lists 等 |
| 仅查代码 | `search_symbols.py` | search_symbols |

**默认规则**：用户说「XXX股票近日数据」「XXX怎么样」等模糊问题，默认用 `query_stock.py`（K线）。

---

## 调用方式

### 1. 近日K线（最常用）
```bash
python scripts/query_stock.py <股票名或代码> [--count N] [--interval day] [--adjust forward]
```
**interval**：`1m` `5m` `15m` `30m` `60m` `day`(默认) `week` `month` `quarter` `year`  
**adjust**：`forward`(前复权) `backward`(后复权) 空(不复权，默认)
```bash
python scripts/query_stock.py 贵州茅台
python scripts/query_stock.py 比亚迪 --count 20 --adjust forward
python scripts/query_stock.py 同花顺 --interval week --count 10
```

### 2. 实时行情快照
```bash
python scripts/market_snapshot.py <股票名或代码>
```

### 3. 日内分时
```bash
python scripts/intraday.py <股票名或代码>
```

### 4. 历史某日分时
```bash
python scripts/min_snapshot.py <股票名或代码> [--date YYYYMMDD]
```

### 5. 五档深度盘口
```bash
python scripts/depth_quote.py <股票名或代码>
```

### 6. 新闻资讯
```bash
python scripts/stock_news.py <股票名或代码>
```

### 7. 大单资金流向
```bash
python scripts/big_order.py <股票名或代码>
```

### 8. 分红送股权息历史
```bash
python scripts/corporate_action.py <股票名或代码>
```

### 9. 问财条件选股
```bash
python scripts/wencai.py <条件语句>
```

问财支持自然语言，直接把用户的筛选条件原文传入即可。常见用法分类：

**热度/排行类**
```bash
python scripts/wencai.py "热度排名前50只股票"
python scripts/wencai.py "今年以来涨幅最大的前50名，非ST"
python scripts/wencai.py "近一个月涨幅最大的前20只股票"
python scripts/wencai.py "今日换手率最高的前30只股票"
python scripts/wencai.py "近一周资金净流入最多的前20只股票"
```

**概念/板块类**
```bash
python scripts/wencai.py "脑机接口概念股"
python scripts/wencai.py "低空经济概念股"
python scripts/wencai.py "人工智能概念股，市值大于100亿"
python scripts/wencai.py "半导体行业股票"
```

**财务指标类**
```bash
python scripts/wencai.py "营业收入增长率>10%;营业利润增长率>10%;加权净资产收益率>15%;总资产报酬率>5%"
python scripts/wencai.py "ROE大于15%且市净率小于3"
python scripts/wencai.py "连续3年净利润增长且负债率小于50%"
python scripts/wencai.py "近三年每年分红且股息率大于4%"
```

**技术形态类**
```bash
python scripts/wencai.py "涨停"
python scripts/wencai.py "连续5日上涨"
python scripts/wencai.py "今日成交量大于昨日成交量的两倍"
python scripts/wencai.py "macd金叉且成交量放大"
python scripts/wencai.py "突破60日均线且成交量创近20日新高"
```

**综合筛选类**
```bash
python scripts/wencai.py "市值小于50亿的次新股，非ST，上市不足2年"
python scripts/wencai.py "科创板股票，净利润同比增长大于30%"
python scripts/wencai.py "北交所股票，市盈率低于20"
```

### 10. IPO数据
```bash
python scripts/ipo.py [--type today|wait]
# today=今日新股（默认），wait=待上市新股
```

### 11. 板块数据
```bash
python scripts/sector.py --type industry          # 行业板块列表
python scripts/sector.py --type concept           # 概念板块列表
python scripts/sector.py --type index             # 指数列表
python scripts/sector.py --constituents <板块代码>  # 板块成分股
```

### 12. 竞价异动
```bash
python scripts/auction_anomaly.py [--market USHA|USZA]
```

### 13. 市场股票列表
```bash
python scripts/stock_list.py --market cn|us|hk|bj|etf|futures|forex|bond|nasdaq
```

### 14. 仅搜索代码
```bash
python scripts/search_symbols.py <关键词>
```

---

## 返回数据处理

所有脚本返回 JSON，解析后向用户展示原则：

**K线（query_stock.py）**：表格呈现时间/开收高低/成交量，计算区间涨跌幅，点评趋势（上升/下跌/震荡）。

**实时行情（market_snapshot.py）**：重点展示价格、涨跌幅、成交量，与昨收对比。

**分时（intraday.py / min_snapshot.py）**：描述日内走势特点（开盘、波动区间、尾盘）。

**大单（big_order.py）**：统计买卖方向，说明主力动向。

**权息（corporate_action.py）**：按时间列出分红送股记录，计算近年股息率。

**问财（wencai.py）**：列出符合条件的股票数量和明细，按涨跌幅排序展示。

**IPO（ipo.py）**：展示股票名称、发行价、中签率、申购日期等关键字段。

**板块（sector.py）**：列出板块名称和代码；成分股时展示股票列表。

**竞价异动（auction_anomaly.py）**：按异动类型分组，重点关注涨停试盘信号。

**资讯（stock_news.py）**：用自己的话总结新闻要点，勿逐条罗列。

---

## 错误处理

脚本返回 `{"success": false, "error": "..."}` 时：
- 搜索不到：告知用户检查股票名称，可尝试股票代码
- K线失败：告知可能是账户权限问题或该股票代码不支持

---

## 安装与配置

### 1. 安装 SDK
```bash
pip install --upgrade thsdk
```

### 2. 账户配置

默认使用**临时游客账户**，无需任何配置，直接运行脚本即可：
```python
ths = THS()  # 自动使用临时账户
```
> ⚠️ 游客账户仅适合功能测试。

---

## 参考文档

完整 API 文档见 `references/thsdk_api.md`（包含所有接口的参数和返回示例）。
