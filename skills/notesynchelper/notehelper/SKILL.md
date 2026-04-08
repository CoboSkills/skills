---
name: notehelper
description: 当用户想保存文章/链接到笔记库、搜索已保存的文章、或配置 API 密钥时触发。触发词：「保存」「存一下」「收藏」（save），「搜文章」「找找」「最近存了什么」（search），「配置笔记」「设置密钥」「连接笔记服务」（config）。也可直接使用 /notehelper save、search、config 命令。
license: MIT-0
compatibility: 需要网络访问 claw.notebooksyncer.com（笔记同步助手官方服务）；API 密钥手动获取后写入 ~/.openclaw/notehelper.json，无自动授权流程，不修改 shell 配置文件
metadata:
  openclaw:
    version: "1.0.0"
    optionalEnv:
      - NOTEHELPER_API_KEY
      - NOTEHELPER_BASE_URL
    configFile: ~/.openclaw/notehelper.json
    baseUrl: https://claw.notebooksyncer.com
    homepage: https://notebooksyncer.com
---

# NoteHelper

统一入口，管理 Obsidian Omnivore Server 笔记库。当前支持子命令：`save`、`search`、`config`。

## 安全说明

- **网络访问**：仅通过 HTTPS 请求 `claw.notebooksyncer.com`（笔记同步助手官方服务），不访问其他域名
- **本地文件**：仅在用户主动执行 config 时，将 API 密钥写入 `~/.openclaw/notehelper.json`，不修改 shell 配置文件（~/.bashrc 等）
- **授权方式**：无自动 OAuth 流程；密钥由用户手动获取后配置，**请勿在对话中直接粘贴 API 密钥**
- **传输内容**：save 时发送用户主动提供的文章标题/URL/正文；search 时发送搜索关键词；密钥仅作为请求头传输，不出现在请求体中

## Auth

执行 `save`/`search` 前，先检查 `$NOTEHELPER_API_KEY` 是否已设置。未设置时停止并提示：

```
未检测到 NOTEHELPER_API_KEY，请先运行 /notehelper config 完成配置。
```

**所有请求均需携带请求头**：
```
x-api-key: $NOTEHELPER_API_KEY
```

**Base URL**（可通过 `$NOTEHELPER_BASE_URL` 覆盖）：
```
https://claw.notebooksyncer.com
```

---

## 指令路由

| 用户意图 | 子命令 |
|---------|--------|
| 保存文章/链接，说"存一下"、"收藏"、发出一个 URL | `/notehelper save` |
| 搜索文章，说"找找"、"有没有关于 X 的"、"最近存了什么" | `/notehelper search` |
| 配置密钥，说"配置笔记"、"设置 API Key"、"连接笔记服务" | `/notehelper config` |

---

## /notehelper save

**接口**：`POST /api/articles`

从用户输入中提取以下字段，无法提取的留空：

| 字段 | 说明 | 必需 |
|------|------|------|
| `title` | 文章标题 | ✅ |
| `url` | 文章链接 | 建议填写 |
| `author` | 作者 | 可选 |
| `description` | 摘要 | 可选 |
| `content` | Markdown 正文 | 可选 |
| `siteName` | 来源站点名称 | 可选 |
| `labels` | 标签数组，自动 find-or-create | 可选 |
| `publishedAt` | 原文发布时间，ISO 8601 | 可选 |

**示例**：
```bash
curl -s -X POST https://claw.notebooksyncer.com/api/articles \
  -H "x-api-key: $NOTEHELPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "深入理解闭包",
    "url": "https://example.com/closures",
    "labels": ["前端", "JavaScript"]
  }'
```

**成功后**：显示保存的文章标题和 ID，格式：`✓ 已保存「{title}」(id: {id})`

---

## /notehelper search

**接口**：`POST /api/graphql`

> ⚠️ **关键**：搜索参数必须通过 `variables` 对象传递，key 固定为 `query`。内联在 GraphQL 字符串中的参数会被忽略。

**请求格式**：
```json
{
  "query": "query { search(query: \"\", first: 10, after: 0) { edges { node { id title url author savedAt } } pageInfo { totalCount hasNextPage } } }",
  "variables": {
    "query": "<搜索词或过滤器>",
    "first": 10,
    "after": 0
  }
}
```

**响应结构**：顶层 `edges[].node`（非 `data.search.items`）

**示例**：
```bash
curl -s -X POST https://claw.notebooksyncer.com/api/graphql \
  -H "x-api-key: $NOTEHELPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query{search(query:\"\",first:10,after:0){edges{node{id title url author savedAt}}pageInfo{totalCount hasNextPage}}}","variables":{"query":"react","first":10,"after":0}}'
```

**支持的过滤器**（写入 `variables.query` 字符串内）：

| 过滤器 | 含义 |
|--------|------|
| `in:archive` | 已归档文章 |
| `in:library` | 未归档文章 |
| `updated:2024-01-15T10:30:00Z` | 指定时间后更新 |

过滤器可与关键词组合：`variables.query` = `"react in:library"` 表示搜索未归档的 React 相关文章。

**结果展示**：列表形式，每条显示标题、作者、保存时间，底部显示总数。无结果时提示「笔记库中暂无相关文章」。

---

## /notehelper config

引导用户完成密钥配置，分两种情况：

### 情况 A：已有密钥

**第一步**：将密钥保存到配置文件（永久生效）
```bash
mkdir -p ~/.openclaw
echo '{"api_key":"<your_api_key>"}' > ~/.openclaw/notehelper.json
```

**第二步**：当前会话加载密钥
```bash
export NOTEHELPER_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.openclaw/notehelper.json'))['api_key'])")
```

**第三步**：验证连通性
```bash
curl -s -H "x-api-key: $NOTEHELPER_API_KEY" \
  https://claw.notebooksyncer.com/api/stats/article-count
# 预期：{"count": N}，HTTP 200
```

> 密钥存储在 `~/.openclaw/notehelper.json`，不修改 shell 配置文件。

### 情况 B：还没有密钥

通过**笔记同步助手**公众号（服务号）获取：

1. 扫描同目录下的 `qrcode.txt`（用等宽字体打开，对准手机扫码），或微信搜索关注「**笔记同步助手**」服务号
2. 在菜单中选择 **Obsidian** 或**思源笔记**
3. 按提示操作，即可获得专属 API 密钥
4. 拿到密钥后按情况 A 设置环境变量

---

## Common Mistakes

- search 参数必须走 `variables` 对象，key 为 `query`：`"variables":{"query":"AI"}` ✅，内联在 GraphQL 字符串里 ❌
- `labels` 传标签名字符串数组，不是 ID：`["前端", "JS"]` ✅，`["uuid-xxx"]` ❌
- 过滤器拼在 `variables.query` 字符串内：`"react in:library"` ✅，作为单独字段传 ❌
- 笔记 ID 为 UUID，操作具体文章需先 search 获取
