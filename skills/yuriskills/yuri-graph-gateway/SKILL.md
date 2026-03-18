---
name: yuri-graph-gateway
description: Yuri Graph Gateway — Facebook Graph API Proxy Service Usage Guide
homepage: https://baiz.ai
primary_credential: BAIZ_API_TOKEN
env:
  BAIZ_API_TOKEN:
    description: "API Token from baiz.ai platform. Generate it in the baiz.ai dashboard under 'API Management'. Format: xxx|xxx. This is NOT a Facebook access token. Use a least-privilege test account token."
    required: true
    sensitive: true
---

# Yuri Graph Gateway

A transparent proxy for the Facebook Graph API. Replace the domain, pass your Yuri API token, and call any Facebook endpoint — no Facebook access token needed on the client side.

Facebook Graph API 透明代理服务。只需替换域名、传入尤里改 API Token，即可调用所有 Facebook 端点 — 客户端无需持有 Facebook Access Token。

---

## Quick Start / 快速开始

### Step 1: Sign Up / 注册账号

Register an account at https://baiz.ai.

前往 https://baiz.ai 注册尤里改账号。

### Step 2: Connect Facebook / 获取 Facebook 授权

Choose one:
1. **Request access** — Contact the Yuri team to get a pre-authorized Facebook account
2. **Authorize your own** — Link your Facebook account through the Yuri dashboard

两种方式（二选一）：
1. **联系官方** — 联系尤里改官方获取已授权的 Facebook 账号
2. **自行授权** — 将你自己的 Facebook 账号在尤里改后台完成授权绑定

### Step 3: Get Your API Token / 获取 API Token

Generate an API token in the Yuri dashboard under **API Management**.

在尤里改后台「API管理」页面生成 API Token。

### Step 4: Start Calling / 开始调用

Replace `graph.facebook.com` with `facebook-graph.baiz.ai` and set your Yuri API token as the Bearer token.

将域名替换为 `facebook-graph.baiz.ai`，并将获取到的 Token 放到请求头的 `Authorization: Bearer {token}` 中。

---

## Usage / 使用示例

**Before (direct Facebook API) / 替换前（直接调用 Facebook API）：**

```
GET https://graph.facebook.com/v25.0/act_123456/campaigns?fields=name,status
Authorization: Bearer {facebook_access_token}
```

**After (via Yuri Graph Gateway) / 替换后（通过 Yuri Graph Gateway）：**

```
GET https://facebook-graph.baiz.ai/v25.0/act_123456/campaigns?fields=name,status
Authorization: Bearer {BAIZ_API_TOKEN}
```

Two changes only / 只需改两处：
1. Domain / 域名: `graph.facebook.com` → `facebook-graph.baiz.ai`
2. Token: use your `BAIZ_API_TOKEN` (not a Facebook access token) / 使用尤里改平台的 `BAIZ_API_TOKEN`（非 Facebook Access Token）

**You do not need to pass an `access_token` parameter.** The gateway automatically resolves the resource ID in the request path and injects the correct Facebook access token server-side.

**无需传递 `access_token` 参数。** 网关会根据请求路径中的资源 ID 自动解析并在服务端注入对应的 Facebook Access Token。

Everything else — paths, query parameters, request bodies, HTTP methods — stays identical to the official Facebook Graph API documentation.

其余所有参数、路径、请求方法、请求体保持不变，与 Facebook Graph API 官方文档完全一致。

---

## Supported Requests / 支持的请求

- All HTTP methods: GET, POST, PUT, DELETE, etc. / 所有 HTTP 方法
- All Facebook Graph API endpoints and versions / 所有 Facebook Graph API 端点和版本
- File uploads (multipart/form-data) / 文件上传
- JSON and form-encoded request bodies / JSON 与表单请求体

---

## Security & Privacy / 安全与隐私

### Token Handling / Token 说明

- **Token separation / Token 区分**: The `BAIZ_API_TOKEN` (format `xxx|xxx`) is a Yuri platform credential, **not** a Facebook access token. Do not confuse the two. / `BAIZ_API_TOKEN`（格式 `xxx|xxx`）是尤里改平台凭证，**不是** Facebook Access Token，请勿混淆。
- **Server-side injection / 服务端注入**: Facebook access tokens are securely stored and managed on the server. The gateway resolves the correct token based on the resource ID in your request path — tokens are never exposed to the client. / Facebook Access Token 由服务端安全托管，网关根据请求路径中的资源 ID 自动匹配注入，不会暴露给客户端。
- **Token storage / Token 保管**: Store your `BAIZ_API_TOKEN` in a secret manager or environment variable. Restrict access to the minimum necessary scope. Rotate or revoke it immediately if compromised. / 请将 `BAIZ_API_TOKEN` 存储在密钥管理工具或环境变量中，限制最小访问范围，泄露时立即轮换或吊销。
- **Token scoping & rotation / Token 权限范围与轮换**: Each `BAIZ_API_TOKEN` is scoped to the team that created it and can only access Facebook resources authorized by that team. Tokens can be regenerated or revoked at any time from the Yuri dashboard under **API Management**. We recommend rotating tokens periodically (e.g., every 90 days). / 每个 `BAIZ_API_TOKEN` 仅限创建它的团队使用，只能访问该团队已授权的 Facebook 资源。可随时在尤里改后台「API管理」中重新生成或吊销 Token，建议定期轮换（如每 90 天）。
- **Facebook token lifecycle / Facebook Token 生命周期**: The gateway uses short-lived Facebook access tokens where possible and automatically refreshes them. Long-lived tokens are encrypted at rest with AES-256 and scoped per-team. / 网关尽可能使用短期 Facebook Access Token 并自动续期；长期 Token 使用 AES-256 加密存储，按团队隔离。

### Data & Logging / 数据与日志

- **Request logging / 请求日志**: Proxied request metadata (URL path, HTTP method, status code, timestamp) is logged for billing and troubleshooting. Request and response bodies are **not** persisted in logs. Do not include sensitive PII, passwords, or unrelated secrets in query parameters. / 代理请求的元数据（URL 路径、HTTP 方法、状态码、时间戳）会被记录用于计费与排障。请求体和响应体**不会**持久化到日志中。请勿在查询参数中携带无关敏感信息（如密码、长期密钥等）。
- **Encrypted storage / 加密存储**: All Facebook access tokens are encrypted at rest using AES-256. Access is scoped by team-level permissions — one team cannot access another team's tokens or data. / 所有 Facebook Access Token 使用 AES-256 加密存储，按团队级别权限隔离 — 不同团队之间无法相互访问。
- **Data retention / 日志保留**: Request metadata logs are retained for 90 days and then automatically purged. Billing records are retained for 1 year per financial compliance requirements. Users can request early deletion by contacting support. / 请求元数据日志保留 90 天后自动清除。计费记录按财务合规要求保留 1 年。用户可联系客服申请提前删除。
- **Audit logs / 审计日志**: Token creation, revocation, and Facebook account binding events are logged in the Yuri dashboard under **Audit Log**, visible to team admins. / Token 创建、吊销、Facebook 账号绑定等操作均记录在尤里改后台的「审计日志」中，团队管理员可查看。

### Best Practices / 使用建议

- **Least privilege / 最小权限**: Authorize only a dedicated Facebook test/sandbox account with minimum required permissions. Avoid binding high-privilege production accounts unless absolutely necessary. / 仅使用最小权限的测试/沙盒 Facebook 账号授权，非必要不绑定高权限主账号。
- **No PII in requests / 请勿传递敏感信息**: Do not include passwords, personal identification numbers, or unrelated secrets in request parameters or bodies. The proxy is designed for Facebook Graph API calls only. / 请勿在请求参数或请求体中包含密码、身份证号等无关敏感信息。本代理仅用于 Facebook Graph API 调用。
- **Verify TLS / 验证域名**: The gateway endpoint `https://facebook-graph.baiz.ai` is served over HTTPS with a valid TLS certificate issued by a public CA. You can verify the certificate in your browser or via `curl -v` before first use. / 网关端点 `https://facebook-graph.baiz.ai` 通过 HTTPS 提供服务，使用公共 CA 签发的有效 TLS 证书。首次使用前可通过浏览器或 `curl -v` 验证证书。
- **Rate limits / 频率限制**: Each team has independent rate limits (default: 60 requests/minute) and an optional total request cap. The gateway returns HTTP 429 when limits are exceeded — implement exponential backoff in your client. / 每个团队有独立的频率限制（默认 60 次/分钟）和请求总量上限，超限返回 HTTP 429，请设计合理的退避重试策略。
- **HTTPS only / 仅限 HTTPS**: All traffic between the client and gateway is encrypted via TLS. Plain HTTP connections are rejected. / 客户端与网关之间的所有流量通过 TLS 加密传输，不接受 HTTP 明文连接。

### Contact & Support / 联系与支持

For questions about data security, privacy policies, credential management, or compliance, contact the Yuri team:

- Website: https://baiz.ai
- Dashboard: https://baiz.ai (login to access API Management, Audit Logs, and Support)

如对数据安全、隐私政策、密钥管理或合规有任何疑问，请联系尤里改官方：https://baiz.ai（登录后台可访问 API 管理、审计日志与在线客服）。
