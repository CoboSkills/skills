#!/usr/bin/env bash

export SUBSCUT_API_BASE_URL="https://subscut.com"
export SUBSCUT_API_KEY="subscut_your_api_key"

npm --prefix .agents/skills/generate-podcast-clips run generate-podcast-clips -- \
  --video-url "https://example.com/podcast.mp4" \
  --max-clips 5 \
  --clip-style viral \
  --captions true
