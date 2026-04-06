# Discord Workspace Setup

Complete guide to setting up a Discord server as your OpenClaw workspace. Discord replaces WhatsApp as the primary communication channel with significant upgrades: streaming responses, voice channels, interactive components, thread-bound coding sessions, and per-project channel isolation.

## Why Discord Over WhatsApp

| Feature | WhatsApp | Discord |
|---------|----------|---------|
| Streaming responses | ❌ | ✅ See text as it generates |
| Voice conversations | ❌ | ✅ Real-time STT → LLM → TTS |
| Interactive buttons | ❌ | ✅ Approve/reject, dropdowns |
| Channel separation | ❌ One chat | ✅ Per-project channels |
| Thread-bound coding | ❌ | ✅ Codex/Claude Code in threads |
| Reactions | ❌ | ✅ Ack reactions, emoji |
| Message search | Basic | ✅ Full-text across channels |
| Polls | ❌ | ✅ Native polls |
| Pins | ❌ | ✅ Pin important messages |
| File size limit | 16MB | 25MB (50MB with Nitro) |

## Server Architecture

### Recommended Channel Layout

```
🏠 Home
  #general          — Casual chat, quick questions (daily driver)
  #tasks            — Task tracking, reminders, todos
  #coding           — General coding, debugging, code review

🔊 Voice
  🎙 General        — Voice conversations with the agent

🏥 [Your Org]       — Organization-specific channels
  #project-a        — Project A work
  #project-b        — Project B work
  #project-c        — Project C work

🤖 Agents
  #agents           — Subagent/ACP coding sessions (threads spawn here)

📋 Ops
  #logs             — Deployment logs, alerts
  #cron             — Cron job output, scheduled tasks

🧪 Research
  #research         — Deep research, analysis tasks
```

**Key principle:** Each channel = isolated session with its own context. When you ask about Project A in #project-a, the agent doesn't waste tokens loading Project B context.

### Channel Topics as Context Pointers

Set channel topics to include vault pointers so the agent knows where to find project docs:

```
Project A digital signage | vault: 20-projects/project-a/ | repo: user/project-a | admin: port 3001
```

This gives the agent routing context without loading full project docs every message.

## OpenClaw Discord Configuration

### Minimum Config

```json5
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "dmPolicy": "allowlist",
      "allowFrom": ["YOUR_DISCORD_USER_ID"],
      "groupPolicy": "allowlist",
      "guilds": {
        "YOUR_GUILD_ID": {
          "requireMention": false,
          "users": ["YOUR_DISCORD_USER_ID"]
        }
      }
    }
  }
}
```

### Recommended Full Config

```json5
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "groupPolicy": "allowlist",
      "historyLimit": 30,
      "streaming": "partial",
      "replyToMode": "first",
      "dmPolicy": "allowlist",
      "allowFrom": ["YOUR_DISCORD_USER_ID"],
      "guilds": {
        "*": {},
        "YOUR_GUILD_ID": {
          "requireMention": false,
          "users": ["YOUR_DISCORD_USER_ID"]
        }
      },
      "ui": {
        "components": {
          "accentColor": "#1a1a2e"
        }
      },
      "threadBindings": {
        "enabled": true,
        "spawnSubagentSessions": true,
        "spawnAcpSessions": true
      },
      "voice": {
        "enabled": true,
        "tts": {
          "provider": "openai",
          "openai": { "voice": "onyx" }
        }
      },
      "ackReaction": "🦅",
      "autoPresence": {
        "enabled": true,
        "healthyText": "Watching the crawl",
        "degradedText": "Recovering...",
        "exhaustedText": "Token budget hit — {reason}"
      }
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true
  },
  "session": {
    "threadBindings": {
      "enabled": true
    }
  }
}
```

### Config Explained

| Setting | Value | Why |
|---------|-------|-----|
| `streaming: "partial"` | See responses as they generate | Better UX than waiting for full reply |
| `replyToMode: "first"` | Agent replies thread to your message | Clean conversation flow |
| `requireMention: false` | No @mention needed | Just type naturally |
| `historyLimit: 30` | Load 30 previous messages for context | Balance context vs tokens |
| `threadBindings.enabled` | Subagents get their own threads | Isolates coding sessions |
| `voice.enabled` | Voice channel support | Real-time voice conversations |
| `ackReaction` | React to messages with emoji | Visual confirmation |
| `autoPresence` | Bot status messages | See agent health at a glance |

## Features

### Voice Channels

Real-time voice conversations: your voice → Whisper STT → LLM → OpenAI TTS → your speakers.

**Setup:**
1. Create a voice channel in your server
2. Add `voice` config (see above)
3. Bot needs Connect + Speak permissions
4. Use `/vc join` in the voice channel

**Voice options:** alloy, echo, fable, onyx, nova, shimmer (OpenAI TTS voices).

**Cost:** ~$0.015 per response for TTS. STT is minimal (Whisper).

**Use case:** Hands-free work — keep coding while talking to your agent.

### Interactive Components

Buttons, select menus, and forms for quick interactions.

**Buttons:** Approve/reject actions, quick choices
```json5
{
  "components": {
    "reusable": true,
    "blocks": [{
      "type": "actions",
      "buttons": [
        { "label": "✅ Approve", "style": "success" },
        { "label": "❌ Reject", "style": "danger" }
      ]
    }]
  }
}
```

**Select menus:** Pick from options
```json5
{
  "type": "actions",
  "select": {
    "type": "string",
    "placeholder": "Pick a project...",
    "options": [
      { "label": "Project A", "value": "a" },
      { "label": "Project B", "value": "b" }
    ]
  }
}
```

**Forms:** Multi-field input via modal dialogs.

### Thread-Bound Coding Sessions

When spawning Codex, Claude Code, or other ACP agents, they get their own Discord thread. Full conversation history preserved, isolated from the main channel.

Requires: `threadBindings.enabled: true`, `spawnSubagentSessions: true`, `spawnAcpSessions: true`.

### Streaming Responses

With `streaming: "partial"`, you see the agent's response as it types — no waiting for the complete message. Much better UX for long responses.

### Reactions

The agent reacts to your messages with the configured `ackReaction` emoji to confirm it received your message before processing.

## Heartbeat with Journaling

Configure `HEARTBEAT.md` to update memory when there's been recent interaction:

```markdown
# HEARTBEAT.md

## Rule: Only act if there was interaction in the last 30 minutes.
Check the conversation history — if there are NO user messages from the last 30 minutes, reply HEARTBEAT_OK immediately. Do NOT read files, search memory, or do any work.

## If there WAS recent interaction:

### Update Memory
1. **Journal** — Append to `vault/10-journal/YYYY-MM-DD.md` (today's date)
   - Summarize work done since last update
   - Include proper YAML frontmatter, tags, and [[wikilinks]]
   - If file doesn't exist, create it from template
2. **Project docs** — If significant changes happened to a project:
   - Update the relevant `vault/20-projects/<project>/overview.md`
3. **Core files** — If new tools, preferences, or lessons learned:
   - Update `MEMORY.md` (only for lasting preferences/lessons)
   - Update `TOOLS.md` if infrastructure changed
4. Reply HEARTBEAT_OK when done (don't message the user about the update)
```

This ensures memory stays current without wasting tokens on empty heartbeats.

## Discord Bot Setup (Prerequisites)

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a New Application → name it (e.g., "MordecAI")
3. Go to Bot → create bot, copy token
4. Enable these Privileged Intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
5. Go to OAuth2 → URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Permissions: Administrator (or fine-tune: Send Messages, Read Messages, Connect, Speak, Manage Threads, Add Reactions, Use External Emojis, Attach Files, Embed Links, Read Message History)
6. Copy the invite URL → open in browser → add to your server
7. Add the bot token to your OpenClaw config

## Migration from WhatsApp

1. Set up Discord server with the channel architecture above
2. Configure OpenClaw with Discord config
3. Update `USER.md` to list Discord as primary channel
4. Update `AGENTS.md` trust anchor with your Discord user ID
5. Keep WhatsApp config as fallback if desired (`channels.whatsapp.enabled: true`)
6. Test: send a message in #general — agent should respond without @mention
