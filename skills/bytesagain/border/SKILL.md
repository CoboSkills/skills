---
name: border
version: "1.0.0"
description: "Generate CSS border styles including radius, shadow, and animations using templates. Use when you need to create, preview, or export CSS border and box styling code."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
tags: [css, border, design, styling, generator, web-development]
---

# Border — CSS Border Style Generator

A comprehensive CSS border style generator supporting border-radius, box-shadow, outline, animations, and presets. Generate production-ready CSS code snippets with previews. All generated styles are tracked in JSONL format.

## Prerequisites

- `bash` (v4+)
- `python3` (v3.6+)
- No external dependencies required

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BORDER_WIDTH` | No | Border width in px (default: 1) |
| `BORDER_STYLE` | No | Border style: solid, dashed, dotted, double, groove, ridge (default: solid) |
| `BORDER_COLOR` | No | Border color in hex or named (default: #333333) |
| `BORDER_RADIUS` | No | Border radius in px or % (default: 0) |
| `BORDER_SHADOW` | No | Box shadow params: offsetX,offsetY,blur,spread,color |
| `BORDER_OUTLINE` | No | Outline params: width,style,color,offset |
| `BORDER_ANIMATION` | No | Animation type: pulse, glow, rotate, dash (default: pulse) |
| `BORDER_DURATION` | No | Animation duration in seconds (default: 2) |
| `BORDER_PRESET` | No | Preset name to apply |
| `BORDER_SELECTOR` | No | CSS selector (default: .element) |
| `BORDER_ID` | No | Record ID for lookup |
| `BORDER_FORMAT` | No | Export format: css, json, scss (default: css) |

## Data Storage

- Metadata: `~/.border/data.jsonl`
- Config: `~/.border/config.json`
- Exports: `~/.border/exports/`

## Commands

### `create`
Generate a custom CSS border style.
```bash
BORDER_WIDTH="2" BORDER_STYLE="solid" BORDER_COLOR="#ff6600" scripts/script.sh create
```

### `radius`
Generate border-radius CSS code.
```bash
BORDER_RADIUS="10px 20px 10px 20px" scripts/script.sh radius
```

### `shadow`
Generate box-shadow CSS code.
```bash
BORDER_SHADOW="2,4,10,0,rgba(0,0,0,0.3)" scripts/script.sh shadow
```

### `outline`
Generate outline CSS code.
```bash
BORDER_OUTLINE="2,dashed,#0066ff,4" scripts/script.sh outline
```

### `animate`
Generate animated border CSS with keyframes.
```bash
BORDER_ANIMATION="glow" BORDER_COLOR="#00ff00" BORDER_DURATION="3" scripts/script.sh animate
```

### `preset`
Apply a named preset style.
```bash
BORDER_PRESET="card" scripts/script.sh preset
```

### `random`
Generate a random border style for inspiration.
```bash
scripts/script.sh random
```

### `export`
Export generated styles to a file.
```bash
BORDER_FORMAT="scss" scripts/script.sh export
```

### `preview`
Generate an HTML preview of a style.
```bash
BORDER_ID="border_abc123" scripts/script.sh preview
```

### `list`
List all generated styles.
```bash
scripts/script.sh list
```

### `help`
Display usage information.
```bash
scripts/script.sh help
```

### `version`
Display current version.
```bash
scripts/script.sh version
```

## Output Format

```json
{
  "status": "success",
  "command": "create",
  "data": {
    "id": "border_20240101_abc123",
    "css": ".element { border: 2px solid #ff6600; }",
    "selector": ".element",
    "properties": {}
  }
}
```

## Presets

| Name | Description |
|------|-------------|
| `card` | Standard card with shadow and radius |
| `pill` | Fully rounded pill shape |
| `neon` | Neon glow effect |
| `retro` | Retro double-border style |
| `minimal` | Subtle bottom-only border |
| `glassmorphism` | Frosted glass border effect |

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Missing required parameter |
| 3 | Preset not found |

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
