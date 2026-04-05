# MCP Configuration Guide

> OpenCode MCP (Model Context Protocol) integration configuration reference

---

## Contents

- [Configuration Levels](#configuration-levels)
- [Security Considerations](#security-considerations)
- [Global MCP Configuration](#global-mcp-configuration)
  - [Playwright MCP](#playwright-mcp-ui-automation-testing)
  - [Context7 MCP](#context7-mcp-context-management)
- [Project-level MCP Configuration](#project-level-mcp-configuration)
  - [Supabase MCP](#supabase-mcp-database)
- [Complete Configuration Example](#complete-configuration-example)
- [Running Constraints](#running-constraints)
- [Adding New MCP](#adding-new-mcp)
- [Troubleshooting](#troubleshooting)

---

## Configuration Levels

| Level | Location | Purpose | Example |
|-------|----------|---------|---------|
| Global | `~/.config/opencode/opencode.json` | Common tools | Playwright, Context7 |
| Project | `<project>/.opencode/opencode.json` | Project-specific tools | Supabase |

---

## Security Considerations

### ⚠️ Critical: Remote Code Execution Risk

MCP servers run as separate processes. Configuration methods have different security profiles:

| Method | Risk | Description |
|--------|------|-------------|
| **Global Install** | Low | Code verified once, runs locally |
| **npx (no flags)** | Medium | Downloads code, prompts before first run |
| **npx -y** | High | Downloads and executes without confirmation |

### ✅ Recommended: Global Install

**Most secure approach** — verify package integrity once, then run locally:

```bash
# 1. Check package details
npm view @executeautomation/playwright-mcp-server

# 2. Install globally
npm install -g @executeautomation/playwright-mcp-server

# 3. Configure with installed binary
"command": ["playwright-mcp-server"]
```

**Benefits:**
- Code verified at install time
- No repeated downloads
- No network dependency at runtime
- Version pinned until explicit update

### ⚠️ Alternative: npx (Use Only in Trusted Environments)

**Convenience trade-off** — `npx` downloads and executes remote code:

```bash
# Downloads package on each run (or cached for a period)
"command": ["npx", "@executeautomation/playwright-mcp-server"]
```

**If using npx:**
1. Only in trusted, isolated environments
2. Pin specific version: `@executeautomation/playwright-mcp-server@1.2.3`
3. Never use `-y` flag (it bypasses confirmation)
4. Verify package integrity before first use

### Environment Variables

MCP servers may require API keys or credentials. Store them securely:

- **Development**: Use `.env` files (add to `.gitignore`)
- **Production**: Use system environment variables or secret managers
- **Never** hardcode secrets in config files that get committed

---

## Global MCP Configuration

### Playwright MCP (UI Automation Testing)

#### Recommended (Global Install)

```bash
# Install
npm install -g @executeautomation/playwright-mcp-server
```

```json
{
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["playwright-mcp-server"]
    }
  }
}
```

#### Alternative (npx)

> ⚠️ Only use in trusted environments. Downloads remote code.

```json
{
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "@executeautomation/playwright-mcp-server@1.0.0"]
    }
  }
}
```

**Purpose:**
- UI automation testing
- Page interaction simulation
- Screenshot comparison

**Tool chain:**
| Tool | Purpose |
|------|---------|
| `browser snapshot` | Get page state |
| `browser act` | Click/input operations |
| `browser screenshot` | Screenshot comparison |

---

### Context7 MCP (Context Management)

#### Recommended (Global Install)

```bash
# Install
npm install -g @upstash/context7-mcp
```

```json
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["context7-mcp"],
      "environment": {
        "CONTEXT7_API_KEY": "<your-api-key>",
        "DEFAULT_MINIMUM_TOKENS": "10000"
      }
    }
  }
}
```

#### Alternative (npx)

> ⚠️ Only use in trusted environments. Downloads remote code.

```json
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "@upstash/context7-mcp"],
      "environment": {
        "CONTEXT7_API_KEY": "<your-api-key>",
        "DEFAULT_MINIMUM_TOKENS": "10000"
      }
    }
  }
}
```

**Purpose:**
- Long-term context storage
- Cross-session memory

**Get API Key:** https://upstash.com

---

## Project-level MCP Configuration

### Supabase MCP (Database)

#### Recommended (Global Install)

```bash
# Install
npm install -g @supabase/mcp-server-supabase
```

**Config file:** `<project>/.opencode/opencode.json`

```json
{
  "mcp": {
    "supabase": {
      "type": "local",
      "command": ["mcp-server-supabase"],
      "environment": {
        "SUPABASE_URL": "<your-project-url>",
        "SUPABASE_ANON_KEY": "<your-anon-key>"
      }
    }
  }
}
```

#### Alternative (npx)

> ⚠️ Only use in trusted environments. Downloads remote code.

```json
{
  "mcp": {
    "supabase": {
      "type": "local",
      "command": ["npx", "@supabase/mcp-server-supabase"],
      "environment": {
        "SUPABASE_URL": "<your-project-url>",
        "SUPABASE_ANON_KEY": "<your-anon-key>"
      }
    }
  }
}
```

**Purpose:**
- Database operations
- Schema migrations
- Data queries

**Tool chain:**
| Tool | Purpose |
|------|---------|
| `supabase_apply_migration` | Create/modify tables, functions |
| `supabase_execute_sql` | Execute SQL queries |
| `supabase_list_tables` | List tables |
| `supabase_get_advisors` | Security recommendations |

**⚠️ Running constraint:** Must start OpenCode in project root directory to load project-level config

---

## Complete Configuration Example

### Global Config (~/.config/opencode/opencode.json)

> Using recommended global install method

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["playwright-mcp-server"]
    },
    "context7": {
      "type": "local",
      "command": ["context7-mcp"],
      "environment": {
        "CONTEXT7_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

### Project Config (<project>/.opencode/opencode.json)

> Using recommended global install method

```json
{
  "mcp": {
    "supabase": {
      "type": "local",
      "command": ["mcp-server-supabase"],
      "environment": {
        "SUPABASE_URL": "https://xxx.supabase.co",
        "SUPABASE_ANON_KEY": "eyJ..."
      }
    }
  }
}
```

---

## Running Constraints

### ⚠️ Must run in project root directory

```bash
# Correct
cd /path/to/project
opencode run -m <model> -- "task"

# Wrong (project-level MCP won't load)
opencode run --dir /path/to/project "task"
```

### Reason

OpenCode looks for `.opencode/opencode.json` from **current working directory**. If not in project root, project-level MCP config won't load.

---

## Adding New MCP

1. Find MCP Server package name (e.g., `@modelcontextprotocol/server-filesystem`)
2. **Verify package integrity**: `npm view <package>` and check for vulnerabilities
3. **Recommended**: Install globally with `npm install -g <package>`
4. Add to `mcp` object in config file using installed binary name
5. Set required environment variables securely
6. Restart OpenCode or start new session

---

## Troubleshooting

### MCP not loading

**Symptoms:** OpenCode cannot call MCP tools

**Check:**
1. Is config file path correct?
2. Is JSON format valid?
3. Are environment variables set?
4. Are you running in project root?
5. Is the MCP binary installed globally?

### Debug MCP

```bash
# View available MCP
opencode mcp list

# Test MCP connection
opencode mcp debug <name>

# Check if binary is installed
which playwright-mcp-server
```

---

*Configuration Guide v1.2 - 2026-04-05*