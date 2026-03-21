# THSDK API 快速参考

## 核心接口速查

### search_symbols — 搜索证券
```python
ths.search_symbols("同花顺")
# 返回: [{THSCODE, Name, Code, MarketStr, MarketDisplay, CodeDisplay}]
# MarketStr 前缀: USZA=深A, USHA=沪A, UBJA=北交所, UHKA=港股, UUSA=美股
```

### klines — K线
```python
ths.klines(thscode, count=10, interval="day", adjust="")
# interval: 1m/5m/15m/30m/60m/120m/day/week/month/quarter/year
# adjust: forward/backward/""
# 返回字段: 时间, 开盘价, 收盘价, 最高价, 最低价, 成交量, 总金额
```

### market_data_cn — A股实时行情
```python
ths.market_data_cn(thscode)
# 返回字段: 价格, 昨收价, 开盘价, 最高价, 最低价, 成交量, 总金额, 涨速, 名称
```

### intraday_data — 日内分时
```python
ths.intraday_data(thscode)
# 返回字段: 时间, 价格, 成交量, 总金额
```

### depth — 五档深度
```python
ths.depth(thscode)
# 返回字段: 买1-5价/量, 卖1-5价/量, 昨收价
```

### news — 资讯
```python
ths.news(code="1A0001", market="USHI")
# 返回字段: Time, Title, ID, Properties(含摘要summ)
```

## 其他常用接口
- `ths.big_order_flow(thscode)` — 大单数据
- `ths.corporate_action(thscode)` — 权息资料（分红送股）
- `ths.ths_industry()` — 行业板块列表
- `ths.ths_concept()` — 概念板块列表
- `ths.ipo_today()` — 今日IPO
- `ths.wencai_nlp(condition)` — 问财自然语言查询
