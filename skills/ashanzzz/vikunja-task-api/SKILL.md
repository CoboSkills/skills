---
name: vikunja-task-api
version: 2.0.0
description: Manage Vikunja projects and tasks (overdue/due/today), mark done, and get quick summaries via the Vikunja API.
homepage: https://vikunja.io/
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":["curl","jq"],"env":["VIKUNJA_URL"],"optionalEnv":["VIKUNJA_TOKEN","VIKUNJA_USERNAME","VIKUNJA_PASSWORD"]},"primaryEnv":"VIKUNJA_TOKEN"}}
---

# ✅ Vikunja Fast Skill (v2 API)

Use Vikunja as the **source of truth** for all task management. This skill supersedes any internal working-buffer tracking for user-visible tasks.

## API Base

- **Base URL**: `$VIKUNJA_URL/api/v1`（自动规范化）
- **Auth**: JWT Bearer token（`Authorization: Bearer <token>`）
- **Token 获取**: `POST /login`（用户名字段是 `username`）

## Critical API Differences（必须记住）

| 操作 | 正确方法 |
|------|---------|
| 创建项目 | `PUT /projects`（**PUT**，不是 POST） |
| 更新项目 | `POST /projects/{id}`（**POST**） |
| 创建任务 | `PUT /projects/{id}/tasks`（**PUT**，不是 POST） |
| 更新任务（含标记完成） | `POST /tasks/{id}` |
| 获取所有任务 | `GET /tasks`（**不是** `/tasks/all`） |
| 删除任务 | `DELETE /tasks/{id}` |
| 移动任务到看板桶 | `POST /projects/{project}/views/{view}/buckets/{bucket}/tasks` |

## Setup

```bash
# 环境变量（推荐写入 secure/api-fillin.env）
VIKUNJA_URL=http://192.168.8.11:3456
VIKUNJA_TOKEN=tk_xxxx   # API Token 或 JWT
```

## Quick Commands

```bash
# 登录获取 JWT（如果只有用户名密码）
curl -X POST "$VIKUNJA_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS","long_token":true}' | jq

# 列出所有项目
curl -s "$VIKUNJA_URL/projects" -H "Authorization: Bearer $VIKUNJA_TOKEN" | jq '.[] | {id,title}'

# 列出所有开放任务
curl -s "$VIKUNJA_URL/tasks" -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  | jq '.[] | select(.done == false) | {id,.title,due_date: .due_date,project_id}'

# 创建项目（PUT /projects）
curl -X PUT "$VIKUNJA_URL/projects" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"项目名称","description":"","identifier":"","hex_color":""}' | jq '{id,title}'

# 在项目中创建任务（PUT /projects/{id}/tasks）
curl -X PUT "$VIKUNJA_URL/projects/9/tasks" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"任务标题","description":"","due_date":"2026-04-30T23:59:00Z"}' | jq '{id,title}'

# 标记任务完成（POST /tasks/{id}）
curl -X POST "$VIKUNJA_URL/tasks/123" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"done": true}' | jq '{id,done,done_at}'

# 更新任务（POST /tasks/{id}，可改 project_id 移动任务）
curl -X POST "$VIKUNJA_URL/tasks/123" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":9,"title":"新标题"}' | jq '{id,project_id,title}'

# 删除任务（DELETE /tasks/{id}）
curl -X DELETE "$VIKUNJA_URL/tasks/123" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN"

# 批量更新任务
curl -X POST "$VIKUNJA_URL/tasks/bulk" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tasks":[{"id":1,"done":true},{"id":2,"done":true}]}' | jq
```

## Helper CLI（vikunja.sh）

```bash
# 列出开放任务（按到期时间排序）
vikunja.sh list --filter 'done = false'

# 逾期任务
vikunja.sh overdue

# 今日到期
vikunja.sh due-today

# 查看任务详情
vikunja.sh show 123

# 标记完成
vikunja.sh done 123

# 创建任务
vikunja.sh create 9 "新任务标题"

# 删除任务
vikunja.sh delete 123
```

## Task Display Format

每个任务输出格式：
```
<EMOJI> <DUE_DATE> - #<ID> <TASK>
```

- Emoji：项目标题首字符（中文/英文标题第一个非字母数字token）
- 无 Emoji 时默认 🔨
- 无到期日显示 `(no due)`

## Filtering Syntax

Vikunja filter 示例：
```
done = false
done = false && due_date < now
done = false && project_id = 9
done = false && due_date >= now/d && due_date < now/d + 1d
```

完整文档：https://vikunja.io/docs/filters/

## Task Model（重要字段）

```json
{
  "id": 123,
  "title": "任务标题",
  "description": "",
  "done": false,
  "done_at": null,
  "due_date": "2026-04-30T15:59:00Z",
  "project_id": 9,
  "repeat_after": 0,
  "priority": 0,
  "start_date": "0001-01-01T00:00:00Z",
  "end_date": "0001-01-01T00:00:00Z",
  "hex_color": "",
  "percent_done": 0,
  "created": "2026-03-31T12:00:00Z",
  "updated": "2026-03-31T12:00:00Z"
}
```

注意：`due_date` 为 `0001-01-01T00:00:00Z` 表示无期限。
