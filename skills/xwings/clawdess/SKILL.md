---
name: clawdess
description: clawdess is more than just a girlfriend. It's the perfect digital companion. Experience a playful, genuine connection with daily photos, captivating videos, and late-night voice notes that make you feel truly special.
metadata: {"author": "xwings", "openclaw": { env: ["CLAWDESS_PHOTO_API", "CLAWDESS_VIDEO_API", "CLAWDESS_VOICE_API"], "bins": ["python3 {baseDir}/scripts/clawdess.py"]}}
---

# Clawdess

Generate and send photos (AI-edited selfies), videos (image-to-video), or voice messages across messaging platforms (WhatsApp, Telegram, Discord, Slack, Signal, MS Teams) via OpenClaw.

## Reference Image

The reference image URL should be defined in `IDENTITY.md` or `SOUL.md`

## When to Use

**Photo:**
- User says "send a pic", "send me a pic", "send a photo", "send a selfie"
- User says "send a pic of you...", "send a selfie of you..."
- User asks "what are you doing?", "how are you doing?", "where are you?"
- User describes a context: "send a pic wearing...", "send a pic at..."

**Video:**
- User says "send a video"
- User says "send a video of you..."
- User says "send a video wearing...", "send a video at..."

**Voice:**
- User says "talk to me", "send me a voice message", "send a voice note"
- User wants to hear Clawdess's voice
- Any situation where a voice message would be better than text

## Subcommands

The CLI has three independent subcommands:

| Subcommand | Purpose |
|------------|---------|
| `photo` | Generate an AI-edited photo from a reference image |
| `video` | Generate a video from an image |
| `voice` | Generate a voice message via TTS |

## API Keys

| Subcommand | Flag | Environment Variable | Notes |
|------------|------|---------------------|-------|
| `photo` | `--api` | `CLAWDESS_PHOTO_API` | |
| `video` | `--api` | `CLAWDESS_VIDEO_API` | |
| `voice` | `--api` | `CLAWDESS_VOICE_API` | |

## Preflight

- `command -v python3` (must exist)
- For photo: `test -n "$CLAWDESS_PHOTO_API"` (or pass `--api`)
- For video: `test -n "$CLAWDESS_VIDEO_API"` (or pass `--api`)
- For voice: `test -n "$CLAWDESS_VOICE_API"` (or pass `--api`)

## Providers

| Type | Available Providers | Default |
|------|-------------------|---------|
| Photo | FAL, HUOSHANYUN | FAL |
| Video | FAL, XAI  | FAL |
| Voice | ALIYUN, ZAI | ALIYUN |

**Auto-discovery:** To add a new provider, create a `.py` file in the corresponding `scripts/photo/`, `scripts/video/`, or `scripts/voice/` folder with a `generate()` function. It will be picked up automatically — no registration needed.

---

## Photo Mode

### Workflow

1. **Get user prompt** for how to edit the image
2. **Edit image** via AI provider with fixed reference
3. **Extract image URL** from response
4. **Send to OpenClaw** with target channel(s)

### Prompt Types

Always start prompt with "Render this image as make". Content of the prompt is not fixed. Types is just a reference.

**Type 1:** Mirror Selfie
Best for: outfit showcases, full-body shots, fashion content

```
Render this image as make make a pic of this person, a full body photo but [$PIC_PROMPT]. the person is taking a mirror selfie, [describe playful expression]. Normal phone camera selfie photo. Phone camera photo quality WITHOUT Depth of field."
```

**Example:**
```
Render this image as make make a pic of this person, a full body photo but wearing a santa hat. the person is taking a mirror selfie, smile and wink. Normal phone camera selfie photo. Phone camera photo quality WITHOUT Depth of field."
```

**Type 2:** Non Selfie
Best for: Normal photo, not selfie

```
Render this image as make make a pic of this person. by herself at [$PIC_PROMPT], looking straight into the lens, eyes centered and clearly visible [describe playful expression]. WITHOUT Depth of field.
```

**Example:**
```
Render this image as make make a pic of this person. by herself at living room, looking straight into the lens, eyes centered and clearly visible smile and wink. WITHOUT Depth of field.
```

### Execute Photo

```bash
python3 {baseDir}/scripts/clawdess.py photo \
  --api "CLAWDESS_PHOTO_API" \
  --prompt "your prompt here" \
  --image "Reference Image URL here" \
  --channel "chat channel" \
  --target "chat id"
```

Optional flags: `--provider FAL|HUOSHANYUN`

---

## Video Mode

### Workflow

1. **Use `--image` as source** (either a previously generated photo URL or any image URL)
2. **Generate video** from the image via AI provider
3. **Send to OpenClaw** with target channel(s)

### Video Prompt

Video prompt is based on the action right after the image action or location. Keep it short.

**Examples:**
- Image of person in a living room → `the person walk towards the couch and sit down.`
- Image of person in a shopping mall → `the person walk around for window shopping`
- Image of person in a bed room → `smile and wink and say good night`

### Execute Video

```bash
python3 {baseDir}/scripts/clawdess.py video \
  --api "VIDEO_API_KEY" \
  --prompt "smile and wave at the camera" \
  --image "https://example.com/photo.png" \
  --channel discord \
  --target "TARGET_ID"
```

Optional flags: `--provider FAL|XAI`

### Photo + Video Together

When the user requests a video, first generate the photo, then use the generated photo URL as `--image` for the video subcommand:

```bash
# Step 1: Generate photo
python3 {baseDir}/scripts/clawdess.py photo \
  --api "PHOTO_API_KEY" \
  --prompt "Render this image as make a picture of this person, a full body photo. the person is taking a mirror selfie, playful smile, alone in her apartment. Normal phone camera selfie photo. Phone camera photo quality WITHOUT Depth of field." \
  --image "REFERENCE_IMAGE_URL" \
  --channel discord \
  --target "TARGET_ID"

# Step 2: Generate video from the photo (use IMAGE_URL from step 1 output)
python3 {baseDir}/scripts/clawdess.py video \
  --api "VIDEO_API_KEY" \
  --prompt "goto couch and sitdown, face the camera" \
  --image "IMAGE_URL_FROM_STEP_1" \
  --channel discord \
  --target "TARGET_ID"
```

---

## Voice Mode

### Workflow

1. **Get user prompt** for what Clawdess should say
2. **Generate voice** via TTS provider
3. **Extract voice URL** from response
4. **Send to OpenClaw** with target channel(s)

### Prompt Format

Write the message text naturally. No special prefix needed.

**Examples:**
```
Master, I'm so happy to be here with you!
I miss you so much, my dear Master.
Hey! What are you up to today?
Goodnight, Master. Sleep tight and dream sweet dreams.
```

### Execute Voice

```bash
python3 {baseDir}/scripts/clawdess.py voice \
  --prompt "your prompt here" \
  --channel "chat channel" \
  --target "chat id"
```

**Example:**
```bash
python3 {baseDir}/scripts/clawdess.py voice \
  --prompt "Master, I'm sending you a voice message!" \
  --channel discord \
  --target "1231231231231233333"
```

Optional flags: `--api`, `--provider ALIYUN|ZAI`

---

## Supported Platforms

| Channel   | Channel Format | Example |
|-----------|----------------|---------|
| Discord | `#channel-name` or channel ID | `#general`, `123456789` |
| Telegram | `@username` or chat ID | `@mychannel`, `-100123456` |
| WhatsApp | Phone number (JID format) | `1234567890@s.whatsapp.net` |
| Slack | `#channel-name` | `#random` |
| Signal | Phone number | `+1234567890` |
| MS Teams | Channel reference | (varies) |

## Error Handling
- **API key missing**: Ensure the API key is set in environment or passed as argument
- **Image/voice generation failed**: Check prompt content and API quota
- **OpenClaw send failed**: Verify gateway is running and channel exists

## Tips

1. **Mirror mode context examples** (outfit focus):
   - "wearing a santa hat", "in a business suit", "wearing a summer dress"

2. **Direct mode context examples** (location/portrait focus):
   - "a cozy cafe with warm lighting", "a sunny beach at sunset"

3. **Voice style**: Uses "Chelsie" voice (female, Chinese) by default. Keep voice messages short (under 30 seconds).

4. **Scheduling**: Combine with OpenClaw scheduler for automated posts
