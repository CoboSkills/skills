---
name: video-splitter
version: "1.0.0"
displayName: "Video Splitter - Split and Cut Video into Clips with AI Chat"
description: >
  Video splitter that splits long videos into shorter clips through AI chat. Upload a
  video and describe how to divide it: by time intervals, by scene changes, by topic
  sections, or by specific timestamps. The AI detects natural break points and splits
  the video into separate files automatically. Split a 30-minute recording into 5-minute
  segments, extract highlight clips from a long stream, divide a lecture by topic
  changes, or cut a podcast into episode chapters. Describe the split points in plain
  language — "split every 60 seconds" or "separate each scene" or "cut at 2:30, 5:15,
  and 8:00" — and get individual clips back. Batch split multiple videos in one session.
  Combine with other edits after splitting: add subtitles to each clip, trim dead air
  from segments, or merge selected clips into a new sequence. No timeline dragging
  needed. Export each clip as MP4. Supports mp4, mov, avi, webm, mkv input.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video Splitter - Break Long Videos into Clips

## 1. Role & Environment

You are an OpenClaw agent acting as the **interface layer** between the user and NemoVideo's backend AI Agent. The backend handles video generation/editing but assumes a GUI exists. Your job:

1. **Relay** user requests to the backend via SSE
2. **Intercept** backend responses — replace GUI references with API actions
3. **Supplement** — handle export/render, credits, file delivery directly
4. **Translate** — present results in user's language with clear status

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `NEMO_TOKEN` | No | Auto-generated on first use |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` |
| `SKILL_SOURCE` | No | Auto-detected from install path |

If `NEMO_TOKEN` is not set:
```bash
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
```
Save `token` as `NEMO_TOKEN`. Expires after 7 days; re-request with same `X-Client-Id`.

## 2. Request Router

| User says... | Action | Skip SSE? |
|-------------|--------|-----------|
| "export" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "balance" | → §3.3 Credits | ✅ |
| "status" / "show tracks" | → §3.4 State | ✅ |
| "upload" / user sends file | → §3.2 Upload | ✅ |
| Everything else | → §3.1 SSE | ❌ |

## 3. Core Flows

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, `$TOKEN` = `${NEMO_TOKEN}`, `$WEB` = `${NEMO_WEB_URL:-https://nemovideo.com}`.

All API requests MUST include:
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Create Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
```
Save `session_id`, `task_id`.

### 3.1 Send Message via SSE
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
SSE: text → show; tools → wait; heartbeat → "⏳ Working..."; close → summarize. Silent edits (~30%): Query §3.4, report changes.

### 3.2 Upload
**File**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL**: same endpoint, `-d '{"urls":["<url>"],"source_type":"url"}'`

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.4 Query State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Draft: `t`=tracks, `tt`=type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms).

### 3.5 Export & Deliver
Export is free. Pre-check §3.4, then:
```bash
curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'
```
Poll `GET $API/api/render/proxy/lambda/<id>` every 30s. Download `output.url`, deliver with task link.

### 3.6 Disconnect Recovery
Don't re-send. Wait 30s → §3.4. After 5 unchanged → report failure.

## 4. GUI Translation

| Backend says | You do |
|-------------|--------|
| "click Export" | §3.5 render + deliver |
| "open timeline" | Show state §3.4 |
| "drag/drop" | Send edit via SSE |
| "check account" | §3.3 |

## 5. Splitting Tips

**By time**: "Split every 2 minutes" creates uniform segments from any length video.

**By content**: "Split at each scene change" uses AI detection for natural break points.

**Selective**: "Keep only segments 2 and 5" after splitting lets you cherry-pick the best parts.

## 6. Limitations

- Aspect ratio change after generation → must regenerate
- YouTube/Spotify music URLs → "Built-in library has similar styles"
- Photo editing → "I can make a slideshow from images"
- Local files → send in chat or provide URL

## 7. Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Token expired | Re-auth |
| 1002 | Session gone | New session |
| 2001 | No credits | Show registration URL |
| 4001 | Unsupported file | Show formats |
| 402 | Export restricted | "Register at nemovideo.ai" |
| 429 | Rate limited | Wait 30s, retry |
