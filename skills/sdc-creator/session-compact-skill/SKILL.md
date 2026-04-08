---
name: session-compact-skill
description: |
  Intelligent session compression for OpenClaw that automatically manages token consumption and supports unlimited-length conversations. Compresses historical messages into structured summaries to reduce token usage by 85-95%. Features cross-session memory, pre-compaction protection (WAL), and context recovery.
metadata: {
  "clawdbot": {
    "emoji": "🗜️",
    "requires": { "bins": ["node"] },
    "tools": [
      {
        "name": "compact_session",
        "description": "压缩当前会话历史以节省 tokens。自动检测 token 数，将早期消息替换为摘要",
        "inputSchema": {
          "type": "object",
          "properties": {
            "maxTokens": {
              "type": "number",
              "description": "触发压缩的 token 阈值 (默认 10000)"
            },
            "preserveRecent": {
              "type": "number",
              "description": "保留的最新消息数 (默认 4)"
            },
            "force": {
              "type": "boolean",
              "description": "是否强制压缩 (即使未超阈值)"
            }
          }
        }
      },
      {
        "name": "save_session_state",
        "description": "保存当前会话状态到持久化存储",
        "inputSchema": {
          "type": "object",
          "properties": {
            "task": { "type": "string", "description": "当前任务" },
            "details": { "type": "array", "items": { "type": "string" }, "description": "关键细节" }
          }
        }
      },
      {
        "name": "recover_context",
        "description": "压缩后恢复上下文",
        "inputSchema": { "type": "object", "properties": {} }
      }
    ]
  }
}
---

# Session Compact Skill v1.1.0

Intelligent session compression for OpenClaw that automatically manages token consumption and supports **unlimited-length conversations**. By compressing historical messages into structured summaries, it significantly reduces token usage (typically 85-95% savings).

## ✨ New in v1.1.0

- **Cross-Session Memory**: Session state persists across `/new` and compaction
- **Pre-Compaction Protection**: WAL protocol captures critical state before compression
- **Context Recovery**: Automatic recovery after compaction from multiple sources
- **Working Buffer**: Danger zone buffer at 60%+ context utilization
- **Daily Memory Archive**: Automatic daily memory logging

---

## ✨ Features

- **Automatic Compression**: Triggers when session tokens approach threshold
- **Smart Summaries**: Preserves key information (timeline, todos, files, tools used)
- **Seamless Continuation**: Conversations continue without user intervention
- **Fallback Protection**: Code-based extraction when LLM unavailable
- **Recursive Compression**: Supports multiple compression cycles
- **Cross-Session Memory**: Session state persists across `/new` and compaction
- **Pre-Compaction Protection**: WAL protocol captures critical state before compression
- **Context Recovery**: Automatic recovery after compaction from multiple sources
- **Working Buffer**: Danger zone buffer at 60%+ context utilization
- **Daily Memory Archive**: Automatic daily memory logging

## 🧠 Cross-Session Memory

### Problem Solved
Your OpenClaw agent forgets everything between sessions — after `/new`, after compaction, after overnight. This feature fixes all three.

### How It Works

**1. Session State Persistence**
- State stored in `~/.openclaw/memory/SESSION-STATE.md`
- Captures: current task, key details, decisions, preferences, files
- Valid for 72 hours (configurable)

**2. Working Buffer (Danger Zone)**
- Activates at 60% context utilization
- Stores recent exchanges in `~/.openclaw/memory/working-buffer.md`
- Survives compaction and session resets

**3. Daily Memory Archive**
- Automatic daily logging to `~/.openclaw/memory/YYYY-MM-DD.md`
- Preserves long-term context across days

### Usage

**Save State Manually**:
```
"保存当前状态" or "save session state"
```

**Recover Context After Compaction**:
```
"恢复上下文" or "recover context"
```

## 🛡️ Pre-Compaction Protection (WAL Protocol)

### The Problem
When context window fills up, OpenClaw compacts older messages into a summary. Summaries lose precision — exact numbers become "approximately," file paths vanish, decisions lose their rationale.

### The Fix: Write-Ahead Logging

**On EVERY incoming message, scan for:**
- ✏️ **Corrections** — "It's X, not Y" / "Actually..." / "应该是..."
- 📍 **Proper Nouns** — names, places, companies, products
- 🎨 **Preferences** — styles, approaches, "I like/don't like"
- 📋 **Decisions** — "Let's do X" / "Go with Y" / "决定..."
- 📝 **Draft Changes** — edits to active work
- 🔢 **Specific Values** — numbers, dates, IDs, URLs, paths

**If ANY appear:**
1. **STOP** — do not compose response yet
2. **WRITE** — update `SESSION-STATE.md` with the detail
3. **THEN** — respond to the human

### Compaction Recovery

**Auto-trigger when:**
- Session starts with `<summary>` tag in context
- You should know something but don't
- Human says "where were we?" / "continue" / "what were we doing?"

**Recovery steps (in order):**
1. Read `memory/working-buffer.md` — raw danger-zone exchanges
2. Read `SESSION-STATE.md` — active task state
3. Read today's + yesterday's `memory/YYYY-MM-DD.md`
4. Extract important context from buffer → update SESSION-STATE.md
5. Report: "Recovered context. Last task was X. Continuing."

**NEVER ask "what were we discussing?"** — the buffer has the answer.

---

## 🚀 Quick Start

### Installation

```bash
openclaw skills install session-compact-skill
```

### Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "session-compact-skill": {
        "enabled": true,
        "max_tokens": 10000,
        "preserve_recent": 4,
        "auto_compact": true
      }
    }
  }
}
```

### Usage

**Automatic Mode** (Recommended):
```bash
# Start OpenClaw - compression works automatically
openclaw start
# Auto-compacts when conversation exceeds threshold
```

**Manual Trigger**:
```bash
# Tell your agent to compress
"压缩当前会话" or "compact session"
```

**Tool Call**:
```bash
openclaw tools call compact_session '{"force": false}'
```

## ⚙️ Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_tokens` | number | 10000 | Token threshold to trigger compression |
| `preserve_recent` | number | 4 | Number of recent messages to keep uncompressed |
| `auto_compact` | boolean | true | Enable automatic compression |

## 🔧 How It Works

1. **Token Estimation**: Uses heuristic method (~4 chars ≈ 1 token)
2. **Trigger Detection**: Checks if total tokens exceed 90% of threshold
3. **Message Selection**: Keeps last N messages intact (preserve_recent)
4. **Summary Generation**: Extracts structured summary from older messages
5. **Replacement**: Swaps old messages with summary, continues seamlessly

### Summary Structure

```
<summary>
- Scope: X earlier messages compacted (user=Y, assistant=Z, tool=W).
- Recent requests: [Last 3 user requests]
- Pending work: [Outstanding tasks]
- Key files: [Referenced file paths]
- Tools used: [Tool names]
- Key timeline: [Message timeline]
</summary>
```

## 📊 Example

### Before Compression
```json
[
  {"role":"user","content":"请分析赛力斯2025年报"},
  {"role":"assistant","content":"[tavily_search] 正在搜索..."},
  {"role":"user","content":"还要2024年对比数据"},
  {"role":"assistant","content":"[tavily_search] 已找到..."}
  // ... continues to 50+ messages
]
```

### After Compression
```json
[
  {"role":"system","content":"Summary:\n- Scope: 45 earlier messages compacted...\n- Key timeline:..."},
  {"role":"user","content":"那么深信服的2025预测呢？"},
  {"role":"assistant","content":"继续..."}
  // ... latest 4 messages preserved
]
```

## ⚠️ Important Notes

- **Compression is irreversible** - Early message details are permanently lost
- **Threshold setting** - Recommend setting max_tokens high (8000-12000) to avoid premature compression
- **Summary quality** - Uses code-based extraction for reliability, LLM enhancement when available

## 📦 Advanced Version

For full features including:
- Session persistence (JSON file storage)
- Token usage tracking (actual API usage + cache metrics)
- Rich message structure (ContentBlock types)
- CLI commands (compact, compact-status, compact-config, sessions, session-info)
- 150 test suite with 82.78% coverage

Install the Code Plugin version:
```bash
openclaw plugins install clawhub:openclaw-session-compact
```

---

**Version**: 1.1.0  
**Author**: sdc-creator  
**License**: MIT  
**GitHub**: https://github.com/SDC-creator/openclaw-session-compact

## 📦 Advanced Version

For full features including:
- Session persistence (JSON file storage with version tracking)
- Token usage tracking (actual API usage + cache metrics)
- Rich message structure (ContentBlock types)
- CLI commands (compact, compact-status, compact-config, sessions, session-info)
- 150 test suite with 82.78% coverage

Install the Code Plugin version:
```bash
openclaw plugins install clawhub:openclaw-session-compact
```
