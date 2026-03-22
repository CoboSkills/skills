---
name: productivity-improving
description: A local skill update management tool for OpenClaw. Provides version checking, backup management, rollback capabilities, and configurable upgrade strategies. All operations are local - no network requests.
triggers:
  - productivit
  - skill update
  - skill management
  - 检查 skill
  - 更新 skill
  - skill 备份
  - skill 回滚
---

# Productivity Improving

A local skill update management tool for OpenClaw.

## Overview

Productivity Improving helps you manage OpenClaw skill updates safely. It provides version checking, backup management, and rollback functionality to ensure updates are performed securely.

## Core Principles

**Safety First**:
- Only reads local files, no dangerous operations
- Automatic backups before updates
- Supports version rollback
- Tiered update strategies

## Features

- **Version Check** - View current versions of installed skills
- **Backup Management** - Automatic backups before updates, manual backup support
- **Version Rollback** - Roll back to previous versions if upgrade fails
- **Configuration Management** - Blacklist, auto-upgrade policies, etc.
- **Cache Management** - Smart caching to avoid duplicate checks

## Installation

```bash
clawhub install productivity-improving
```

## Usage

### Check Versions

```bash
# Check all installed skills
productivity-improving check

# Check specific skill
productivity-improving check my-skill
```

### Update Skills

```bash
# Get update suggestions (actual update uses clawhub)
productivity-improving update my-skill

# Then follow prompts to run
clawhub update my-skill
```

### Configuration Management

```bash
# View configuration
productivity-improving config

# Add to blacklist (skip auto-check)
productivity-improving config blacklist add my-skill

# Remove from blacklist
productivity-improving config blacklist remove my-skill

# Set auto-upgrade policy
productivity-improving config auto patch true
productivity-improving config auto minor false
productivity-improving config auto major false
```

### Backup and Rollback

```bash
# List backups
productivity-improving backup list

# Rollback to specific version
productivity-improving rollback my-skill --version 1.0.0

# Clear cache
productivity-improving refresh
```

## Configuration

Config file location: `~/.openclaw/productivity-improving.json`

```json
{
  "mode": "interactive",
  "cacheDuration": 86400000,
  "autoUpgrade": {
    "patch": true,
    "minor": false,
    "major": false
  },
  "remindInterval": 604800000,
  "blacklist": [],
  "quietHours": {
    "start": "22:00",
    "end": "08:00"
  }
}
```

## Update Strategy

| Version Change | Strategy | Description |
|---------------|----------|-------------|
| **Patch** (1.0.1→1.0.2) | Recommended | Bug fixes, security updates |
| **Minor** (1.1→1.2) | Recommended | New features, backward compatible |
| **Major** (1→2) | Requires confirmation | Breaking changes, may affect functionality |

## Security Notes

- This tool **only reads local files**, no network requests
- Actual update operations are performed via `clawhub` CLI
- All backups stored locally in `~/.openclaw/skill-backups/`
- No sensitive information collection or transmission

## Requirements

- Node.js
- OpenClaw installed
- clawhub CLI configured

## Technical Information

| Attribute | Value |
|-----------|-------|
| **Name** | Productivity Improving |
| **Slug** | productivity-improving |
| **Version** | 1.0.2 |
| **Category** | Utility |
| **Tags** | skill-management, backup, update, local-only |

## License

MIT-0
