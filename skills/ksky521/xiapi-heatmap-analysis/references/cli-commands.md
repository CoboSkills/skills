# CLI 命令参考

## 基本命令

### 获取行业板块热力图

```bash
npx daxiapi-cli@latest sector heatmap
```

**返回数据**：
- 板块名称
- CS 值（Commodity Selection Index）
- 当日涨跌幅
- 5日涨跌幅
- CS 20日均线

### 获取热门概念板块

```bash
npx daxiapi-cli@latest sector gn
```

**返回数据**：
- 概念板块名称
- 涨跌幅
- 领涨股

### 获取各板块领涨股

```bash
npx daxiapi-cli@latest sector top
```

**返回数据**：
- 板块名称
- 领涨股票代码
- 领涨股票名称
- 涨跌幅

## HTTP API 请求

### 行业板块热力图

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://daxiapi.com/coze/get_sector_heatmap"
```

### 概念板块

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://daxiapi.com/coze/get_sector_gn"
```

### 领涨股

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://daxiapi.com/coze/get_sector_top"
```

## 配置命令

### 设置 Token

```bash
npx daxiapi-cli@latest config set token YOUR_TOKEN
```

### 查看 Token 配置

```bash
npx daxiapi-cli@latest config get token
```

## 使用示例

### 获取完整热力图分析数据

```bash
# 获取热力图
npx daxiapi-cli@latest sector heatmap

# 获取概念板块
npx daxiapi-cli@latest sector gn

# 获取领涨股
npx daxiapi-cli@latest sector top
```
