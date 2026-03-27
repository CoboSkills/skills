---
name: email-summarizer
description: Email summary and contact profiling skill. Fetches and summarizes emails from the last N days, and generates gender/occupation/relationship profiles for contacts. Trigger when user says "summarize my emails", "check recent emails", "any important emails", "analyze my contacts", "who is this sender", "profile email contacts", "parse pst file", "analyze outlook export", etc. Supports 163, QQ, Tencent Exmail, Gmail, Outlook IMAP mailboxes AND local file formats: .pst, .mbox, .msg.

# Runtime dependencies
# Python packages (pip install -r requirements.txt):
#   extract-msg>=0.52.0   — .msg file parsing
#   openpyxl>=3.1.0       — Excel report generation
#
# Node.js packages (cd scripts && npm install):
#   pst-extractor>=1.10.0 — native .pst parsing (optional; fallback: readpst system binary)
#
# System tools (optional):
#   readpst               — alternative .pst engine (apt install pst-utils / brew install libpst)
#   python3               — required (stdlib: imaplib, mailbox, smtplib, email)
#   node >= 16            — required only for native PST parsing

# Credentials (IMAP/SMTP modes only — not needed for local file parsing)
env:
  EMAIL_USER:
    description: Your email address (e.g. you@163.com). Used for IMAP fetch and SMTP send.
    required: false
    example: "you@163.com"
  EMAIL_PASS:
    description: IMAP app password / authorization code (NOT your login password). Generate one in your mailbox settings under POP3/SMTP/IMAP.
    required: false
    example: "your-app-password"
---

# Email Summarizer + Contact Profiler

Fetches emails from the last N days and produces a 4-dimension summary plus contact profile analysis.

Supports two input modes:
- **IMAP mode** (`fetch_emails.py`) — live connection to a remote mailbox
- **Local file mode** (`parse_local.py`) — parse offline exports: `.pst`, `.mbox`, `.msg` files (no credentials needed)

---

## Installation

```bash
# 1. Python dependencies
pip install -r requirements.txt

# 2. Node.js dependency (only needed for native .pst parsing)
cd scripts && npm install && cd ..
```

> **Credentials** are only needed for IMAP/SMTP modes (fetching live mailbox or sending reports).
> Local file parsing (`.pst`, `.mbox`, `.msg`) requires no credentials.

---

## Mode A: IMAP (Live Mailbox)

### Setup Credentials

Set environment variables before first use:

```bash
export EMAIL_USER="your@email.com"
export EMAIL_PASS="your-imap-app-password"   # NOT your login password!
```

### Usage

```bash
# Basic: fetch inbox from last 3 days
python3 scripts/fetch_emails.py --days 3 --preset 163

# With sent folder (better relationship analysis)
python3 scripts/fetch_emails.py --days 7 --preset qq --with-sent

# Contact profile mode (aggregated contact data for AI analysis)
python3 scripts/fetch_emails.py --days 30 --preset 163 --profile --with-sent
```

### Supported Mailboxes

| Mailbox | --preset | IMAP Server |
|---------|----------|-------------|
| 163 Mail | `163` | imap.163.com:993 |
| QQ Mail | `qq` | imap.qq.com:993 |
| Tencent Exmail | `exmail` | imap.exmail.qq.com:993 |
| Gmail | `gmail` | imap.gmail.com:993 |
| Outlook | `outlook` | outlook.office365.com:993 |

---

## Mode B: Local File Parsing (No Credentials Needed)

Use `parse_local.py` when the user has a local email export and does not want to configure IMAP.

### Supported Formats

| Format | How to obtain | Command flag |
|--------|--------------|--------------|
| `.pst` | Outlook → File → Export | `--pst FILE` |
| `.mbox` | Any mail client export, or converted from .pst via readpst | `--mbox FILE` |
| `.msg` folder | Outlook → drag-and-drop export multiple emails | `--msg-dir DIR` |

### PST Parse Engine

`.pst` parsing supports two engines (auto-selected by default):

| Engine | Flag | Requires | Notes |
|--------|------|----------|-------|
| **native** (default) | `--pst-engine native` | Node.js + `pst-extractor` npm pkg | No system install needed; npm pkg auto-installed if missing |
| **readpst** | `--pst-engine readpst` | `readpst` system binary | Traditional approach via libpst |
| **auto** | `--pst-engine auto` | — | Tries native first, falls back to readpst |

Native engine is preferred: works without any system-level install and handles Unicode folder names correctly.

### Usage

```bash
# Parse a .pst file — native engine (default, no extra install needed)
python3 scripts/parse_local.py --pst ~/Downloads/outlook.pst

# Force native engine explicitly
python3 scripts/parse_local.py --pst ~/Downloads/outlook.pst --pst-engine native

# Force readpst engine (requires readpst system binary)
python3 scripts/parse_local.py --pst ~/Downloads/outlook.pst --pst-engine readpst

# Parse a .mbox file
python3 scripts/parse_local.py --mbox ~/Downloads/Inbox.mbox

# Parse inbox + sent mbox for better relationship analysis
python3 scripts/parse_local.py --mbox Inbox.mbox --sent-mbox SentItems.mbox

# Parse a folder of .msg files exported from Outlook
python3 scripts/parse_local.py --msg-dir ~/Downloads/exported_msgs/

# Limit by date range
python3 scripts/parse_local.py --pst outlook.pst --days 30
python3 scripts/parse_local.py --mbox Inbox.mbox --since 2026-01-01 --until 2026-03-01

# Contact profile mode
python3 scripts/parse_local.py --msg-dir ./msgs/ --profile
```

### parse_local.py options

| Flag | Default | Description |
|------|---------|-------------|
| `--pst FILE` | — | Parse a .pst file via readpst |
| `--mbox FILE` | — | Parse a .mbox file |
| `--msg-dir DIR` | — | Parse all .msg files in a directory |
| `--sent-mbox FILE` | — | Additional sent folder .mbox (mbox mode only) |
| `--days N` | all | Only include emails from the last N days |
| `--since DATE` | — | Start date inclusive (YYYY-MM-DD) |
| `--until DATE` | — | End date exclusive (YYYY-MM-DD) |
| `--max N` | 500 | Max emails per source |
| `--profile` | off | Output contact profile data |
| `--pst-engine` | auto | PST engine: `auto` \| `native` \| `readpst` |

### PST Dependencies

**Native engine (recommended, no system install needed):**

```bash
# Step 1: install Node.js dependency (one-time, ~2MB)
cd email-summarizer/scripts && npm install

# Step 2: use as normal — no extra flags needed
python3 scripts/parse_local.py --pst ~/Downloads/outlook.pst
```

**readpst engine (traditional, requires system binary):**

```bash
# Linux (Debian/Ubuntu)
sudo apt install pst-utils

# Linux (RHEL/CentOS)
sudo yum install libpst

# macOS
brew install libpst
```

### Dependencies for local mode

```bash
pip3 install extract-msg   # required for .msg parsing
# .mbox parsing uses Python stdlib (mailbox) — no extra install needed
# .pst parsing uses readpst system tool — no Python package needed
```

---

## Part A: 4-Dimension Email Summary Template

After fetching the email JSON, output a summary in the following four sections:

### 🔥 Part 1: Important Emails & Action Items

Sort by priority:

```
🚨 [URGENT] Subject — Sender — Date
   Summary: xxx
   Action needed: xxx (Deadline: xxx)

⚡ [IMPORTANT] Subject — Sender — Date
   Summary: xxx / Action needed: xxx

📌 [NOTE] Subject — Sender — Date
   Summary: xxx
```

Priority criteria:
- 🚨 Urgent: has deadline, escalation, approval request, or incident alert
- ⚡ Important: requires reply, decision, or confirmation
- 📌 Note: FYI but worth attention

### 📊 Part 2: Grouped by Sender / Project

```
👤 Sender A (N emails)
   • Subject 1 — Date
   • Subject 2 — Date

📁 Topic / Project B (N emails)
   • Subject — Sender — Date
```

### ✅ Part 3: To-Do List

```
□ [Task] — From: xxx — Due: xxx
□ No clear deadline: [Task] — From: xxx
```

### 📅 Part 4: Timeline

```
YYYY-MM-DD  Sender → Subject: one-line summary
```

---

## Part B: Contact Profile Analysis Template

Use `--profile --with-sent` mode when the user requests contact profiling.

Data field reference:
- `received_from_count`: emails received from this contact
- `sent_to_count`: emails the owner sent to this contact
- `subjects`: list of email subjects in the exchange
- `body_snippets`: short excerpts from email bodies
- `is_system`: whether this is a system/bot sender

### Contact Profile Output Format

**Step 1: Sort by total interactions**

Calculate `total = received_from_count + sent_to_count` for each contact, sort descending.
System accounts (`is_system: true`) go to a separate table at the end.

**Step 2: Overview table (sorted by interaction count)**

```
| # | Name | Email | Received | Sent | Total | Heat | Gender | Role | Relationship |
|---|------|-------|----------|------|-------|------|--------|------|--------------|
| 1 | xxx  | xxx   |    N     |  N   |   N   | 🔥 Heavy | Male | Engineer | Colleague |
| 2 | xxx  | xxx   |    N     |  0   |   N   | ⚡ Active | Female | Recruiter | Stranger |
...
```

Heat scale:
- 🔥 Heavy: total ≥ 10
- ⚡ Active: total 5–9
- 💬 Moderate: total 2–4
- 🌙 Light: total 1

**Step 3: Detailed profile cards for contacts with heat ≥ Moderate**

One card per contact, sorted by interaction count descending:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Rank #N | [Name] <email>   Total: N emails (Received: N / Sent: N)

🧑 Gender       Male/Female/Unknown   Confidence: High/Medium/Low   Basis: xxx
💼 Role/Title   xxx                   Basis: domain / signature / content keywords
🔗 Relationship  Colleague / Friend / Family / Client / Institution / Stranger
   Direction    Owner-initiated / Contact-initiated / Mutual
   Basis: xxx

📝 Typical Topics
   • Subject 1
   • Subject 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 4: System / institutional senders summary (separate table, no personal profiling)**

```
| Institution | Email | Received | Type |
|-------------|-------|----------|------|
| iCloud | noreply@icloud.com | N | Service notification |
...
```

### Profiling Notes

- Gender inference relies primarily on name and honorifics (Mr./Ms./Sir/Madam); always state confidence level
- Contacts with only 1 email on record: note "Insufficient data — for reference only" in detailed card
- Keep inferences objective; avoid over-speculation
- If sent folder is not included (`--with-sent` not used), show `Sent: 0` for all contacts and note it in the table header

---

## Full Workflow

### IMAP mode (live mailbox)

```
User requests email summary
  → python3 scripts/fetch_emails.py --days N --preset xxx > /tmp/emails.json
  → AI reads JSON → outputs Part A 4-dimension summary

User requests contact profiles (chat output)
  → python3 scripts/fetch_emails.py --days 30 --profile --with-sent --preset xxx > /tmp/profile.json
  → AI reads JSON → outputs Part B profile for each contact in the contacts field

User requests contact profile report sent to email inbox
  → EMAIL_USER=you@163.com EMAIL_PASS=xxx \
    python3 scripts/send_contact_report.py --days 30 --preset 163 [--to recipient@email.com]
  → Script fetches emails, builds a fully-English HTML report, and sends via SMTP
  → Report columns: Preferred Name / Email / Company / Position / Subject Summary / Source / Emails
```

### Local file mode (no credentials needed)

```
User provides a .pst / .mbox / .msg export

Email summary from local file:
  → python3 scripts/parse_local.py --pst outlook.pst > /tmp/emails.json
  → AI reads JSON → outputs Part A 4-dimension summary

Contact profiles from local file:
  → python3 scripts/parse_local.py --pst outlook.pst --profile > /tmp/profile.json
  → AI reads JSON → outputs Part B contact profile analysis

With .msg folder:
  → python3 scripts/parse_local.py --msg-dir ./exported/ --profile > /tmp/profile.json

With .mbox (inbox + sent):
  → python3 scripts/parse_local.py --mbox Inbox.mbox --sent-mbox Sent.mbox --profile > /tmp/profile.json
```

### send_contact_report.py options

| Flag | Default | Description |
|------|---------|-------------|
| `--days` | 30 | Look-back window |
| `--max` | 100 | Max emails to fetch |
| `--preset` | 163 | Mailbox preset (163/qq/exmail/gmail/outlook) |
| `--to` | EMAIL_USER | Override recipient address |

### Contact Profile Fields

| Field | Source | Notes |
|-------|--------|-------|
| Preferred Name | Display name → body signature → email local-part | Human-friendly name |
| Email | IMAP header | Raw sender/recipient address |
| Company | Domain lookup table → body text → domain label | Best-effort inference |
| Position | Domain pattern → body signature → subject keywords | "Unknown" if not determinable |
| Subject Summary | All subjects deduplicated → theme extraction | One-line synthesis |
| Source | IMAP header fields | Coloured badges: 🔵 From / 🟢 To / 🟣 CC — a contact may have multiple |
| Emails | Recv + Sent count | Badge colour: red ≥10, orange 5–9, blue 2–4, grey 1; Recv / Sent shown below |

## Notes

- Credentials are passed via environment variables — never hardcoded
- Script is read-only (IMAP readonly mode) — will not modify or delete any emails
- Email body is truncated to 2000 characters; profile snippets to 300 characters
- 163 Mail requires an IMAP ID command before SELECT — handled automatically; harmless on other servers
