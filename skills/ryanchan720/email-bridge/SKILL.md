---
name: email-bridge
description: Email management skill with real-time notifications, verification code extraction, and multi-provider support (Gmail, QQ Mail, NetEase). Users can configure email accounts through natural conversation.
---

# Email Bridge Skill

Email management skill for OpenClaw. Supports Gmail, QQ Mail, and NetEase Mail (163/126).

## Installation

After installing this skill, run the setup:

```bash
cd skills/email-bridge
python3 scripts/email_bridge.py --version
```

The wrapper script will automatically install dependencies on first run.

## Capabilities

- **Receive emails**: Sync and read emails from configured accounts
- **Send emails**: Send emails via SMTP
- **Real-time notifications**: Get notified when new emails arrive (IMAP IDLE)
- **Verification code extraction**: Extract verification codes from emails
- **Link extraction**: Extract action links from emails

## Trigger Keywords

**Chinese:**
- 邮箱、邮件、电子邮件
- 发邮件、发送邮件
- 查看邮件、读取邮件
- 验证码
- QQ邮箱、Gmail、163邮箱、126邮箱

**English:**
- email, mail
- send email
- check email, read email
- verification code

## Conversational Setup

### QQ Mail / NetEase Mail (5 minutes)

When user says "帮我配置 QQ 邮箱" or "set up my email":

1. **Ask for email address**
   ```
   What's your QQ Mail address?
   ```

2. **Guide to get authorization code**
   ```
   Please open https://service.mail.qq.com/detail/0/75
   Send SMS to verify and get your 16-character authorization code.
   ```

3. **Execute configuration** (assistant handles the command)
   
   ⚠️ **Security Note**: The authorization code is passed directly to the CLI command and stored locally in `~/.email-bridge/`. It is NOT logged in chat history when using the `--config` parameter with JSON.

   ```bash
   email-bridge accounts add {email} -p qq \
     --config '{"password": "{auth_code}"}'
   ```

4. **Sync and start daemon**
   ```bash
   email-bridge sync
   email-bridge daemon start -d
   ```

5. **Confirm success**
   ```
   ✅ Setup complete! Your QQ Mail is now connected.
   
   You can now:
   - Say "check recent emails" to read emails
   - Receive automatic notifications for new emails
   ```

### Alternative: Manual Configuration

For users who prefer not to share authorization codes in chat, they can manually edit the config file:

```bash
# Create config directory
mkdir -p ~/.email-bridge

# Add account manually
email-bridge accounts add your@qq.com -p qq

# The command will prompt for the authorization code interactively
# Or edit the database directly at ~/.email-bridge/email_bridge.db
```

### Gmail Setup (Advanced, 20 minutes)

For advanced users only. Requires OAuth configuration. See README.md for details.

## Common Commands

After setup, users can request these operations through conversation:

### Read Emails
```
User: 查看最近邮件 / check recent emails
User: 有没有未读邮件 / any unread emails?
User: 搜索包含"验证码"的邮件 / search emails with "verification code"
```

Execute:
```bash
email-bridge messages list -n 10
email-bridge messages unread
email-bridge messages search --keyword "verification"
```

### Send Emails
```
User: 给 test@example.com 发邮件 / send email to test@example.com
```

Execute:
```bash
email-bridge send -a <account_id> -t <recipient> -s "<subject>" -b "<body>"
```

### Extract Verification Codes
```
User: 帮我看看验证码 / get verification codes
```

Execute:
```bash
email-bridge codes
```

### Manage Daemon
```
User: 启动邮件监听 / start email monitoring
User: 停止邮件监听 / stop email monitoring
User: 邮件守护进程状态 / daemon status
```

Execute:
```bash
email-bridge daemon start -d
email-bridge daemon stop
email-bridge daemon status
```

## File Structure

```
skills/email-bridge/
├── SKILL.md              # This document
├── scripts/
│   └── email_bridge.py   # Entry point with auto-install
├── email_bridge/         # Python package source
├── pyproject.toml        # Dependencies
├── references/           # Additional docs
└── README.md             # Detailed documentation
```

## Data Storage

All credentials are stored locally, not in chat history:

```
~/.email-bridge/
├── email_bridge.db       # SQLite database (includes account configs)
├── daemon.pid            # Daemon PID
├── daemon.log            # Logs
└── gmail/
    ├── credentials.json  # Gmail OAuth credentials
    └── token_*.json      # OAuth tokens
```

## Security Notes

1. **Authorization codes** are stored locally in `~/.email-bridge/email_bridge.db`
2. **Chat history** does not retain the actual codes when using `--config` parameter
3. **OAuth tokens** for Gmail are stored locally after browser-based authentication
4. **Daemon process** runs as the current user with standard permissions

## Dependencies

The skill requires these Python packages (automatically installed):
- click >= 8.0
- pydantic >= 2.0
- imaplib2 >= 3.6
- google-api-python-client >= 2.0 (for Gmail)
- google-auth-oauthlib >= 1.0 (for Gmail)

All dependencies are from PyPI and are widely used, well-maintained packages.