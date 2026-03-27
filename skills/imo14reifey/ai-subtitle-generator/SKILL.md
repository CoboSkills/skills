---
name: ai-subtitle-generator
version: "1.0.0"
displayName: "AI Subtitle Generator — Auto Generate Subtitles, Translate and Burn Captions into Video"
description: >
  Automatically generate subtitles for any video using AI speech recognition, translate them into 90+ languages, and burn them directly into the video or export as SRT and VTT files. NemoVideo transcribes spoken audio with 98% accuracy, syncs word-level timing, supports multiple speaker identification, offers animated caption styles from TikTok bold to Netflix minimal, and handles batch subtitle generation for entire video libraries — making every video accessible, searchable, and watchable on mute.
metadata: {"openclaw": {"emoji": "📝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Subtitle Generator — Auto Generate and Burn Subtitles into Video

Subtitles used to be a post-production afterthought — something added for accessibility compliance or foreign-language distribution. In 2026, subtitles are the primary text interface of video content. On TikTok, Instagram, YouTube Shorts, and LinkedIn, the majority of viewers watch with sound off. Search engines index subtitle text for video SEO. YouTube's algorithm uses auto-generated captions to understand video content for recommendations. Accessibility laws (ADA, EAA, WCAG 2.2) increasingly require captions on all published video. Subtitles are no longer optional for any of these reasons — and yet generating accurate, well-timed subtitles manually takes 5-10x the video duration (a 10-minute video requires 50-100 minutes of manual captioning). NemoVideo's AI subtitle generator reduces this to seconds: upload a video, receive word-level transcription with speaker identification, choose a caption style, and export — burned into the video for social media, or as SRT/VTT sidecar files for YouTube, LMS platforms, and web players. The subtitle pipeline handles the three things that make manual captioning painful: transcription accuracy (getting every word right), timing precision (syncing each word to the exact millisecond it's spoken), and styling consistency (maintaining readable formatting across the entire video regardless of background changes).

## Use Cases

1. **Social Media Captions — TikTok/Reels Style (15-90 sec)** — A creator posts daily short-form content. NemoVideo generates: word-by-word animated captions (each word highlights as spoken in yellow against white base text), bold sans-serif font at 48px, positioned in the bottom safe zone above platform UI, with automatic line breaks at natural phrase boundaries (not mid-sentence). The creator never manually captions again — every video ships with the professional animated subtitle style audiences expect.
2. **YouTube Full-Length Subtitles + Chapters (10-60 min)** — A YouTuber uploads a 25-minute video. NemoVideo generates: complete SRT file with 98%+ accuracy for YouTube's closed-caption system, auto-detected chapter markers with titles ("00:00 Intro, 02:15 Setup, 05:40 Main Topic...") for YouTube's chapter feature, and a highlighted-keyword clip of the most quotable 30 seconds (with burned captions, 9:16) for Shorts cross-promotion. Three deliverables from one upload.
3. **Multilingual Subtitle Translation (any length)** — A company's product demo video in English needs subtitles in Spanish, French, German, Portuguese, Japanese, and Korean. NemoVideo transcribes the English audio, then translates to all 6 target languages with timestamp preservation — each translated subtitle appears and disappears at the exact same moment as the English original, accounting for text-length differences across languages (German runs 30% longer than English; Japanese runs 20% shorter). Exports: 7 SRT files plus 7 burned-in versions.
4. **Podcast Video — Multi-Speaker Identification** — A three-person podcast publishes video episodes. NemoVideo identifies each speaker by voice fingerprint, assigns colors (Host: white, Guest 1: cyan, Guest 2: amber), and positions speaker labels ("Dr. Sarah Chen:") before each caption segment. The viewer always knows who is speaking — critical for podcast content where faces may not be on screen during every segment.
5. **Accessibility Compliance — Enterprise Video Library** — A university has 500 lecture recordings that need WCAG 2.1 AA-compliant captions for an accessibility audit. NemoVideo batch-processes the entire library: accurate transcription with proper punctuation and capitalization, speaker identification for lectures with Q&A, VTT export with positioning metadata for web players, and a compliance report documenting accuracy rates and any segments flagged for human review (proper nouns, technical terminology, accented speech).

## How It Works

### Step 1 — Upload Video
Provide any video with spoken audio. All major formats accepted. No duration limit — from 15-second Reels to 3-hour lectures.

### Step 2 — Configure Subtitles
Choose: language (or auto-detect), caption style, font, colors, position, translation targets, and output format (burned-in, SRT, VTT, or all).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-subtitle-generator",
    "prompt": "Generate subtitles for a 20-minute YouTube tutorial in English. Transcribe with word-level timing. Generate SRT for YouTube upload. Also create burned-in version with clean white sans-serif captions (42px) with dark semi-transparent background bar for readability. Detect chapter markers at topic transitions and output as YouTube chapter timestamps. Translate subtitles to Spanish and French — export as separate SRT files preserving original timing.",
    "source_language": "en",
    "translate_to": ["es", "fr"],
    "caption_style": "clean-bar",
    "font": "sans-serif",
    "font_size": 42,
    "color": "#FFFFFF",
    "background": "semi-transparent-dark",
    "burn_in": true,
    "srt_export": true,
    "chapter_detection": true,
    "format": "16:9"
  }'
```

### Step 4 — Review, Correct Proper Nouns, Export
Preview the transcription. NemoVideo flags low-confidence words (typically proper nouns and technical terms) for quick human review. Correct any errors, then export all deliverables.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the video and subtitle requirements |
| `source_language` | string | | Audio language or "auto-detect" (default) |
| `translate_to` | array | | Target languages: ["es", "fr", "de", "ja", "ko", "pt", "zh"] |
| `caption_style` | string | | "word-highlight", "clean-bar", "netflix-minimal", "tiktok-bold", "karaoke" |
| `font` | string | | "sans-serif", "bold-sans", "serif", "monospace", "handwritten" |
| `font_size` | integer | | Size in pixels (default: 42) |
| `color` | string | | Text color hex (default: "#FFFFFF") |
| `highlight_color` | string | | Word-highlight color (default: "#FBBF24") |
| `background` | string | | "none", "semi-transparent-dark", "solid-black", "blur" |
| `burn_in` | boolean | | Render subtitles into the video (default: true) |
| `srt_export` | boolean | | Export SRT sidecar file (default: true) |
| `vtt_export` | boolean | | Export VTT with positioning (default: false) |
| `speaker_labels` | boolean | | Identify and label speakers (default: auto-detect) |
| `chapter_detection` | boolean | | Detect topic changes as chapter markers (default: false) |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "asg-20260328-001",
  "status": "completed",
  "duration_seconds": 1205,
  "format": "mp4",
  "resolution": "1920x1080",
  "transcription": {
    "language": "en",
    "confidence": 0.982,
    "word_count": 3240,
    "segments": 285,
    "speakers_detected": 1,
    "low_confidence_words": 12
  },
  "outputs": {
    "burned_in_video": "tutorial-subtitled-en.mp4",
    "srt_english": "tutorial-en.srt",
    "srt_spanish": "tutorial-es.srt",
    "srt_french": "tutorial-fr.srt",
    "chapters": [
      {"title": "Introduction", "timestamp": "00:00"},
      {"title": "Setting Up the Environment", "timestamp": "02:18"},
      {"title": "Writing Your First Function", "timestamp": "06:45"},
      {"title": "Error Handling", "timestamp": "11:30"},
      {"title": "Testing and Debugging", "timestamp": "15:52"},
      {"title": "Summary and Next Steps", "timestamp": "18:40"}
    ]
  }
}
```

## Tips

1. **Word-level timing is what separates professional subtitles from amateur** — Per-sentence subtitles that appear all at once force the viewer to read ahead of the speaker. Word-level timing syncs reading speed to speaking speed — the viewer never waits and never rushes.
2. **Semi-transparent background bar ensures readability on any footage** — White text on bright footage is invisible. A dark bar behind the text guarantees contrast without blocking the video like a solid black bar would.
3. **Always export SRT alongside burned-in** — Burned-in looks better on social media. SRT lets YouTube and LinkedIn index the text for search and recommendations. Both formats serve different purposes; generate both.
4. **Translate after proofreading the source** — Fix transcription errors in the English source before translating. One error in English becomes one error in every target language.
5. **Chapter detection saves 15 minutes per YouTube upload** — Manually writing chapter timestamps is tedious and error-prone. NemoVideo detects topic shifts from the transcript and generates YouTube-formatted chapter timestamps automatically.

## Output Formats

| Format | Description | Use Case |
|--------|------------|----------|
| MP4 (burned-in) | Subtitles rendered into video | Social media direct upload |
| SRT | SubRip subtitle file | YouTube / LinkedIn / LMS |
| VTT | WebVTT with positioning | Web players / accessibility |
| JSON transcript | Full word-level transcript | Search indexing / blog post |
| TXT | Plain text transcript | Show notes / documentation |

## Related Skills

- [gaming-video-editor](/skills/gaming-video-editor) — Gaming content with captions
- [online-video-editor](/skills/online-video-editor) — Full online video editing
- [video-editor-ai](/skills/video-editor-ai) — AI-powered video editing
