# SKILL: Pengleni Login Session HTML Bridge

## 1) Skill 作用

该 Skill 用于把 OpenClaw 或其他调用方接入到 Pengleni 的登录会话能力，核心目标是：

- 复用现有手机号验证码登录链路
- 通过登录态建立 user_id + session_id
- 以 HTML 作为消息载体调用智能体
- 返回可展示的 answer_html 和可检索的 answer_text

该 Skill 默认按非流式方式工作，便于直接接入；也保留可选流式参数。

## 2) 调用流程

1. 发送验证码（站点级接口）
2. 用户提交手机号 + 验证码，调用登录接口创建会话
3. 使用登录返回的 user_id 与 session_id 调用消息接口
4. 获取 answer_html / answer_text 并展示给最终用户

## 3) 当前目录文件作用

### skill_manifest.clawhub.yaml

Skill 发布清单文件，定义了：

- Skill 基本信息（id、name、version、owner、tags）
- 能力与协议（是否要求流式、鉴权模式、输入输出类型）
- 入口点（/session/login 与 /session/message）
- 站点级辅助接口（/chainlit/send-verification-code）
- 输入输出结构、错误码映射、安全策略、观测项

这是 ClawHub 侧识别与发布该 Skill 的主描述文件。

### openapi.yaml

接口契约文件，定义了 API 结构与字段：

- /session/login 请求与响应
- /session/message 请求与响应
- Bearer 鉴权方案
- 状态码与错误语义

这是联调、SDK 生成、平台校验时的标准参考。

### skill_client.py

零依赖单文件 Python 客户端，支持三类命令：

- send-code: 调用站点级验证码接口
- login: 调用登录接口获取会话
- message: 调用消息接口发送 HTML 内容

该脚本可直接下载使用，用于快速联调、演示与验收。

### README.md

面向使用者的快速说明文档，包含：

- 文件清单
- 最短可运行步骤
- 三条命令示例
- 路径说明与注意事项

用于帮助接入方在最短时间完成首次调用。

## 4) 运行环境变量

运行该 Skill 时需要配置以下环境变量：

```env
# Site-level base URL (for verification code endpoint)
SITE_BASE_URL=https://www.zhibianai.com

# API-level base URL (for skill endpoints)
API_BASE_URL=https://www.zhibianai.com/api/v1/clawhub

# Bearer token for skill API
CLAWHUB_SKILL_TOKEN=leeray_test_clawhub_skill
```

变量说明：

- SITE_BASE_URL: 站点级域名，用于验证码接口 `/chainlit/send-verification-code`
- API_BASE_URL: Skill API 基础路径，建议配置到 `/api/v1/clawhub`
- CLAWHUB_SKILL_TOKEN: Skill 服务间 Bearer Token

## 5) 安全与边界

- 该 Skill 使用服务间 Bearer Token 保护 API 调用。
- HTML 内容需在服务端执行安全过滤与长度限制。
- session_id 必须与 user_id 绑定校验，防止会话串用。
- 生产环境应通过环境变量或密钥管理服务注入 Token。

## 6) 适用场景

- OpenClaw Skill 接入
- 需要复用已有登录体系的智能体调用
- 需要保留 HTML 富文本交互的业务流程

## 7) 非目标

- 不负责短信通道实现细节
- 不负责前端页面渲染
- 不负责底层模型编排策略定义
