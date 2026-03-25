---
name: heartbeat-memory
description: 自动记忆保存 Skill。支持 Heartbeat 自动触发和手动触发两种方式，自动检查新 sessions，生成 Daily 笔记，并定期提炼 MEMORY.md。具备智能自愈能力，自动适配调用环境。
---

# heartbeat-memory

> 🌐 **ClawHub:** [clawhub.ai/JustZeroX/heartbeat-memory](https://clawhub.ai/JustZeroX/heartbeat-memory)  
> 💻 **GitHub:** [github.com/JustZeroX/skill-heartbeat-memory](https://github.com/JustZeroX/skill-heartbeat-memory.git)

Heartbeat 自动记忆保存 - 支持 **Heartbeat 自动触发** 和 **手动触发** 两种方式。自动检查新 sessions，使用 OpenClaw 主 LLM 生成/更新 daily 笔记，并定期提炼 MEMORY.md。

**特点：**
- ✅ 智能自愈 - 自动检测调用环境，不对自动重启
- ✅ 双模式支持 - Heartbeat 自动触发 + 手动触发
- ✅ 文件系统扫描 - 支持备份已删除的 sessions

**推荐安装位置：** `~/.openclaw/skills/heartbeat-memory/`（全局目录，所有工作区共享）

---

## 🚀 快速开始

### 方式 1：自动触发（推荐 ⭐）

```bash
# 1. 安装
clawhub install heartbeat-memory

# 2. 重启 Gateway
openclaw gateway restart

# 3. 等待 Heartbeat 自动触发
```

首次运行会自动创建配置文件，无需额外配置！

### 方式 2：手动触发

**在你的 agent 代码中添加：**

```javascript
// 监听用户命令
if (message.includes('/heartbeat') || message.includes('保存记忆')) {
  await sessions_spawn({
    task: `const heartbeat = require('~/.openclaw/skills/heartbeat-memory/index.js'); await heartbeat.run();`,
    runtime: 'subagent',
    timeoutSeconds: 900
  });
}
```

**特点：**
- ✅ 智能自愈 - 即使直接调用也会自动重启
- ✅ 无需担心环境 - Skill 自己会处理

---

**建议首次配置（避免处理大量历史数据）：**
```json
// 编辑 $OPENCLAW_WORKSPACE/memory/heartbeat-memory-config.json
{
  "memorySave": {
    "processSessionsAfter": "2026-03-01T00:00:00Z",
    "maxSessionsPerRun": 20
  }
}
```

---

## 🎯 核心功能

- **自动检查新 sessions** - 每次 Heartbeat 触发时自动扫描
- **智能分批处理** - 根据任务量自动选择处理策略
- **Daily 笔记生成** - 自动生成格式化的每日聊天记录
- **MEMORY.md 提炼** - 定期提炼长期记忆
- **状态追踪** - 记录处理进度，支持断点续处理
- **完成通知** - 处理后自动发送通知

---

## 🔧 安装

### 方式 1：Via ClawHub（推荐 ⭐）

若未安装 clawhub，请先安装：
```bash
npm install -g clawhub
```

已安装 clawhub 后，执行：
```bash
clawhub install heartbeat-memory
openclaw gateway restart
```

**优点：**
- ✅ 一键安装，自动下载到全局目录
- ✅ 所有工作区共享
- ✅ 支持后续更新

### 方式 2：Manual / Git

```bash
git clone https://github.com/JustZeroX/skill-heartbeat-memory.git ~/.openclaw/skills/heartbeat-memory
openclaw gateway restart
```

**适用场景：**
- ✅ 想要自定义代码
- ✅ 参与贡献开发
- ✅ ClawHub 不可用时

### 验证安装

```bash
ls ~/.openclaw/skills/heartbeat-memory/SKILL.md
```

看到文件即表示安装成功。

---

## 📖 使用指南

### 执行方式

**方式 1：Heartbeat 自动触发（推荐）**
```
Heartbeat 每 30 分钟触发 → 自动执行 heartbeat-memory
```

**方式 2：手动调用（subagent 环境）**
```javascript
const heartbeat = require('~/.openclaw/skills/heartbeat-memory/index.js');
await heartbeat.run();  // 自动使用全局工具
```

**方式 3：手动调用（传工具函数）**
```javascript
await heartbeat.processSessions(
  sessions_list,
  sessions_history,
  sessions_spawn,
  message,
  feishu_get_user,
  configOverride,
  specifiedWorkspace
);
```

### 查看结果

```bash
# 查看当前工作区
echo $OPENCLAW_WORKSPACE

# 查看 Daily 笔记
cat $OPENCLAW_WORKSPACE/memory/daily/YYYY-MM-DD.md

# 查看长期记忆
cat $OPENCLAW_WORKSPACE/MEMORY.md

# 查看配置
cat $OPENCLAW_WORKSPACE/memory/heartbeat-memory-config.json

# 查看状态
cat $OPENCLAW_WORKSPACE/memory/heartbeat-state.json
```

### 修改配置

```bash
vim $OPENCLAW_WORKSPACE/memory/heartbeat-memory-config.json
```

---

## 🚀 手动触发

**用户要求立即执行时（不等待 Heartbeat）：**

### 方式 1：通过聊天命令触发

在你的 agent 代码中添加：

```javascript
// 监听用户命令
if (message.includes('/heartbeat') || message.includes('触发记忆保存')) {
  await sessions_spawn({
    task: `
      const heartbeat = require('~/.openclaw/skills/heartbeat-memory/index.js');
      await heartbeat.run();
    `,
    runtime: 'subagent',
    timeoutSeconds: 900
  });
}
```

### 方式 2：直接在 subagent 中调用

```javascript
await sessions_spawn({
  task: `const heartbeat = require('~/.openclaw/skills/heartbeat-memory/index.js'); await heartbeat.run();`,
  runtime: 'subagent',
  timeoutSeconds: 900
});
```

### ⚠️ 重要注意事项

**必须用 `sessions_spawn`，不能直接 require！**

```javascript
// ❌ 错误：直接 require 会报错（缺少工具注入）
const heartbeat = require('./heartbeat-memory/index.js');
await heartbeat.run();  // 报错：sessions_list 不可用

// ✅ 正确：通过 sessions_spawn 启动 subagent
await sessions_spawn({
  task: `const heartbeat = require('...'); await heartbeat.run();`,
  runtime: 'subagent'
});
```

**原因：** heartbeat-memory 需要以下工具注入：
- `sessions_list` - 获取会话列表
- `sessions_history` - 获取消息内容
- `sessions_spawn` - 启动 LLM 提炼
- `message` - 发送通知

这些工具只在 subagent 环境中自动注入。

---

## 🤖 智能自愈

**Skill 会自动检测环境，不对就自己重启！**

### 工作原理

```
用户调用 run()
    ↓
检查工具是否可用
    ↓
┌─────────────────────────────────┐
│  工具可用？                     │
│  - 是 → 直接执行 ✅             │
│  - 否 → 自动通过 sessions_spawn │
│            重启执行 🔄          │
└─────────────────────────────────┘
```

### 示例

**场景 1：直接调用（环境不对）**

```javascript
// 用户在主 Agent 中直接调用
const heartbeat = require('~/.openclaw/skills/heartbeat-memory/index.js');
await heartbeat.run();

// 之前：报错 ❌
// 现在：自动通过 sessions_spawn 重启，正常执行 ✅
```

**输出：**
```
🚀 heartbeat-memory (自包含模式) 启动...

⚠️  检测到当前环境缺少必要工具
🔄 尝试通过 sessions_spawn 自动重启...

✅ 自愈成功！已在正确的环境中执行
```

**场景 2：通过 sessions_spawn 调用（环境正确）**

```javascript
// 通过 sessions_spawn 调用
await sessions_spawn({
  task: `const heartbeat = require('...'); await heartbeat.run();`,
  runtime: 'subagent'
});

// 直接执行，无需重启
```

**输出：**
```
🚀 heartbeat-memory (自包含模式) 启动...

✅ 工具检查通过:
   ✅  sessions_list
   ✅  sessions_history
   ✅  sessions_spawn
   ✅  message
   ✅  feishu_get_user
```

### 优势

| 特性 | 之前 | 现在 |
|------|------|------|
| **环境检测** | ✅ 有 | ✅ 有 |
| **报错提示** | ✅ 有 | ✅ 有 |
| **自动修复** | ❌ 无 | ✅ 有 |
| **用户体验** | ⚠️ 需要手动改 | ✅ 自动完成 |

**现在用户不需要知道技术细节，Skill 自己会处理！**

---

## 💡 获取帮助

**如果自愈失败，Skill 会告诉你原因！**

### 错误提示

如果在不正确的环境中调用且无法自愈，Skill 会输出：

```
❌ 当前环境缺少必要工具，且无法自动重启。
请通过 sessions_spawn 调用此 Skill。
```

### 设计理念

**Skill 应该"智能"而不是"教育"！**

- ✅ 检测调用环境
- ✅ 自动修复问题（优先）
- ✅ 修复失败才报错
- ✅ 错误信息包含解决方案

这样用户不需要学习技术细节，直接调用就能用！

---

## 🔧 配置说明

### 🚀 无需配置 LLM！

Skill 会自动使用 OpenClaw 主配置的 LLM，无需单独配置 API Key。

### 自动初始化

首次运行时会自动：
1. ✅ 创建配置文件
2. ✅ 初始化状态文件
3. ✅ 创建必要目录

### 可选配置项

编辑 `<工作区>/memory/heartbeat-memory-config.json`：

| 配置项 | 说明 | 默认值 | 可选值 |
|--------|------|--------|--------|
| enabled | 是否启用 | true | true/false |
| batchSize | 每批处理数 | 5 | 1-10 |
| largeTaskThreshold | subagent 阈值 | 10 | 5-20 |
| timeoutSeconds | LLM 超时时间（秒） | 1000 | 300-3600 |
| notifyTarget | 通知目标（user:xxx 或 chat:xxx） | 自动获取当前用户 | 任意 channel 支持的 target |
| processSessionsAfter | 只处理此日期后的 sessions | null (全部) | ISO 日期格式 |
| specifiedWorkspace | 手动指定工作区路径 | null (自动检测) | 绝对路径 |
| maxSessionsPerRun | 单次最多处理 sessions 数 | 50 | 10-200 |
| refineSchedule.type | 提炼频率 | weekly | weekly/interval |
| refineSchedule.dayOfWeek | 每周几 | sunday | monday-sunday |
| refineSchedule.time | 每日时间 | "20:00" | HH:mm 格式 |
| refineSchedule.days | 每几天 | 7 | 1-30 |

**timeoutSeconds 建议：**
- 少量 sessions (<10 个)：300-600 秒
- 中量 sessions (10-30 个)：600-1000 秒
- 大量 sessions (>30 个)：1000-1800 秒
- 首次运行（全量处理）：1800-3600 秒

**notifyTarget 自动获取逻辑：**
1. 优先用 `feishu_get_user` 获取当前用户
2. Fallback: 从 sessionKey 提取用户 ID
3. 最终 fallback: 不发送通知（静默执行）

### 配置示例

**基础配置（默认）：**
```json
{
  "memorySave": {
    "enabled": true
  }
}
```

**首次运行限制（避免处理大量历史数据）：**
```json
{
  "memorySave": {
    "enabled": true,
    "processSessionsAfter": "2026-03-01T00:00:00Z",
    "maxSessionsPerRun": 20
  }
}
```

**指定通知渠道（飞书）：**
```json
{
  "notifyTarget": "feishu:ou_xxxxxxxxxxxxx",
  "memorySave": {
    "enabled": true
  }
}
```

**完整配置示例：**
```json
{
  "notifyTarget": "feishu:ou_xxxxxxxxxxxxx",
  "specifiedWorkspace": null,
  "memorySave": {
    "enabled": true,
    "batchSize": 5,
    "maxSessionsPerRun": 50,
    "processSessionsAfter": "2026-03-01T00:00:00Z",
    "timeoutSeconds": 600,
    "refineSchedule": {
      "type": "weekly",
      "dayOfWeek": "sunday",
      "time": "20:00"
    }
  }
}
```

---

## 📊 处理策略

### 首次启用

首次运行时：
- 自动扫描所有 sessions
- 分批处理（每批 5 个）
- 生成对应日期的 Daily 笔记
- 首次强制触发一次 MEMORY.md 提炼

### 日常增量

| 数量 | 策略 | 耗时 |
|------|------|------|
| < 5 个 | 直接处理 | <2 分钟 |
| 5-10 个 | 分批处理 | 2-5 分钟 |
| > 10 个 | 启动 subagent | 5-10 分钟 |

### 处理流程

```
Heartbeat 触发
    ↓
sessions_list 获取会话列表
    ↓
sessions_history 获取消息内容
    ↓
sessions_spawn 启动 subagent 进行 LLM 提炼
    ↓
写入 Daily 笔记
    ↓
检查 shouldRefine（根据 lastRefine 判断）
    ↓
定期提炼 MEMORY.md
    ↓
发送完成通知
```

---

## ❓ 常见问题

**Q: 需要配置 LLM API Key 吗？**  
A: **不需要！** Skill 会自动使用 OpenClaw 主配置的 LLM，通过 subagent 方式调用。

**Q: 多久检查一次？**  
A: 跟随 Heartbeat 频率：
- 工作日：09:00 / 14:00 / 20:00
- 周末：10:00 / 20:00

**Q: 如何查看处理进度？**  
A: 处理完成后会自动发送通知，包含：检查 sessions 数、新处理数、是否提炼 MEMORY。

**Q: 可以修改提炼频率吗？**  
A: 可以，编辑配置文件：
```json
{
  "refineSchedule": {
    "type": "weekly",
    "dayOfWeek": "sunday",
    "time": "20:00"
  }
}
```

**Q: 如何处理大量 sessions？**  
A: 自动分批处理，每次 Heartbeat 最多处理 5 个，剩余下次继续。

**Q: 可以禁用自动保存吗？**  
A: 可以，配置文件中设置 `"enabled": false`。

**Q: 首次运行会提炼 MEMORY.md 吗？**  
A: **会！** 首次运行会强制触发一次 MEMORY.md 提炼，之后按计划频率执行。

---

## 🌍 多工作区与跨平台

### 跨平台兼容

- ✅ **macOS** - 完全支持
- ✅ **Linux** - 完全支持
- ✅ **Windows** - 完全支持（PowerShell/CMD）

### 多工作区支持

Skill 自动支持多工作区，无需额外配置：

| 工作区类型 | 配置位置 | 数据位置 |
|-----------|---------|---------|
| **默认工作区** | `~/.openclaw/workspace/` | `~/.openclaw/workspace/memory/` |
| **自定义工作区** | `$OPENCLAW_WORKSPACE/` | `$OPENCLAW_WORKSPACE/memory/` |
| **项目工作区** | `./.openclaw/` | `./.openclaw/memory/` |

### 切换工作区

**方法 1：环境变量**
```bash
export OPENCLAW_WORKSPACE=/path/to/your/workspace
openclaw gateway restart
```

**方法 2：当前目录**
```bash
cd /path/to/your/workspace
# Skill 会自动检测当前目录
```

---

## 📝 示例

### Daily 笔记示例

```markdown
# YYYY-MM-DD 聊天记录

## 📊 当日总结
- 总会话数：X 个
- 活跃：X | 删除：X | 重置：X
- 主要话题：[话题 1], [话题 2]

## 💬 会话详情

### 📋 通用技能迁移到全局目录
**标签：** ✅ | #Skill #技能管理 #OpenClaw
**时间：** 10:05-10:16
**摘要：** 讨论将通用技能从工作区迁移到全局技能库...

**关键决策：**
- 通用技能迁移到 ~/.openclaw/skills/
- 个人专用技能保留在工作区
```

### MEMORY.md 示例

```markdown
# MEMORY.md - 长期记忆

## 👤 用户偏好
- **语言：** 简体中文
- **时区：** 东八区
- **交流风格：** 直接高效

## 🎯 重要决策
- [日期]：[决策内容]

## 📈 项目进展
- 记忆系统：已完成
- 技能管理：已完成
```

---

## ⚠️ 错误处理

**LLM 调用失败**
- 自动重试 2 次
- 失败后使用降级摘要
- 记录错误日志

**超时处理**
- 单次处理超时 600 秒
- 保存已处理内容
- 下次 Heartbeat 继续

**通知失败**
- 不影响主流程
- 记录错误日志
- 继续处理

---

## 🔮 未来计划

- [ ] 支持自定义通知渠道
- [ ] 支持记忆搜索
- [ ] 支持记忆关联
- [ ] 支持记忆导出

---

## 📦 附录：状态文件说明

```json
{
  "processedSessions": ["session-id-1", "session-id-2"],  // 已处理的 session
  "lastCheck": "2026-03-20T12:00:00.000Z",              // 上次检查时间
  "lastRefine": "2026-03-20T12:00:00.000Z",            // 上次 MEMORY.md 提炼时间
  "memorySave": { "enabled": true }                      // 配置
}
```
