---
name: media-saber-recommend-helper
description: 通过 Media Saber MCP 生成带有结构化过滤器和可解释选择的电影和电视推荐。
---

# Media Saber 推荐助手

在推荐场景中使用此技能。

## ⚠️ 必须配置：MCP 服务连接

在使用此技能前，**您必须配置以下信息**：

### 1. MCP 地址配置（需要用户填写）

- **transport**: `streamable-http`
- **endpoint**: `<MCP_ENDPOINT_URL>` （例如：http://localhost:22698/message 或你的其他部署地址）
- **需要用户填写实际的 MCP 服务地址**

### 2. 认证信息配置（需要用户填写）

**请在以下位置之一配置您的 API_KEY**：

#### 方式 A：OpenClaw 配置（推荐）

在 `~/.claw/mcpServers.json` 中配置 Media Saber 连接：

```json
{
  "mcpServers": {
    "MediaSaber": {
      "transport": "streamable-http",
      "url": "http://localhost:22698/message",
      "headers": {
        "Authorization": "Bearer sk-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

**替换 `sk-YOUR_API_KEY_HERE` 为您的实际 API 密钥**

#### 方式 B：环境变量配置

- 设置环境变量：`MEDIA_SABER_API_KEY=sk-your-api-key`
- 该密钥将被自动注入到请求头中

### 3. 获取 API_KEY

请从 Media Saber 系统获取您的 API 密钥：
- 访问 Media Saber Web 界面
- 进入 "设置" → "API 密钥"
- 复制您的密钥（通常以 `sk-` 开头）

**安全提示**：
- ⚠️ **切勿将 API_KEY 硬编码在代码、提示词或文档中**
- ⚠️ **切勿通过不安全的通道传输 API_KEY**
- ⚠️ **定期轮换您的 API_KEY**
- ⚠️ **不要与他人共享您的 API_KEY**

## 主要工具

- recommend_movies(country?, sort?, tag?, year?)
- recommend_tvs(country?, sort?, tag?, year?)
- get_tmdb_info(tmdbId, mediaType)

## 推荐策略

1. 向用户询问媒体类型和偏好维度。
2. 将偏好转换为工具过滤器。
3. 调用 recommend_movies 或 recommend_tvs。
4. 使用 get_tmdb_info 补充热门选择。
5. 返回简明的候选列表并说明理由。

## 防护措施

- 将过滤值保持在服务器允许的枚举集内。
- 如果用户给出不支持的值，映射到空值（全部）并解释。
- 切勿暴露授权令牌。
