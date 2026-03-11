# Security Remediation Playbook

**Purpose**: Safe, step-by-step procedures for fixing security issues without breaking remote access.

## Golden Rules

### Rule 1: Never Brick Remote Deployments ⚠️

**Before ANY security fix:**
1. ✅ Verify backup access (SSH, console, secondary channel)
2. ✅ Create config backup
3. ✅ Test restore procedure
4. ✅ Schedule maintenance window
5. ✅ Prepare rollback script

### Rule 2: Stage High-Risk Changes

```
Phase 1: Preparation (Day 1)
├─ Backup config
├─ Document current state
├─ Verify alternative access
└─ Notify stakeholders

Phase 2: Staging (Day 2-3)
├─ Apply to test environment
├─ Verify functionality
├─ Test rollback
└─ Get approval

Phase 3: Production (Day 4)
├─ Apply during maintenance window
├─ Monitor closely (24-48h)
├─ Keep rollback ready
└─ Document changes

Phase 4: Verification (Day 5-7)
├─ Verify security improvement
├─ Check for side effects
├─ Update documentation
└─ Close change ticket
```

### Rule 3: Always Have Rollback

Every fix must have tested rollback:
```bash
# Standard rollback template
#!/bin/bash
# rollback_<fix_name>.sh

echo "🔄 Rolling back: <fix_name>"
echo "⚠️  This will restore previous configuration"

# Backup current (in case we need to rollback the rollback)
cp ~/.openclaw/config.json ~/.openclaw/config.json.rollback2.$(date +%s)

# Restore original backup
cp ~/.openclaw/config.json.backup.<timestamp> ~/.openclaw/config.json

# Restart service
openclaw gateway restart

# Verify
openclaw status

echo "✅ Rollback complete"
```

## Common Fixes

### Fix 1: Restrict Telegram Group Policy

**Risk Level**: CRITICAL  
**Risk of Fix**: LOW (won't break 1:1 chats)

**Current (Unsafe)**:
```json
{
  "channels": {
    "telegram": {
      "groupPolicy": "allow"
    }
  }
}
```

**Target (Safe)**:
```json
{
  "channels": {
    "telegram": {
      "groupPolicy": "allowlist",
      "allowedGroups": ["group-id-1", "group-id-2"]
    }
  }
}
```

**Procedure**:
```bash
# Step 1: Backup
cp ~/.openclaw/config.json ~/.openclaw/config.json.backup.$(date +%s)

# Step 2: Get your admin group IDs
# Send this to your bot in Telegram:
# /start - bot will reply with chat ID

# Step 3: Edit config
jq '.channels.telegram.groupPolicy = "allowlist" | 
    .channels.telegram.allowedGroups = ["<your-admin-group-id>"]' \
    ~/.openclaw/config.json > /tmp/config.tmp

# Step 4: Validate JSON
jq . /tmp/config.tmp > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"

# Step 5: Apply
mv /tmp/config.tmp ~/.openclaw/config.json

# Step 6: Restart
openclaw gateway restart

# Step 7: Verify
openclaw status
# Send test message to bot from allowed group
```

**Rollback**:
```bash
cp ~/.openclaw/config.json.backup.<timestamp> ~/.openclaw/config.json
openclaw gateway restart
```

---

### Fix 2: Bind Gateway to Localhost

**Risk Level**: CRITICAL  
**Risk of Fix**: HIGH (will break remote access if not careful)

⚠️ **STAGED ROLLOUT REQUIRED**

**Current (Unsafe)**:
```json
{
  "gateway": {
    "host": "0.0.0.0",
    "port": 18789
  }
}
```

**Target (Safe)**:
```json
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18789
  },
  "firewall": {
    "enabled": true,
    "allowedIPs": ["192.168.3.0/24"]
  }
}
```

**Procedure**:

**Phase 1: Preparation**
```bash
# 1. Verify SSH access
ssh user@openclaw-host
# ✅ Must work

# 2. Verify console access (physical or IPMI)
# ✅ Must have alternative to network

# 3. Backup config
cp ~/.openclaw/config.json ~/.openclaw/config.json.backup.$(date +%s)

# 4. Document current state
openclaw status > /tmp/pre_fix_status.txt
netstat -tlnp | grep 18789 > /tmp/pre_fix_ports.txt
```

**Phase 2: Firewall First (Safer)**
```bash
# Instead of changing binding, add firewall rules first

# macOS
sudo pfctl -f /etc/pf.conf
# Add: block in quick on !lo0 proto tcp from any to any port 18789

# Or use socket filter firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --addblocked "/usr/local/bin/node"

# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 18789 -s 192.168.3.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 18789 -j DROP

# Verify
nmap -p 18789 localhost  # Should show open
nmap -p 18789 192.168.3.x  # Should show filtered (from other hosts)
```

**Phase 3: Change Binding (Maintenance Window)**
```bash
# 1. Notify users
# "Gateway will restart in 5 minutes for security update"

# 2. Edit config
jq '.gateway.host = "127.0.0.1"' ~/.openclaw/config.json > /tmp/config.tmp
mv /tmp/config.tmp ~/.openclaw/config.json

# 3. Restart
openclaw gateway restart

# 4. Verify locally
curl http://127.0.0.1:18789/status

# 5. Verify blocked remotely (from another machine)
# nmap -p 18789 openclaw-host  # Should show filtered
```

**Rollback**:
```bash
# If something goes wrong, SSH in and:
cp ~/.openclaw/config.json.backup.<timestamp> ~/.openclaw/config.json
openclaw gateway restart
```

---

### Fix 3: Restrict Tool Execution

**Risk Level**: CRITICAL  
**Risk of Fix**: MEDIUM (may break workflows)

**Current (Unsafe)**:
```json
{
  "tools": {
    "exec": {
      "policy": "allow"
    }
  }
}
```

**Target (Safe)**:
```json
{
  "tools": {
    "exec": {
      "policy": "allowlist",
      "allowedCommands": [
        "openclaw status",
        "openclaw gateway restart",
        "git status",
        "ls",
        "cat",
        "grep"
      ]
    }
  }
}
```

**Procedure**:
```bash
# 1. Audit current tool usage
# Check logs for commonly used commands
grep "exec" ~/.openclaw/logs/*.log | \
  jq -r '.command' | sort | uniq -c | sort -rn | head -20

# 2. Create allowlist based on actual usage
# Start with most common, add more as needed

# 3. Backup
cp ~/.openclaw/config.json ~/.openclaw/config.json.backup.$(date +%s)

# 4. Apply
cat > /tmp/exec_policy.json << 'EOF'
{
  "policy": "allowlist",
  "allowedCommands": [
    "openclaw *",
    "git status",
    "git diff",
    "ls *",
    "cat *",
    "grep *"
  ]
}
EOF

jq '.tools.exec = $(cat /tmp/exec_policy.json)' \
  ~/.openclaw/config.json > /tmp/config.tmp
mv /tmp/config.tmp ~/.openclaw/config.json

# 5. Test
openclaw gateway restart

# 6. Monitor for denials
tail -f ~/.openclaw/logs/*.log | grep "denied"
# Add missing commands to allowlist as needed
```

**Rollback**:
```bash
cp ~/.openclaw/config.json.backup.<timestamp> ~/.openclaw/config.json
openclaw gateway restart
```

---

### Fix 4: Enable Web Authentication

**Risk Level**: CRITICAL  
**Risk of Fix**: LOW (won't break, just requires login)

**Current (Unsafe)**:
```json
{
  "channels": {
    "web": {
      "enabled": true,
      "authentication": {
        "enabled": false
      }
    }
  }
}
```

**Target (Safe)**:
```json
{
  "channels": {
    "web": {
      "enabled": true,
      "authentication": {
        "enabled": true,
        "provider": "password",
        "users": [
          {
            "username": "admin",
            "passwordHash": "<bcrypt-hash>"
          }
        ]
      }
    }
  }
}
```

**Procedure**:
```bash
# 1. Generate password hash
# Use bcrypt or similar
python3 -c "import bcrypt; print(bcrypt.hashpw(b'your-password', bcrypt.gensalt()).decode())"

# 2. Backup
cp ~/.openclaw/config.json ~/.openclaw/config.json.backup.$(date +%s)

# 3. Apply
jq '.channels.web.authentication.enabled = true |
    .channels.web.authentication.users = [
      {
        "username": "admin",
        "passwordHash": "<your-hash>"
      }
    ]' ~/.openclaw/config.json > /tmp/config.tmp
mv /tmp/config.tmp ~/.openclaw/config.json

# 4. Restart
openclaw gateway restart

# 5. Test
# Open web UI, should require login
```

**Rollback**:
```bash
cp ~/.openclaw/config.json.backup.<timestamp> ~/.openclaw/config.json
openclaw gateway restart
```

---

## Emergency Procedures

### When Fix Goes Wrong

**Symptoms**:
- Gateway won't start
- Can't connect remotely
- Constant restarts
- Error loops

**Immediate Actions**:
```bash
# 1. Don't panic
# 2. Access via SSH or console
ssh user@openclaw-host

# 3. Check status
openclaw status
openclaw gateway logs --tail 100

# 4. If gateway is broken, restore config
cp ~/.openclaw/config.json.backup.<timestamp> ~/.openclaw/config.json
openclaw gateway restart

# 5. If still broken, try recovery mode
openclaw --recovery-mode

# 6. Last resort: reinstall
# (Document this for post-mortem)
```

### Post-Mortem Template

```markdown
# Security Fix Incident Report

**Date**: YYYY-MM-DD
**Fix Attempted**: [Description]
**Outcome**: [Success/Partial/Failure]

## Timeline
- HH:MM: Started fix
- HH:MM: Issue detected
- HH:MM: Rollback initiated
- HH:MM: Service restored

## Root Cause
[What went wrong]

## Lessons Learned
1. [Lesson 1]
2. [Lesson 2]

## Action Items
- [ ] Update playbook
- [ ] Improve testing
- [ ] Add monitoring
- [ ] Training needed
```

## Monitoring After Fixes

### Verify Security Improvement

```bash
# 1. Re-run security scan
python3 skills/openclaw-security-scanner/scripts/security_scan.py

# 2. Check specific fix
# Example: Verify port binding
lsof -i :18789 | grep LISTEN

# 3. Check logs for issues
tail -f ~/.openclaw/logs/*.log

# 4. Test functionality
# Send test messages, run commands, etc.
```

### Alert Configuration

```json
{
  "alerts": {
    "afterFix": {
      "enabled": true,
      "duration": "48h",
      "events": [
        "gateway_restart",
        "config_change",
        "auth_failure",
        "tool_denied"
      ],
      "notify": ["admin-channel"]
    }
  }
}
```

## Checklist

### Pre-Fix Checklist
- [ ] Backup created and verified
- [ ] Alternative access confirmed
- [ ] Rollback script tested
- [ ] Maintenance window scheduled
- [ ] Stakeholders notified
- [ ] Monitoring enabled

### Post-Fix Checklist
- [ ] Service running normally
- [ ] Security improvement verified
- [ ] No functionality broken
- [ ] Logs clean (no errors)
- [ ] Users can access (if applicable)
- [ ] Documentation updated
- [ ] Backup of new config created

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-08  
**Next Review**: 2026-06-08
