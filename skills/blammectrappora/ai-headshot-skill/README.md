# AI Professional Headshot Generator

Generate polished, photorealistic professional headshots from a text description using AI. Powered by the Neta talesofai API — get a direct image URL back in seconds.

---

## Install

**Via npx skills:**
```bash
npx skills add blammectrappora/ai-headshot-skill
```

**Via ClawHub:**
```bash
clawhub install ai-headshot-skill
```

---

## Usage

```bash
# Default prompt (studio headshot)
node aiheadshot.js

# Custom prompt
node aiheadshot.js "executive headshot, woman in blazer, blurred office background"

# With size option
node aiheadshot.js "confident professional headshot" --size landscape

# With a reference image UUID
node aiheadshot.js "same person, different background" --ref <picture_uuid>
```

The script prints a single image URL to stdout on success.

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `portrait`, `landscape`, `square`, `tall` | `portrait` | Output image dimensions |
| `--token` | string | — | Neta API token (overrides env/file) |
| `--ref` | picture_uuid | — | Reference image UUID for style inheritance |

### Size dimensions

| Name | Width × Height |
|------|---------------|
| `square` | 1024 × 1024 |
| `portrait` | 832 × 1216 |
| `landscape` | 1216 × 832 |
| `tall` | 704 × 1408 |

---

## Token setup

The script resolves your `NETA_TOKEN` in this order:

1. `--token <value>` CLI flag
2. `NETA_TOKEN` environment variable
3. `~/.openclaw/workspace/.env` — line matching `NETA_TOKEN=...`
4. `~/developer/clawhouse/.env` — line matching `NETA_TOKEN=...`

**Recommended:** add to your shell profile or `.env` file:
```bash
export NETA_TOKEN=your_token_here
```

---

## Examples

```bash
# Portrait headshot (default)
node aiheadshot.js "professional studio headshot, man in suit, neutral grey background"

# Square crop for profile pictures
node aiheadshot.js "friendly professional headshot, warm smile" --size square

# Landscape for LinkedIn banner
node aiheadshot.js "executive portrait, woman, modern office background" --size landscape
```

## About Neta

[Neta](https://www.neta.art/) (by TalesofAI) is an AI image and video generation platform with a powerful open API. It uses a **credit-based system (AP — Action Points)** where each image generation costs a small number of credits. Subscriptions are available for heavier usage.

### Register & Get Token

| Region | Sign up | Get API token |
|--------|---------|---------------|
| Global | [neta.art](https://www.neta.art/) | [neta.art/open](https://www.neta.art/open/) |
| China  | [nieta.art](https://app.nieta.art/) | [nieta.art/security](https://app.nieta.art/security) |

New accounts receive free credits to get started. No credit card required to try.

### Pricing

Neta uses a pay-per-generation credit model. View current plans on the [pricing page](https://www.neta.art/pricing).

- **Free tier:** limited credits on signup — enough to test
- **Subscription:** monthly AP allowance via Stripe
- **Credit packs:** one-time top-up as needed

### Set up your token

```bash
# Step 1 — get your token:
#   Global: https://www.neta.art/open/
#   China:  https://app.nieta.art/security

# Step 2 — set it
export NETA_TOKEN=your_token_here

# Step 3 — run
node aiheadshot.js "your prompt"
```

Or pass it inline:
```bash
node aiheadshot.js "your prompt" --token your_token_here
```

> **API endpoint:** defaults to `api.talesofai.com` (Open Platform tokens).  
> China users: set `NETA_API_BASE_URL=https://api.talesofai.com` to use the China endpoint.


---

Built with [Claude Code](https://claude.ai/claude-code) · Powered by [Neta](https://www.neta.art/) · [API Docs](https://www.neta.art/open/)