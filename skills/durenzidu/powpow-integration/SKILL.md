---
name: powpow
version: 2.1.9
description: |
  将 OpenClaw 数字人发布到 Powpow 地图平台，让其他用户可以在真实地图上与你的 AI 数字人对话。
  
  USE FOR:
  - "我要把数字人放到 powpow"
  - "在 powpow 上创建数字人"
  - "注册 powpow 账号"
  - "管理我的 powpow 数字人"
  - "删除 powpow 上的数字人"
  - "查看我的 powpow 数字人"
  - "powpow 数字人"
  
  关键词: powpow, 数字人, 地图, 位置, 发布, 注册, 徽章

metadata:
  openclaw:
    emoji: 🗺️
    requires:
      bins: []
      config:
        - powpow.baseUrl
---

# Powpow Skill

## 简介

Powpow 是一个基于地理位置的 AI 数字人平台。通过这个 Skill，你可以：

1. **注册 Powpow 账号** - 在 Powpow 平台上创建账号（获得 3 个徽章）
2. **创建数字人** - 创建带有名称、人设和位置的数字人（消耗 2 个徽章）
3. **发布到地图** - 让其他用户在 `https://global.powpow.online/map` 上发现你的数字人
4. **管理数字人** - 查看、更新或删除你的数字人

## 前置条件

在使用此 Skill 前，你需要：

1. 确保你的 OpenClaw Gateway 正在运行
2. 知道你的 Gateway URL（通常是 `http://localhost:18789`）
3. Powpow 平台地址：`https://global.powpow.online`

## 徽章系统

Powpow 使用徽章系统来管理资源：

- **新用户注册**: 获得 3 个徽章
- **创建数字人**: 消耗 2 个徽章
- **数字人有效期**: 30 天

## 快速开始

### 1. 注册 Powpow 账号

告诉 OpenClaw：
> "帮我在 powpow 上注册一个账号"

你需要提供：
- 用户名（唯一）
- 昵称（可选，默认使用用户名）
- 头像 URL（可选）

### 2. 创建数字人

告诉 OpenClaw：
> "我要在 powpow 上创建一个数字人"

你需要提供：
- 数字人名称
- 人设描述（数字人的性格、背景、专长等）
- 位置（经纬度或城市名称）
- 头像 URL（可选，默认使用 Powpow 默认头像）
- Webhook URL（你的 OpenClaw Gateway 地址，用于接收消息）

### 3. 查看数字人

告诉 OpenClaw：
> "查看我的 powpow 数字人"

### 4. 删除数字人

告诉 OpenClaw：
> "删除 powpow 上的 [数字人名称]"

## 详细说明

### 注册流程

```
用户: "帮我在 powpow 上注册"
AI: "好的，我来帮你在 Powpow 上注册账号。请提供：
     1. 用户名（唯一标识）
     2. 昵称（可选，默认使用用户名）
     3. 头像 URL（可选）"
     
用户: "用户名: myagent, 昵称: 我的数字人"
AI: [调用 register 工具完成注册]
   "注册成功！你的 Powpow 账号已创建。
    用户名: myagent
    徽章余额: 3
    你现在可以创建数字人并发布到地图上了。"
```

### 创建数字人流程

```
用户: "创建一个 powpow 数字人"
AI: "好的，请告诉我：
     1. 数字人的名称
     2. 人设描述（性格、背景、专长等）
     3. 位置（比如：北京、上海，或提供经纬度）
     4. 头像 URL（可选）
     5. 你的 OpenClaw Gateway URL（用于接收消息，如 http://localhost:18789）"
     
用户: "名称: 小明, 人设: 我是一个知识渊博的历史学家..."
AI: [调用 createAgent 工具]
   "数字人创建成功！
    名称: 小明
    位置: 北京
    有效期: 30天
    徽章余额: 1（消耗了2个徽章）
    其他用户现在可以在 Powpow Map 上找到并与你的数字人对话了。"
```

### 对话机制

当 Powpow 用户与你的数字人对话时：

1. Powpow 用户发送消息
2. Powpow 后端通过 Webhook 将消息转发到你的 OpenClaw Gateway
3. OpenClaw 根据数字人的人设生成回复
4. 回复通过 Webhook 返回给 Powpow 用户

**重要**: 你需要保持 OpenClaw Gateway 运行，数字人才能回复消息。

## 工具使用说明

### register

注册 Powpow 账号。

**参数：**
- `username` (string, required): 用户名（唯一）
- `nickname` (string, optional): 昵称
- `avatar_url` (string, optional): 头像 URL

**返回：**
- `user_id`: 用户ID
- `username`: 用户名
- `badges`: 徽章数量（新用户为3）

### login

登录 Powpow 账号。

**参数：**
- `username` (string, required): 用户名

**返回：**
- `token`: JWT Token（有效期30天）
- `user_id`: 用户ID
- `badges`: 徽章数量

### createAgent

创建新的数字人。

**参数：**
- `name` (string, required): 数字人名称
- `description` (string, required): 人设描述
- `lat` (number, required): 纬度
- `lng` (number, required): 经度
- `locationName` (string, required): 位置名称
- `avatarUrl` (string, optional): 头像 URL
- `webhookUrl` (string, required): OpenClaw Gateway URL
- `webhookToken` (string, optional): Webhook 验证令牌

**注意**: 创建数字人需要消耗 2 个徽章

**返回：**
- `id`: 数字人ID
- `name`: 名称
- `expiresAt`: 过期时间（30天后）
- `badgesRemaining`: 剩余徽章数

### listAgents

列出当前用户的所有数字人。

**参数：**
- `userId` (string, required): 用户ID
- `token` (string, required): JWT Token

**返回：**
- 数字人列表，包含 ID、名称、描述、位置、状态、过期时间等

### deleteAgent

删除指定的数字人。

**参数：**
- `agentId` (string, required): 数字人 ID
- `userId` (string, required): 用户ID
- `token` (string, required): JWT Token

## 配置存储

此 Skill 会在你的 OpenClaw 配置中存储以下信息：

- `powpow.username`: Powpow 用户名
- `powpow.token`: JWT Token（自动管理）
- `powpow.userId`: 用户ID
- `powpow.baseUrl`: Powpow 基础 URL
- `powpow.badges`: 徽章数量

## API 端点

Powpow 提供的 OpenClaw API：

- `POST /api/openclaw/auth/register` - 注册
- `POST /api/openclaw/auth/login` - 登录
- `POST /api/openclaw/digital-humans` - 创建数字人
- `GET /api/openclaw/digital-humans?userId=xxx` - 获取数字人列表
- `DELETE /api/openclaw/digital-humans/[id]` - 删除数字人
- `POST /api/openclaw/chat/send` - 发送消息
- `POST /api/openclaw/webhook/reply` - 接收回复（OpenClaw 调用）

## 常见问题

### Q: 我的数字人能被多少人同时对话？
A: 取决于你的 OpenClaw Gateway 性能，通常可以支持多个并发对话。

### Q: 我需要保持电脑开机吗？
A: 是的，你的 OpenClaw Gateway 需要保持运行，数字人才能回复消息。

### Q: 可以创建多个数字人吗？
A: 可以，只要你有足够的徽章（每个数字人消耗 2 个徽章）。

### Q: 如何获得徽章？
A: 新用户注册获得 3 个徽章。未来可能会开放其他获取方式。

### Q: 数字人过期后怎么办？
A: 数字人有效期为 30 天，过期后需要重新创建。

### Q: 数字人的回复速度如何？
A: 取决于你使用的 AI 模型和网络状况，通常在 1-5 秒内。

## 错误处理

常见错误及解决方案：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 用户名已存在 | 该用户名已被注册 | 换一个用户名 |
| 徽章不足 | 需要 2 个徽章创建数字人 | 确保你有足够的徽章 |
| Webhook 未配置 | 创建数字人时未提供 webhookUrl | 提供你的 OpenClaw Gateway URL |
| Token 过期 | JWT Token 已过期（30天） | 重新登录 |
| 数字人不存在 | 数字人 ID 错误或已删除 | 检查数字人 ID |

## 安全提示

1. **妥善保管 Token**: 不要在对话中透露你的 JWT Token
2. **使用强密码**: 建议包含大小写字母、数字和符号
3. **Gateway 安全**: 确保你的 Gateway 不暴露在不安全的网络中
4. **人设内容**: 避免在人设中包含敏感个人信息

## 技术支持

遇到问题？
- Powpow 平台: https://global.powpow.online
- OpenClaw 文档: https://docs.openclaw.ai
