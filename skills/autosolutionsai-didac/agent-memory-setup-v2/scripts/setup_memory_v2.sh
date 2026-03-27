#!/usr/bin/env bash
# setup_memory_v2.sh — Initialize the full memory system with Gemini Embeddings 2
# Usage: bash setup_memory_v2.sh [workspace_dir]
#
# Creates directory structure, initializes memory files, installs plugins,
# and configures openclaw.json for the 3-tier memory system with Google Gemini embeddings.

set -euo pipefail

WORKSPACE="${1:-$(pwd)}"
TODAY=$(date +%Y-%m-%d)

echo "═══════════════════════════════════════════════"
echo "  OpenClaw Agent Memory System v2"
echo "  (Gemini Embeddings 2 — Semantic Search)"
echo "═══════════════════════════════════════════════"
echo ""
echo "Workspace: $WORKSPACE"
echo ""

# ── Step 1: Create directory structure ──
echo "→ Creating memory directories..."
mkdir -p "$WORKSPACE/memory/hot"
mkdir -p "$WORKSPACE/memory/warm"
echo "  ✓ memory/, memory/hot/, memory/warm/"

# ── Step 2: Initialize memory files ──
echo "→ Initializing memory files..."

if [ ! -f "$WORKSPACE/memory/hot/HOT_MEMORY.md" ]; then
  cat > "$WORKSPACE/memory/hot/HOT_MEMORY.md" << 'EOF'
# 🔥 HOT MEMORY — Active Session State

_Current task, pending actions, temporary context. Updated frequently, pruned aggressively._
EOF
  echo "  ✓ memory/hot/HOT_MEMORY.md"
else
  echo "  · memory/hot/HOT_MEMORY.md (already exists, skipped)"
fi

if [ ! -f "$WORKSPACE/memory/warm/WARM_MEMORY.md" ]; then
  cat > "$WORKSPACE/memory/warm/WARM_MEMORY.md" << 'EOF'
# 🌡️ WARM MEMORY — Stable Config & Preferences

_User preferences, team roster, API references, critical gotchas. Updated when things change._
EOF
  echo "  ✓ memory/warm/WARM_MEMORY.md"
else
  echo "  · memory/warm/WARM_MEMORY.md (already exists, skipped)"
fi

if [ ! -f "$WORKSPACE/MEMORY.md" ]; then
  cat > "$WORKSPACE/MEMORY.md" << EOF
# MEMORY.md — Long-Term Memory

_Created: ${TODAY}_

## Notes
- Agent workspace initialized on ${TODAY}
- Memory system v2 with Gemini Embeddings 2
EOF
  echo "  ✓ MEMORY.md"
else
  echo "  · MEMORY.md (already exists, skipped)"
fi

if [ ! -f "$WORKSPACE/memory/$TODAY.md" ]; then
  cat > "$WORKSPACE/memory/$TODAY.md" << EOF
# $TODAY

- Workspace initialized. Memory system v2 set up (Gemini Embeddings 2).
EOF
  echo "  ✓ memory/$TODAY.md"
else
  echo "  · memory/$TODAY.md (already exists, skipped)"
fi

if [ ! -f "$WORKSPACE/memory/heartbeat-state.json" ]; then
  cat > "$WORKSPACE/memory/heartbeat-state.json" << 'EOF'
{
  "lastChecks": {
    "email": null,
    "calendar": null
  }
}
EOF
  echo "  ✓ memory/heartbeat-state.json"
else
  echo "  · memory/heartbeat-state.json (already exists, skipped)"
fi

# ── Step 3: Check Gemini API key ──
echo ""
echo "→ Checking for Gemini API key..."
if [ -n "${GEMINI_API_KEY:-}" ]; then
  echo "  ✓ GEMINI_API_KEY found in environment"
elif command -v openclaw &>/dev/null && openclaw config get agents.defaults.memorySearch 2>/dev/null | grep -q "gemini"; then
  echo "  ✓ Gemini configured in openclaw.json"
else
  echo "  ⚠ No GEMINI_API_KEY found."
  echo ""
  echo "  To use Gemini Embeddings 2, you need a Gemini API key:"
  echo "    1. Get one free at https://aistudio.google.com/apikey"
  echo "    2. Set it as environment variable: export GEMINI_API_KEY=your-key"
  echo "    3. Or add it to openclaw.json under models.providers.google.apiKey"
fi

# ── Step 4: Install Lossless Claw plugin ──
echo ""
echo "→ Checking Lossless Claw plugin..."
if command -v openclaw &>/dev/null; then
  if openclaw plugins list 2>/dev/null | grep -q "lossless-claw"; then
    echo "  ✓ Lossless Claw already installed"
  else
    echo "  Installing @martian-engineering/lossless-claw..."
    openclaw plugins install @martian-engineering/lossless-claw && echo "  ✓ Installed" || echo "  ⚠ Install failed — run manually: openclaw plugins install @martian-engineering/lossless-claw"
  fi
else
  echo "  ⚠ openclaw CLI not found. Install Lossless Claw manually:"
  echo "    openclaw plugins install @martian-engineering/lossless-claw"
fi

# ── Step 5: Config reminder ──
echo ""
echo "═══════════════════════════════════════════════"
echo "  Manual config step required"
echo "═══════════════════════════════════════════════"
echo ""
echo "Add these to your openclaw.json under agents.defaults:"
echo ""
echo '  "memorySearch": { "provider": "gemini" },'
echo '  "compaction": { "mode": "safeguard" },'
echo '  "contextPruning": { "mode": "cache-ttl", "ttl": "1h" },'
echo '  "heartbeat": { "every": "1h" }'
echo ""
echo "And make sure your Gemini API key is available:"
echo "  Option A: export GEMINI_API_KEY=your-key"
echo "  Option B: add to openclaw.json → models.providers.google.apiKey"
echo ""
echo "Enable plugins:"
echo '  "lossless-claw": { "enabled": true }'
echo ""
echo "Then restart: openclaw gateway restart"
echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Memory system v2 setup complete!"
echo "═══════════════════════════════════════════════"
