# Usage Guide

## Prerequisites

安装并使用本 skill 前，至少需要准备：
- Python 3
- `requests` 依赖
- `NOAH_API_BASE_URL`
- `NOAH_MARKET_APIKEY`

默认配置文件位置：
- `<repo-or-workspace-root>/.secrets/noah-market.env`

未配置 API key 时，skill 虽然可以被加载，但无法执行真实行情查询。

> 注意：`NOAH_MARKET_APIKEY` 必须是公司证券行情服务的 API key，不能使用 GitHub token 或其他平台凭证替代。

## Recommended Entry Order

### 1. 精准调用
优先使用：
- `scripts/run_query.py`

适用于：
- 已知意图
- 已知标准代码
- 调试接口与参数

示例：
```bash
python3 scripts/run_query.py snapshot HK-00700
python3 scripts/run_query.py kline HK-00700 num=10 ktype=K_DAY
python3 scripts/run_query.py capital_flow HK-00700 num=5
```

### 2. 自然语言入口
当用户直接说自然语言时，可先用：
- `scripts/route_query.py`

示例：
```bash
python3 scripts/route_query.py 看腾讯最近10根日K
python3 scripts/route_query.py 看腾讯资金流向
python3 scripts/route_query.py 看腾讯盘口
```

### 3. 健康检查
在怀疑配置或接口异常时，使用：
- `scripts/smoke_test.py`
- `scripts/nl_smoke_test.py`

## Verified HK Scenarios

当前已验证较稳定的港股场景：
- 快照 / 最新行情
- 市场状态
- 分时
- K线
- 摆盘
- 资金流向
- 基础信息

## Caution

- 美股自然语言解析已具备基础能力，但美股 K 线接口当前返回 404，需继续排查。
- 板块与期权相关接口当前环境未完全开放，不应作为一期强承诺能力。
- 面向最终用户使用时，默认采用“股票帮手模式”，不要把接口和内部实现细节直接暴露给用户。
