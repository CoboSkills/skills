---
name: openclaw-security-scanner
version: 1.0.2
slug: openclaw-security-scanner
description: |
  Security expert for OpenClaw deployments. Scans for vulnerabilities in network config, 
  channel policies, and tool permissions. Provides safe remediation with rollback plans 
  to prevent bricking remote deployments. Fully offline - no external network access required.
homepage: https://github.com/openclaw/openclaw/tree/main/skills/openclaw-security-scanner
changelog: |
  1.0.2 - Remove external network access
    - Removed GitHub API fetching to eliminate outbound HTTP requests
    - Scan now operates fully offline on local configuration only
    - Fixes ClawHub suspicious flag
  1.0.0 - Initial release
    - Network port scanning (exposed ports, default ports, binding config)
    - Channel policy audit (Telegram, WhatsApp, Web authentication)
    - Permission analysis (tool exec, filesystem access)
    - Safe remediation playbook with rollback procedures
    - Context-aware permission management guide
license: MIT
author: DTClaw Team <dtclaw@163.com>
tags:
  - security
  - audit
  - scanner
  - hardening
  - compliance
minOpenClawVersion: 2026.3.0
---

# OpenClaw Security Scanner

**Role**: Security Expert for OpenClaw Deployments

**Purpose**: Audit OpenClaw configurations for security vulnerabilities and provide safe, actionable remediation guidance.

## Installation

### Via ClawHub (Recommended)

```bash
# Install from ClawHub registry
clawhub install openclaw-security-scanner

# Or install from local workspace
clawhub install skills/openclaw-security-scanner

# Verify installation
clawhub list | grep security-scanner
```

### Manual Installation

```bash
# Clone or copy to skills directory
cp -r openclaw-security-scanner ~/.openclaw/workspace/skills/

# Validate installation
python3 ~/.openclaw/workspace/skills/skill-creator/scripts/quick_validate.py openclaw-security-scanner
```

### Requirements

- OpenClaw >= 2026.3.0
- Python 3.8+
- **Optional**: `lsof` (macOS/Linux) or `ss` (Linux, from iproute2) for port binding detection. If neither is available, port scan still works but cannot determine whether a port is bound to 0.0.0.0 vs 127.0.0.1.

## Quick Start

After installation, run a security scan:

```bash
# Full security audit (recommended)
openclaw security-scan

# Or use the Python script directly
python3 skills/openclaw-security-scanner/scripts/security_scan.py

# Generate report to file
openclaw security-scan --output security_report.md
```

## When to Use

Trigger this skill when:
- User requests security audit: "scan my OpenClaw for security issues"
- After initial setup to verify security posture
- Before exposing OpenClaw to production/multi-user environments
- After major configuration changes
- Periodic security health checks (recommended: weekly)
- User reports suspicious activity

## Commands

The skill provides these commands via `openclaw` CLI:

| Command | Description | Example |
|---------|-------------|---------|
| `security-scan` | Full security audit | `openclaw security-scan` |
| `security-scan --ports-only` | Scan network ports only | `openclaw security-scan --ports-only` |
| `security-scan --channels` | Audit channel policies | `openclaw security-scan --channels` |
| `security-scan --permissions` | Analyze permissions | `openclaw security-scan --permissions` |
| `security-scan --output FILE` | Save report to file | `openclaw security-scan -o report.md` |

## Features

### 1. Network Security Scan

Detects:
- Exposed gateway ports (bound to 0.0.0.0 vs 127.0.0.1)
- Default/predictable ports
- SSH and other service exposure
- Firewall configuration issues

**Example Output**:
```
🔴 CRITICAL: Gateway port 18789 exposed to all interfaces
   Impact: Attackers on the network can access gateway API
   Fix: Bind gateway to 127.0.0.1 or use firewall rules
   Risk: MEDIUM - may break remote access if not careful
```

### 2. Channel Policy Audit

Checks:
- Telegram `groupPolicy` (allow vs allowlist)
- WhatsApp webhook secrets
- Web channel authentication
- Group chat allowlists
- Unknown user policies

**Example Output**:
```
🔴 CRITICAL: Telegram allows all group messages
   Current: groupPolicy="allow"
   Impact: Anyone can send messages, potential for abuse
   Fix: Set groupPolicy="allowlist" and configure allowedGroups
   Risk: LOW - won't break 1:1 chats
```

### 3. Permission Analysis

Evaluates:
- Tool execution policy (allow vs deny vs allowlist)
- Filesystem access scope (workspaceOnly)
- Dangerous tools enabled (exec, shell, system.run)
- Context-aware permission configuration

**Example Output**:
```
🔴 CRITICAL: Tool execution policy is 'allow'
   Impact: Any tool can run arbitrary commands
   Fix: Set tools.exec.policy="deny" or "allowlist"
   Risk: HIGH - may break existing workflows
```

### 4. Safe Remediation

Every finding includes:
- **Risk Assessment**: CRITICAL/HIGH/MEDIUM/LOW
- **Impact Description**: What could go wrong
- **Remediation Steps**: How to fix
- **Risk of Fix**: LOW/MEDIUM/HIGH (will this break things?)
- **Rollback Plan**: How to undo if something goes wrong

## Risk Scoring

| Level | Response Time | Examples |
|-------|---------------|----------|
| 🔴 **CRITICAL** | < 1 hour | Exposed admin port, allow-all channel policy, default credentials |
| 🟠 **HIGH** | < 24 hours | Missing authentication, excessive tool permissions, no TLS |
| 🟡 **MEDIUM** | < 1 week | Weak rate limiting, verbose errors, outdated dependencies |
| 🔵 **LOW** | < 1 month | Missing security headers, suboptimal logging |

## Safe Remediation Protocol

⚠️ **CRITICAL RULE**: Never apply fixes that may break remote access without:

1. ✅ Verified backup access (SSH, console, secondary channel)
2. ✅ Config backup with tested restore procedure
3. ✅ Maintenance window scheduled
4. ✅ Rollback plan ready

### High-Risk Changes Require Staged Rollout

```
Phase 1: Preparation
├─ Backup config: cp config.json config.json.backup.$(date +%s)
├─ Document current state
├─ Verify alternative access (SSH, console)
└─ Schedule maintenance window

Phase 2: Staging
├─ Apply to test environment first
├─ Verify functionality
├─ Test rollback procedure
└─ Get approval

Phase 3: Production
├─ Apply during maintenance window
├─ Monitor closely (24-48 hours)
├─ Keep rollback ready
└─ Document changes

Phase 4: Verification
├─ Test all critical functions
├─ Verify security improvement
├─ Monitor for issues
└─ Update documentation
```

## Output Format

Reports are generated in Markdown format:

```markdown
# OpenClaw Security Audit Report

**Scan Date**: 2026-03-08 16:30
**Hostname**: mybot.local
**Overall Risk Level**: HIGH

## Executive Summary
- 🔴 CRITICAL: 2
- 🟠 HIGH: 3
- 🟡 MEDIUM: 5
- 🔵 LOW: 2

## Findings
[Detailed findings with remediation steps]

## Remediation Plan
### Immediate Actions (< 24h)
- [ ] Fix 1 (Risk: LOW)
- [ ] Fix 2 (Risk: MEDIUM)

### Staged Rollout Required
- [ ] Fix 3 (Risk: HIGH - may break remote access)
```

## Examples

### Basic Security Scan

User: "Scan my OpenClaw for security issues"

Assistant runs:
```bash
openclaw security-scan --output security_report.md
```

Output:
```
✅ Network scan complete: 2 ports exposed
✅ Channel audit: 1 unsafe policy found  
✅ Permission analysis: 3 excessive permissions

Risk Level: HIGH
Report saved to: security_report.md
```

### Targeted Channel Audit

User: "Check if my Telegram configuration is safe"

Assistant runs:
```bash
openclaw security-scan --channels --output telegram_audit.md
```

### Weekly Security Check

Add to `HEARTBEAT.md`:
```markdown
## Weekly Security Scan

Every Sunday at 02:00:
- Run: `openclaw security-scan -o weekly_security.md`
- Review CRITICAL/HIGH findings
- Apply low-risk fixes
- Report summary to admin channel
```

## Integration

### Heartbeat Integration

```yaml
# ~/.openclaw/workspace/HEARTBEAT.md
weekly_security_scan:
  schedule: "0 2 * * 0"  # Sunday 2 AM
  command: "openclaw security-scan -o docs/reports/weekly_security.md"
  review: "Within 24 hours"
```

### Alert Triggers

Configure alerts for:
- New CRITICAL findings
- Configuration drift from secure baseline
- Failed authentication attempts > 10/hour
- Unusual tool execution patterns

## Scripts

All scripts are located in `skills/openclaw-security-scanner/scripts/`:

| Script | Purpose | Usage |
|--------|---------|-------|
| `security_scan.py` | Main security scanner | `python3 security_scan.py [options]` |

### Script Options

```bash
# security_scan.py
--ports-only        Only scan network ports
--channels-only     Only audit channel policies
--permissions-only  Only analyze permissions
--output, -o FILE   Save report to file
--verbose, -v       Verbose output
--full              Full scan (default)
```

## References

Detailed guides in `skills/openclaw-security-scanner/references/`:

- **permission-management.md** - Context-aware permission configuration
  - Permission levels (Restricted/Standard/Elevated/Emergency)
  - User-based, channel-based, time-based contexts
  - Lifecycle management and approval workflows
  - Quick switch commands and profiles

- **remediation-playbook.md** - Safe fix procedures
  - Golden rules for safe remediation
  - Step-by-step fixes for common issues
  - Rollback procedures for every fix
  - Emergency recovery procedures
  - Post-mortem templates

## Troubleshooting

### Config Not Found

```
[WARN] No config file found
```

**Solution**: Ensure OpenClaw config exists at:
- `~/.openclaw/config.json`
- `~/.openclaw/gateway.config.json`
- Or set `OPENCLAW_CONFIG` environment variable

### Permission Denied

```
Error: [Errno 13] Permission denied
```

**Solution**: Run with appropriate permissions or check file ownership.

## Safety Warnings

⚠️ **NEVER** apply security fixes that may break remote access without:
1. Verified backup access (SSH, console, secondary channel)
2. Config backup with tested restore procedure
3. Maintenance window scheduled
4. Rollback plan ready

⚠️ **ALWAYS** test high-risk changes in staging first

⚠️ **DOCUMENT** all changes for audit trail

## Limitations

- Cannot scan network topology beyond host
- Cannot test physical security
- Cannot assess social engineering risks
- Some checks require elevated permissions

## Support

For security emergencies:
1. Run full scan immediately
2. Apply CRITICAL fixes with rollback ready
3. Report findings to security team
4. Schedule follow-up audit in 7 days

## Contributing

To contribute improvements:
1. Fork the repository
2. Create feature branch
3. Add tests for new checks
4. Submit pull request

## License

MIT License - See LICENSE file for details.

---

**Skill Version**: 1.0.2
**Last Updated**: 2026-03-09  
**Maintainer**: Security Team  
**Contact**: security@openclaw.ai
