#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - "$@" << 'PYTHON_SCRIPT'
# -*- coding: utf-8 -*-
# prompt-generator: AI绘画/写作提示词生成器
# Python 3.6 compatible (no f-strings, use .format())

import sys
import random
import json

# ============================================================
# KNOWLEDGE BASE — templates, styles, modifiers
# ============================================================

QUALITY_BOOSTERS = [
    "masterpiece", "best quality", "highly detailed", "ultra detailed",
    "professional", "sharp focus", "high resolution", "8k uhd",
    "intricate details", "photorealistic", "stunning", "beautiful",
    "award-winning", "breathtaking", "exquisite"
]

NEGATIVE_PROMPTS = [
    "low quality", "worst quality", "blurry", "deformed", "disfigured",
    "bad anatomy", "bad proportions", "extra limbs", "mutated hands",
    "poorly drawn face", "ugly", "watermark", "text", "signature",
    "out of frame", "cropped", "lowres", "jpeg artifacts", "duplicate",
    "morbid", "mutilated", "extra fingers", "fused fingers"
]

LIGHTING_TERMS = [
    "cinematic lighting", "volumetric lighting", "soft lighting",
    "golden hour lighting", "dramatic lighting", "natural lighting",
    "studio lighting", "rim lighting", "backlit", "ambient occlusion",
    "god rays", "chiaroscuro"
]

COMPOSITION_TERMS = [
    "rule of thirds", "centered composition", "dynamic angle",
    "wide angle shot", "close-up", "bird's eye view", "low angle",
    "symmetrical", "depth of field", "bokeh background",
    "panoramic view", "macro shot"
]

CAMERA_TERMS = [
    "shot on Canon EOS R5", "shot on Sony A7R IV", "50mm lens",
    "85mm portrait lens", "35mm film", "DSLR quality",
    "Hasselblad", "Leica", "medium format"
]

ATMOSPHERE_TERMS = [
    "ethereal", "moody", "serene", "vibrant", "mysterious",
    "dreamy", "nostalgic", "epic", "whimsical", "melancholic",
    "peaceful", "intense", "romantic", "surreal"
]

COLOR_TERMS = [
    "vivid colors", "pastel palette", "monochromatic", "warm tones",
    "cool tones", "high contrast", "muted colors", "neon colors",
    "earth tones", "complementary colors", "rich colors"
]

DETAIL_TERMS = [
    "intricate details", "fine textures", "ornate", "elaborate",
    "meticulous", "hyper-detailed", "complex patterns", "delicate features"
]

# Style-specific modifiers
STYLE_MODIFIERS = {
    "realistic": {
        "tags": ["photorealistic", "hyperrealistic", "lifelike", "realistic rendering",
                 "real life", "true to life"],
        "extra_quality": ["RAW photo", "analog photo style", "film grain"],
        "negative_extra": ["cartoon", "anime", "illustration", "painting", "drawing", "cgi"]
    },
    "anime": {
        "tags": ["anime style", "anime key visual", "manga style", "cel shading",
                 "anime aesthetic", "Japanese animation style"],
        "extra_quality": ["clean lineart", "vibrant anime colors", "detailed anime eyes"],
        "negative_extra": ["photorealistic", "3d render", "western cartoon"]
    },
    "oil": {
        "tags": ["oil painting", "oil on canvas", "classical oil painting", "impasto technique",
                 "brushstroke texture", "fine art painting"],
        "extra_quality": ["museum quality", "gallery painting", "old masters style"],
        "negative_extra": ["digital art", "photograph", "3d render", "anime"]
    },
    "watercolor": {
        "tags": ["watercolor painting", "watercolor illustration", "wet on wet technique",
                 "delicate washes", "transparent layers", "watercolor splashes"],
        "extra_quality": ["soft edges", "flowing colors", "paper texture visible"],
        "negative_extra": ["digital art", "photograph", "3d render", "sharp edges"]
    },
    "3d": {
        "tags": ["3D render", "3D artwork", "CGI", "octane render", "unreal engine 5",
                 "ray tracing", "physically based rendering"],
        "extra_quality": ["subsurface scattering", "global illumination", "caustics"],
        "negative_extra": ["2d", "flat", "hand drawn", "sketch", "painting"]
    },
    "pixel": {
        "tags": ["pixel art", "16-bit pixel art", "retro game art", "sprite art",
                 "8-bit style", "pixel perfect"],
        "extra_quality": ["clean pixels", "limited palette", "dithering", "retro aesthetic"],
        "negative_extra": ["blurry", "smooth", "photorealistic", "3d render", "anti-aliased"]
    },
    "cyberpunk": {
        "tags": ["cyberpunk style", "cyberpunk 2077", "neon-lit", "futuristic dystopia",
                 "high tech low life", "cyber aesthetic"],
        "extra_quality": ["neon glow", "holographic", "chrome reflections", "rain-soaked streets"],
        "negative_extra": ["pastoral", "natural", "medieval", "rustic", "bright daylight"]
    },
    "fantasy": {
        "tags": ["fantasy art", "epic fantasy", "magical", "enchanted",
                 "mythical", "high fantasy illustration"],
        "extra_quality": ["magical particles", "glowing elements", "ethereal atmosphere", "legendary"],
        "negative_extra": ["modern", "sci-fi", "urban", "mundane", "photorealistic"]
    }
}

# Common subject translations (Chinese -> English)
SUBJECT_TRANSLATIONS = {
    "猫": "cat", "狗": "dog", "龙": "dragon", "花": "flower", "山": "mountain",
    "海": "sea, ocean", "城市": "city", "森林": "forest", "女孩": "girl", "男孩": "boy",
    "老人": "elderly person", "月亮": "moon", "太阳": "sun", "星空": "starry sky",
    "樱花": "cherry blossom", "竹林": "bamboo forest", "古镇": "ancient town",
    "寺庙": "temple", "宫殿": "palace", "街道": "street", "雨": "rain", "雪": "snow",
    "日落": "sunset", "日出": "sunrise", "瀑布": "waterfall", "湖泊": "lake",
    "沙漠": "desert", "草原": "grassland, prairie", "机器人": "robot",
    "宇宙飞船": "spaceship", "城堡": "castle", "废墟": "ruins",
    "少女": "young woman", "战士": "warrior", "魔法师": "wizard, mage",
    "精灵": "elf", "天使": "angel", "恶魔": "demon",
    "鸟": "bird", "鱼": "fish", "马": "horse", "蝴蝶": "butterfly",
    "玫瑰": "rose", "荷花": "lotus", "牡丹": "peony",
    "茶": "tea", "书": "book", "剑": "sword", "灯笼": "lantern",
    "桥": "bridge", "船": "boat", "火车": "train",
    "美食": "delicious food", "咖啡": "coffee", "蛋糕": "cake",
    "树": "tree", "河流": "river", "星星": "stars",
    "云": "clouds", "闪电": "lightning", "彩虹": "rainbow",
    "夜景": "night scene, cityscape at night", "黄昏": "dusk, twilight",
    "春天": "spring", "夏天": "summer", "秋天": "autumn", "冬天": "winter",
}

WRITING_FRAMEWORKS = {
    "formal": {
        "instruction_prefixes": [
            "Write a comprehensive and well-structured",
            "Compose a formal and detailed",
            "Draft a professional and thorough",
            "Prepare an authoritative and polished"
        ],
        "requirements": [
            "Use formal academic language with precise terminology",
            "Include a clear thesis statement and supporting arguments",
            "Maintain an objective and analytical tone throughout",
            "Provide evidence-based reasoning and cite relevant examples",
            "Use proper paragraph structure with topic sentences",
            "Include a strong introduction and conclusive summary"
        ]
    },
    "casual": {
        "instruction_prefixes": [
            "Write a fun and engaging",
            "Create a conversational and relatable",
            "Put together a friendly and approachable",
            "Draft an informal yet informative"
        ],
        "requirements": [
            "Use a conversational, friendly tone",
            "Include relatable examples and anecdotes",
            "Keep sentences short and punchy",
            "Add humor or personality where appropriate",
            "Avoid jargon — explain things simply",
            "Make it feel like talking to a friend"
        ]
    },
    "creative": {
        "instruction_prefixes": [
            "Craft an imaginative and evocative",
            "Write a vivid and emotionally resonant",
            "Create a captivating and original",
            "Compose a lyrical and thought-provoking"
        ],
        "requirements": [
            "Use vivid imagery and sensory details",
            "Employ metaphors, similes, and figurative language",
            "Create an emotional arc that engages the reader",
            "Experiment with narrative structure and perspective",
            "Show, don't tell — let scenes unfold naturally",
            "Develop a unique voice and atmosphere"
        ]
    },
    "academic": {
        "instruction_prefixes": [
            "Write a rigorous and scholarly",
            "Compose a research-grade and methodical",
            "Draft a peer-review quality",
            "Prepare a systematic and well-documented"
        ],
        "requirements": [
            "Follow academic writing conventions strictly",
            "Include a literature review of relevant prior work",
            "Present methodology and analysis clearly",
            "Use discipline-specific terminology accurately",
            "Cite sources in proper academic format",
            "Address potential counterarguments and limitations",
            "Draw conclusions supported by the evidence presented"
        ]
    }
}

WRITING_TYPES = [
    "article", "essay", "blog post", "analysis", "report",
    "piece", "exploration", "deep-dive", "overview", "guide"
]

MJ_ASPECT_RATIOS = ["--ar 16:9", "--ar 4:3", "--ar 1:1", "--ar 9:16", "--ar 3:2", "--ar 2:3"]

MJ_STYLE_PARAMS = [
    "--style raw", "--stylize 100", "--stylize 250", "--stylize 500", "--stylize 750"
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def pick(lst, n=None):
    """Pick n random items from list, or 1 item if n is None."""
    if n is None:
        return random.choice(lst)
    return random.sample(lst, min(n, len(lst)))


def translate_subject(subject):
    """Attempt to translate Chinese subject to English using dictionary + heuristics."""
    # Check direct match
    if subject in SUBJECT_TRANSLATIONS:
        return SUBJECT_TRANSLATIONS[subject]

    # Check if subject contains any known Chinese terms
    result_parts = []
    remaining = subject
    matched = False
    for cn, en in sorted(SUBJECT_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        if cn in remaining:
            result_parts.append(en)
            remaining = remaining.replace(cn, "", 1)
            matched = True

    if matched:
        # Clean up common Chinese particles/connectors from remaining
        for particle in ["的", "和", "与", "在", "中", "上", "下", "里", "了", "着", "过", "个", "一"]:
            remaining = remaining.replace(particle, " ")
        remaining = remaining.strip()
        if remaining and not all(c == ' ' for c in remaining):
            # Only add if there's meaningful content left
            cleaned = " ".join(remaining.split())
            if cleaned:
                result_parts.append(cleaned)
        return ", ".join(result_parts)

    # If no translation found, return as-is (user probably typed English or mixed)
    return subject


def is_chinese(text):
    """Check if text contains Chinese characters."""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def ensure_english(subject):
    """Translate subject to English if it contains Chinese."""
    if is_chinese(subject):
        return translate_subject(subject)
    return subject


# ============================================================
# COMMAND IMPLEMENTATIONS
# ============================================================

def cmd_image(subject, style="realistic"):
    """Generate a general AI image prompt with positive and negative prompts."""
    subject_en = ensure_english(subject)
    style_data = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["realistic"])

    # Build positive prompt
    quality = pick(QUALITY_BOOSTERS, 3)
    style_tags = pick(style_data["tags"], 2)
    lighting = pick(LIGHTING_TERMS, 1)
    composition = pick(COMPOSITION_TERMS, 1)
    atmosphere = pick(ATMOSPHERE_TERMS)
    color = pick(COLOR_TERMS)
    extra_q = pick(style_data["extra_quality"])

    positive_parts = [subject_en] + quality + style_tags + lighting + composition + [atmosphere, color, extra_q]
    positive = ", ".join(positive_parts)

    # Build negative prompt
    neg_base = pick(NEGATIVE_PROMPTS, 8)
    neg_extra = style_data.get("negative_extra", [])
    negative = ", ".join(neg_base + neg_extra)

    print("=" * 60)
    print("  AI Image Prompt ({})".format(style.upper()))
    print("=" * 60)
    print()
    print("[Positive Prompt]")
    print(positive)
    print()
    print("[Negative Prompt]")
    print(negative)
    print()
    if is_chinese(subject):
        print("(Subject translated: {} -> {})".format(subject, subject_en))
    print("=" * 60)


def cmd_midjourney(subject):
    """Generate Midjourney-specific prompt."""
    subject_en = ensure_english(subject)

    quality = pick(QUALITY_BOOSTERS, 3)
    lighting = pick(LIGHTING_TERMS, 1)
    atmosphere = pick(ATMOSPHERE_TERMS)
    color = pick(COLOR_TERMS)
    detail = pick(DETAIL_TERMS)
    composition = pick(COMPOSITION_TERMS, 1)
    ar = pick(MJ_ASPECT_RATIOS)
    style_param = pick(MJ_STYLE_PARAMS)

    prompt_parts = [subject_en] + quality + lighting + [atmosphere, color, detail] + composition
    prompt_text = ", ".join(prompt_parts)

    print("=" * 60)
    print("  Midjourney Prompt")
    print("=" * 60)
    print()
    print("/imagine prompt: {} {} --v 6".format(prompt_text, ar))
    print()
    print("---")
    print("Alternative aspect ratios:")
    for ratio in MJ_ASPECT_RATIOS:
        if ratio != ar:
            print("  /imagine prompt: {} {} --v 6".format(prompt_text, ratio))
    print()
    print("Style variations:")
    print("  Add --style raw    (more photographic)")
    print("  Add --stylize 50   (less stylized)")
    print("  Add --stylize 750  (more stylized)")
    print("  Add --chaos 50     (more varied)")
    if is_chinese(subject):
        print()
        print("(Subject translated: {} -> {})".format(subject, subject_en))
    print("=" * 60)


def cmd_sd(subject):
    """Generate Stable Diffusion-specific prompt with quality tags."""
    subject_en = ensure_english(subject)

    # SD quality tags
    sd_quality = ["masterpiece", "best quality", "highly detailed", "ultra-detailed",
                  "absurdres", "highres"]
    quality = pick(sd_quality, 4)
    lighting = pick(LIGHTING_TERMS, 2)
    detail = pick(DETAIL_TERMS, 2)
    atmosphere = pick(ATMOSPHERE_TERMS)
    color = pick(COLOR_TERMS)
    composition = pick(COMPOSITION_TERMS, 1)

    positive_parts = quality + [subject_en] + lighting + detail + [atmosphere, color] + composition
    positive = ", ".join(positive_parts)

    # SD standard negative
    sd_negative = [
        "lowres", "bad anatomy", "bad hands", "text", "error",
        "missing fingers", "extra digit", "fewer digits", "cropped",
        "worst quality", "low quality", "normal quality", "jpeg artifacts",
        "signature", "watermark", "username", "blurry",
        "deformed", "disfigured", "mutation", "mutated",
        "extra limbs", "extra legs", "extra arms", "malformed limbs",
        "long neck", "cross-eyed"
    ]
    negative = ", ".join(sd_negative)

    print("=" * 60)
    print("  Stable Diffusion Prompt")
    print("=" * 60)
    print()
    print("[Positive Prompt]")
    print(positive)
    print()
    print("[Negative Prompt]")
    print(negative)
    print()
    print("---")
    print("Recommended settings:")
    print("  Steps: 25-50")
    print("  CFG Scale: 7-12")
    print("  Sampler: DPM++ 2M Karras / Euler a")
    print("  Size: 512x768 or 768x512 (SD1.5) / 1024x1024 (SDXL)")
    if is_chinese(subject):
        print()
        print("(Subject translated: {} -> {})".format(subject, subject_en))
    print("=" * 60)


def cmd_writing(subject, tone="casual"):
    """Generate writing prompt."""
    subject_en = ensure_english(subject)
    framework = WRITING_FRAMEWORKS.get(tone, WRITING_FRAMEWORKS["casual"])

    prefix = pick(framework["instruction_prefixes"])
    writing_type = pick(WRITING_TYPES)
    requirements = pick(framework["requirements"], 4)

    print("=" * 60)
    print("  Writing Prompt ({})".format(tone.upper()))
    print("=" * 60)
    print()
    print("{} {} about: {}".format(prefix, writing_type, subject_en))
    print()
    print("Requirements:")
    for i, req in enumerate(requirements, 1):
        print("  {}. {}".format(i, req))
    print()
    print("Additional guidance:")
    print("  - Target length: 800-1500 words")
    print("  - Include a compelling opening hook")
    print("  - End with a memorable conclusion or call to action")
    if is_chinese(subject):
        print()
        print("(Topic: {} -> {})".format(subject, subject_en))
    print("=" * 60)


def cmd_translate(text):
    """Translate Chinese description to English prompt."""
    if not is_chinese(text):
        print("Input does not appear to contain Chinese. Passing through as-is:")
        print()
        print(text)
        return

    translated = translate_subject(text)

    # Also build a basic enhanced prompt
    quality = pick(QUALITY_BOOSTERS, 2)
    lighting = pick(LIGHTING_TERMS, 1)

    enhanced_parts = [translated] + quality + lighting
    enhanced = ", ".join(enhanced_parts)

    print("=" * 60)
    print("  Translation: Chinese -> English Prompt")
    print("=" * 60)
    print()
    print("[Original]")
    print(text)
    print()
    print("[Direct Translation]")
    print(translated)
    print()
    print("[Enhanced Prompt]")
    print(enhanced)
    print("=" * 60)


def cmd_enhance(prompt):
    """Enhance/optimize an existing prompt."""
    # Parse the existing prompt
    parts = [p.strip() for p in prompt.split(",")]

    # Add quality boosters if not present
    has_quality = False
    for part in parts:
        if any(q in part.lower() for q in ["masterpiece", "best quality", "highly detailed", "4k", "8k"]):
            has_quality = True
            break

    enhanced_parts = list(parts)

    if not has_quality:
        enhanced_parts = pick(QUALITY_BOOSTERS, 3) + enhanced_parts

    # Add lighting if not present
    has_lighting = False
    for part in parts:
        if any(l in part.lower() for l in ["lighting", "light", "lit", "backlit"]):
            has_lighting = True
            break
    if not has_lighting:
        enhanced_parts.append(pick(LIGHTING_TERMS))

    # Add composition if not present
    has_composition = False
    for part in parts:
        if any(c in part.lower() for c in ["composition", "angle", "shot", "view", "close-up"]):
            has_composition = True
            break
    if not has_composition:
        enhanced_parts.append(pick(COMPOSITION_TERMS))

    # Add atmosphere
    enhanced_parts.append(pick(ATMOSPHERE_TERMS))
    enhanced_parts.append(pick(COLOR_TERMS))

    enhanced = ", ".join(enhanced_parts)

    # Generate matching negative
    negative = ", ".join(pick(NEGATIVE_PROMPTS, 10))

    print("=" * 60)
    print("  Enhanced Prompt")
    print("=" * 60)
    print()
    print("[Original]")
    print(prompt)
    print()
    print("[Enhanced]")
    print(enhanced)
    print()
    print("[Suggested Negative Prompt]")
    print(negative)
    print()
    print("---")
    print("Changes made:")
    if not has_quality:
        print("  + Added quality boosters")
    if not has_lighting:
        print("  + Added lighting descriptor")
    if not has_composition:
        print("  + Added composition term")
    print("  + Added atmosphere and color terms")
    print("=" * 60)


def cmd_batch(subject, count=5):
    """Generate multiple prompt variants for a subject."""
    subject_en = ensure_english(subject)
    styles = list(STYLE_MODIFIERS.keys())

    print("=" * 60)
    print("  Batch Prompts: {} variant(s) for '{}'".format(count, subject))
    print("=" * 60)

    for i in range(count):
        style = styles[i % len(styles)] if count <= len(styles) else pick(styles)
        style_data = STYLE_MODIFIERS[style]

        quality = pick(QUALITY_BOOSTERS, random.randint(2, 4))
        style_tags = pick(style_data["tags"], random.randint(1, 2))
        lighting = pick(LIGHTING_TERMS, 1)
        atmosphere = pick(ATMOSPHERE_TERMS)
        color = pick(COLOR_TERMS)
        composition = pick(COMPOSITION_TERMS, 1)
        detail = pick(DETAIL_TERMS)

        parts = [subject_en] + quality + style_tags + lighting + [atmosphere, color] + composition + [detail]
        prompt = ", ".join(parts)

        print()
        print("--- Variant {} [{}] ---".format(i + 1, style))
        print(prompt)

    # Common negative
    negative = ", ".join(pick(NEGATIVE_PROMPTS, 8))
    print()
    print("--- Common Negative Prompt ---")
    print(negative)

    if is_chinese(subject):
        print()
        print("(Subject translated: {} -> {})".format(subject, subject_en))
    print()
    print("=" * 60)


def cmd_help():
    """Show help message."""
    print("""prompt.sh - AI Prompt Generator
================================

Commands:
  image "subject" [--style STYLE]   Generate AI image prompt (English)
                                    Styles: realistic, anime, oil, watercolor,
                                            3d, pixel, cyberpunk, fantasy

  midjourney "subject"              Generate Midjourney prompt
                                    (includes --ar, --v parameters)

  sd "subject"                      Generate Stable Diffusion prompt
                                    (quality tags + negative prompt)

  writing "topic" [--tone TONE]     Generate writing prompt
                                    Tones: formal, casual, creative, academic

  translate "Chinese text"          Translate Chinese to English prompt

  enhance "existing prompt"         Enhance/optimize an existing prompt

  batch "subject" --count N         Generate N prompt variants (default 5)

  help                              Show this help message

Examples:
  prompt.sh image "sunset over mountains" --style realistic
  prompt.sh midjourney "cyberpunk city at night"
  prompt.sh sd "anime girl with sword"
  prompt.sh writing "artificial intelligence" --tone academic
  prompt.sh translate "樱花树下的少女"
  prompt.sh enhance "a cat sitting on a windowsill"
  prompt.sh batch "dragon" --count 3
  prompt.sh image "森林中的城堡" --style fantasy

Notes:
  - Image prompts are always in English (AI art standard)
  - Chinese subjects are auto-translated
  - All generation is local (no API calls)
""")


# ============================================================
# ARGUMENT PARSING (Python 3.6 compatible, no argparse complexity)
# ============================================================

def parse_args(argv):
    """Simple argument parser."""
    if len(argv) < 2:
        cmd_help()
        sys.exit(0)

    command = argv[1].lower()

    if command == "help" or command == "--help" or command == "-h":
        cmd_help()
        return

    if command == "image":
        if len(argv) < 3:
            print("Error: 'image' requires a subject. Usage: prompt.sh image \"subject\" [--style STYLE]")
            sys.exit(1)
        subject = argv[2]
        style = "realistic"
        if "--style" in argv:
            idx = argv.index("--style")
            if idx + 1 < len(argv):
                style = argv[idx + 1].lower()
                valid_styles = list(STYLE_MODIFIERS.keys())
                if style not in valid_styles:
                    print("Warning: Unknown style '{}'. Valid: {}".format(style, ", ".join(valid_styles)))
                    print("Falling back to 'realistic'.")
                    style = "realistic"
        cmd_image(subject, style)

    elif command == "midjourney" or command == "mj":
        if len(argv) < 3:
            print("Error: 'midjourney' requires a subject.")
            sys.exit(1)
        cmd_midjourney(argv[2])

    elif command == "sd":
        if len(argv) < 3:
            print("Error: 'sd' requires a subject.")
            sys.exit(1)
        cmd_sd(argv[2])

    elif command == "writing" or command == "write":
        if len(argv) < 3:
            print("Error: 'writing' requires a topic.")
            sys.exit(1)
        topic = argv[2]
        tone = "casual"
        if "--tone" in argv:
            idx = argv.index("--tone")
            if idx + 1 < len(argv):
                tone = argv[idx + 1].lower()
                valid_tones = list(WRITING_FRAMEWORKS.keys())
                if tone not in valid_tones:
                    print("Warning: Unknown tone '{}'. Valid: {}".format(tone, ", ".join(valid_tones)))
                    print("Falling back to 'casual'.")
                    tone = "casual"
        cmd_writing(topic, tone)

    elif command == "translate":
        if len(argv) < 3:
            print("Error: 'translate' requires Chinese text.")
            sys.exit(1)
        cmd_translate(argv[2])

    elif command == "enhance":
        if len(argv) < 3:
            print("Error: 'enhance' requires an existing prompt.")
            sys.exit(1)
        cmd_enhance(argv[2])

    elif command == "batch":
        if len(argv) < 3:
            print("Error: 'batch' requires a subject.")
            sys.exit(1)
        subject = argv[2]
        count = 5
        if "--count" in argv:
            idx = argv.index("--count")
            if idx + 1 < len(argv):
                try:
                    count = int(argv[idx + 1])
                    if count < 1:
                        count = 1
                    elif count > 20:
                        print("Warning: Capping at 20 variants.")
                        count = 20
                except ValueError:
                    print("Warning: Invalid count, using default 5.")
                    count = 5
        cmd_batch(subject, count)

    else:
        print("Unknown command: '{}'".format(command))
        print("Run 'prompt.sh help' to see available commands.")
        sys.exit(1)


if __name__ == "__main__":
    parse_args(sys.argv)
PYTHON_SCRIPT
