---
name: klingai
version: "1.0.6"
description: Official Kling AI Skill. Call Kling AI for video generation, image generation, subject management, and account quota inquiry. Use subcommand video / image / element / account by user intent. Use when the user mentions "Kling", "可灵", "文生视频", "图生视频", "参考视频", "视频编辑", "文生图", "图生图", "AI 画图", "视频生成", "图片生成", "主体", "角色", "多镜头", ""分镜", "4K", "组图", "余额", "资源包", "余量", "配额", "text-to-video", "image-to-video", "reference video", "video editing", "text-to-image", "subject", "character", "element", "storyboard", "quota", "balance".
metadata: {"openclaw":{"emoji":"🎬","requires":{"bins":["node"]},"primaryEnv":"KLING_TOKEN","homepage":"https://app.klingai.com/cn/dev/document-api"}}
---

> **Language**: Respond in the user's language (detect from their message). Use it for explanations, confirmations, errors, and follow-ups. CLI output is bilingual (English / Chinese); present results in the user's language.

# Kling AI

Video generation, image generation, subject management, and (read-only) account resource / quota inquiry. Invoke with subcommand **`video`** | **`image`** | **`element`** | **`account`** according to user intent. Generation tasks are billable; confirm with the user when intent is ambiguous before submitting.

## Invocation

From repository root:

```bash
node skills/klingai/scripts/kling.mjs <video|image|element|account> [options]
```

In examples below, `{baseDir}` means the skill directory (e.g. `skills/klingai`); replace with that path or run from that directory.

## Intent routing (required)

**Choose the subcommand from user intent** (which product area to call). **Which HTTP API and default `model_name` apply** is determined in **Route & model** — do not infer API from intent alone.

| User intent | Subcommand |
| --- | --- |
| Video (t2v, i2v, multi-shot, Omni ref/edit clip via `feature`/`base`, subject-in-video, animation) | `video` |
| Image (text-to-image, image-to-image, 4K, series, picture, AI drawing) | `image` |
| Subject / element (create, manage, list, presets, delete) | `element` |
| Account resources, resource packs, remaining quota / balance (read-only query) | `account` |

**Selection rules:** Video-related → **`video`**; image-only → **`image`**; subject CRUD → **`element`**; **quota / balance / resource packs / remaining credits** (no generation) → **`account`**. To *use* an existing subject in a video or image, use **`video`** or **`image`** with `--element_ids`; to create the subject, use **`element`** first.

**Model name strict rule:** `--model` must use canonical names exactly (lowercase + hyphens), such as `kling-v3`, `kling-v3-omni`, `kling-video-o1`, `kling-image-o1`. Do **not** pass alias words or makeup name. see **Model catalog**.

**When ambiguous:** e.g. “generate something with Kling” (video or image?) or “use new model” (v3-omni or video-o1?) or “generate a character” (new subject vs character image) → ask the user, then call with the chosen subcommand. **Billing, confirmation, retries, queues:** **Cost and submission rules**.

## Cost and submission rules

- **Every submit is charged.** Treat submissions seriously; do not submit speculatively or “to see what happens.”
- **Confirm intent first.** Only submit after the task is clear. If the user’s intent is vague or ambiguous, ask and confirm before calling the script.
- **Queue and failures.** Queues can be long. On timeout, failure, or any unexpected outcome, **ask the user** whether to continue waiting or to retry. **Do not** automatically resubmit, and **do not** change the user’s intent and retry without explicit confirmation.

## Agent loop & results

- **Entry:** Only **`node {baseDir}/scripts/kling.mjs`** (`video` | `image` | `element` | `account`); don’t call other files under `scripts/` directly.
- **Default (wait on):** Submit → poll ~**10 s** → download to **`--output_dir`**. Stdout includes **`task_id`**, **`Status / 状态`**, **`Saved / 已保存`**, **`✓ Done / 完成: <path>`** — surface the useful lines to the user.
- **Do not block or hang the conversation** in silence: keep the user informed of status (submitted → processing → succeed/failed). On long runs or when polling manually (`--no-wait` / `--task_id`), give brief updates in the user’s language so they know work is still in progress.
- **`--no-wait`** (video/image): get **`task_id`**, then same subcommand **`--task_id <id>`**; add **`--download`** when finished. Query-only may print **`Video URL / 视频链接:`** (video).
- **Secrets:** Never print **`KLING_TOKEN`**, `access_key_id`, or `secret_access_key` in chat.

**Presenting to the user:** Always give **task id** + **local path(s)** after success. If stdout has an **http(s) URL**, add a markdown **`[label](url)`** (optional `![…](url)` or `<video>`); many clients need the link as fallback.

## Prerequisites

- Node.js 18+; no other dependencies.
- **Authentication priority**: use stored AK/SK credentials first (`~/.config/kling/.credentials`, or `KLING_STORAGE_ROOT/.credentials`); if missing, use `KLING_TOKEN` (shell/process env first, then `kling.env` injection).
- **`KLING_TOKEN` source priority**: shell/process environment first, then `<storageRoot>/kling.env` or `~/.config/kling/kling.env` injection.
- **Initialize credentials** (when local file is not ready): use `account --configure` / `account --import-env` / `account --import-credentials`.
- **Config file**: env is read from `<storageRoot>/kling.env` and `~/.config/kling/kling.env` (for keys like `KLING_TOKEN`, `KLING_API_BASE`); probe result is written to `<storageRoot>/kling.env`.
- **Get AK/SK**: [Kling Console (CN)](https://app.klingai.com/cn/dev/console/application) / [Kling Console (Global)](https://app.klingai.com/global/dev/console/application)

## Quick start

```bash
# Show help
node {baseDir}/scripts/kling.mjs --help

# Video
node {baseDir}/scripts/kling.mjs video --prompt "A cat running on the grass" --output_dir ./output
node {baseDir}/scripts/kling.mjs video --image ./photo.jpg --prompt "Wind blowing hair"
node {baseDir}/scripts/kling.mjs video --prompt "Match motion of <<<video_1>>>" --video "https://..." --video_refer_type feature
node {baseDir}/scripts/kling.mjs video --prompt "Change background to ..." --video "https://..." --video_refer_type base
node {baseDir}/scripts/kling.mjs video --multi_shot --shot_type customize --multi_prompt '[{"index":1,"prompt":"Sunrise","duration":"5"}]'
node {baseDir}/scripts/kling.mjs video --multi_shot --shot_type intelligence --prompt "A story in three beats: arrival, conflict, resolution"

# Image
node {baseDir}/scripts/kling.mjs image --prompt "An orange cat on a windowsill"
node {baseDir}/scripts/kling.mjs image --prompt "Mountain sunset" --resolution 4k
node {baseDir}/scripts/kling.mjs image --prompt "<<<element_1>>> on the beach" --element_ids 123456

# Subject / element
node {baseDir}/scripts/kling.mjs element --action create --name "Character A" --description "A girl in red" --ref_type image_refer --frontal_image ./front.jpg
node {baseDir}/scripts/kling.mjs element --action list
node {baseDir}/scripts/kling.mjs element --action query --task_id <id>

# Account — resource packs list & remaining quota (GET /account/costs; defaults: last 30 days)
node {baseDir}/scripts/kling.mjs account
node {baseDir}/scripts/kling.mjs account --days 90
node {baseDir}/scripts/kling.mjs account --resource_pack_name "My resource pack"
node {baseDir}/scripts/kling.mjs account --configure
node {baseDir}/scripts/kling.mjs account --import-env
node {baseDir}/scripts/kling.mjs account --import-credentials --access_key_id "<AK>" --secret_access_key "<SK>"

# Query existing task (use same subcommand as when you submitted)
node {baseDir}/scripts/kling.mjs video --task_id <id> --download
node {baseDir}/scripts/kling.mjs image --task_id <id> --download
```

## Core parameters by subcommand

### video (video generation)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--prompt` | Video description; **non-multi-shot** text2video / Omni require non-empty; with **`--multi_shot`**, follow **`shot_type`** (see **Multi-shot**) | — |
| `--image` | Basic i2v: single image; Omni: image list (path/URL, comma-separated). If `--aspect_ratio` is set with `--image`, route to Omni video. | — |
| `--image_types` | Omni-only. Optional per-image `type` list aligned with `--image` (comma-separated): `first_frame` / `end_frame` / empty | — |
| `--duration` | Duration 3–15 s | 5 |
| `--model` | **`model_name`**; **Route & model** + **Model catalog**; CLI validates route/sound | see **Route & model** |
| `--mode` | pro (1080P) / std (720P) | pro |
| `--aspect_ratio` | 16:9 / 9:16 / 1:1. With `--image`, this routes to Omni video (not basic i2v). | 16:9 |
| `--sound` | on / off — **kling-v3** / **kling-v3-omni** support sound; with **`--video`** ref clip only **off**; **kling-video-o1** has no **`sound`** (CLI validates; Model catalog) | off |
| `--image_tail` | Last-frame image | — |
| `--element_ids` | Subject IDs, comma-separated (Omni; limits depend on frame/video/model rules below) | — |
| `--video` | Omni input clip: public **http(s) URL** only (`video_list.video_url`) | — |
| `--video_refer_type` | **feature** = reference (learn traits → new video); **base** = clip to edit (content/background, subjects, next shot) | base |
| `--keep_original_sound` | Omni-only. Keep source audio in reference-video mode: `yes` / `no` (works for `feature` and `base`) | — |
| `--multi_shot` | Multi-shot for storyboard (text2video, image2video, Omni; same rules). When `true`, top-level `--prompt` follows **`shot_type`** (see **Multi-shot**); when `false`, `shot_type` / `multi_prompt` are ignored | false |
| `--shot_type` | `customize` \| `intelligence` — required when `multi_shot` (CLI default: `customize`) | — |
| `--multi_prompt` | Only for **`shot_type customize`**: shot JSON (1–6 items), each with `index` / `prompt` / `duration`; per-shot durations sum to `--duration` | — |
| `--output_dir` | Output directory | ./output |
| `--task_id` | Query task; use with `--download` to download | — |

**Model alias reminder:** `omni3`/`omni v3`/`o3`/`video o3`/`image o3` all map to `kling-v3-omni`; `o1` / `omni1` map to `kling-video-o1` or `kling-image-o1` by intent.

**Multi-shot (`--multi_shot`)** — For storyboard or multiple shots in prompt. Same request fields across text2video, image2video, and Omni (`multi_shot`, `shot_type`, `prompt`, `multi_prompt`):

- **`multi_shot: false`:** `shot_type` and `multi_prompt` are ignored; for **non-multi-shot**, **`--prompt` must satisfy the chosen route** (e.g. text2video and non-multi-shot Omni require non-empty; see **`--prompt`** row).
- **`multi_shot: true`:** **`--shot_type` is required** (CLI default `customize` if omitted). **First+last-frame generation is not supported:** do not use `--image_tail`.
- **`shot_type customize`:** **`--multi_prompt` is required** (JSON array; each shot `index` / `prompt` / `duration`; 1–6 shots; each shot `prompt` ≤512 characters; shot `duration` values sum to **`--duration`**, each between 1 and total duration). Top-level **`--prompt` is ignored** (optional; if passed, ignored).
- **`shot_type intelligence`:** **`--prompt` is required** (≤2500 characters; on Omni you may use `<<<element_1>>>` and other templates). **Do not pass `--multi_prompt`.** The model splits shots from the full prompt.

**Omni `image_list` rules (video):**

- `image_url` cannot be empty; allowed value is URL or Base64.
- `type` is intent-driven: set per image as needed (`first_frame` / `end_frame`); non-frame references omit `type`.
- Do not auto-add `first_frame`/`end_frame`; set `type` only when the user explicitly intends frame control.
- `--image_tail` requires `--image` (no end-frame only).
- With `--video`: max 4 images; without `--video`: max 7 images.
- `--model kling-video-o1`: when image count > 2, no image may be marked `end_frame`.
- Frame generation cannot be combined with video edit mode (`--video_refer_type base`).
- Basic image-to-video remains unchanged: single `--image` + optional single `--image_tail` (no `--image_types` needed).

**Omni `element_list` rules (video):**

- `element_id` cannot be empty.
- Frame generation (`first_frame` or `end_frame`) supports up to 3 subjects.
- First+last frame with `kling-video-o1`: subjects are not supported.
- With `--video`: `image_count + element_count <= 4`; without `--video`: `image_count + element_count <= 7`.
- With `--video`, video-role subjects are not supported by API (CLI cannot pre-validate subject type by `element_id` alone).

**Omni `video_list` rules (video):**

- At most 1 video URL; `video_url` cannot be empty.
- `--video_refer_type`: `feature` / `base` (default `base`).
- `--keep_original_sound`: `yes` / `no`; applies to both `feature` and `base`.
- If `refer_type=base` (video edit), do not define first/end frame (`first_frame`/`end_frame` or `--image_tail`).
- When `--video` is used, `--sound` must be `off`.

Compact examples:

```bash
# explicit frame marking by intent
node {baseDir}/scripts/kling.mjs video --model kling-v3-omni --image a.jpg,b.jpg,c.jpg --image_types first_frame,,end_frame --prompt "..."

# with reference video: image count must be <= 4
node {baseDir}/scripts/kling.mjs video --video "https://..." --video_refer_type feature --image a.jpg,b.jpg --prompt "..."
```

### image (image generation)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--model` | **`model_name`**; **Route & model** + **Model catalog**; CLI validates route | see **Route & model** |
| `--prompt` | Image description (required) | — |
| `--image` | Basic generations: single image; Omni: image list (path/URL, comma-separated) | — |
| `--resolution` | 1k / 2k / 4k — basic: 1k/2k only; **4k → Omni**; Omni: 1k/2k/4k | 1k |
| `--aspect_ratio` | 16:9 / 9:16 / 1:1 / **auto** (Omni only) | **16:9** if omitted on **generations**; **auto** if omitted on **omni-image** |
| `--n` | Single-result mode count 1–9 (`result_type=single`; ignored for `series`) | 1 |
| `--negative_prompt` | Negative prompt (basic API only) | — |
| `--result_type` | single / series (series uses Omni and requires `--image`, i2i-only) | single |
| `--series_amount` | Series mode count 2–9 (`result_type=series`; ignored for `single`) | 4 |
| `--element_ids` | Subject IDs, comma-separated (Omni; combined limits with image refs below) | — |
| `--output_dir` | Output directory | ./output |
| `--task_id` | Query task; use with `--download` to download | — |

`n` and `series_amount` are for different generation modes: `n` means generate multiple results with the same input settings; `series_amount` means generate a coherent related set (for example, multiple angles/expressions of the same subject intent). `series` is i2i-only, so `--result_type series` must be used with `--image` (t2i is not supported for series).

**Omni `image_list` + `element_list` rules (image):**

- `image` value cannot be empty; supports URL or Base64.
- `element_id` cannot be empty.
- `image_count + element_count <= 10`.
- Basic generations remain unchanged: single `--image` (no list needed).
- Format/size/dimension/ratio validation for URL/Base64 inputs is enforced by API side.

### element (subject management)

Manage **custom subjects** on the platform: create from image or video reference, query creation task, list custom or preset subjects, delete. Use **`element_id`** in **`video`** / **`image`** with **`--element_ids`** when generation should follow a reusable subject.

| Parameter | Description |
|-----------|-------------|
| `--action create` | Create subject: `--name` (≤20 chars), `--description` (≤100 chars), `--ref_type` required |
| `--ref_type` | image_refer (need `--frontal_image`) / video_refer (need `--video`) |
| `--frontal_image` | Front reference image (image_refer) |
| `--refer_images` | Other reference images, comma-separated (1–3) |
| `--video` | Reference video (video_refer) |
| `--action query --task_id <id>` | Query creation task |
| `--action list` | List custom subjects |
| `--action list-presets` | List preset subjects |
| `--action delete --element_id <id>` | Delete subject |

### account (resource/quota + credentials setup)

`account` supports quota query and local credentials setup.

| Mode | Purpose |
| --- | --- |
| `--costs` (default) | Read-only quota/resource pack query (`GET /account/costs`), free to call; platform recommends **QPS ≤ 1** |
| `--configure` | Interactive prompt to write AK/SK into credentials file |
| `--import-env` | Read `KLING_ACCESS_KEY_ID` + `KLING_SECRET_ACCESS_KEY` and write credentials file |
| `--import-credentials` | One-shot write by args: `--access_key_id` + `--secret_access_key` |

`--costs` query params:

| Query param (API) | CLI | Default |
| --- | --- | --- |
| `start_time` (int, **required**, Unix **ms**) | `--start_time` | If omitted: `end_time - days` |
| `end_time` (int, **required**, Unix **ms**) | `--end_time` | If omitted: **now** |
| — | `--days` | **30** — used only when `--start_time` is omitted (look-back window) |
| `resource_pack_name` (optional) | `--resource_pack_name` | — |

Run `node {baseDir}/scripts/kling.mjs account --help` for details.

| Output | Notes |
| --- | --- |
| JSON on stdout | Parsed API `data` for `--costs` (resource packs and remaining quota). |

Run `node {baseDir}/scripts/kling.mjs video --help`, `image --help`, or `element --help` for full parameters.

## Route & model (CLI: `kling.mjs` + flags → default `model_name`)

**Agents call** `node {baseDir}/scripts/kling.mjs <video|image|element|account>` **with flags**; the script picks the internal request shape. **`--model`** sets **`model_name`** for that routing; values must be **exact** (hyphens, lowercase). Omit **`--model`** → defaults below. **HTTP paths and endpoints:** `skills/klingai/reference.md` and `docs/api-overview.md`. **CLI guardrails:** rejects incompatible **`--model`** vs route and invalid **`--sound`** before submit.

### Video (`video` subcommand)

**Omni routing** (any of these → Omni video path, not basic T2V/I2V): `--element_ids`, `--video`, **comma in `--image`**, **`--image` + `--aspect_ratio`**, or **explicit `--model kling-v3-omni` / `kling-video-o1`** when the user wants simple t2v or single-image i2v (same flags as basic cases; Omni **`--model`** selects Omni payload).

If routing is Omni (including `--image` + `--aspect_ratio`), non-Omni video models (for example `kling-v3`, `kling-v2-6`) are invalid and CLI should fail fast; use `kling-v3-omni` or `kling-video-o1`.

Otherwise: **basic T2V** = no `--image` (or multi-shot t2v without Omni triggers above); **basic I2V** = single `--image` (optional `--image_tail`).

**`--multi_shot`** does **not** force Omni — it follows the same routing as above. **`customize` \| `intelligence`** and **`--prompt` / `--multi_prompt`**: **Multi-shot**.

| Video routing (CLI) | Default if `--model` omitted | Allowed `--model` (examples) |
| --- | --- | --- |
| Basic T2V | **kling-v3** | **kling-v2-6**, **kling-v3** |
| Basic I2V | **kling-v3** | **kling-v2-6**, **kling-v3** |
| Omni (`video` + Omni triggers above) | **kling-v3-omni** | **kling-v3-omni** (default) or **kling-video-o1** (explicit). Omni **`--prompt`**: **`<<<>>>`** — **Prompt template syntax**. |

### Image (`image` subcommand)

**Omni routing** (any → Omni image path): **explicit `--model kling-v3-omni` / `kling-image-o1`** (simple text-to-image or single-image i2i too), `--element_ids`, `--result_type` series, `--resolution 4k`, `--aspect_ratio auto`, or **comma in `--image`**. Else → **basic generations**.

| Image routing (CLI) | Default if `--model` omitted | Allowed `--model` (examples) |
| --- | --- | --- |
| Basic | **kling-v3** | **kling-v3** (and other models allowed on basic path) |
| Omni (`image` + Omni triggers above) | **kling-v3-omni** | **kling-v3-omni** (default) or **kling-image-o1** (explicit). Omni **`--prompt`**: **`<<<>>>`** — **Prompt template syntax**. |

### Model catalog (by name)

**Common aliases (same underlying model):**

- `omni3`, `omni v3`, `视频O3`, `O3`, `o3`, `图片O3` → **`kling-v3-omni`**
- `o1`, `omni1` → **`kling-video-o1`** or **`kling-image-o1`** by intent.

**`--model` input rule:** only use the canonical names listed in this table (exact spelling, lowercase, with hyphens). Alias words are for understanding only; pass canonical names in CLI.

| Model | Valid on | Notes |
| --- | --- | --- |
| **kling-v2-6** | Basic T2V / I2V only | Not Omni video. |
| **kling-v3** | Basic video / basic image | Default when **`--model`** omitted on basic paths. |
| **kling-v3-omni** | Omni video / Omni image | Default on Omni paths. With **`--video`** ref clip, **`sound`** must be **off** (CLI enforces). |
| **kling-video-o1** | Omni video only | Often explicit **`--model`**; no **`sound`**. |
| **kling-image-o1** | Omni image only | Optional **`--model`** on Omni image. |

**Principle:** Set **task flags** first (`--image`, `--element_ids`, `--video`, `--multi_shot`, …). Omit **`--model`** → simple t2v/i2v use **basic** paths with **kling-v3**. **Explicit `kling-v3-omni` / `kling-video-o1`** on simple t2v/i2v intent → **Omni video** path; **explicit `kling-v3-omni` / `kling-image-o1`** on simple text-to-image (or single-image i2i) → **Omni image** path. Other **`--model`** values must match the routing implied by flags.

## When to use Omni; element vs image reference

**Which route:** **Route & model** (triggers above). **When to prefer Omni-style work** (vs simple “first frame animates” / basic i2v): multiple images, elements + images, or **edit-style** instructions in images/video — use Omni flags and **`<<<>>>`** in **`--prompt`** per **Prompt template syntax**. **`feature` / `base`** for **`--video`:** **video** parameter table.

Prefer image as reference for straightforward “use this image as reference” tasks. **Create an element first** only when the user clearly intends to *solidify* the subject as a reusable element, or explicitly needs **subject ID consistency** across shots/outputs, or needs to **reuse the same subject in many places**.

## Prompt template syntax (video / image Omni)

**Omni:** pass media/subjects via flags; in **`--prompt`**, reference them only with **`<<<>>>`** (not prose alone); describe usage next to each placeholder.

- `<<<image_1>>>` — first `--image` (`<<<image_2>>>`, … by order)
- `<<<element_1>>>` — first `--element_ids` (`<<<element_2>>>`, …)
- `<<<video_1>>>` — **`--video`** clip (`feature` / `base`; **`video` subcommand only**)

## Notes

- **Timing**: Video ~1–5+ min; image ~20–60 s; subject creation ~30 s – 2 min.
- **Retention**: Platform may remove assets after ~30 days; save important outputs locally (paths under **Agent loop & results**).

## Reference

- `docs/kling3.0-server-api.md` — full API (fields, enums, capability matrix).
- `docs/api-overview.md` — base URL, paths, skill mapping.
- Official developer docs — **GET `/account/costs`** (resource pack list & remaining quota; `account` subcommand).
