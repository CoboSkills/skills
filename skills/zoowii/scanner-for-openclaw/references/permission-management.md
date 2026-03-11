# Context-Aware Permission Management

**Purpose**: Implement flexible, scenario-based permission switching for OpenClaw to achieve least-privilege security while maintaining usability.

## Problem Statement

Traditional permission models face a dilemma:
- **Too restrictive**: Users can't complete legitimate tasks
- **Too permissive**: Security vulnerabilities, potential abuse

**Solution**: Context-aware permissions that adapt based on:
- User identity and role
- Channel type (1:1 vs group)
- Time of day
- Location/network
- Task sensitivity

## Permission Levels

### Level 1: Restricted (Default)
```json
{
  "context": "default",
  "tools": {
    "exec": { "policy": "deny" },
    "fs": { "workspaceOnly": true },
    "enabled": ["read", "search", "web_fetch"]
  }
}
```

**Use cases**:
- Unknown users
- Group chats
- Untrusted channels

### Level 2: Standard
```json
{
  "context": "trusted_user",
  "tools": {
    "exec": { "policy": "allowlist", "allowedCommands": ["ls", "cat", "grep"] },
    "fs": { "workspaceOnly": true },
    "enabled": ["read", "search", "web_fetch", "write", "edit"]
  }
}
```

**Use cases**:
- Known users (owner, admins)
- 1:1 chats
- Trusted channels

### Level 3: Elevated
```json
{
  "context": "admin_maintenance",
  "tools": {
    "exec": { "policy": "allowlist", "allowedCommands": ["systemctl", "docker", "git"] },
    "fs": { "workspaceOnly": false, "allowedPaths": ["/var/log", "/etc/openclaw"] },
    "enabled": ["*"]
  },
  "timeLimit": "30m",
  "requireApproval": true
}
```

**Use cases**:
- System maintenance
- Debugging
- Emergency fixes
- **Time-limited**
- **Requires approval**

### Level 4: Emergency
```json
{
  "context": "emergency",
  "tools": {
    "exec": { "policy": "allow" },
    "fs": { "workspaceOnly": false }
  },
  "timeLimit": "10m",
  "requireApproval": true,
  "auditLevel": "full",
  "notifyOnUse": true
}
```

**Use cases**:
- Critical incidents
- System recovery
- **Strictly time-limited**
- **Full audit logging**
- **Immediate notification**

## Implementation Patterns

### Pattern 1: User-Based Contexts

```json
{
  "contexts": {
    "enabled": true,
    "rules": [
      {
        "name": "owner",
        "condition": { "userId": "6055210169" },
        "permissionLevel": "standard"
      },
      {
        "name": "admin",
        "condition": { "roleId": "admin" },
        "permissionLevel": "elevated"
      },
      {
        "name": "unknown",
        "condition": { "userId": "*" },
        "permissionLevel": "restricted"
      }
    ]
  }
}
```

### Pattern 2: Channel-Based Contexts

```json
{
  "contexts": {
    "rules": [
      {
        "name": "private_chat",
        "condition": { "chatType": "direct" },
        "permissionLevel": "standard"
      },
      {
        "name": "group_chat",
        "condition": { "chatType": "group" },
        "permissionLevel": "restricted"
      },
      {
        "name": "admin_channel",
        "condition": { "channelId": "admin-telegram-id" },
        "permissionLevel": "elevated"
      }
    ]
  }
}
```

### Pattern 3: Time-Based Contexts

```json
{
  "contexts": {
    "rules": [
      {
        "name": "business_hours",
        "condition": { 
          "timeRange": "09:00-18:00",
          "timezone": "Asia/Shanghai"
        },
        "permissionLevel": "standard"
      },
      {
        "name": "after_hours",
        "condition": { 
          "timeRange": "18:00-09:00"
        },
        "permissionLevel": "restricted"
      },
      {
        "name": "maintenance_window",
        "condition": { 
          "scheduled": true,
          "timeRange": "02:00-04:00"
        },
        "permissionLevel": "elevated"
      }
    ]
  }
}
```

### Pattern 4: Network-Based Contexts

```json
{
  "contexts": {
    "rules": [
      {
        "name": "trusted_network",
        "condition": { 
          "network": "192.168.3.0/24"
        },
        "permissionLevel": "standard"
      },
      {
        "name": "public_network",
        "condition": { 
          "network": "*"
        },
        "permissionLevel": "restricted"
      }
    ]
  }
}
```

## Lifecycle Management

### Permission Request Flow

```
┌─────────────┐
│   User      │
│  Request    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Context Engine  │
│ - Check user    │
│ - Check channel │
│ - Check time    │
│ - Check network │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Permission      │
│ Level Assigned  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐     ┌──────────────┐
│ Restricted?     │────►│ Auto-approve │
└──────┬──────────┘     └──────────────┘
       │
       ▼
┌─────────────────┐     ┌──────────────┐
│ Elevated?       │────►│ Require MFA  │
└──────┬──────────┘     │ Time limit   │
       │                └──────────────┘
       ▼
┌─────────────────┐     ┌──────────────┐
│ Emergency?      │────►│ Require      │
└──────┬──────────┘     │ Approval +   │
                        │ Full Audit   │
                        └──────────────┘
```

### Time-Limited Permissions

```bash
# Request elevated access for 30 minutes
openclaw contexts request --level elevated --duration 30m --reason "Debugging deployment issue"

# Output:
✅ Elevated permissions granted
⏰ Expires: 2026-03-08 14:30:00
📋 Reason: Debugging deployment issue
🔔 Notification sent to admins

# Auto-revert after expiry
⏰ Elevated permissions expired, reverted to standard
```

### Approval Workflow

```json
{
  "approval": {
    "required": true,
    "approvers": ["user:admin1", "user:admin2"],
    "quorum": 1,
    "timeout": "15m",
    "notification": {
      "channel": "telegram",
      "chatId": "admin-chat-id"
    }
  }
}
```

## Audit Logging

### Log All Permission Changes

```json
{
  "audit": {
    "enabled": true,
    "logLevel": "info",
    "events": [
      "permission_granted",
      "permission_denied",
      "permission_expired",
      "context_switched",
      "elevated_access_used"
    ],
    "retention": "90d",
    "format": "json"
  }
}
```

### Example Log Entry

```json
{
  "timestamp": "2026-03-08T13:45:00Z",
  "event": "permission_granted",
  "user": "6055210169",
  "context": "elevated",
  "previousLevel": "standard",
  "newLevel": "elevated",
  "reason": "Debugging deployment issue",
  "approvedBy": "admin1",
  "expiresAt": "2026-03-08T14:15:00Z",
  "ipAddress": "192.168.3.100"
}
```

## Quick Switch Commands

### Predefined Profiles

```bash
# Switch to restricted mode (safe for public demos)
openclaw contexts switch restricted

# Switch to standard mode (daily use)
openclaw contexts switch standard

# Request elevated mode (requires approval)
openclaw contexts switch elevated --reason "System maintenance"

# Emergency mode (requires 2 approvers)
openclaw contexts switch emergency --reason "Critical incident"
```

### Profile Definitions

```yaml
profiles:
  restricted:
    description: "Safe mode for public/untrusted scenarios"
    tools:
      exec: deny
      fs: workspace-only
    channels:
      groups: deny
      unknown-users: deny
  
  standard:
    description: "Normal operation for trusted users"
    tools:
      exec: allowlist
      fs: workspace-only
    channels:
      groups: allowlist
      unknown-users: deny
  
  elevated:
    description: "Admin tasks, time-limited"
    tools:
      exec: allowlist-extended
      fs: selective-paths
    time-limit: 30m
    requires: approval
  
  emergency:
    description: "Critical incidents only"
    tools:
      exec: allow
      fs: full
    time-limit: 10m
    requires: 2-approvals, full-audit
```

## Best Practices

### DO ✅
- Default to restricted permissions
- Use time-limited elevated access
- Require approval for sensitive operations
- Log all permission changes
- Regularly audit permission usage
- Implement least-privilege per context

### DON'T ❌
- Grant permanent elevated permissions
- Share elevated access credentials
- Skip approval workflows
- Disable audit logging
- Use emergency mode for routine tasks
- Forget to revoke temporary permissions

## Rollback Procedures

### If Permissions Lock You Out

```bash
# 1. Access via console/SSH
ssh user@openclaw-host

# 2. Disable context engine temporarily
openclaw contexts disable

# 3. Or restore from backup
cp ~/.openclaw/config.json.backup ~/.openclaw/config.json
openclaw gateway restart

# 4. Or use recovery mode
openclaw --recovery-mode
# This starts with minimal config, no contexts
```

### Emergency Recovery Script

```bash
#!/bin/bash
# recovery_permissions.sh

echo "🚨 Emergency Permission Recovery"
echo "This will reset all contexts to default"

read -p "Are you sure? (y/N) " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted"
    exit 1
fi

# Backup current config
cp ~/.openclaw/config.json ~/.openclaw/config.json.recovery.$(date +%s)

# Remove context configuration
jq 'del(.contexts)' ~/.openclaw/config.json > /tmp/config.tmp
mv /tmp/config.tmp ~/.openclaw/config.json

# Restart gateway
openclaw gateway restart

echo "✅ Permissions reset to default"
echo "📋 Backup saved: ~/.openclaw/config.json.recovery.*"
```

## Monitoring & Alerts

### Alert on Suspicious Activity

```json
{
  "alerts": {
    "rules": [
      {
        "name": "elevated_after_hours",
        "condition": {
          "context": "elevated",
          "timeRange": "22:00-06:00"
        },
        "action": "notify_admin"
      },
      {
        "name": "multiple_denials",
        "condition": {
          "event": "permission_denied",
          "count": 5,
          "window": "5m"
        },
        "action": "notify_admin"
      },
      {
        "name": "emergency_used",
        "condition": {
          "context": "emergency"
        },
        "action": "notify_all_admins"
      }
    ]
  }
}
```

## References

- OpenClaw Security Scanner: `../SKILL.md`
- Network Security Guide: `network-security.md`
- Remediation Playbook: `remediation-playbook.md`

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-08
