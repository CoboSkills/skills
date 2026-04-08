---
name: Global Financial Downloader
slug: global-financial-downloader
version: 1.0.0
description: "全球财报智能下载器。自动识别市场（A 股/港股/美股），自动选择爬虫，支持股票代码/公司名称，一键下载全球三大市场财报。"
metadata: {"clawdbot":{"emoji":"🌍","requires":{"bins":["python3.11"],"pip":["requests","beautifulsoup4","playwright"]},"os":["linux","darwin","win32"]}}
---

## When to Use

- Download financial reports from global markets (A-shares, HK, US)
- Automatically identify market from stock code
- Batch download annual/interim/quarterly reports
- Support both stock codes and company names

## Quick Start

### Download Single Company

```bash
# Use stock code (recommended - supports all companies)
python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
  600519 --from=2020 --to=2025 --type=年报 --pdf

# Use company name (predefined companies only)
python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
  贵州茅台 --from=2020 --to=2025 --pdf
```

### Batch Download

```bash
# Create a script for batch download
cat > download_all.sh << 'EOF'
#!/bin/bash
stocks=("600519 贵州茅台" "00700 腾讯" "AAPL 苹果")
for stock in "${stocks[@]}"; do
    code=$(echo $stock | cut -d' ' -f1)
    python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
      $code --from=2020 --to=2024 --pdf
done
EOF
chmod +x download_all.sh
./download_all.sh
```

## Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `stock` | Stock code or company name | Required | `600519`, `贵州茅台`, `AAPL` |
| `--from` | Start year | 2020 | `--from=2020` |
| `--to` | End year | 2025 | `--to=2025` |
| `--type` | Report type | 年报 | `年报`, `中报`, `10-K`, `10-Q` |
| `--pdf` | Download PDF files | No | `--pdf` |
| `--no-pdf` | Skip PDF download | No | `--no-pdf` |

## Supported Markets

### A-Shares (China)

| Code | Name (CN) | Name (EN) |
|------|-----------|-----------|
| 600519 | 贵州茅台 | kweichow_moutai |
| 000858 | 五粮液 | wuliangye |
| 601318 | 中国平安 | ping_an_insurance |
| 600036 | 招商银行 | china_merchants_bank |
| ... | ... | ... |

**Use stock code for ANY A-share company!**

### Hong Kong

| Code | Name (CN) | Name (EN) |
|------|-----------|-----------|
| 00700 | 腾讯 | tencent |
| 09988 | 阿里巴巴 | alibaba |
| 03690 | 美团 | meituan |
| 01810 | 小米 | xiaomi |
| ... | ... | ... |

**Use stock code for ANY HK company!**

### US Stocks

| Code | Name (CN) | Name (EN) |
|------|-----------|-----------|
| AAPL | 苹果 | apple |
| MSFT | 微软 | microsoft |
| GOOGL | 谷歌 | alphabet |
| AMZN | 亚马逊 | amazon |
| NVDA | 英伟达 | nvidia |
| ... | ... | ... |

**Use stock code for ANY US company!**

## Report Types

### A-Shares / HK

| Type | Parameter | Description |
|------|-----------|-------------|
| 年报 | `年报`, `annual` | Annual Report |
| 中报 | `中报`, `interim` | Interim Report |
| 季报 | `季报`, `quarterly` | Quarterly Report |
| 全部 | `全部`, `all` | All Reports |

### US Stocks

| Type | Parameter | Description |
|------|-----------|-------------|
| 年报 | `10-K`, `年报` | Annual Report (10-K) |
| 季报 | `10-Q`, `季报` | Quarterly Report (10-Q) |
| 全部 | `all`, `全部` | All Reports |

## Output Files

```
/root/.openclaw/workspace/exports/
├── cninfo_{name}/          # A-shares
│   ├── cninfo_{code}.json
│   ├── cninfo_{code}.csv
│   └── pdfs/
├── hkex_{name}/            # HK
│   ├── hkex_{name}_financial.json
│   ├── hkex_{name}_financial.csv
│   └── financial_pdfs/
└── sec_{name}/             # US
    ├── sec_{code}_{type}.json
    ├── sec_{code}_{type}.csv
    └── pdfs/
```

## Examples

### Example 1: Download Moutai Annual Reports

```bash
python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
  600519 --from=2020 --to=2025 --type=年报 --pdf
```

### Example 2: Download Tencent Reports

```bash
python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
  00700 --from=2020 --to=2025 --pdf
```

### Example 3: Download Apple 10-K

```bash
python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
  AAPL --from=2020 --to=2025 --type=10-K --pdf
```

### Example 4: Download All Reports (No PDF)

```bash
python3 /root/.openclaw/workspace/skills/global-financial-downloader/downloader.py \
  贵州茅台 --type=全部 --no-pdf
```

## Technical Details

### Market Identification

1. **6-digit code starting with 6/0**: A-shares
2. **5-digit code starting with 0**: HK stocks
3. **Letter code**: US stocks
4. **Company name**: Lookup in mapping table

### Report Type Mapping

| Input | A-Shares | HK | US |
|-------|----------|----|----|
| 年报/annual | annual | financial | 10-K |
| 中报/interim | interim | financial | 10-Q |
| 季报/quarterly | regular | quarterly | 10-Q |
| 全部/all | regular | financial | all |

## Configuration

### Add New Companies

Edit `/root/.openclaw/workspace/skills/global-financial-downloader/stock_mapping.json`:

```json
{
  "cn_stocks": {
    "stocks": [
      ["股票代码", "中文名称", "英文名称"],
      ["601318", "中国平安", "ping_an_insurance"]
    ]
  }
}
```

### Supported Companies

**Predefined**: 204 companies (50 A-shares, 51 HK, 100 US)

**All companies**: Use stock code for ANY company!

## Troubleshooting

### Issue: Company Not Recognized

**Solution**: Use stock code instead of company name

```bash
# ❌ May not work for undefined companies
python3 downloader.py 某公司 --pdf

# ✅ Always works
python3 downloader.py 600XXX --pdf
```

### Issue: PDF Download Failed

**Solution**: Check network and disk space

### Issue: No Reports Found

**Solution**: Expand year range or check report type

## Related Files

- **Main Script**: `/root/.openclaw/workspace/skills/global-financial-downloader/downloader.py`
- **Stock Mapping**: `/root/.openclaw/workspace/skills/global-financial-downloader/stock_mapping.json`
- **Output**: `/root/.openclaw/workspace/exports/`

## Author

Created by 玄武 🐢
Version: 1.0.0
Last Updated: 2026-04-03
