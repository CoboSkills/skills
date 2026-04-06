# GWS 安装与授权指南

完整的安装、配置和故障排查指南。

---

## 1. 安装 gws CLI

```bash
npm install -g @googleworkspace/cli
```

---

## 2. GCP 项目配置

### 2.1 启用 API

在 [Google Cloud Console](https://console.cloud.google.com) 启用以下 API：

| 服务 | 控制台 URL |
|------|-----------|
| Gmail | `apis/library/gmail.googleapis.com` |
| Drive | `apis/library/drive.googleapis.com` |
| Calendar | `apis/library/calendar.googleapis.com` |
| Sheets | `apis/library/sheets.googleapis.com` |
| Docs | `apis/library/docs.googleapis.com` |
| Slides | `apis/library/slides.googleapis.com` |
| Tasks | `apis/library/tasks.googleapis.com` |
| People | `apis/library/people.googleapis.com` |
| Forms | `apis/library/forms.googleapis.com` |
| Meet | `apis/library/meet.googleapis.com` |
| Classroom | `apis/library/classroom.googleapis.com` |

### 2.2 OAuth 同意屏幕配置

1. 访问 `apis/credentials/consent`
2. 配置应用信息（名称、支持邮箱、开发者联系邮箱）
3. **Scopes 标签页**：添加以下 scope：
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/presentations`
   - `https://www.googleapis.com/auth/tasks`
   - `https://www.googleapis.com/auth/forms.body`
   - `https://www.googleapis.com/auth/meetings.space.created`
   - `https://www.googleapis.com/auth/classroom.courses`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/userinfo.email`
4. **测试用户**（如处于测试模式）：添加你的 Google 账号

> **注意**：授权时若看到 "Google hasn't verified this app"，点击 Advanced → "Go to [app name] (unsafe)" 继续

### 2.3 OAuth 凭证

1. 访问 `apis/credentials` → "+ CREATE CREDENTIALS" → "OAuth client ID"
2. 应用类型：**Desktop app**
3. 下载 JSON → 保存为 `~/.config/gws/client_secret.json`

---

## 3. 授权方法

### 方法 A：直接授权（推荐）

```bash
export GOOGLE_WORKSPACE_PROJECT_ID=your-project-id
export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file

# 完整授权（所有服务）
gws auth login --full

# 或仅授权特定服务
gws auth login -s gmail,drive,calendar
```

授权完成后，凭证保存在 `~/.config/gws/credentials.enc`

### 方法 B：手动授权（无浏览器环境）

```bash
gws auth login --full
# 复制显示的 URL，在浏览器中打开并授权
# 复制回调 URL（http://localhost:xxxx/?code=...）
# 在终端粘贴 code 完成授权
```

---

## 4. 验证授权

```bash
gws auth status
```

应显示：
- `scope_count`: 12+
- `token_valid`: true

---

## 5. 故障排查

### "Insufficient authentication scopes" (403)

```bash
rm ~/.config/gws/token_cache.json
gws auth login --full
```

### "No OAuth client configured"

检查 `~/.config/gws/client_secret.json` 是否存在且命名正确

### "API has not been used in project"

在 GCP Console 中启用对应 API

### 完全重新授权

```bash
rm ~/.config/gws/credentials.enc
rm ~/.config/gws/token_cache.json
gws auth login --full
```

---

## 6. 环境变量

添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
export GOOGLE_WORKSPACE_PROJECT_ID=your-gcp-project-id
export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file
```
