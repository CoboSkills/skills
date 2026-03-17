---
name: xhs-publish
description: 小红书一键发布 — AI 全流程搞定：自动生成标题 → 撰写正文 → 设计封面 → 制作视频 → 一键发布。3 分钟从创意到上线，支持多模型自由切换。触发词：发小红书、发布笔记、小红书发布、发笔记、小红书笔记、写小红书、写笔记、小红书文案、小红书封面、帮我写个笔记、生成小红书内容。
metadata: {"openclaw": {"emoji": "📕", "requires": {"bins": ["convert"], "anyBins": ["curl"]}}}
---

# 📕 小红书发布助手

**核心能力**：文案创作（标题+正文+封面图）和笔记发布（图文/视频）

---

## 一、完整发布流程

```
用户请求写笔记/发小红书
        │
        ▼
  生成标题（5个风格）
        │
        ▼
  确认标题 → 询问笔记类型
        │
   ┌────┴────┐
   │         │
   ▼         ▼
📷 图文     🎬 视频
   │         │
   ▼         ▼
 生成正文   生成正文
(600-800字) (200-300字)
   │         │
   ▼         ▼
 确认正文   确认正文
   │         │
   ▼         ▼
 AI生成封面 AI生成视频
 (自动)      (自动)
   │         │
   ▼         ▼
 确认封面   确认视频
   │         │
   └────┬────┘
        │
        ▼
    发布流程
```

---

## 二、文案创作

### 2.1 生成标题

**优先使用当前对话模型**，参考 [references/title-guide.md]({baseDir}/references/title-guide.md) 生成 5 个不同风格的标题。

**核心要求**：

1. 每个标题使用不同风格
2. 20 字以内
3. 含 1-2 个 emoji
4. 禁用平台禁忌词

**输出后询问用户**：

> 标题已生成，请选择：
> 1. 选择某个标题继续
> 2. 重新生成
> 3. 自定义标题

**用户确认标题后，询问**：

> 请选择笔记类型：
> 1. **📷 图文笔记** — 封面图 + 正文（最常用）
> 2. **🎬 视频笔记** — 视频文件 + 正文（适合教程/分享）

---

### 2.2 生成正文

**优先使用当前对话模型**，参考 [references/content-guide.md]({baseDir}/references/content-guide.md)。

**字数要求**：

- 图文笔记：600-800 字，自然语气，文末 5-10 个标签
- 视频笔记：200-300 字，简洁有力，突出重点

**格式要求**：

1. 小标题：加合适的图标（如 💡、🔧、📚、🎯 等）
2. 有顺序的内容：加数字图标（如 1️⃣、2️⃣、3️⃣ 或 ①②③）
3. 分段清晰：段落之间用空行分隔

**输出后询问用户**：

> 正文已生成，是否满意？
> 1. 满意，继续下一步
> 2. 重新生成
> 3. 手动修改

**用户确认正文后**：

- 📷 图文笔记 → 进入 2.3 生成封面图
- 🎬 视频笔记 → 进入 2.4 生成视频

---

### 2.3 生成封面图（图文笔记）

**⚠️ 直接使用 AI 生成，不需要询问用户选择方式！**

**自动执行流程**：

1. 生成英文 Prompt：根据文案主题和 [references/cover-guide.md]({baseDir}/references/cover-guide.md) 自动生成
2. 调用 AI 生图：优先使用 Doubao（豆包）API
3. 输出封面图：1080x1080 正方形

**Prompt 模板**：

```
cute cartoon illustration style, [场景描述], kawaii anime style, soft pastel [色调] colors, minimal clean background, with Chinese text "[标题]" at top, no watermark, high quality, square format, poster design
```

**生图调用示例**：

```bash
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/images/generations" \
  -H "Authorization: Bearer $DOUBAO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "cute cartoon illustration style, ...",
    "size": "2048x2048",
    "n": 1
  }'
```

**封面图生成后询问用户**：

> 封面图已生成，是否满意？
> 1. 满意，直接发布
> 2. 重新生成
> 3. 手动调整

**用户选择 1（满意，直接发布）** → 进入「三、发布流程」

---

### 2.4 生成视频（视频笔记）

**⚠️ 直接使用 AI 生成，不需要询问用户选择方式！**

**⚠️ 视频笔记不需要生成封面图！** 小红书会自动从视频中截取。

**自动执行流程**：

1. 生成英文 Prompt：根据文案主题生成视频描述
2. 检查可用模型：Doubao（豆包）、Kling（可灵）
3. 生成视频：5-10 秒
4. 输出视频文件

**Prompt 生成规则（根据主题选择风格）**：

**教程类**：
- 风格：步骤演示
- 示例：`A step-by-step tutorial animation showing [具体操作], clean UI design, professional lighting, 4K quality`

**分享类**：
- 风格：生活场景
- 示例：`A cozy lifestyle scene with [具体场景], warm lighting, soft colors, cinematic quality, 4K`

**产品类**：
- 风格：产品展示
- 示例：`Product showcase of [产品名], rotating view, clean background, studio lighting, 4K quality`

**知识类**：
- 风格：图文动画
- 示例：`Animated infographic explaining [知识点], modern design, smooth transitions, professional style`

**日常类**：
- 风格：Vlog 风格
- 示例：`Daily life vlog scene showing [场景], natural lighting, authentic feel, handheld camera style`

**Prompt 模板**：

```
[视频风格], [具体场景描述], [画面细节], [光照/色调], [质量要求], --duration 10
```

**示例**：

```
# 教程类
"A step-by-step tutorial animation showing how to install AI skills, with floating icons and text labels, clean modern UI design, professional lighting, 4K quality, smooth motion, --duration 10"

# 分享类
"A cozy lifestyle scene with a friendly robot assistant working at a desk, warm golden hour lighting, soft pastel colors, cinematic quality, depth of field, --duration 10"

# 知识类
"Animated infographic explaining what Skills are, with colorful icons floating and connecting, modern flat design, smooth transitions, professional style, --duration 10"
```

**视频生成调用（Doubao）**：

```bash
# 1. 提交任务
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Authorization: Bearer $DOUBAO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [{"type": "text", "text": "...prompt内容..."}]
  }'

# 2. 轮询任务状态（每 15 秒）
curl -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}" \
  -H "Authorization: Bearer $DOUBAO_API_KEY"

# 3. 下载视频（状态为 succeeded 时）
# 视频 URL 在响应的 output.video_urls 中
```

**注意事项**：

1. 视频时长：5-10 秒（用 `--duration` 参数控制）
2. 生成时间：1-5 分钟
3. Prompt 语言：必须用英文
4. 质量要求：始终包含 "4K quality" 或 "high quality"

**视频生成后询问用户**：

> 视频已生成，是否满意？
> 1. 满意，直接发布
> 2. 重新生成
> 3. 手动调整

**用户选择 1（满意，直接发布）** → 进入「三、发布流程」

---

## 三、发布流程

**⚠️ 用户确认封面图/视频后，立即发布，不需要询问！**

### 3.1 立即发布

#### 前置检查

执行环境检查：

```bash
bash {baseDir}/check_env.sh
```

**返回码说明**：

- `0` = 正常已登录 → 继续发布
- `1` = 未安装 → 进入「五、安装 MCP 服务」
- `2` = 未登录 → 进入「四、登录流程」

#### 发布图文笔记

调用 MCP `publish_content` 工具：

```python
{
    "name": "publish_content",
    "arguments": {
        "title": "标题",
        "content": "正文",
        "images": ["/path/to/cover.jpg"],  # ⚠️ 用路径，不要用 base64！
        "tags": ["标签1", "标签2"]
    }
}
```

#### 发布视频笔记

调用 MCP `publish_with_video` 工具：

```python
{
    "name": "publish_with_video",
    "arguments": {
        "title": "标题",
        "content": "正文",
        "video": "/path/to/video.mp4"  # ⚠️ 用路径，不要用 base64！
    }
}
```

#### 超时处理

**MCP 发布超时设置为 180 秒（3 分钟）**：

```bash
curl -s --max-time 180 -X POST "$MCP_URL" ...
```

**💡 温馨提示**：
> 发布中，请耐心等待 1-3 分钟，不要关闭页面...

**发布失败自动重试机制**：

1. 第一次发布：调用 MCP 发布笔记
2. 如果失败：自动重试 1 次
3. 如果仍然失败：自动获取登录二维码，提示用户重新登录

**完整处理流程**：

```bash
# 第一次发布
RESULT=$(curl -s --max-time 180 -X POST "$MCP_URL" ...)

# 检查是否成功
if echo "$RESULT" | grep -q '"error"'; then
  # 自动重试 1 次
  echo "第一次发布失败，自动重试..."
  RESULT=$(curl -s --max-time 180 -X POST "$MCP_URL" ...)
  
  # 如果仍然失败，获取登录二维码
  if echo "$RESULT" | grep -q '"error"'; then
    echo "发布失败，需要重新登录"
    # 调用 get_login_qrcode 获取二维码
    # 发送给用户扫码
  fi
fi
```

**发布失败后输出给用户**：

> ⚠️ 发布失败，已自动重试 1 次，仍然失败。可能是登录状态失效，请扫码重新登录：[二维码图片]

### 3.2 稍后发布（手动）

**仅当用户选择"手动调整"或发布失败时使用**

**保存内容到本地**：

- 封面图：`/root/.openclaw/media/inbound/xhs_cover_标题.png`
- 视频文件：原位置不变
- 标题+正文：输出给用户复制

**输出给用户**：

> 内容已保存：
> - 封面图：`/path/to/cover.jpg`
> - 标题：xxx
> - 正文：xxx
> 
> 你可以手动复制到小红书 App 发布。

---

## 四、登录流程

当前置检查返回 `2`（未登录）或发布超时时执行。

### 4.1 方式一：扫码登录（优先尝试）

**⚠️ 小红书需要扫码两次**：
1. 第一次：验证账号
2. 第二次：确认登录设备

**获取二维码**：

```bash
MCP_URL="http://localhost:18060/mcp"

# 1. 初始化
SESSION_ID=$(curl -s -D /tmp/headers -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}},"id":1}' \
  > /dev/null && grep -i 'Mcp-Session-Id' /tmp/headers | awk '{print $2}')

# 2. 获取第一个二维码（超时 30 秒）
curl -s --max-time 30 -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_login_qrcode","arguments":{}},"id":2}'
```

**输出给用户**：
> 🔄 小红书登录需要扫码两次
> 
> 1️⃣ 第一次：验证账号
> 2️⃣ 第二次：确认登录设备
> 
> 请先扫第一个二维码：[二维码图片]

**等待扫码并检测二次确认**：

```bash
# 每 5 秒检查一次登录状态
for i in $(seq 1 18); do  # 最多等待 90 秒
  sleep 5
  
  # 检查登录状态
  STATUS=$(curl -s -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
    -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"check_login_status","arguments":{}},"id":3}')
  
  if echo "$STATUS" | grep -q "已登录"; then
    echo "✅ 登录成功"
    break
  fi
  
  # 如果检测到需要二次确认，发送第二个二维码
  if echo "$STATUS" | grep -q "确认\|二次"; then
    # 获取第二个二维码
    QR2=$(curl -s -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
      -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_login_qrcode","arguments":{}},"id":4}')
    
    # 发送第二个二维码给用户
    echo "请再扫第二个二维码确认：[二维码图片]"
  fi
done
```

**如果扫码失败或超时** → 直接提示用户使用 Cookie 登录（见 4.2）

---

### 4.2 方式二：Cookie 登录（备选）

当扫码登录失败时使用。

**获取 Cookie**：
1. 打开浏览器，访问 https://www.xiaohongshu.com 并登录
2. 按 F12 打开开发者工具 → Application → Cookies
3. 复制以下 Cookie 值：`a1`、`web_session`、`websectiga`、`id_token`

**更新 Cookie 文件**：
```bash
nano /root/xiaohongshu-mcp/cookies.json
```

**重启 MCP 服务**：
```bash
pkill -f xiaohongshu-mcp && sleep 3
cd /root/xiaohongshu-mcp && export DISPLAY=:99
nohup ./xiaohongshu-mcp-linux-amd64 -port :18060 > mcp.log 2>&1 &
```

**验证登录**：返回 `✅ 已登录` 即成功。

**前置检查**：

```bash
# 检查 Xvfb 是否运行
if ! pgrep -x Xvfb > /dev/null; then
  echo "Xvfb 未运行，正在启动..."
  Xvfb :99 -screen 0 1920x1080x24 &
  sleep 2
fi

# 重启 MCP（确保 DISPLAY=:99）
pkill -f xiaohongshu-mcp
sleep 2
cd /root/xiaohongshu-mcp
export ROD_DEFAULT_TIMEOUT=10m
DISPLAY=:99 nohup ./xiaohongshu-mcp-linux-amd64 -port :18060 > mcp.log 2>&1 &
sleep 5
```

调用 MCP `get_login_qrcode` 获取二维码：

```bash
MCP_URL="http://localhost:18060/mcp"

# 1. 初始化
SESSION_ID=$(curl -s -D /tmp/headers -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}},"id":1}' \
  > /dev/null && grep -i 'Mcp-Session-Id' /tmp/headers | awk '{print $2}')

# 2. 确认初始化
curl -s -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' > /dev/null

# 3. 获取二维码（超时 30 秒）
curl -s --max-time 30 -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_login_qrcode","arguments":{}},"id":2}'
```

**如果超时（30 秒无响应或空响应）**：

1. 立即检查 Xvfb 是否运行：`pgrep -x Xvfb`
2. 如果未运行，启动 Xvfb：`Xvfb :99 -screen 0 1920x1080x24 &`
3. 重启 MCP：`DISPLAY=:99 nohup ./xiaohongshu-mcp-linux-amd64 -port :18060 &`
4. 等待 5 秒后重新获取二维码

**输出给用户**：

> 请用小红书 App 扫码登录：[二维码图片]

### 4.2 验证登录状态

用户扫码后，调用 MCP `check_login_status` 验证：

```bash
curl -s -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"check_login_status","arguments":{}},"id":3}'
```

**判断登录结果**：

1. `"isLoggedIn": true` → ✅ 登录成功，重新执行发布流程
2. `"isLoggedIn": false` → ❌ 未登录，提示用户重新扫码
3. 超时/无响应 → ❌ 登录失败，提示用户重新扫码

---

## 五、安装 MCP 服务

当前置检查返回 `1`（未安装）时执行。

### 5.1 安装依赖

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y xvfb imagemagick zbar-tools xdotool fonts-noto-cjk

# CentOS/RHEL
sudo yum install -y xorg-x11-server-Xvfb ImageMagick zbar xdotool
```

### 5.2 启动虚拟显示

```bash
Xvfb :99 -screen 0 1920x1080x24 &
```

### 5.3 下载并启动 MCP

```bash
mkdir -p ~/xiaohongshu-mcp && cd ~/xiaohongshu-mcp
wget https://github.com/xpzouying/xiaohongshu-mcp/releases/latest/download/xiaohongshu-mcp-linux-amd64.tar.gz
tar xzf xiaohongshu-mcp-linux-amd64.tar.gz
chmod +x xiaohongshu-*

# 启动（设置超时避免视频发布超时）
export ROD_DEFAULT_TIMEOUT=10m
DISPLAY=:99 nohup ./xiaohongshu-mcp-linux-amd64 -port :18060 > mcp.log 2>&1 &
```

---

## 六、MCP 调用规范

### 6.1 调用流程

```bash
MCP_URL="http://localhost:18060/mcp"

# 1. 初始化并获取 Session ID
SESSION_ID=$(curl -s -D /tmp/headers -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}},"id":1}' \
  > /dev/null && grep -i 'Mcp-Session-Id' /tmp/headers | awk '{print $2}')

# 2. 确认初始化
curl -s -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' > /dev/null

# 3. 调用工具
curl -s -X POST "$MCP_URL" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"工具名","arguments":{}},"id":2}'
```

### 6.2 超时设置

- 登录检查/二维码：10-15 秒
- 搜索/详情：30 秒
- **发布笔记：180 秒（3 分钟）**

**⚠️ 发布失败自动重试 1 次，仍然失败则自动获取登录二维码！**

### 6.3 可用工具

- `check_login_status` — 检查登录状态
- `get_login_qrcode` — 获取登录二维码
- `publish_content` — 发布图文笔记
- `publish_with_video` — 发布视频笔记

---

## 🔴 强制规则

### ✅ 正确做法

图片/视频必须使用服务器本地绝对路径：

```python
# ✅ 正确
"images": ["/root/.openclaw/media/inbound/cover.jpg"]
"video": "/root/.openclaw/media/inbound/video.mp4"
```

### ❌ 错误做法

不要用 base64 编码（会导致上传超时）：

```python
# ❌ 错误
"images": ["data:image/jpeg;base64,..."]
```

**⚠️ 永远用文件路径，永远不要用 base64！**

---

## 七、故障排查

### 7.1 诊断命令

```bash
pgrep -f xiaohongshu-mcp           # MCP 是否运行
pgrep -x Xvfb                      # Xvfb 是否运行
tail -20 ~/xiaohongshu-mcp/mcp.log # 查看日志
lsof -i :18060                     # 检查端口
```

### 7.2 常见错误

**1. 发布失败（已重试）**

- 原因：登录状态失效
- 解决：自动获取二维码，扫码重新登录

**2. `context deadline exceeded`**

- 原因：rod 库超时
- 解决：设置 `ROD_DEFAULT_TIMEOUT=10m`

**3. 图片上传超时**

- 原因：使用 base64 编码
- 解决：改用文件路径

---

## 八、参考文档

- 标题创作指南：[references/title-guide.md]({baseDir}/references/title-guide.md)
- 正文创作指南：[references/content-guide.md]({baseDir}/references/content-guide.md)
- 封面图生成指南：[references/cover-guide.md]({baseDir}/references/cover-guide.md)
