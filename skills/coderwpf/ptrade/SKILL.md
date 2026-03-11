---
name: ptrade
description: Ptrade quantitative trading platform by 恒生电子 — cloud-hosted Python strategies with broker-grade execution for Chinese securities.
version: 1.0.0
homepage: https://ptradeapi.com
metadata: {"clawdbot":{"emoji":"🏦","requires":{"bins":["python3"]}}}
---

# Ptrade (恒生量化交易平台)

[Ptrade](https://ptradeapi.com) is a professional quantitative trading platform by 恒生电子 (Hundsun). Strategies run on **broker servers** (intranet), providing low-latency execution. It uses an event-driven Python framework.

> ⚠️ **Requires broker account with Ptrade access**. Strategies run in broker's cloud — no internet access from within strategies. Cannot install pip packages; only built-in third-party libraries are available.

## Supported markets & business types

**Backtest supports:**
1. 普通股票买卖 (单位：股)
2. 可转债买卖 (单位：张，T+0)
3. 融资融券担保品买卖 (单位：股)
4. 期货投机类型交易 (单位：手，T+0)
5. LOF基金买卖 (单位：股)
6. ETF基金买卖 (单位：股)

**Trading (live) supports:**
1. 普通股票买卖 (单位：股)
2. 可转债买卖 (T+0)
3. 融资融券交易 (单位：股)
4. ETF申赎、套利 (单位：份)
5. 国债逆回购 (单位：份)
6. 期货投机类型交易 (单位：手，T+0)
7. ETF基金买卖 (单位：股)

**Default supports Level2 十档行情**, some brokers provide free L2 逐笔数据.

### Price decimal rules

| Asset | Min tick | Decimals |
|---|---|---|
| Stock | 0.01 | 2 |
| Convertible bond | 0.001 | 3 |
| LOF / ETF | 0.001 | 3 |
| Reverse repo | 0.005 | 3 |
| Stock index futures | 0.2 | 1 |
| Treasury futures | 0.005 | 3 |
| ETF options | 0.0001 | 4 |

> ⚠️ When using `limit_price` in order functions, price must match the correct decimal precision or the order will be rejected.

## Stock code format

- Shanghai: `600570.SS`
- Shenzhen: `000001.SZ`
- Index: `000300.SS` (沪深300)

---

## Strategy lifecycle (event-driven)

```python
def initialize(context):
    """Required — called once at startup. Use for setting universe, benchmark, scheduling."""
    g.security = '600570.SS'
    set_universe(g.security)

def before_trading_start(context, data):
    """Optional — called before market open.
    In backtest: runs at 8:30 each trading day.
    In trading: runs immediately on first start, then daily at 9:10 (default, broker configurable)."""
    log.info('Pre-market preparation')

def handle_data(context, data):
    """Required — called on each bar.
    Daily mode: runs once at 14:50 (default).
    Minute mode: runs every minute at each bar close.
    data[sid] provides: open, high, low, close, price, volume, money."""
    current_price = data[g.security]['close']
    cash = context.portfolio.cash

def after_trading_end(context, data):
    """Optional — called after market close at 15:30."""
    log.info('Trading day ended')

def tick_data(context, data):
    """Optional — called every 3 seconds during 9:30-14:59 (trading only).
    Must use order_tick() for orders inside this function.
    data is dict: {stock_code: {'order': DataFrame/None, 'tick': DataFrame, 'transcation': DataFrame/None}}"""
    for stock, d in data.items():
        tick = d['tick']
        price = tick['last_px']
        bid1 = tick['bid_grp'][1]       # [price, volume, order_count]
        ask1 = tick['offer_grp'][1]     # [price, volume, order_count]
        log.info(f'{stock}: {price}, up={tick["up_px"]}, down={tick["down_px"]}')
        # Level2 fields (requires L2 permission, otherwise None):
        order_data = d['order']         # 逐笔委托: business_time, hq_px, business_amount, order_no, business_direction, trans_kind
        trans_data = d['transcation']   # 逐笔成交: business_time, hq_px, business_amount, trade_index, business_direction, buy_no, sell_no

def on_order_response(context, order_list):
    """Optional — called when order status changes (faster than get_orders).
    order_list is list of dicts with: entrust_no, stock_code, amount, price, business_amount, status, order_id, entrust_type, entrust_prop, error_info, order_time."""
    for o in order_list:
        log.info(f'Order {o["stock_code"]}: status={o["status"]}, filled={o["business_amount"]}/{o["amount"]}')

def on_trade_response(context, trade_list):
    """Optional — called when trade executes (faster than get_trades).
    trade_list is list of dicts with: entrust_no, stock_code, business_amount, business_price, business_balance, business_id, status, order_id, entrust_bs, business_time.
    Note: if status=9, it's a waste order (废单)."""
    for t in trade_list:
        direction = 'BUY' if t['entrust_bs'] == '1' else 'SELL'
        log.info(f'{direction} {t["stock_code"]}: {t["business_amount"]}@{t["business_price"]}')
```

### Strategy running cycles

| Mode | Frequency | Execution time |
|---|---|---|
| **Daily** | Once/day | Backtest: 15:00, Trading: 14:50 (configurable) |
| **Minute** | Once/min | At each minute bar close |
| **Tick** | Every 3s | 9:30–14:59, via `tick_data` or `run_interval` |

### Timing reference

| Phase | Time | Functions |
|---|---|---|
| **Pre-market** | Before 9:30 | `before_trading_start`, `run_daily(time='09:15')` |
| **Intraday** | 9:30–15:00 | `handle_data`, `run_daily`, `run_interval`, `tick_data` |
| **After-market** | 15:30 | `after_trading_end`, `run_daily(time='15:10')` |

---

## Setup functions (in initialize only)

### Stock universe & benchmark

```python
def initialize(context):
    set_universe(['600570.SS', '000001.SZ'])   # required: set stock pool
    set_benchmark('000300.SS')                  # backtest benchmark
```

### Commission & slippage (backtest only)

```python
def initialize(context):
    set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, unit='perValue', min_cost=5))
    set_slippage(FixedSlippage(0.02))           # or set_fixed_slippage(0.02)
    set_volume_ratio(0.025)                     # max trade as % of daily volume
    set_limit_mode(0)                           # 0=percent of volume, 1=fixed amount
```

### Scheduled tasks

```python
def initialize(context):
    # run_daily: execute func at specific time each day
    run_daily(context, my_morning_task, time='09:31')
    run_daily(context, my_afternoon_task, time='14:50')

    # run_interval: execute func every N seconds (trading only, min 3s)
    run_interval(context, my_tick_handler, seconds=10)
```

### Strategy parameters (configurable from UI)

```python
def initialize(context):
    set_parameters(
        context,
        ma_fast=5,         # can be changed from Ptrade UI without modifying code
        ma_slow=20,
        position_ratio=0.95
    )
```

### Bottom position (底仓)

```python
def initialize(context):
    set_yesterday_position(convert_position_from_csv('positions.csv'))
```

---

## Data functions

### get_history — recent N bars

```python
get_history(count, frequency='1d', field='close', security_list=None, fq=None, include=False, fill='nan', is_dict=False)
```

```python
# Get last 20 days OHLCV
df = get_history(20, '1d', ['open', 'high', 'low', 'close', 'volume'], '600570.SS', fq='pre')

# K-line frequencies: 1m, 5m, 15m, 30m, 60m, 120m, 1d, 1w/weekly, mo/monthly, 1q/quarter, 1y/yearly
# fq: None (no adjust), 'pre' (前复权), 'post' (后复权), 'dypre' (动态前复权)
# fields: open, high, low, close, volume, money, price, is_open, preclose, high_limit, low_limit, unlimited (日线only)
```

### get_price — date range query

```python
get_price(security, start_date=None, end_date=None, frequency='1d', fields=None, fq=None, count=None, is_dict=False)
```

```python
# By date range
df = get_price('600570.SS', start_date='20240101', end_date='20240630', frequency='1d',
               fields=['open', 'high', 'low', 'close', 'volume'])

# By count (last N bars)
df = get_price('600570.SS', end_date='20240630', frequency='1d', count=20)

# Multiple stocks
df = get_price(['600570.SS', '000001.SZ'], start_date='20240101', end_date='20240630')

# Minute data
df = get_price('600570.SS', start_date='2024-06-01 09:30', end_date='2024-06-01 15:00', frequency='5m')
```

> ⚠️ `get_history` and `get_price` cannot be called concurrently from different threads (e.g. `run_daily` + `handle_data` at same time).

### get_snapshot — real-time quote (trading only)

```python
snapshot = get_snapshot('600570.SS')
# Returns dict with fields:
# last_px (最新价), open_px (开盘), high_px (最高), low_px (最低), preclose_px (昨收)
# up_px (涨停价), down_px (跌停价), business_amount (总成交量), business_balance (总成交额)
# bid_grp (买档: {1:[price,vol,count], 2:...}), offer_grp (卖档)
# pe_rate (动态市盈率), pb_rate (市净率), turnover_ratio (换手率), vol_ratio (量比)
# entrust_rate (委比), entrust_diff (委差), wavg_px (加权均价), px_change_rate (涨跌幅)
# circulation_amount (流通股本), trade_status (交易状态)
# business_amount_in (内盘), business_amount_out (外盘)

# Multiple stocks
snapshots = get_snapshot(['600570.SS', '000001.SZ'])
price = snapshots['600570.SS']['last_px']
```

### get_gear_price — order book depth (trading only)

```python
gear = get_gear_price('600570.SS')
# Returns: {'bid_grp': {1: [price, vol, count], 2: ...}, 'offer_grp': {1: [price, vol, count], 2: ...}}
bid1_price, bid1_vol, bid1_count = gear['bid_grp'][1]
ask1_price, ask1_vol, ask1_count = gear['offer_grp'][1]

# Multiple stocks
gears = get_gear_price(['600570.SS', '000001.SZ'])
```

### get_trend_data — auction period data

```python
data = get_trend_data('600570.SS')  # 获取集中竞价期间数据
```

### Level2 data (requires L2 permission)

```python
# 逐笔委托
entrust = get_individual_entrust(
    stocks=['600570.SS'],
    data_count=50,       # max 200
    start_pos=0,
    search_direction=1,  # 1=forward, 2=backward
    is_dict=False        # True for faster dict return
)
# Fields: business_time, hq_px, business_amount, order_no, business_direction (0=sell,1=buy), trans_kind (1=market,2=limit,3=best)

# 逐笔成交
transaction = get_individual_transaction(
    stocks=['600570.SS'],
    data_count=50,
    is_dict=False
)
# Fields: business_time, hq_px, business_amount, trade_index, business_direction, buy_no, sell_no, trans_flag

# 分时成交
tick_dir = get_tick_direction('600570.SS')
```

### get_sort_msg — sector/industry ranking

```python
# 获取板块、行业涨幅排名
sort_data = get_sort_msg(sector='行业', sort_key='涨跌幅', count=10)
```

---

## Stock & reference data

### Basic info

```python
name = get_stock_name('600570.SS')               # 股票名称
info = get_stock_info('600570.SS')                # 基础信息
status = get_stock_status('600570.SS')            # 状态 (停牌/涨跌停等)
exrights = get_stock_exrights('600570.SS')        # 除权除息信息
blocks = get_stock_blocks('600570.SS')            # 所属板块

stocks = get_index_stocks('000300.SS')            # 指数成分股
stocks = get_industry_stocks('银行')              # 行业成分股
stocks = get_Ashares()                            # 全部A股
etfs = get_etf_list()                             # ETF列表
```

### Convertible bond data

```python
cb_codes = get_cb_list()                          # 可转债代码表
cb_info = get_cb_info()                           # 可转债基础信息 DataFrame
# Fields: bond_code, bond_name, stock_code, stock_name, list_date,
#         premium_rate (溢价率%), convert_date, maturity_date,
#         convert_rate, convert_price, convert_value
```

### ETF info

```python
etf_info = get_etf_info('510050.SS')              # ETF基本信息
etf_stocks = get_etf_stock_info('510050.SS')      # ETF成分券
etf_list = get_etf_stock_list('510050.SS')        # ETF成分券列表
```

### REITs

```python
reits_list = get_reits_list()                     # REITs代码列表
```

### Financial data

```python
get_fundamentals(security, table, fields=None, date=None, start_year=None, end_year=None,
                 report_types=None, date_type=None, merge_type=None)
```

```python
# By date (returns latest report before date)
df = get_fundamentals('600570.SS', 'balance_statement', 'total_assets', date='20240630')

# By year range
df = get_fundamentals('600570.SS', 'income_statement', fields=['revenue', 'net_profit'],
                      start_year='2022', end_year='2024')

# report_types: '1'=Q1, '2'=H1, '3'=Q3, '4'=annual
# date_type: None=by publish date, 1=by accounting period
# merge_type: None=original data (avoid future data), 1=latest revised data

# Tables: balance_statement, income_statement, cash_flow_statement, valuation, indicator
```

> ⚠️ Rate limit: max 100 calls/second, max 500 data items per call. Add `sleep` for batch queries.

### Market info & trading calendar

```python
today = get_trading_day()                         # 当前交易日
all_days = get_all_trades_days()                  # 全部交易日列表
days = get_trade_days('2024-01-01', '2024-06-30') # 指定范围
markets = get_market_list()                       # 市场列表
detail = get_market_detail('SH')                  # 市场详情
```

### Other info

```python
account = get_user_name()                         # 资金账号
path = get_research_path()                        # 研究路径 (for file I/O)
trades_file = get_trades_file()                   # 对账数据文件
deliver = get_deliver(start_date='20240101', end_date='20240630')  # 历史交割单
fundjour = get_fundjour()                         # 资金流水
trade_name = get_trade_name()                     # 交易名称
lucky_info = get_lucky_info()                     # 中签信息
```

---

## Trading functions

### order — buy/sell by quantity

```python
order(security, amount, limit_price=None)
# amount: positive=buy, negative=sell
# Returns: order_id (str) or None

order('600570.SS', 100)                           # buy 100 shares at latest price
order('600570.SS', 100, limit_price=39.0)         # buy at limit price
order('600570.SS', -500)                          # sell 500 shares
order('131810.SZ', -10)                           # 国债逆回购 1000元 (10张)
```

### order_target — target quantity

```python
order_target('600570.SS', 1000)                   # adjust to hold 1000 shares
order_target('600570.SS', 0)                      # clear position
```

### order_value — buy by value

```python
order_value('600570.SS', 100000)                  # buy ¥100,000 worth
```

### order_target_value — target market value

```python
order_target_value('600570.SS', 200000)           # adjust to hold ¥200,000 worth
```

### order_market — market order types (trading only)

```python
order_market(security, amount, market_type, limit_price=None)
# market_type:
#   0 = 对手方最优价格
#   1 = 最优五档即时成交剩余转限价 (SH only, requires limit_price)
#   2 = 本方最优价格
#   3 = 即时成交剩余撤销 (SZ only)
#   4 = 最优五档即时成交剩余撤销
#   5 = 全额成交或撤单 (SZ only)

order_market('600570.SS', 100, 0, limit_price=35.0)    # SH: 对手方最优 + 保护限价
order_market('000001.SZ', 100, 4)                       # SZ: 最优五档即时成交剩余撤销
```

> ⚠️ SH stocks require `limit_price` for `order_market`. Does not support convertible bonds.

### order_tick — tick-triggered order (in tick_data only)

```python
def tick_data(context, data):
    order_tick('600570.SS', 100, limit_price=39.0)
```

### cancel_order

```python
cancel_order(order_id)
cancel_order_ex(order_id)                         # extended cancel
```

### IPO subscription

```python
ipo_stocks_order()                                # one-click new share/bond subscription
```

### After-hours order (盘后固定价)

```python
after_trading_order('600570.SS', 100)             # 盘后固定价委托
after_trading_cancel_order(order_id)              # 盘后撤单
```

### Debt-to-stock (债转股)

```python
debt_to_stock_order('128000.SZ', 100)
```

### ETF operations

```python
# ETF成分券篮子下单
etf_basket_order('510050.SS', 1,
                 price_style='S3',     # B1-B5(买档), S1-S5(卖档), 'new'(最新价)
                 position=True,        # use existing holdings as substitution
                 info={'600000.SS': {'cash_replace_flag': 1, 'position_replace_flag': 1, 'limit_price': 12}})

# ETF申购/赎回
etf_purchase_redemption('510050.SS', 900000)      # positive = purchase
etf_purchase_redemption('510050.SS', -900000)     # negative = redemption
```

---

## Query functions

### Positions

```python
pos = get_position('600570.SS')
# Position object: amount, cost_basis, last_sale_price, sid, ...

positions = get_positions(['600570.SS', '000001.SZ'])  # multiple stocks
```

### Orders

```python
open_orders = get_open_orders()                   # unfilled orders
order = get_order(order_id)                       # specific order
orders = get_orders()                             # all orders today (from strategy)
all_orders = get_all_orders()                     # all orders today (including manual)
trades = get_trades()                             # today's trades
```

### Portfolio (via context)

```python
context.portfolio.cash                            # available cash
context.portfolio.total_value                     # total asset value (cash + positions)
context.portfolio.positions_value                 # positions market value
context.portfolio.positions                       # dict of Position objects
context.capital_base                              # initial capital
context.previous_date                             # previous trading date
context.blotter.current_dt                        # current datetime
```

---

## Margin trading (融资融券)

### Trading

```python
margin_trade('600570.SS', 1000, limit_price=39.0) # 担保品买卖
margincash_open('600570.SS', 1000, limit_price=39.0)   # 融资买入
margincash_close('600570.SS', 1000, limit_price=40.0)  # 卖券还款
margincash_direct_refund(amount=100000)                 # 直接还款
marginsec_open('600570.SS', 1000, limit_price=40.0)    # 融券卖出
marginsec_close('600570.SS', 1000, limit_price=39.0)   # 买券还券
marginsec_direct_refund('600570.SS', 1000)              # 直接还券
```

### Query

```python
cash_stocks = get_margincash_stocks()             # 融资标的列表
sec_stocks = get_marginsec_stocks()               # 融券标的列表
contract = get_margin_contract()                  # 合约查询
contract_real = get_margin_contractreal()         # 实时合约流水
margin_asset = get_margin_assert()                # 信用资产
assure_list = get_assure_security_list()           # 担保券列表
max_buy = get_margincash_open_amount('600570.SS')  # 融资最大可买
max_sell = get_margincash_close_amount('600570.SS') # 卖券还款最大可卖
max_short = get_marginsec_open_amount('600570.SS') # 融券最大可卖
max_cover = get_marginsec_close_amount('600570.SS') # 买券还券最大可买
entrans = get_margin_entrans_amount('600570.SS')   # 现券还券数量
enslo_info = get_enslo_security_info('600570.SS')  # 融券信息
crdt_fund = get_crdt_fund()                        # 可融资金
```

---

## Futures trading (期货)

### Trading

```python
buy_open('IF2401.CFX', 1, limit_price=3500.0)     # 多开
sell_close('IF2401.CFX', 1, limit_price=3550.0)   # 多平
sell_open('IF2401.CFX', 1, limit_price=3550.0)    # 空开
buy_close('IF2401.CFX', 1, limit_price=3500.0)    # 空平
```

### Query & settings (backtest)

```python
margin_rate = get_margin_rate('IF2401.CFX')       # 保证金比例
instruments = get_instruments('IF2401.CFX')       # 合约信息
set_future_commission(0.000023)                   # 设置期货手续费 (backtest)
set_margin_rate('IF2401.CFX', 0.15)               # 设置保证金比例 (backtest)
```

---

## Technical indicators (built-in)

```python
macd = get_MACD('600570.SS', N1=12, N2=26, M=9)
kdj = get_KDJ('600570.SS', N=9, M1=3, M2=3)
rsi = get_RSI('600570.SS', N=14)
cci = get_CCI('600570.SS', N=14)
```

---

## Utility functions

```python
log.info('message')                               # 日志记录 (also log.warn, log.error)
is_trade('600570.SS')                             # 判断是否可交易
check_limit('600570.SS')                          # 涨跌停状态判断
permission_test()                                 # 权限校验
freq = get_frequency()                            # 当前策略运行周期
biz_type = get_business_type()                    # 当前业务类型
filtered = filter_stock_by_status(stocks, status='停牌')  # 过滤指定状态股票
check_strategy()                                  # 检查策略内容
create_dir('/path/to/dir')                        # 创建目录
```

### Notifications

```python
send_email(context, subject='Signal', content='Buy 600570', to_address='you@email.com')
send_qywx(context, msg='Buy signal triggered')   # 企业微信
```

### Fund transfer

```python
fund_transfer(amount=100000, direction=1)         # 资金调拨
market_fund_transfer(amount=100000, from_market='SH', to_market='SZ')  # 市场间资金调拨
```

---

## Global object & context

```python
# g — global object (persists across bars, auto-serialized for persistence)
g.my_var = 100
g.stock_list = ['600570.SS', '000001.SZ']
# Variables starting with '__' are private and NOT persisted:
g.__my_class_instance = SomeClass()

# context — strategy context
context.portfolio.cash              # available cash
context.portfolio.total_value       # total asset value
context.portfolio.positions_value   # positions market value
context.portfolio.positions         # dict of Position objects
context.capital_base                # initial capital
context.previous_date               # previous trading date
context.blotter.current_dt          # current datetime (datetime.datetime)
context.blotter.current_dt.strftime("%Y-%m-%d")   # formatted date
context.blotter.current_dt.isoweekday()           # weekday (1=Mon, 7=Sun)
```

---

## Persistence (持久化)

Ptrade auto-persists `g` object (global variables) using pickle after `before_trading_start`, `handle_data`, and `after_trading_end`. On restart, `initialize` runs first, then persisted data overwrites.

For custom persistence:

```python
import pickle
NOTEBOOK_PATH = get_research_path()

def initialize(context):
    try:
        with open(NOTEBOOK_PATH + 'hold_days.pkl', 'rb') as f:
            g.hold_days = pickle.load(f)
    except:
        g.hold_days = {}
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    # ... trading logic ...
    with open(NOTEBOOK_PATH + 'hold_days.pkl', 'wb') as f:
        pickle.dump(g.hold_days, f, -1)
```

> ⚠️ IO objects (open files, class instances) cannot be serialized. Use `g.__private_var` (double underscore prefix) for non-serializable objects.

---

## Strategy examples

### Example 1: Auction chase limit-up (集合竞价追涨停)

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)
    run_daily(context, aggregate_auction_func, time='9:23')

def aggregate_auction_func(context):
    stock = g.security
    snapshot = get_snapshot(stock)
    price = snapshot[stock]['last_px']
    up_limit = snapshot[stock]['up_px']
    if float(price) >= float(up_limit):
        order(g.security, 100, limit_price=up_limit)

def handle_data(context, data):
    pass
```

### Example 2: Tick-level MA strategy (tick级别均线)

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)
    run_interval(context, func, seconds=3)

def before_trading_start(context, data):
    history = get_history(10, '1d', 'close', g.security, fq='pre', include=False)
    g.close_array = history['close'].values

def func(context):
    stock = g.security
    snapshot = get_snapshot(stock)
    price = snapshot[stock]['last_px']
    ma5 = (g.close_array[-4:].sum() + price) / 5
    ma10 = (g.close_array[-9:].sum() + price) / 10
    cash = context.portfolio.cash

    if ma5 > ma10:
        order_value(stock, cash)
        log.info('Buying %s' % stock)
    elif ma5 < ma10 and get_position(stock).amount > 0:
        order_target(stock, 0)
        log.info('Selling %s' % stock)

def handle_data(context, data):
    pass
```

### Example 3: Dual MA with persistence (双均线 + 持久化)

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    security = g.security
    df = get_history(20, '1d', 'close', security, fq=None, include=False)
    ma5 = df['close'][-5:].mean()
    ma20 = df['close'][-20:].mean()
    current_price = data[security]['close']
    cash = context.portfolio.cash
    position = get_position(security)

    if current_price > 1.01 * ma20 and position.amount == 0:
        order_value(security, cash * 0.95)
        log.info(f'Buy {security}')
    elif current_price < ma5 and position.amount > 0:
        order_target(security, 0)
        log.info(f'Sell {security}')
```

### Example 4: Auto reverse repo + IPO (盘后逆回购 + 新股申购)

```python
def initialize(context):
    g.security = '131810.SZ'
    set_universe(g.security)
    run_daily(context, reverse_repo, time='14:50')
    run_daily(context, ipo_subscribe, time='09:31')

def reverse_repo(context):
    cash = context.portfolio.cash
    lots = int(cash / 1000) * 10
    if lots >= 10:
        order(g.security, -lots)
        log.info(f'Reverse repo: {lots} lots')

def ipo_subscribe(context):
    ipo_stocks_order()
    log.info('IPO subscription submitted')

def handle_data(context, data):
    pass
```

---

## Order status codes

| status | Description |
|---|---|
| 0 | 未报 (not sent) |
| 1 | 待报 (pending) |
| 2 | 已报 (submitted) |
| 5 | 部分成交 (partially filled) |
| 6 | 全部成交 (fully filled, in backtest) |
| 7 | 部撤 (partially cancelled) |
| 8 | 全部成交 (fully filled, in trading) |
| 9 | 废单 (rejected/waste) |
| a | 已撤 (cancelled) |

---

## Tips

- Strategies run on **broker intranet servers** — no internet access, no `pip install`.
- Use `g` (global object) to persist variables across function calls. Variables with `__` prefix are not persisted.
- Built-in libraries include: pandas, numpy, talib, scipy, sklearn, etc.
- `handle_data` frequency depends on strategy period setting (tick/1m/5m/1d etc.).
- Backtest and live trading use the same code — `set_commission`/`set_slippage` are backtest-only.
- Always add exception handling (`try/except`) in trading strategies to prevent termination.
- `get_history` and `get_price` **cannot be called concurrently** from different threads.
- When using limit orders, ensure price decimal precision matches the asset type.
- Multiple strategies running concurrently have **independent** callback events.
- Use `get_research_path()` for file I/O (reading/writing CSVs, pickle files).
- Docs: https://ptradeapi.com
- QMT API docs: http://qmt.ptradeapi.com
