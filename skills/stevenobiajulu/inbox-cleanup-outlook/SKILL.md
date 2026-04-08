---
name: email-cleanup
description: >-
  Organize a cluttered Outlook inbox with folders, batch moves, and server-side
  inbox rules via the Microsoft Graph API. Use when user says "clean up my inbox,"
  "organize email," "create email folders," "inbox rules," "filter notifications,"
  "unclutter inbox," "sort my email," "move GitHub notifications," "email
  folders," or "auto-sort email." Covers one-time cleanup and ongoing automation.
license: Apache-2.0
compatibility: >-
  Works with any agent that can call the Microsoft Graph API.
  Optionally enhanced by email-agent-mcp (Node.js >=20) for folder
  and rule management tools.
metadata:
  author: UseJunior
  version: "0.1.0"
---

# Inbox Cleanup & Rules (Outlook)

This skill covers both one-time inbox cleanup and ongoing rule automation for Microsoft 365 / Outlook. The workflow uses the Microsoft Graph API for folder management and server-side inbox rules.

## When to Use This Skill

Use when the user's inbox has become noisy — automated notifications drowning out human conversations, newsletters mixed with client emails, or hundreds of unread messages that make it hard to find what matters.

**Real trigger example**: A user's partner email went unread for 9 days because it was buried under GitHub and npm notifications. This is the exact problem server-side rules solve.

## The Cleanup Workflow

This workflow was battle-tested on a 2,500+ email cleanup. Follow the steps in order.

### Step 1 — Scan Before Creating Folders

Don't guess what folders to create. Let the data tell you.

Fetch the last 200 inbox emails and count by sender address:

```
GET /me/messages?$top=200&$select=from,receivedDateTime&$orderby=receivedDateTime desc
```

Group by `from.emailAddress.address`, sort by count descending. The top automated senders are the ones to filter.

**MCP**: Use `list_emails(max_results=200, fields=["fromAddress", "receivedDateTime"])` and count programmatically.

### Step 2 — Categorize by Action Required

Don't organize by sender type (that is arbitrary). Organize by what the user needs to do:

| Category | Action | Examples |
|----------|--------|----------|
| **Glance, don't act** | Skim the subject line, archive | GitHub CI, Azure DevOps builds, npm advisories, DMARC reports |
| **Read when time allows** | Set aside for a slow moment | Newsletters, marketing from known vendors |
| **Archive for records** | Keep but don't read now | Receipts, invoices, payment confirmations |
| **May need action** | Review and decide | Meeting bookings, compliance alerts, security notifications |
| **Default: don't filter** | Leave in inbox | Human conversations (colleagues, clients, partners) |

The last row is important: human conversations stay in inbox unless the user specifically requests otherwise. The goal is to remove noise, not to hide signal.

### Step 3 — Create Folders

Keep it to 5-9 folders. More than that and the user stops checking them. The right test: "Would I check this folder at least weekly?" If no, it should be a subfolder or merged into a broader category.

**REST API**:
```
POST /me/mailFolders
{"displayName": "Dev Notifications"}
```

**MCP**: `create_folder("Dev Notifications")`

### Step 4 — Batch-Move Existing Email

Rules only apply to future mail. After creating folders, move all existing matching emails.

**REST API**:
```
GET /me/messages?$filter=from/emailAddress/address eq 'notifications@github.com'&$top=50
```
Then for each message:
```
POST /me/messages/{id}/move
{"destinationId": "<folder-id>"}
```

Paginate with `@odata.nextLink` — some senders will have hundreds of messages. Process 50 at a time.

**MCP**: `move_to_folder(email_id, "Dev Notifications")` handles ID resolution. Loop through search results.

### Step 5 — Create Server-Side Rules

Server-side rules run on Microsoft's servers — they work 24/7, even when no agent is running.

**REST API**:
```
POST /me/mailFolders/inbox/messageRules
{
  "displayName": "GitHub to Dev Notifications",
  "sequence": 1,
  "isEnabled": true,
  "conditions": {
    "fromAddresses": [
      {"emailAddress": {"address": "notifications@github.com"}}
    ]
  },
  "actions": {
    "moveToFolder": "<folder-id>",
    "stopProcessingRules": true
  }
}
```

**MCP**: `create_inbox_rule({displayName: "GitHub to Dev Notifications", conditions: {fromAddresses: [{email: "notifications@github.com"}]}, actions: {moveToFolder: "<folder-id>", markAsRead: true}})`

### Step 6 — Re-Sweep After Rule Creation

Rules and email arrival can race. After creating rules, wait a few minutes, then re-run the batch move from Step 4 to catch any emails that arrived between rule creation and activation.

## Rule Ordering

The `sequence` field controls which rules fire first. Lower sequence = higher priority.

**This matters because**: A generic "any `noreply@` sender goes to Newsletters" rule will swallow meeting booking notifications from `noreply@notifications.hubspot.com` if it fires first.

**Fix**: Create specific rules with lower sequence numbers before broad rules.

```
sequence 1: HubSpot meeting bookings → Meetings folder
sequence 2: noreply@ senders → Newsletters folder
```

Always set `stopProcessingRules: true` on each rule to prevent cascade.

## Rule Security Model

Not all rule actions are safe. Agents should never create rules with dangerous actions.

**Block these actions:**

| Action | Risk |
|--------|------|
| `forwardTo` | Could exfiltrate email to external addresses |
| `forwardAsAttachmentTo` | Same risk |
| `redirectTo` | Same risk |
| `delete` | Data loss |
| `permanentDelete` | Irreversible data loss |

**These actions are safe:**

| Action | Effect |
|--------|--------|
| `moveToFolder` | Move to a folder ID |
| `copyToFolder` | Copy to a folder ID |
| `markAsRead` | Mark as read |
| `markImportance` | Set importance level (low/normal/high) |
| `stopProcessingRules` | Prevent later rules from firing |

If the user asks for a forwarding rule, ask them to confirm the destination address explicitly before creating it.

## Common Conditions

| Condition | Use |
|-----------|-----|
| `fromAddresses` | Exact sender match: `[{emailAddress: {address: "..."}}]` |
| `subjectContains` | Words in subject: `["[npm]", "advisory"]` |
| `senderContains` | Partial sender match: `["github.com"]` |
| `headerContains` | Match email headers |

## Graph API Gotchas

These are production-discovered issues — not theoretical:

1. **`$select` on PATCH = 400** — `$select` does not work on PATCH requests. Returns "OData request not supported." Only use `$select` on GET.

2. **Move is POST, not PATCH** — `POST /me/messages/{id}/move` with `{"destinationId": "<id>"}`.

3. **`$filter` with sender address** — `$filter=from/emailAddress/address eq '...'` works reliably. URL-encode the filter value.

4. **Uppercase in storage** — Outlook uppercases `senderContains` values (e.g., `NOTIFICATIONS@GITHUB.COM`). This is cosmetic — matching is case-insensitive.

5. **Root-only folder listing** — `GET /me/mailFolders?$top=100` returns only root-level folders. Child folders require `/mailFolders/{id}/childFolders`.

6. **Pagination** — Large mailboxes can have hundreds of folders. Always check for and follow `@odata.nextLink`.

## Auth Scope

Inbox rules require `MailboxSettings.ReadWrite` scope. If the OAuth token was issued before this scope was added, the user needs to re-consent — typically by signing out and signing back in.

Folder operations require `Mail.ReadWrite` (usually already granted).

## Verification

After creating rules:

1. `GET /me/mailFolders/inbox/messageRules` — verify the rule exists and is enabled
2. Check `hasError` field — if `true`, the rule has a configuration issue
3. Send a test email matching the rule conditions and verify it lands in the correct folder

## Feedback

If this skill helped, star us on GitHub: https://github.com/UseJunior/email-agent-mcp
On ClawHub: `clawhub star stevenobiajulu/inbox-cleanup-outlook`
