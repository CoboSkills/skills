---
name: fboxmcp
description: >
  管理 FBox 工业物联网设备。
  查看设备在线状态和统计信息，实时读写 PLC 监控点数据，处理和确认设备报警，查询历史采集数据趋势，远程打开 VNC 监控画面。
  当用户提到 FBox、盒子、设备状态、LC、监控点、温度/压力/电流等传感器数据、报警告警、历史数据、远程监控、VNC、设备运维时使用此技能。
  注意：所有数据均需要通过工具调用获取，禁止假设或硬编码任何设备信息、监控点配置、报警规则等。
compatibility: >
  Requires network access to FBox MCP Server (Streamable HTTP).
  Requires FBOXMCP_API_KEY environment variable.
metadata:
  version: "1.0.0"
  author: flexem
  homepage: https://fbox360.com
  openclaw:
    requires:
      env:
        - FBOXMCP_API_KEY
    primaryEnv: FBOXMCP_API_KEY
    emoji: "\U0001F4E1"
    os:
      - darwin
      - linux
      - win32
---

# FBox MCP Server 技能

通过 FBox MCP Server 提供的工具，帮助用户查询设备状态、读写监控点、处理报警和查询历史数据。

## 连接配置

FBox MCP Server 使用 Streamable HTTP 传输协议，端点地址为 `POST /`。

在 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "fboxmcp": {
      "description": "FBox MCP Server",
      "transport": "streamable-http",
      "baseUrl": "https://<your-fboxmcp-host>",
      "headers": {
        "Authorization": "Bearer ${FBOXMCP_API_KEY}"
      }
    }
  }
}
```

将环境变量 `FBOXMCP_API_KEY` 设为以 `sk-` 开头的 API Key。

## 认证

支持两种方式，通过 Authorization 头中 Token 前缀自动区分：

| 方式 | 格式 | 说明 |
|------|------|------|
| API Key（推荐） | `Bearer sk-xxxxxx` | 长期有效，服务端自动管理底层 Token 刷新 |
| JWT Token | `Bearer eyJhbGci...` | 传统 OAuth2 JWT，需自行管理续期 |

**获取 API Key：**

```http
POST /api/apikey/generate
Content-Type: application/json

{
  "clientId": "<由 FBox 平台管理员分配>",
  "clientSecret": "<由 FBox 平台管理员分配>"
}
```

响应：

```json
{
  "apiKey": "sk-abc123...",
  "usage": "Authorization: Bearer sk-abc123..."
}
```

## 核心规则

执行工具调用时，严格遵守以下规则：

### 时间处理
- 服务端所有时间均为 **UTC 时间**
- 展示给用户时**必须转为北京时间（UTC+8）**，仅精确到秒
- **禁止假设当前时间**，必须通过 `utc_now` 工具获取服务器实时时间
- 历史数据和报警历史中的 `Timestamp` 为 UTC 毫秒级时间戳

### 参数处理
- `BoxNo`（设备序列号）和 `BoxAlias`（设备别名）**二选一**即可定位设备
- 用户说出的设备名称优先作为 `BoxAlias` 传入
- 缺少必填参数时设为 `null` 调用工具，服务端会返回候选列表
- **禁止自动猜测或补全参数**，必须从候选列表中让用户选择

### 在线设备优先
- 除非用户明确说"所有设备"或"离线设备"，默认 `OnlyOnline = true`
- `ConnState` 为 `Online` 或 `TimedOut` 视为在线

### 数据展示
- `bool` 值展示为"是"或"否"
- 报警历史和历史数据默认以**表格形式**展示
- 监控点、报警、历史数据条目之间**逻辑上没有强制关联性**，不要假设名称一致

### 写操作安全
- `write_user_box_dmon_value` 和 `confirm_current_alarm` 是写操作
- **必须获得用户明确确认后才能执行**
- 写入前先读取当前值展示给用户对比

## 响应格式

所有业务工具返回统一结构：

```json
{
  "success": true,
  "code": 0,
  "message": null,
  "data": { "..." },
  "suggestedParameters": null
}
```

| Code | 含义 | 处理方式 |
|------|------|---------|
| 0 | 成功 | 解析 `data` 展示给用户 |
| 300 | 参数需要选择 | 解析 `suggestedParameters` 候选列表让用户选择，选择后用 `value` 字段（非 `label`）重新调用 |
| 400 | 请求错误 | 展示 `message` 错误信息 |
| 401 | 未认证 | 提示用户检查认证配置 |
| 404 | 未找到 | 提示目标资源不存在 |
| 500 | 服务器错误 | 提示系统异常，建议稍后重试 |

## 用户意图分类

| 意图 | 说明 | 典型用语 |
|------|------|---------|
| device_management | 设备状态查看、信息查询 | "查看设备""设备列表""哪些设备在线" |
| data_query | 监控点、历史数据、报警查询 | "温度多少""查看历史""报警记录" |
| page_control | 远程控制、画面操作 | "打开远程画面""VNC" |
| knowledge_rag | FBox 产品知识问答 | "FBox 怎么配置""文档在哪" |

---

## 工具总览

共 20 个工具，分为 6 大类。详细参数和返回值见 `references/` 目录下的参考文档。

### 设备管理（7 个）

| 工具 | 说明 | 只读 |
|------|------|------|
| `get_user_box_stats` | 获取设备统计（总数、在线数、报警数） | 是 |
| `get_user_box_list` | 获取设备列表（按分组返回） | 是 |
| `get_user_box_info` | 获取单个设备详情 | 是 |
| `get_user_box_settings` | 获取设备系统配置（IP、固件等） | 是 |
| `get_user_box_location` | 获取设备地理位置 | 是 |
| `get_sim_card_info` | 获取物联网卡信息（流量、运营商） | 是 |
| `get_user_box_plc_list` | 获取 PLC 设备列表 | 是 |

### 监控点（5 个）

| 工具 | 说明 | 只读 |
|------|------|------|
| `get_user_box_dmon_group_list` | 获取监控点分组列表 | 是 |
| `get_user_box_dmon_list` | 获取指定分组下的监控点列表 | 是 |
| `get_user_box_dmon_info` | 获取单个监控点详细配置 | 是 |
| `get_user_box_dmon_value` | 读取监控点实时值 | 是 |
| `write_user_box_dmon_value` | 写入监控点值（需二次确认） | **否** |

### 报警管理（4 个）

| 工具 | 说明 | 只读 |
|------|------|------|
| `get_alarm_define_list` | 获取报警规则定义列表 | 是 |
| `get_current_alarm_list` | 获取当前活跃报警列表 | 是 |
| `confirm_current_alarm` | 确认报警（需用户确认） | **否** |
| `get_alarm_history_list` | 查询报警历史记录 | 是 |

### 历史数据（2 个）

| 工具 | 说明 | 只读 |
|------|------|------|
| `get_history_data_define_list` | 获取历史数据条目定义列表 | 是 |
| `get_history_data_list` | 查询历史数据（支持聚合） | 是 |

### 远程控制（1 个）

| 工具 | 说明 | 只读 |
|------|------|------|
| `open_vnc` | 打开设备 VNC 远程监控画面 | 是 |

### 系统工具（1 个）

| 工具 | 说明 | 认证 |
|------|------|------|
| `utc_now` | 获取服务器当前 UTC 时间 | 否 |

---

## 典型工作流

### 设备状态概览
```
get_user_box_stats → get_user_box_list(OnlyOnline=true) → get_user_box_info(BoxAlias=xxx)
```

### 查看监控点数据
```
get_user_box_dmon_group_list(BoxAlias=xxx)
  → [如返回 300，让用户选择设备]
get_user_box_dmon_list(BoxNo=xxx, GroupName=xxx)
  → [如返回 300，让用户选择分组]
get_user_box_dmon_value(BoxNo=xxx, GroupName=xxx, Name=xxx)
```

### 处理设备报警
```
get_user_box_stats → 确认存在报警
get_current_alarm_list(BoxAlias=xxx) → 展示当前报警
confirm_current_alarm(BoxNo=xxx, AlarmName=xxx) → 用户确认后执行
```

### 查询历史趋势
```
utc_now → 获取服务器时间
get_history_data_define_list(BoxAlias=xxx) → 了解可查数据
get_history_data_list(BoxNo=xxx, ItemName=xxx, BeginTime=..., EndTime=...)
  → 以表格形式展示，时间转北京时间
```

### 写入监控点
```
get_user_box_dmon_value → 读取当前值展示给用户
  → 用户确认 "将 [监控点] 从 [当前值] 修改为 [目标值]"
write_user_box_dmon_value(Confirmed=true)
```

