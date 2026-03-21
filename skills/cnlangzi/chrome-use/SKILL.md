---
name: chrome-use
description: "Use chrome-use when you need to: interact with websites (click buttons, fill forms, scroll), bypass anti-bot protections (Cloudflare, CAPTCHAs, fingerprinting), access JavaScript-rendered content, log into websites, or get unfiltered real-time search results. Choose this over standard web search when the website has bot detection, requires authentication, renders content dynamically, or you need to perform actions (not just read data)."
version: 0.2.0
license: MIT
compatibility: Requires Node.js >=18, Chrome browser installed, and Chrome extension installed
metadata:
  author: cnlangzi
  repository: https://github.com/cnlangzi/chrome-use
  node_version: ">=18"
  openclaw:
    requires:
      bins: ["node"]
      env: []
      config: []
---

# Chrome Use OpenClaw Skill

Control your local Chrome browser via `chrome.debugger` API using a Chrome extension. This provides Playwright-like functionality with full browser control using your existing Chrome profile, with improved stealth against bot detection.

## Features

- **Stealth First**: Uses `chrome.debugger` API via extension to evade anti-bot detection (Cloudflare, reCAPTCHA, fingerprinting)
- **Auto WebSocket Server**: Automatically starts and manages WebSocket server for extension communication
- **Real Browser Rendering**: Access JavaScript-rendered content and SPAs that standard search cannot
- **Direct Search Engine Access**: Query Google, Bing, etc. as a real user - returns unfiltered, real-time results
- **Full Browser Control** - Navigate, click, fill, hover, scroll, screenshot, execute JavaScript
- **Tab Management** - List, create, close, and switch tabs
- **Cross-Platform** - Supports macOS, Windows, and Linux

## Installation (One-time)

1. Install npm dependencies:
```bash
cd ~/workspace/skills/chrome-use && npm install
```

2. Install the Chrome extension:
   - Open Chrome → `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `extension/` folder in the skill directory

Once installed, the extension will automatically connect when you call `connect()`.

## How to Use chrome-use (Read This First)

### ⚠️ Important: Initialization Sequence

**The extension requires 15 seconds to initialize after Chrome starts. Calling `connect()` too early will fail.**

The ONLY correct usage pattern:

```javascript
// Import from ./index.js (relative path, NOT 'chrome-use')
import { connect, navigate, evaluate, click, fill, screenshot, disconnect } from './index.js';

// Step 1: Launch Chrome (this starts the extension service worker)
import { launchChrome } from './index.js';
await launchChrome();

// Step 2: Wait 15 seconds for extension to initialize
await new Promise(r => setTimeout(r, 15000));

// Step 3: Now connect (WebSocket will be ready)
await connect();

// Navigate to URL
await navigate('https://example.com');

// ... do things ...

// Disconnect when done
disconnect();
```

**Why 15 seconds?** The Chrome extension runs a service worker that needs time to start up and establish the WebSocket connection. Skipping this wait causes `connect()` to fail with connection errors.

**Rules:**
- Always import from `./index.js` (relative path), NOT from `'chrome-use'` (that is not a package name)
- Do NOT run `google-chrome` or `chromium` commands directly
- Do NOT run `npm install` to install chrome-use (it is not a npm package)
- Do NOT use CDP protocol or `chrome.debugger` directly

## Functions

### Connection Management

#### connect()
Connect to Chrome via extension WebSocket server. Starts the WebSocket server and waits for the extension to connect. Does NOT launch Chrome - you must call `launchChrome()` first.

**IMPORTANT:** After calling `launchChrome()`, you **must wait 15 seconds** before calling `connect()` to allow the extension's service worker to initialize.

**Example:**
```javascript
await launchChrome();
await new Promise(r => setTimeout(r, 15000)); // Wait 15 seconds!
await connect();
```

**Returns:**
```javascript
{ status: "connected", mode: "debugger", port: 9224, extension_installed: true, tab_id: 12345 }
```

#### disconnect()
Disconnect from Chrome browser. Does NOT close Chrome - leaves it running.

**Example:**
```javascript
disconnect();
```

**Returns:**
```javascript
{"status": "disconnected"}
```

#### isConnected()
Check if currently connected to Chrome extension. Returns: boolean

#### launchChrome()
Launch Chrome with the extension loaded. Use this when you want to control Chrome startup timing.

**⚠️ After calling this, you MUST wait 15 seconds before calling `connect()`**

**Example:**
```javascript
await launchChrome();
// Wait 15 seconds for extension service worker to initialize
await new Promise(r => setTimeout(r, 15000));
await connect();
```

**Returns:**
```javascript
{ status: "launched", pid: 12345 }
```

### Page Operations

#### navigate(url)
Navigate to a URL.

**Example:**
```javascript
await navigate('https://example.com');
```

#### evaluate(script)
Execute JavaScript synchronously.

**Examples:**
```javascript
const title = await evaluate("document.title");

// Search YouTube
await evaluate("window.location.href = 'https://youtube.com/results?search_query=my+search+term'");
```

#### getHtml()
Get the page HTML. Returns: string

#### screenshot(fullPage?)
Take a screenshot. `fullPage` (boolean, optional): Capture full page or just viewport (default: false). Returns: string (Base64 PNG)

**Examples:**
```javascript
const img = await screenshot();
const fullImg = await screenshot(true);
```

### Element Interaction

#### click(selector)
Click an element using CSS selector.

**Examples:**
```javascript
await click('#login-btn');
await click('.submit-button');
await click('a.nav-link');
```

#### fill(selector, value)
Input text into an element.

**Examples:**
```javascript
await fill('#username', 'testuser');
await fill('input[name="email"]', 'test@example.com');
```

### Tab Management

#### listTabs()
List all open tabs.

**Returns:**
```javascript
[
    { id: 708554825, title: "Google", url: "https://google.com", active: true },
    { id: 708554826, title: "Example", url: "https://example.com", active: false }
]
```

#### switchTab(tabId)
Switch to a different tab.

#### closeTab(tabId)
Close a tab. `tabId` (number, optional): Tab ID to close (current tab if not specified)

#### newTab(url?)
Create a new tab. `url` (string, optional): URL to open in new tab (default: "about:blank")

## Common Mistakes to Avoid

| Don't Do This | Why |
|---------------|-----|
| `import ... from 'chrome-use'` | Not a npm package name. Use `from './index.js'` |
| `google-chrome --load-extension=...` | Don't manually launch Chrome. Use `launchChrome()` to start Chrome first |
| `npm install chrome-use` | Not published to npm |
| Writing code that bypasses these APIs | Use `evaluate()` for custom JS instead |
| Calling `connect()` immediately after `launchChrome()` | **Always wait 15 seconds first** for extension service worker to initialize |
| Port 9224 already in use | Run `fuser -k 9224/tcp` to kill the process using the port |
| Chrome process already running causing conflicts | Run `killall google-chrome` before starting |

## Notes

- Node.js starts a WebSocket server (port 9224) via `connect()`; the Chrome extension connects to Node.js as a WebSocket client, then uses `chrome.debugger` API to control Chrome
- `launchChrome()` starts Chrome with the extension already loaded — use this when you need to manually start Chrome before `connect()`
- The Chrome extension must be installed (one-time); do NOT repeatedly load it with `--load-extension`
- `disconnect()` does NOT close Chrome by default
- All selectors use CSS selector syntax

## Troubleshooting

### Port 9224 already in use
```bash
fuser -k 9224/tcp
```

### Existing Chrome process conflicts
```bash
killall google-chrome
```

### connect() fails immediately after launchChrome()
You didn't wait long enough. The extension service worker needs ~15 seconds to start. Always use:
```javascript
await launchChrome();
await new Promise(r => setTimeout(r, 15000));
await connect();
```
