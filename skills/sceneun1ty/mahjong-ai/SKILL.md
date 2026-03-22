---
name: mahjong-ai
description: "AI Mahjong Assistant 🀄 — Snap a photo of your hand, get optimal discard suggestions. Sichuan Mahjong rules (Blood Battle / 血战到底). Supports tile recognition from photos, shanten analysis, safety ratings, and winning tile calculation. | AI 麻将助手 — 拍照识别手牌，分析最优出牌。川麻规则（血战到底/血流成河）。Use when: user sends a mahjong hand photo, asks for mahjong strategy, tile analysis, or which tile to discard."
---

# Mahjong AI Assistant 🀄 麻将 AI 助手

AI-powered Sichuan Mahjong (川麻) advisor. Snap a photo of your tiles → get the best discard suggestion.

## Features
- 📸 **Photo Recognition** — Identify tiles from a photo of your hand
- 🎯 **Optimal Discard** — Analyze all options, recommend the best tile to discard
- 🟢🟡🔴 **Safety Rating** — Know which tiles are safe to discard
- 🀄 **Shanten Analysis** — Calculate how many tiles away from winning
- 🏆 **Winning Tiles** — Show which tiles complete your hand and how many remain

## Rules: Sichuan Mahjong (血战到底)
- Only **Dots (筒), Bamboo (条), Characters (万)** — 108 tiles total
- Each player holds **13 tiles**, draws to 14 then discards
- Win condition: 4 sets (sequences/triplets) + 1 pair
- Special hands: Seven Pairs, Dragon Seven Pairs, All One Suit, All Triplets
- **Blood Battle**: Game continues after someone wins until only one player remains
- **No Chow (吃)** — only Pong (碰), Kong (杠), and Win (胡)

## Workflow

### Step 1: Tile Recognition (Photo)
Send a photo → AI identifies:
1. **Hand tiles** (13 or 14)
2. **Discarded tiles** (river/pool)
3. **Melded tiles** (exposed sets)

Tile encoding:
- Characters (万): 1m 2m ... 9m
- Dots (筒): 1p 2p ... 9p
- Bamboo (条): 1s 2s ... 9s

Results are shown for user confirmation before analysis.

### Step 2: Run Analysis
```bash
python3 scripts/mahjong_analyze.py \
  --hand "1m,2m,3m,5m,5m,3p,4p,7p,8p,9p,2s,3s,4s,6s" \
  --discard "1p,2p,5p,5p,9s,9s" \
  --meld "6m,6m,6m"
```

Parameters:
- `--hand` / `-H`: Your hand tiles (required, 13 or 14 tiles)
- `--discard` / `-d`: Tiles already discarded on the table (optional)
- `--meld` / `-m`: Exposed melds — pong/kong (optional)

### Step 3: Output
- **14 tiles** → Recommended discard + safety rating 🟢🟡🔴 + waiting tile count
- **13 tiles** → Which tiles complete your hand + remaining count
- Safety is calculated from visible discards (more discards = safer; terminal tiles 1/9 = safer)

## Scoring (番数)
| Hand | Fan |
|------|-----|
| All One Suit (清一色) | 4 |
| Seven Pairs (七对) | 4 |
| Dragon Seven Pairs (龙七对) | 8 |
| All Triplets (对对胡) | 2 |

## References
- Detailed tile theory: `references/mahjong_theory.md`
