# Heartbeat-Memory

🧠 Heartbeat 自动记忆保存 - 支持 **Heartbeat 自动触发** 和 **手动触发** 两种方式。自动检查新 sessions，生成 Daily 笔记，并定期提炼 MEMORY.md。

**特点：**
- ✅ 智能自愈 - 自动检测调用环境，不对自动重启
- ✅ 双模式支持 - Heartbeat 自动触发 + 手动触发
- ✅ 文件系统扫描 - 支持备份已删除的 sessions

<!-- Badge Row 1: Core Info -->
[![ClawHub](https://img.shields.io/badge/ClawHub-heartbeat--memory-E75C46?logo=clawhub)](https://clawhub.ai/JustZeroX/heartbeat-memory)
[![GitHub](https://img.shields.io/badge/GitHub-JustZeroX-181717?logo=github)](https://github.com/JustZeroX/skill-heartbeat-memory)
[![Version](https://img.shields.io/badge/version-0.0.4-orange)](https://github.com/JustZeroX/skill-heartbeat-memory)

<!-- Badge Row 2: Platforms -->
[![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white)](https://openclaw.ai) 
[![Windows](https://img.shields.io/badge/Windows-0078D6?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4OCA4OCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTAgMGgzOXYzOUgweiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik00OSAwaDM5djM5SDQ5eiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0wIDQ5aDM5djM5SDB6Ii8+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTQ5IDQ5aDM5djM5SDQ5eiIvPjwvc3ZnPg==)](https://openclaw.ai) 
[![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)](https://openclaw.ai)

<!-- Badge Row 3: License -->
[![License](https://img.shields.io/badge/License-MIT-BD2D2D)](LICENSE)

---

### 中文 | [English](#english-version)

---

## 目录

- [🚀 快速开始](#-快速开始)
- [✨ 核心功能](#-核心功能)
- [🔧 安装](#-安装)
- [📖 使用指南](#-使用指南)
- [⚙️ 配置说明](#️-配置说明)
- [📊 处理策略](#-处理策略)
- [❓ 常见问题](#-常见问题)
- [🌍 跨平台支持](#-跨平台支持)
- [📄 许可证](#-许可证)

---

## 🚀 快速开始

**3 步上手：**

```bash
# 1. 安装
clawhub install heartbeat-memory

# 2. 重启 Gateway
openclaw gateway restart

# 3. 等待 Heartbeat 自动触发（或手动触发）
```

首次运行会自动创建配置文件，无需额外配置！

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

## ✨ 核心功能

- **🤖 自动检查新 sessions** - 每次 Heartbeat 触发时自动扫描
- **📝 Daily 笔记生成** - 自动生成格式化的每日聊天记录
- **🧠 MEMORY.md 提炼** - 定期提炼长期记忆
- **📊 智能分批处理** - 根据任务量自动选择处理策略
- **📈 状态追踪** - 记录处理进度，支持断点续处理
- **🔔 完成通知** - 处理后自动发送通知
- **🚀 无需配置 LLM** - 自动使用 OpenClaw 主配置的 LLM
- **💾 自动初始化** - 首次运行自动创建配置文件和目录

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

**推荐安装位置：** `~/.openclaw/skills/heartbeat-memory/`（全局目录，所有工作区共享）

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

## ⚙️ 配置说明

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

## 🌍 跨平台支持

### 平台兼容

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

## 📄 许可证

MIT License

---

[Top / 返回顶部](#heartbeat-memory)

---

## English Version

### Table of Contents

- [🚀 Quick Start](#-quick-start)
- [✨ Core Features](#-core-features)
- [🔧 Installation](#-installation)
- [📖 Usage Guide](#-usage-guide)
- [⚙️ Configuration](#️-configuration)
- [📊 Processing Strategy](#-processing-strategy)
- [❓ FAQ](#-faq)
- [🌍 Cross-Platform Support](#-cross-platform-support)
- [📄 License](#-license)

---

### 🚀 Quick Start

**3 steps to get started:**

```bash
# 1. Install
clawhub install heartbeat-memory

# 2. Restart Gateway
openclaw gateway restart

# 3. Wait for Heartbeat auto-trigger (or manual trigger)
```

First run will auto-create config files, no extra configuration needed!

**Recommended first config (avoid processing large history):**
```json
// Edit $OPENCLAW_WORKSPACE/memory/heartbeat-memory-config.json
{
  "memorySave": {
    "processSessionsAfter": "2026-03-01T00:00:00Z",
    "maxSessionsPerRun": 20
  }
}
```

---

### ✨ Core Features

- **🤖 Auto Check Sessions** - Scan new sessions on every Heartbeat trigger
- **📝 Daily Note Generation** - Auto-generate formatted daily chat logs
- **🧠 MEMORY.md Refinement** - Periodically refine long-term memory
- **📊 Smart Batching** - Auto-select processing strategy based on task volume
- **📈 Progress Tracking** - Record processing state, support resume
- **🔔 Completion Notification** - Auto-send notification after processing
- **🚀 No LLM Config** - Auto-use OpenClaw's main LLM
- **💾 Auto Initialization** - Create config files and directories on first run

---

### 🔧 Installation

#### Option 1: Via ClawHub (Recommended ⭐)

If clawhub is not installed, install it first:
```bash
npm install -g clawhub
```

Then execute:
```bash
clawhub install heartbeat-memory
openclaw gateway restart
```

**Advantages:**
- ✅ One-click installation, auto-download to global directory
- ✅ Shared across all workspaces
- ✅ Support future updates

#### Option 2: Manual / Git

```bash
git clone https://github.com/JustZeroX/skill-heartbeat-memory.git ~/.openclaw/skills/heartbeat-memory
openclaw gateway restart
```

**Use Cases:**
- ✅ Want to customize code
- ✅ Participate in development
- ✅ ClawHub unavailable

#### Verify Installation

```bash
ls ~/.openclaw/skills/heartbeat-memory/SKILL.md
```

Seeing the file means installation is successful.

**Recommended Installation Location:** `~/.openclaw/skills/heartbeat-memory/` (global directory, shared by all workspaces)

---

### 📖 Usage Guide

#### Execution Methods

**Method 1: Heartbeat Auto-Trigger (Recommended)**
```
Heartbeat every 30 min → Auto-execute heartbeat-memory
```

**Method 2: Manual Call (subagent)**
```javascript
const heartbeat = require('~/.openclaw/skills/heartbeat-memory/index.js');
await heartbeat.run();
```

**Method 3: Manual Call (with tool functions)**
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

#### View Results

```bash
# View current workspace
echo $OPENCLAW_WORKSPACE

# View Daily notes
cat $OPENCLAW_WORKSPACE/memory/daily/YYYY-MM-DD.md

# View long-term memory
cat $OPENCLAW_WORKSPACE/MEMORY.md

# View config
cat $OPENCLAW_WORKSPACE/memory/heartbeat-memory-config.json

# View state
cat $OPENCLAW_WORKSPACE/memory/heartbeat-state.json
```

#### Modify Config

```bash
vim $OPENCLAW_WORKSPACE/memory/heartbeat-memory-config.json
```

---

### ⚙️ Configuration

#### 🚀 No LLM Config Needed!

Skill auto-uses OpenClaw's main LLM configuration, no need to configure API Key separately.

#### Auto Initialization

First run will automatically:
1. ✅ Create config files
2. ✅ Initialize state files
3. ✅ Create necessary directories

#### Optional Configuration

Edit `<workspace>/memory/heartbeat-memory-config.json`:

| Config | Description | Default | Options |
|--------|-------------|---------|---------|
| enabled | Enable/disable | true | true/false |
| batchSize | Batch size | 5 | 1-10 |
| largeTaskThreshold | Subagent threshold | 10 | 5-20 |
| timeoutSeconds | LLM timeout (seconds) | 1000 | 300-3600 |
| notifyTarget | Notification target | Auto-get current user | Any channel-supported target |
| processSessionsAfter | Only process sessions after this date | null (all) | ISO date format |
| specifiedWorkspace | Manually specify workspace path | null (auto-detect) | Absolute path |
| maxSessionsPerRun | Max sessions per run | 50 | 10-200 |
| refineSchedule.type | Refinement frequency | weekly | weekly/interval |
| refineSchedule.dayOfWeek | Which day of week | sunday | monday-sunday |
| refineSchedule.time | Daily time | "20:00" | HH:mm format |
| refineSchedule.days | Every how many days | 7 | 1-30 |

**timeoutSeconds Recommendations:**
- Few sessions (<10): 300-600 seconds
- Medium sessions (10-30): 600-1000 seconds
- Many sessions (>30): 1000-1800 seconds
- First run (full processing): 1800-3600 seconds

**notifyTarget Auto-Get Logic:**
1. Priority: Use `feishu_get_user` to get current user
2. Fallback: Extract user ID from sessionKey
3. Final fallback: No notification (silent execution)

#### Configuration Examples

**Basic Config (Default):**
```json
{
  "memorySave": {
    "enabled": true
  }
}
```

**First Run Limit (Avoid Processing Large History):**
```json
{
  "memorySave": {
    "enabled": true,
    "processSessionsAfter": "2026-03-01T00:00:00Z",
    "maxSessionsPerRun": 20
  }
}
```

**Specify Notification Channel (Feishu):**
```json
{
  "notifyTarget": "feishu:ou_xxxxxxxxxxxxx",
  "memorySave": {
    "enabled": true
  }
}
```

---

### 📊 Processing Strategy

#### First Enable

First run:
- Auto-scan all sessions
- Batch processing (5 per batch)
- Generate Daily notes for corresponding dates
- Force trigger one MEMORY.md refinement

#### Daily Incremental

| Count | Strategy | Time |
|-------|----------|------|
| < 5 | Direct process | <2 min |
| 5-10 | Batch process | 2-5 min |
| > 10 | Subagent | 5-10 min |

#### Workflow

```
Heartbeat Trigger
    ↓
sessions_list get session list
    ↓
sessions_history get message content
    ↓
sessions_spawn subagent for LLM refinement
    ↓
Write Daily notes
    ↓
Check shouldRefine (based on lastRefine)
    ↓
Periodically refine MEMORY.md
    ↓
Send completion notification
```

---

### ❓ FAQ

**Q: Need LLM API Key?**  
A: **No!** Skill auto-uses OpenClaw's main LLM via subagent.

**Q: How often to check?**  
A: Follows Heartbeat frequency:
- Weekdays: 09:00 / 14:00 / 20:00
- Weekends: 10:00 / 20:00

**Q: How to check progress?**  
A: Auto-send notification after completion, including: sessions checked, newly processed, whether MEMORY was refined.

**Q: Can I change refinement frequency?**  
A: Yes, edit config file:
```json
{
  "refineSchedule": {
    "type": "weekly",
    "dayOfWeek": "sunday",
    "time": "20:00"
  }
}
```

**Q: How to handle large number of sessions?**  
A: Auto-batch processing, max 5 sessions per Heartbeat, remaining will be processed next time.

**Q: Can I disable auto-save?**  
A: Yes, set `"enabled": false` in config file.

**Q: Will first run refine MEMORY.md?**  
A: **Yes!** First run will force trigger one MEMORY.md refinement, then execute according to schedule frequency.

---

### 🌍 Cross-Platform Support

#### Platform Compatibility

- ✅ **macOS** - Full support
- ✅ **Linux** - Full support
- ✅ **Windows** - Full support (PowerShell/CMD)

#### Multi-Workspace Support

Skill auto-supports multiple workspaces, no extra configuration needed:

| Workspace Type | Config Location | Data Location |
|----------------|-----------------|---------------|
| **Default Workspace** | `~/.openclaw/workspace/` | `~/.openclaw/workspace/memory/` |
| **Custom Workspace** | `$OPENCLAW_WORKSPACE/` | `$OPENCLAW_WORKSPACE/memory/` |
| **Project Workspace** | `./.openclaw/` | `./.openclaw/memory/` |

#### Switch Workspace

**Method 1: Environment Variable**
```bash
export OPENCLAW_WORKSPACE=/path/to/your/workspace
openclaw gateway restart
```

**Method 2: Current Directory**
```bash
cd /path/to/your/workspace
# Skill will auto-detect current directory
```

---

### 📄 License

MIT License

---

[Top](#heartbeat-memory)
