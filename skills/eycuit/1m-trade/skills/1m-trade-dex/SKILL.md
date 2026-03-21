---
name: 1m-trade-dex
description: |
  A CLI tool built on the official Hyperliquid Python SDK (`hyperliquid-python-sdk`). It provides one-stop management for Hyperliquid: wallet state queries, perp trading, market data, price discovery, symbol metadata, positions and orders, with HIP-3 compatibility.
metadata:
  openclaw:
    emoji: "🚀"
    os:
      - darwin
      - linux
      - win32
    tags:
      - crypto
      - news
      - trading
      - hyperliquid
      - wallet
      - dex
      - automation
---
## CLI entrypoint
CLI entry: `scripts/hl.py`

Recommended: run from the skill directory: `python3 scripts/hl.py ...`

If installed under the OpenClaw workspace, the default path is:
`~/.openclaw/workspace/skills/1m-trade/skills/1m-trade-dex/scripts/hl.py`

## Prerequisites
**Directory note**
- The `scripts/` directory referenced in this document is located at `skills/1m-trade-dex/scripts/`.

### 1) Runtime requirements
- Python 3.9+
- Install dependencies (including `hyperliquid-python-sdk`) from this skill's `scripts/` directory.
```bash
cd ~/workspace/skills/1m-trade/skills/1m-trade-dex/scripts
pip install -r requirements.txt
```
After installing, write a marker file under the OpenClaw state dir:
- If `OPENCLAW_STATE_DIR` is set: `$OPENCLAW_STATE_DIR/.1m-trade/dependencies-status.md`
- Otherwise: `~/.openclaw/.1m-trade/dependencies-status.md`
```
# Dependency install marker - do not edit manually
Installed: true
Skills: 1m-trade-dex
Skills Path: <skill path>
LastChecked: 2026-03-15 14:30:00 UTC
```

### Constraints
- If the user cannot open a position (e.g., insufficient margin), do not close other positions unless the user explicitly requests it.

### Basic syntax
```bash
# Full command
python3 scripts/hl.py [--testnet] <command> [command_args]
```
### Core flags
- `--testnet`: optional, use testnet (default is mainnet)

### Command list
Note: for any asset name (e.g. `--coin`), you can run `query-meta` to confirm the exact symbol. For example, user input "gold" often maps to `xyz:GOLD`. Always pass the canonical symbol.

#### 1) Query commands
| Command | Description | Example |
|------|------|------|
| `query-user-state` | Query user state (positions + balances). Optional address override; structure follows the API/SDK response. | `python3 scripts/hl.py query-user-state --address 0x123...` |
| `query-open-orders` | Query open orders | `python3 scripts/hl.py --testnet query-open-orders` |
| `query-fills` | Query fills / trade history | `python3 scripts/hl.py query-fills` |
| `query-meta` | Query asset metadata (all symbols) | `python3 scripts/hl.py query-meta` |
| `query-mids` | Query mid prices (all symbols) | `python3 scripts/hl.py query-mids` |
| `query-kline` | Query kline/candles for a symbol | `python3 scripts/hl.py query-kline --coin BTC --period 15m --start 1772511125000 --end 1772597525000` |

**Retry rule (query commands only)**:
- If a query command returns an empty result (null/None, empty string, empty list/array, empty object/dict, or no meaningful fields), retry the **same command** exactly once.
- Do not change any args/flags/symbols/time ranges/formatting between the first attempt and the retry.
- If the second attempt is still empty, stop retrying and report: the command you ran, that it returned empty twice, and a brief possible cause (no data, endpoint delay, wrong symbol, no account activity).

### Query command arguments

#### `query-user-state`
- `--address`: optional. If omitted, the address is derived from the configured private key.

#### `query-kline`
- `--coin`: required. Symbol such as `BTC`, `ETH`, or `xyz:TSLA`. Use `query-meta` to confirm the canonical symbol first.
- `--period`: required. One of: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`.
- `--start`: optional (ms). Default is the start of the last 24 hours.
- `--end`: optional (ms). Default is the current timestamp in ms.

#### 2) Trading commands
| Command | Description | Example |
|------|------|------|
| `place-order` | Place a limit order (HIP-3 supported) | `python3 scripts/hl.py place-order --coin BTC --is-buy True --qty 0.01 --limit-px 50000 --tif Gtc` |
| `market-order` | Place a market order (recommended for HIP-3) | `python3 scripts/hl.py --testnet market-order --coin ETH --is-buy True --qty 0.1 --slippage 0.01` |
| `market-close` | Close a position with a market order (recommended for HIP-3) | `python3 scripts/hl.py market-close --coin ETH --qty 0.1 --slippage 0.01` |
| `cancel-order` | Cancel orders | `python3 scripts/hl.py cancel-order --oid 123456 --coin HYPE` |
| `update-leverage` | Update leverage | `python3 scripts/hl.py update-leverage --coin BTC --leverage 10 --is-cross True` |
| `update-isolated-margin` | Transfer isolated margin (HIP-3) | `python3 scripts/hl.py update-isolated-margin --coin xyz:GOLD --amount 10` |

### Trading command arguments
#### General rules
1. For `--coin`, always resolve the canonical symbol (use `query-meta` if needed).
2. For `--qty`, use `query-meta` results (e.g. `szDecimals`) to format the quantity precision correctly.

#### `update-isolated-margin`
- `--coin`: required. Canonical symbol.
- `--amount`: required. Transfer amount.

#### `place-order`
- `--coin`: required.
- `--is-buy`: required (True/False). True = long, False = short.
- `--qty`: required.
- `--limit-px`: required.
- `--tif`: optional (`Gtc`/`Ioc`/`Alo`, default `Gtc`).
- `--reduce-only`: optional (default False).

#### `market-order`
- `--coin`: required.
- `--is-buy`: required (True/False). True = long, False = short.
- `--qty`: required.
- `--slippage`: optional (default 0.02 = 2%).

#### `market-close`
- `--coin`: required.
- `--qty`: required.
- `--slippage`: optional (default 0.02 = 2%).

#### `cancel-order`
- `--coin`: optional; cancel all orders for a given symbol
- `--oid`: optional; cancel a specific order id
- If neither is provided, cancel all open orders.

#### `update-leverage`
- `--coin`: required.
- `--leverage`: required (integer).
- `--is-cross`: optional (True/False, default True).

## Output
All commands print formatted JSON for easy parsing:
- Query commands: full data for the requested dimension
- Trading commands: results for order submit/cancel/leverage updates (success flags, order IDs, etc.)

## Error handling
- Network issues: handled by the SDK with error messages
- Invalid trading parameters: returns official Hyperliquid error responses

## Notes
1. Private keys are sensitive. Do not expose or share them.
2. Testnet vs mainnet are strictly separated. Confirm `--testnet` before acting.
3. Adjust slippage for market orders based on volatility; too small may fail.
4. Leverage trading is risky. Choose leverage carefully.
5. If using a proxy/private-key setup, ensure `HYPERLIQUID_WALLET_ADDRESS` is set; otherwise trading may fail.

## Summary
- `1m-trade-dex` is built on `hyperliquid-python-sdk` to query wallet/trading/market data and execute perp trades.
- It provides query commands and trading commands, supports mainnet/testnet switching, and prints structured JSON output.