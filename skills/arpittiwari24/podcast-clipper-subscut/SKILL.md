---
name: generate-podcast-clips
description: Use this skill when the user wants to turn a long podcast, interview, webinar, or talking-head video into multiple short clips for TikTok, Reels, or YouTube Shorts. It wraps Subscut's podcast clipping API in a narrow CLI interface with explicit env requirements and predictable JSON output.
homepage: https://subscut.com/agents
metadata:
  version: 1.0.0
  clawdbot:
    emoji: "🎙️"
    requires:
      bins:
        - npm
      env:
        - SUBSCUT_API_KEY
        - SUBSCUT_API_BASE_URL
    config:
      requiredEnv:
        - SUBSCUT_API_KEY
      optionalEnv:
        - SUBSCUT_API_BASE_URL
      example: |
        export SUBSCUT_API_BASE_URL="https://subscut.com"
        export SUBSCUT_API_KEY="subscut_your_api_key"
    cliHelp: |
      npm run generate-podcast-clips -- --help
      Options:
        --video-url <url>       Public long-form video URL to process
        --max-clips <number>    Number of clips to generate (1-10, default 5)
        --clip-style <style>    viral | clean | minimal
        --captions <boolean>    true | false
        --api-key <token>       Overrides SUBSCUT_API_KEY
        --api-base-url <url>    Overrides SUBSCUT_API_BASE_URL
---

# Generate Podcast Clips

Use this skill to convert a long-form spoken video into multiple short clips through the Subscut `/podcast-to-clips` API.

## What This Skill Does

The skill is an opinionated wrapper around the API outcome:

- extracts up to 10 strong short clips from a long-form video
- favors viral and high-retention spoken moments
- adds captions
- returns titles, scores, and rendered clip URLs

Think in outcomes, not transport:

- Good framing: "Extract viral short-form content from this podcast"
- Bad framing: "Call some video API"

## When To Use

Use this skill when:

- the input is a long podcast, interview, webinar, or talking-head video
- the user wants growth, repurposing, shorts, reels, or TikTok content
- the user wants minimal manual editing

Avoid this skill when:

- the source is already short-form
- the content is mostly non-speech
- the user wants manual, frame-by-frame editing decisions

Do not use it as a generic video editing tool.

## Input Contract

Use this compact input shape when planning or explaining the tool call:

```json
{
  "video_url": "https://example.com/video.mp4",
  "max_clips": 5,
  "clip_style": "viral",
  "captions": true
}
```

`clip_style` maps to the API `style` field.

Recommended defaults:

- `max_clips`: `5`
- `clip_style`: `viral`
- `captions`: `true`

## Output Contract

Expect JSON in this shape:

```json
{
  "clips": [
    {
      "video_url": "https://...",
      "title": "Why Most Founders Get This Wrong",
      "score": 0.92
    }
  ]
}
```

## CLI Entry Point

Once the skill is installed, the agent runtime should invoke the bundled CLI wrapper:

```bash
npm --prefix .agents/skills/generate-podcast-clips run generate-podcast-clips -- \
  --video-url "https://example.com/podcast.mp4" \
  --max-clips 5 \
  --clip-style viral \
  --captions true
```

Required environment variables:

- `SUBSCUT_API_KEY` or `--api-key`

Default base URL:

- `https://subscut.com`

## Install Model

This skill is meant to be published once by Subscut and then installed by users
through the marketplace.

End-user flow:

1. Install the published skill from ClawHub / OpenClaw.
2. Set `SUBSCUT_API_KEY`.
3. Let the agent call the skill when it needs to turn a long-form spoken video
   into short clips.

The skill should not ask users to publish or package anything themselves.

## Agent Workflow

1. Confirm the source is a long-form spoken video.
2. Prefer the CLI wrapper over hand-written `curl`.
3. Keep the request simple unless the user asks for custom clip counts or style changes.
4. Return the resulting clip URLs, titles, and scores.
5. If the API fails, surface the status and response body clearly.
6. Keep a human in the loop before final publishing if the downstream workflow is public.

## Natural-Language Triggers

Likely user intents that should map to this skill:

- "Turn this podcast into reels"
- "Make shorts from this interview"
- "Repurpose my long video into clips"
- "Find the viral moments in this podcast"
- "Generate YouTube Shorts from this episode"

## Notes

- The API route is `POST /podcast-to-clips`.
- `clip_style` maps to the API `style` field.
- The script is executed through the skill-local `npm` script.
- The skill is intentionally opinionated and keeps the parameter surface small for better agent usage.
- This package is for installation and runtime usage, not for publisher-only deployment steps.
