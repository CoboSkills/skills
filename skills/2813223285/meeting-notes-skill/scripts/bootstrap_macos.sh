#!/usr/bin/env bash
set -euo pipefail

MODE="all"      # all|asr|tts
WITH_WHISPER=0
for arg in "$@"; do
  case "$arg" in
    --mode=asr) MODE="asr" ;;
    --mode=tts) MODE="tts" ;;
    --mode=all) MODE="all" ;;
    --with-whisper) WITH_WHISPER=1 ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "[ERROR] bootstrap_macos.sh is for macOS only."
  exit 1
fi

echo "meeting-notes-skill bootstrap (macOS) mode=$MODE"
echo

if ! command -v brew >/dev/null 2>&1; then
  echo "[ERROR] Homebrew not found. Install brew first: https://brew.sh"
  exit 1
fi

if [[ "$MODE" == "all" || "$MODE" == "asr" || "$MODE" == "tts" ]] && ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[ACTION] Installing ffmpeg (required for m4a/mp3/aac/mp4 ASR)..."
  if ! brew install ffmpeg; then
    echo
    echo "[WARN] brew install ffmpeg failed."
    echo "If you see permission errors, run:"
    echo "  sudo chown -R \"$(whoami)\" /opt/homebrew/share/pwsh"
    echo "Then rerun:"
    echo "  brew install ffmpeg"
    exit 2
  fi
else
  echo "[OK] ffmpeg already installed."
fi

if [[ "$MODE" == "all" || "$MODE" == "tts" ]]; then
  if ! python3 -c "import edge_tts" >/dev/null 2>&1; then
    echo "[ACTION] Installing edge-tts..."
    python3 -m pip install edge-tts || {
      echo "[WARN] edge-tts install failed. You can retry manually:"
      echo "  python3 -m pip install edge-tts"
    }
  else
    echo "[OK] edge-tts already installed."
  fi
fi

if [[ "$WITH_WHISPER" -eq 1 ]] && [[ "$MODE" == "all" || "$MODE" == "asr" ]]; then
  if ! python3 -c "import whisper" >/dev/null 2>&1; then
    echo "[ACTION] Installing whisper (optional local ASR enhancement)..."
    python3 -m pip install openai-whisper || {
      echo "[WARN] whisper install failed. You can retry manually:"
      echo "  python3 -m pip install openai-whisper"
    }
  else
    echo "[OK] whisper already installed."
  fi
fi

echo
echo "[NEXT] Run health check:"
echo "  bash scripts/doctor.sh --strict"
