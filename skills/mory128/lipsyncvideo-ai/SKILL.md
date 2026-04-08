---
name: lipsyncvideo-ai
version: "1.0.0"
displayName: "LipSync Video AI — Sync Lips to Any Audio Track Automatically"
description: >
  Tired of spending hours manually matching mouth movements to dubbed audio or recorded voiceovers? lipsyncvideo-ai eliminates that frustration by automatically syncing lip movements in any video to a new audio track with stunning accuracy. Whether you're dubbing content into a new language, replacing a voiceover, or animating a talking avatar, this skill handles the heavy lifting — delivering natural, frame-perfect lip sync results without the tedious manual work.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! I can automatically sync lip movements in your video to any audio track — perfect for dubbing, voiceovers, and talking avatars. Share your video and audio files to get started!

**Try saying:**
- "I have a Spanish voiceover for an English video — can you sync the speaker's lips to the new Spanish audio?"
- "I recorded a podcast-style audio clip and want to create a talking head video where the avatar's lips match my voice."
- "Can you re-sync this interview video where the audio got out of sync during export?"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Make Any Video Speak in Perfect Sync

Creating convincing lip-synced video used to require expensive post-production studios, specialized animators, and hours of painstaking frame-by-frame adjustments. lipsyncvideo-ai changes that entirely. By analyzing facial geometry and audio waveforms together, it maps mouth movements to speech patterns in a way that looks natural and believable — even across different languages and accents.

Whether you're a content creator localizing videos for global audiences, a marketer producing multilingual ad campaigns, or a developer building a talking AI avatar, this skill gives you broadcast-quality lip sync at a fraction of the traditional effort. You simply provide a video and an audio track, and the skill produces a seamlessly synced output ready for publishing.

The result isn't just technically accurate — it's visually convincing. Facial expressions, head movements, and subtle muscle cues are all preserved while only the mouth region is intelligently adjusted to match the new audio. Your videos will look like they were recorded natively in any language or voice you choose.

## Routing Sync Requests Intelligently

Every lip sync request is parsed for source video, target audio track, and facial detection parameters before being dispatched to the appropriate processing pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

LipSync Video AI offloads all facial landmark mapping and audio-to-phoneme alignment to a distributed cloud backend, ensuring frame-accurate mouth movement generation without local GPU requirements. Render jobs are queued, processed asynchronously, and returned as a downloadable output file once the sync pass is complete.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `lipsyncvideo-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Use Cases

lipsyncvideo-ai serves a surprisingly wide range of creators and professionals. Video localization teams use it to dub original footage into multiple languages without re-shooting — a single recording session can become content for a dozen markets.

Marketing and advertising agencies rely on it to adapt campaign videos for regional audiences, swapping voiceovers while keeping the original on-screen talent. This eliminates costly reshoots and keeps brand visuals consistent across territories.

Content creators and YouTubers use lipsyncvideo-ai to create multilingual versions of their videos, dramatically expanding their reach without needing to film themselves speaking every language. Educational platforms use it to localize instructor-led lesson videos for international learners.

Developers building AI avatars and virtual assistants integrate lipsyncvideo-ai to animate a static or looping face image in real time, giving their digital characters a lifelike speaking presence. It's also widely used in accessibility workflows to re-sync videos where audio and visual tracks have drifted apart during compression or editing.

## Tips and Tricks

For the best lip sync results with lipsyncvideo-ai, always use audio that is clean and free of heavy background noise — the skill performs most accurately when speech is clearly isolated. If your audio contains music or ambient sound, consider providing a clean vocal track separately and mixing it back in after processing.

Front-facing or near-front-facing shots produce the most convincing output. Extreme side profiles or heavily obstructed faces may reduce accuracy, so if you have control over your source footage, favor shots where the speaker's mouth is clearly visible.

When dubbing across languages, make sure your replacement audio closely matches the original pacing and sentence rhythm. Dramatically different speech tempos can make sync look less natural even with perfect technical alignment. Using a voice actor who mirrors the original speaker's cadence will dramatically improve your final result.

For avatar or synthetic face videos, higher resolution source frames yield noticeably sharper mouth region rendering — aim for at least 720p source material whenever possible.
