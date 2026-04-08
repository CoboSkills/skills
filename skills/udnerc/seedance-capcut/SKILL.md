---
name: seedance-capcut
version: "1.0.0"
displayName: "Seedance CapCut AI — Generate, Edit & Animate Videos with Smart Prompts"
description: >
  Drop a video clip or a text idea and watch seedance-capcut turn it into a polished, dynamic edit in seconds. This skill bridges Seedance's AI video generation with CapCut's editing power — letting you animate scenes, apply trending effects, sync cuts to music, and craft reels ready for TikTok, Instagram, or YouTube Shorts. Built for creators, marketers, and social media teams who want studio-quality results without a timeline headache.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a video description, clip idea, or scene prompt and I'll generate a CapCut-ready Seedance edit for you. No footage? Just describe the vibe and I'll build it from scratch.

**Try saying:**
- "I have a 15-second product clip. Can you generate a Seedance animation overlay and suggest CapCut effects to make it look premium for Instagram Reels?"
- "Create a cinematic intro video using Seedance AI for my travel vlog — moody lighting, slow zoom, with a CapCut-style text reveal at the end."
- "I want to turn 5 static product photos into a 30-second TikTok ad using Seedance motion effects and CapCut beat-sync cuts. How do I set that up?"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Raw Footage to Viral-Ready in One Prompt

Seedance CapCut brings together two powerful creative engines — Seedance's AI-driven video generation and CapCut's intuitive editing toolkit — into a single, conversational workflow. Instead of juggling multiple apps, timelines, and export settings, you describe what you want and the skill handles the heavy lifting.

Whether you're animating a still image into a cinematic scene, remixing existing footage with AI-generated transitions, or building a brand video from scratch using only a text prompt, seedance-capcut interprets your creative intent and produces edit-ready output. You stay in control of the story while the AI manages pacing, effects, and visual coherence.

This skill is designed for content creators, small business owners, and social media managers who produce video regularly but don't have hours to spend in an editing suite. If you can describe a vibe, a product, or a scene — this skill can build it.

## Prompt Routing & Intent Mapping

Every request you send — whether it's a text-to-video generation, a motion prompt, or a clip edit — gets parsed for intent and routed to the matching Seedance or CapCut AI pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud API & Processing Backend

Seedance CapCut AI processes all generation and animation tasks through CapCut's cloud rendering infrastructure, meaning your video frames, keyframes, and motion data are handled server-side with no local compute required. Latency depends on model load and clip complexity, so longer timeline edits or high-resolution exports may queue briefly before returning a result.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-capcut`
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

## Quick Start Guide — Your First Seedance CapCut Edit

Step 1: Open Seedance and enter a text prompt describing your scene or upload a reference image. Choose your aspect ratio based on your target platform — 9:16 for TikTok/Reels, 16:9 for YouTube.

Step 2: Generate and download your Seedance clip. Review it for pacing and visual quality before moving to CapCut.

Step 3: Import the Seedance clip into CapCut. Add your music track, apply auto beat-sync, then layer in text overlays, transitions, and any brand assets using CapCut's template library.

Step 4: Use CapCut's AI enhance feature to sharpen the final output, then export at 1080p or 4K. Your seedance-capcut edit is now ready to publish directly from the CapCut app or download for scheduling.

## Troubleshooting Common Seedance CapCut Issues

If your Seedance-generated video looks choppy inside CapCut, it's usually a frame rate mismatch. Make sure both your generated clip and your CapCut project are set to the same FPS — 24fps for cinematic, 30fps for social content.

If AI-generated motion looks unnatural or 'floaty,' revisit your Seedance prompt and reduce motion intensity keywords like 'fast' or 'dynamic.' Subtle motion prompts like 'gentle drift' or 'slow parallax' tend to export more cleanly into CapCut's timeline.

CapCut sometimes strips color grading when you re-import an edited clip. To avoid this, flatten your Seedance clip with its effects before bringing it into a new CapCut project. Export as MP4 (H.264) at the highest quality setting to preserve the AI-rendered detail.

## Best Practices for Seedance CapCut Workflows

For the best results with seedance-capcut, start with a clear visual direction before prompting. Describe the mood, color tone, pacing, and intended platform — a TikTok edit needs different energy than a YouTube intro.

When using Seedance for AI-generated scenes, keep your text prompts specific. Instead of 'a nice outdoor scene,' try 'golden hour field with soft bokeh and slow camera drift.' The more cinematic your language, the more cinematic the output.

In CapCut, use the beat-sync feature after your Seedance clips are imported to automatically align cuts to your chosen track. This single step dramatically improves perceived production quality. Always export at 1080p minimum, and use CapCut's built-in noise reduction if your source audio was recorded on a phone.
