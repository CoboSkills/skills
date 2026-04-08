---
name: wendaoyun
description: 问道云企业信息查询工具，支持通过问道云 API 查询企业信息、行政处罚、失信被执行人等记录。当用户需要查询企业相关信息时触发。
version: 1.0.5
author: 技能开发者
config:
  - name: WENDAOYUN_API_KEY
    description: 问道云 API Key，可从 https://open.wintaocloud.com/home 获取
    required: true
    path:
      - ~/.config/wendao-yun/config.json
      - wendao-yun-config.json
    format: json
    example: '{"api_key": "your-api-key-here"}'
    env_var: WENDAOYUN_API_KEY
requirements:
  config:
    - WENDAOYUN_API_KEY
  env:
    - WENDAOYUN_API_KEY
  bins:
    - python3
  pip:
    - requests
---

# 问道云 (WenDaoYun)

## Overview

问道云是问道云天提供的企业信息查询 API 服务，本技能封装了问道云 API 的调用流程。

### 核心设计理念

- **两步查询**：始终先搜索企业 → 用户确认 → 再查询详细信息
- **模块化扩展**：新增接口只需在「Supported APIs」中添加定义，并在「详细信息类型」中注册
- **统一交互**：所有详细查询（处罚、失信人、经营异常等）遵循相同的确认流程

### 已支持的详细信息类型

| 类型 | 接口名 | 用户说法示例 | 状态 |
|------|--------|--------------|------|
| 企业基本信息 | `fuzzy-search-org` | "查询腾讯企业" | ✅ 已实现 |
| 行政处罚 | `get-punishments` | "查腾讯的行政处罚" | ✅ 已实现 |
| 失信被执行人 | `get-dishonest` | "查腾讯是不是老赖" | ⏳ 待接入 |
| 经营异常 | `get-abnormal` | "查腾讯经营异常" | ⏳ 待接入 |
| 税收违法 | `get-tax-violation` | "查腾讯税收违法" | ⏳ 待接入 |

> 💡 **提示用户时可以说**："我可以帮你查询企业的行政处罚、失信被执行人、经营异常、税收违法等信息"

---

## Configuration

使用前需要先配置 API Key：
1. 前往 https://open.wintaocloud.com/home 登录获取 API Key
2. 在技能配置文件中设置 `api_key`（配置文件路径：工作空间根目录的 `wendao-yun-config.json`）
3. 每个用户每日有 200 次调用额度，请妥善保管 API Key 避免泄露

详细配置说明见 [references/config.md](references/config.md)

---

## Universal Workflow（通用查询流程）

### 所有查询都遵循以下流程

```
┌─────────────────────────────────────────────────────┐
│  第 1 步：用户提出查询需求                              │
│  例如："帮我查询腾讯的行政处罚"                        │
│       或："查一下阿里的失信被执行人"                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  第 2 步：模糊搜索企业（调用 fuzzy-search-org）        │
│  - 使用用户提供的关键词作为 searchKey                 │
│  - 如果 total=0：提示用户调整关键词                    │
│  - 如果 total>0：列出前 5 条结果                       │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  第 3 步：等待用户确认具体企业                         │
│  **必须询问**："找到多家相关企业，请确认你想查询哪一家？"│
│  - 提供序号或全称让用户选择                           │
│  - 用户可以说"第 X 家"或直接说企业全称                   │
│  ⚠️ 此阶段不要调用任何详细信息接口！                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  第 4 步：用户确认后，查询详细信息                      │
│  - 根据用户请求的类型，调用对应接口                    │
│    - 行政处罚 → get-punishments                      │
│    - 失信被执行 → get-dishonest（待接入）             │
│    - 经营异常 → get-abnormal（待接入）                │
│    - ...                                             │
│  - 整理结果返回给用户                                 │
└─────────────────────────────────────────────────────┘
```

---

## Scenario Examples（场景示例）

### 场景一：只查询企业基本信息

**用户**："帮我查询腾讯企业"

**助手**：
1. 调用 `fuzzy-search-org`（searchKey="腾讯"）
2. 展示前 5 条结果
3. 询问："以上有你想要查询的企业吗？"
4. 用户确认后，可以结束或等待进一步指令

---

### 场景二：查询企业 + 详细信息（如行政处罚）

**用户**："帮我查询腾讯的行政处罚"

**助手**：
1. 调用 `fuzzy-search-org`（searchKey="腾讯"）
2. 展示前 5 条结果
3. **必须询问**："找到多家相关企业，请确认你想查询哪一家的行政处罚？"
4. 用户回复："第 3 家" 或 "腾讯科技（深圳）有限公司"
5. 调用 `get-punishments`（searchKey=用户确认的企业全称）
6. 返回处罚记录

---

### 场景三：查询新类型信息（如失信被执行人）

**用户**："查查腾讯是不是老赖" / "查询腾讯的失信被执行人"

**助手**：
1. 调用 `fuzzy-search-org`（searchKey="腾讯"）
2. 展示前 5 条结果
3. **必须询问**："找到多家相关企业，请确认你想查询哪一家的失信被执行人？"
4. 用户回复："第 3 家"
5. 调用 `get-dishonest`（searchKey=用户确认的企业全称）**← 新接口**
6. 返回失信记录

> 💡 **关键点**：无论查询什么类型的详细信息，**前 3 步完全相同**，只有第 4 步调用的接口不同。

---

## Supported APIs

### 基础接口（必选）

#### `fuzzy-search-org` - 企业模糊搜索

**用途**：所有查询的第一步，用于获取企业列表和用户确认

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 查询关键词（最少 2 个字符） |
| pageNum | integer | 否 | 分页页码，默认从 1 开始，每页固定返回 5 条数据 |

**响应字段**：
```json
{
  "orgId": 227606194,
  "orgName": "腾讯科技（深圳）有限公司",
  "usCreditCode": "9144030071526726XG",
  "incDate": "2000-02-24T00:00:00.000+08:00",
  "legalName": "马化腾",
  "status": "存续/在业",
  "address": "深圳市南山区高新区科技中一路腾讯大厦 35 层"
}
```

**使用说明**：
- ⚠️ 搜索结果可能非常多（如"腾讯"返回 7895 条），**始终只展示前 5 条**
- ✅ 展示时必须包含：序号、企业全称、法定代表人、成立日期、状态
- ✅ 必须询问用户："以上有你想要查询的企业吗？"
- 💡 引导用户：
  - 添加更具体的关键字（如"腾讯科技深圳"而不是"腾讯"）
  - 查询下一页（"帮我查第 2 页"）

---

### 详细信息接口（可选扩展）

#### `get-punishments` - 查询行政处罚 ✅ 已实现

**请求方式**：GET

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称（orgName，从模糊搜索结果获取） |
| pageNum | integer | 否 | 分页页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 10，最大 20 |

**响应字段**：
```json
{
  "punishNo": "深交罚决字第 Z0070576 号",
  "illegalFact": "经调查，本机关认为你（单位）实施了...违法行为",
  "punishResult": "罚款 10000 元",
  "unitName": "深圳市交通运输委员会",
  "punishTime": "2017-11-30",
  "punishAmount": "10000"
}
```

---

#### `get-dishonest` - 查询失信被执行人 ⏳ 待接入

**用途**：查询企业是否为失信被执行人（俗称"老赖"）

**请求方式**：GET（待定）

**请求参数**（预期）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称（orgName） |
| pageNum | integer | 否 | 分页页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 10 |

**响应字段**（预期）：
```json
{
  "caseNo": "（2023）京 01 执 123 号",
  "courtName": "北京市第一中级人民法院",
  "giverDate": "2023-05-15",
  "giverReason": "有履行能力而拒不履行生效法律文书确定义务",
  "holdStatus": "全部未履行",
  "performanceForm": "全部未履行",
  "regDate": "2023-06-01"
}
```

**接入步骤**：
1. 在问道云开放平台查看该接口的确切文档
2. 在 `scripts/api_client.py` 中添加 `get_dishonest()` 方法
3. 在此文档中更新接口定义（替换"预期"为实际参数）
4. 在上方的"已支持的详细信息类型"表格中将状态改为 ✅

---

#### `get-abnormal` - 查询经营异常 ⏳ 待接入

**用途**：查询企业是否被列入经营异常名录

**请求方式**：GET（待定）

**请求参数**（预期）：同上

**响应字段**（预期）：
```json
{
  "abnormalType": "未按照规定的期限公示年度报告",
  "decAuthority": "深圳市市场监督管理局",
  "decDate": "2022-07-01",
  "removeDate": "2022-08-15",
  "removeReason": "已补报年度报告并公示"
}
```

---

#### `get-tax-violation` - 查询税收违法 ⏳ 待接入

**用途**：查询企业是否有税收违法记录

**请求方式**：GET（待定）

**请求参数**（预期）：同上

**响应字段**（预期）：
```json
{
  "taxNo": "9144030071526726XG",
  "violationType": "偷税",
  "decisionDocNo": "深国税稽罚〔2023〕123 号",
  "decisionDate": "2023-03-15",
  "taxAmount": "500000",
  "fineAmount": "250000"
}
```

---

## How to Add New Interface（如何添加新接口）

当你需要添加新的查询类型（如"股权出质"、"动产抵押"等）时：

### 第 1 步：查阅问道云 API 文档

访问问道云开放平台，找到新接口的文档，确认：
- 接口路径（如 `/get-equity-pledge`）
- 请求方式（GET/POST）
- 请求参数
- 响应格式

### 第 2 步：更新 Python 客户端

编辑 `scripts/api_client.py`，添加新方法：

```python
def get_equity_pledge(self, org_name: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    查询企业股权出质信息
    :param org_name: 企业全称
    :param page_num: 分页页码
    :param page_size: 每页大小
    :return: 股权出质列表
    """
    params = {
        "searchKey": org_name,
        "pageNum": page_num,
        "pageSize": page_size
    }
    return self.call_api("get-equity-pledge", params, method="GET")
```

### 第 3 步：更新本文档

1. **在"已支持的详细信息类型"表格中添加一行**：
   ```markdown
   | 股权出质 | `get-equity-pledge` | "查腾讯的股权出质" | ⏳ 开发中 |
   ```

2. **在"详细信息接口"章节添加新接口定义**（参考上面的模板）

3. **如果用户可能用多种说法**，在场景示例中添加：
   ```markdown
   ### 场景 X：查询股权出质
   **用户**："查查腾讯的股权出质" / "腾讯有没有股权质押"
   ```

### 第 4 步：测试

```bash
cd /home/gem/workspace/agent
python3 skills/wendaoyun/scripts/api_client.py --equity-pledge "腾讯科技（深圳）有限公司"
```

### 第 5 步：完成

将表格中的状态改为 ✅ 已实现

---

## API Base URL

固定前缀：`https://h5.wintaocloud.com/prod-api/api/invoke`

完整请求 URL = 基础前缀 + 接口路径，例如：
- `https://h5.wintaocloud.com/prod-api/api/invoke/fuzzy-search-org`
- `https://h5.wintaocloud.com/prod-api/api/invoke/get-punishments`
- `https://h5.wintaocloud.com/prod-api/api/invoke/get-dishonest` ← 新接口示例

---

## Authentication

所有请求都需要在 HTTP Header 中添加认证信息：
```
Authorization: Bearer {api_key}
```

---

## Request Methods

- **GET**：参数通过 URL 查询字符串拼接
- **POST**：参数通过 JSON 格式请求体发送

---

## Resources

### references
- `config.md` - 配置文件模板和说明
- `apis.md` - 完整 API 接口文档（同步更新）

### scripts
- `api_client.py` - Python API 客户端封装

---

## Quick Reference Card（快速参考卡）

### 用户说法 → 接口映射

| 用户可能说的话 | 对应接口 | 备注 |
|---------------|----------|------|
| "查询 XX 企业" | `fuzzy-search-org` | 只查基本信息 |
| "XX 的行政处罚" | `fuzzy-search-org` → `get-punishments` | 需确认企业 |
| "XX 是不是老赖" | `fuzzy-search-org` → `get-dishonest` | 需确认企业 |
| "XX 的失信记录" | `fuzzy-search-org` → `get-dishonest` | 需确认企业 |
| "XX 经营异常" | `fuzzy-search-org` → `get-abnormal` | 需确认企业 |
| "XX 税收违法" | `fuzzy-search-org` → `get-tax-violation` | 需确认企业 |

### 关键原则（再次强调）

- ✅ **所有详细查询都必须先搜索、再确认、后查询**
- ❌ **不要在未确认企业时直接调用详细信息接口**
- 💡 **新增接口只需复制模板，修改接口名和字段说明即可**

---

## 附录：完整对话示例

### 示例：查询失信被执行人（新接口）

```
用户：帮我查查腾讯是不是老赖

助手：（调用 fuzzy-search-org，searchKey="腾讯"）

助手：
🔍 搜索关键词："腾讯"
共找到 7,895 家相关企业，以下是第 1 页（前 5 条）：

| # | 企业名称 | 法定代表人 | 成立日期 | 状态 |
|---|----------|------------|----------|------|
| 1 | 深圳市腾讯斐泰科技有限公司 | 洪丹毅 | 2014-08-11 | 存续/在业 |
| 2 | 深圳市腾讯鑫信科技有限公司 | 林海峰 | 2021-05-25 | 存续/在业 |
| 3 | 深圳市腾讯网域计算机网络有限公司 | 何迪亮 | 1997-04-28 | 存续/在业 |
| 4 | 深圳市腾讯科融企业管理有限公司 | 马化腾 | 2021-05-25 | 存续/在业 |
| 5 | 深圳市腾讯信航有限合伙企业 | 深圳市腾讯博远科技有限公司 | 2017-06-30 | 注销 |

❓ 找到多家相关企业，请确认你想查询哪一家的失信被执行人记录？
- 请告诉我序号（如"第 3 家"）或企业全称

用户：第 3 家

助手：（调用 get-dishonest，searchKey="深圳市腾讯网域计算机网络有限公司"）

助手：
✅ 查询到 **深圳市腾讯网域计算机网络有限公司** 的失信被执行人记录：

共找到 0 条记录

🎉 该企业目前没有失信被执行人记录。
```

---

**文档版本**：v2.0  
**最后更新**：2026-04-08  
**维护者**：技能开发者
