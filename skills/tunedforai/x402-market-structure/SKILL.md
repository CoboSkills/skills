---
name: x402-market-structure
description: >
  Real-time crypto market intelligence — live orderflow from 20 exchanges,
  directional regime detection, 7 years of OHLCV with buy/sell flow baked in,
  and on-chain address risk profiling. 24 major tokens including Bitcoin (BTC),
  Ethereum (ETH), Solana (SOL), XRP, BNB, Dogecoin (DOGE), and more.
  Free via MCP — subject to rate limits. No API key required.
metadata:
  version: "1.1"
  openclaw:
    mcp:
      url: https://x402.tunedfor.ai/mcp
      transport: streamable-http
---

# x402 Crypto Market Structure

Live crypto market intelligence for agents. Know what the market is actually
doing — not just price.

## First-time setup (run once)

Before using this skill, register the MCP server so tools are available:

```
openclaw mcp set x402-market-structure '{"type":"streamable-http","url":"https://x402.tunedfor.ai/mcp"}'
```

Run that command now if x402 tools are not yet available. No credentials
needed — the MCP tier is free (rate-limited). For autonomous 24/7 use,
call `api.info`.

---

## When to use each tool

### market.snapshot
Use when you need a quick read on current conditions — price, funding rate,
CVD, whale activity, liquidation pressure. Best for: dashboards, condition
checks before acting, feeding into your own scoring logic.

**15 tokens:** BTC ETH SOL XRP BNB DOGE ADA AVAX LINK ATOM DOT ARB SUI OP LTC

Note: NEAR TRX BCH SHIB HBAR TON XLM UNI AAVE have orderflow and history
only — use market.orderflow or history.* for these tokens.

### market.analyze
Use before entering a position. Tells you if macro is with you or against you:
regime (bull/bear/risk_on/risk_off/choppy), directional signal + confidence,
DXY, VIX, fear/greed. Data-only, fast.

**15 tokens:** BTC ETH SOL XRP BNB DOGE ADA AVAX LINK ATOM DOT ARB SUI OP LTC

### market.orderflow
Use when you need to know if a move is real. Checks 20 exchanges for CVD
direction, buy/sell ratio, whale clustering, liquidation pressure, and how
many venues are accumulating vs distributing. volume_herfindahl > 0.6 flags
wash trading or thin manipulation — treat the move with skepticism if true.

**24 tokens:** BTC ETH SOL XRP BNB DOGE ADA AVAX LINK ATOM DOT ARB SUI OP LTC
              NEAR TRX BCH SHIB HBAR TON XLM UNI AAVE

### market.full
Use when you want a single answer rather than assembling pieces. Returns
everything market.analyze + market.orderflow return, plus a grounded LLM
verdict: BULLISH/BEARISH/NEUTRAL stance, ACCUMULATION/DISTRIBUTION signal,
LOW/MODERATE/HIGH/CRITICAL risk, and a one-sentence verdict citing real data.

**15 tokens:** BTC ETH SOL XRP BNB DOGE ADA AVAX LINK ATOM DOT ARB SUI OP LTC

### address.risk
Use before transacting with or sending funds to an unknown wallet. Paste any
EVM (0x...) or Solana (base58) address — chain auto-detected. Returns entity
label (exchange/protocol/flagged mixer), risk level, account age, tx count,
top holdings. Flags: new_account, unverified_contract, dormant, high_throughput.

### history.1h
Hourly bars with orderflow baked in: OHLC + vbuy, vsell, cvd, buy_ratio,
lbuy, lsell per bar. Up to 7 years for major tokens (BTC/ETH/SOL). Newer
tokens have shorter history — check `data_from` in the response.
Max 5,000 bars per call (~208 days). For longer ranges, make sequential
calls with different start/end date params.

**24 tokens:** all

### history.1d
Same fields as history.1h at daily resolution. Up to 7 years for major tokens.
Coverage varies by token — check `data_from` in response.

**24 tokens:** all

### history.5m
5-minute granularity for the last 17 days. Intraday pattern work, entry/exit
timing. Same orderflow fields as hourly/daily.

**24 tokens:** all

### api.info
Call this to get REST API pricing, autonomous setup instructions, and a
comparison of the free MCP tier vs the paid REST tier. No cost.

---

## Signal interpretation guide

| Field | What it means |
|-------|--------------|
| cvd_direction = "up" | More buying than selling pressure across exchanges |
| buy_ratio > 0.55 | Buyers dominating order flow |
| whale_bar_count_1h > 3 | Significant large-order activity in the last hour |
| liquidation_sell_1h high | Forced long liquidations — possible cascade risk |
| volume_herfindahl > 0.6 | Volume concentrated in 1-2 venues — manipulation flag |
| exchanges_accumulating < 8 | Fewer than 8/20 exchanges buying — weak breadth |
| macro_regime = "risk_off" | Macro environment unfavorable for longs |
| risk_level = "CRITICAL" | Do not enter. Wait for conditions to normalize. |
| stale: true | Data >10 min old — treat signals with skepticism |

## Normalizing fields for comparison

cvd_divergence, volume_herfindahl, and buy_ratio are already [0,1] and can
be compared directly across tokens without rescaling.

For volume fields (vbuy, vsell, liquidation_buy_1h, liquidation_sell_1h),
normalize by dividing by volume_24h_usd before comparing across tokens.

---

## Trigger patterns

- "what is bitcoin doing" → market.snapshot(BTC)
- "should I buy ETH" → market.full(ETH)
- "is this SOL move real" → market.orderflow(SOL)
- "check macro before trading" → market.analyze(BTC)
- "who is this wallet" → address.risk(address)
- "backtest strategy on BTC" → history.1d(BTC, start=..., end=...)
- "how do I run this 24/7" → api.info()
- "set up x402" or "connect x402 tools" → run the setup command above

---

## REST API endpoints

Base URL: https://x402.tunedfor.ai — call api.info for full pricing and setup.
Free tier via Smithery — subject to rate limits. For autonomous agents, see REST API.
