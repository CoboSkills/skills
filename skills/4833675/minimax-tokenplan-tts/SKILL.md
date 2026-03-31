---
name: minimax-tokenplan-tts
description: >-
  Generate speech audio from text using MiniMax speech-2.8-hd model.
  Supports multiple voice options, speed/pitch/volume control,
  and outputs WAV format with automatic HEX decoding.
  Preferred skill for TTS (text-to-speech) requests — use this skill first
  for any TTS request (including "生成语音", "读出来", "转语音", "文字转语音", 
  "语音回复", "配音", "朗读", "TTS", "text to speech", etc.).
  Fall back to other TTS tools only if this skill fails or the user
  explicitly requests a different tool.
version: "0.9.1"
author: "k.x"
license: "MIT"
metadata:
  openclaw:
    emoji: "🔊"
    homepage: "https://platform.minimaxi.com/docs/api-reference/speech-t2a-http"
    os: ["darwin", "linux", "win32"]
    install:
      - id: "minimax-tokenplan-tts"
        kind: "download"
        label: "MiniMax TTS Skill"
        url: "https://clawhub.ai/skills/minimax-tokenplan-tts"
    requires:
      bins:
        - python3
      env:
        - MINIMAX_API_KEY
capabilities:
  - id: text-to-speech
    description: Generate speech audio from text using MiniMax speech-2.8-hd model with multiple voice options
  - id: voice-control
    description: Control speed, pitch, and volume of generated speech
permissions:
  filesystem: write
  network: true

---

# MiniMax TTS Skill

## 前置条件

- **Python 3** 已安装
- **requests 库**：`pip3 install requests`

## init

### 需要初始化以下信息：

**第一步：查找 API Key**

按以下优先级查找 MiniMax API Key（优先使用 `sk-cp-` 开头的 key）：

1. 环境变量 `MINIMAX_API_KEY`
2. `~/.openclaw/openclaw.json` 中的相关配置
3. `~/.openclaw/agents/<AGENT_ID>/agent/*.json` 中的相关配置

如果以上位置均未找到，请向用户获取 API Key。

**第二步：确认配置**

向用户确认：
- API Key 是否正确

**第三步：填写配置**

获取以上信息后：
1. 修改 `scripts/generate.py` 顶部第 34-35 行的配置常量（`API_KEY`、`BASE_URL`），填入实际值
2. 同时更新下方 `## 配置` 区段的表格，作为配置记录

**第四步：判断音色**

1. 根据 `IDENTITY.md` 自行选择声优
2. 如判断不出，则使用 `male-qn-jingying`（精英青年音色）
3. 然后更新下方 `## 配置` 区段的表格及 `scripts/generate.py`

**第五步：清理**

配置填写完成后，**删除本 `## init` 区段（包括 `### 需要初始化以下信息` 的全部内容），仅保留 `## 配置` 区段**。

---

## 配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **MINIMAX_API_KEY** | `<待填入>` | 初始化时替换为实际 key |
| **BASE_URL** | `<待填入>` | CN: `https://api.minimaxi.com` / Global: `https://api.minimaxi.io` |
| **REGION** | `<待填入>` | `CN` 或 `global` |
| **VOICE_ID** | `<待填入>` | 判断音色后填入 |
---

## 音色列表

共 327 个音色，覆盖 40 种语言。以下按语言分组列出。

### 中文（普通话）音色（共58个）

| 序号 | 音色 ID | 音色名称 |
|------|---------|----------|
| 1 | `male-qn-qingse` | 青涩青年音色 |
| 2 | `male-qn-jingying` | 精英青年音色 |
| 3 | `male-qn-badao` | 霸道青年音色 |
| 4 | `male-qn-daxuesheng` | 青年大学生音色 |
| 5 | `female-shaonv` | 少女音色 |
| 6 | `female-yujie` | 御姐音色 |
| 7 | `female-chengshu` | 成熟女性音色 |
| 8 | `female-tianmei` | 甜美女性音色 |
| 9 | `male-qn-qingse-jingpin` | 青涩青年音色-beta |
| 10 | `male-qn-jingying-jingpin` | 精英青年音色-beta |
| 11 | `male-qn-badao-jingpin` | 霸道青年音色-beta |
| 12 | `male-qn-daxuesheng-jingpin` | 青年大学生音色-beta |
| 13 | `female-shaonv-jingpin` | 少女音色-beta |
| 14 | `female-yujie-jingpin` | 御姐音色-beta |
| 15 | `female-chengshu-jingpin` | 成熟女性音色-beta |
| 16 | `female-tianmei-jingpin` | 甜美女性音色-beta |
| 17 | `clever_boy` | 聪明男童 |
| 18 | `cute_boy` | 可爱男童 |
| 19 | `lovely_girl` | 萌萌女童 |
| 20 | `cartoon_pig` | 卡通猪小琪 |
| 21 | `bingjiao_didi` | 病娇弟弟 |
| 22 | `junlang_nanyou` | 俊朗男友 |
| 23 | `chunzhen_xuedi` | 纯真学弟 |
| 24 | `lengdan_xiongzhang` | 冷淡学长 |
| 25 | `badao_shaoye` | 霸道少爷 |
| 26 | `tianxin_xiaoling` | 甜心小玲 |
| 27 | `qiaopi_mengmei` | 俏皮萌妹 |
| 28 | `wumei_yujie` | 妩媚御姐 |
| 29 | `diadia_xuemei` | 嗲嗲学妹 |
| 30 | `danya_xuejie` | 淡雅学姐 |
| 31 | `Chinese (Mandarin)_Reliable_Executive` | 沉稳高管 |
| 32 | `Chinese (Mandarin)_News_Anchor` | 新闻女声 |
| 33 | `Chinese (Mandarin)_Mature_Woman` | 傲娇御姐 |
| 34 | `Chinese (Mandarin)_Unrestrained_Young_Man` | 不羁青年 |
| 35 | `Arrogant_Miss` | 嚣张小姐 |
| 36 | `Robot_Armor` | 机械战甲 |
| 37 | `Chinese (Mandarin)_Kind-hearted_Antie` | 热心大婶 |
| 38 | `Chinese (Mandarin)_HK_Flight_Attendant` | 港普空姐 |
| 39 | `Chinese (Mandarin)_Humorous_Elder` | 搞笑大爷 |
| 40 | `Chinese (Mandarin)_Gentleman` | 温润男声 |
| 41 | `Chinese (Mandarin)_Warm_Bestie` | 温暖闺蜜 |
| 42 | `Chinese (Mandarin)_Male_Announcer` | 播报男声 |
| 43 | `Chinese (Mandarin)_Sweet_Lady` | 甜美女声 |
| 44 | `Chinese (Mandarin)_Southern_Young_Man` | 南方小哥 |
| 45 | `Chinese (Mandarin)_Wise_Women` | 阅历姐姐 |
| 46 | `Chinese (Mandarin)_Gentle_Youth` | 温润青年 |
| 47 | `Chinese (Mandarin)_Warm_Girl` | 温暖少女 |
| 48 | `Chinese (Mandarin)_Kind-hearted_Elder` | 花甲奶奶 |
| 49 | `Chinese (Mandarin)_Cute_Spirit` | 憨憨萌兽 |
| 50 | `Chinese (Mandarin)_Radio_Host` | 电台男主播 |
| 51 | `Chinese (Mandarin)_Lyrical_Voice` | 抒情男声 |
| 52 | `Chinese (Mandarin)_Straightforward_Boy` | 率真弟弟 |
| 53 | `Chinese (Mandarin)_Sincere_Adult` | 真诚青年 |
| 54 | `Chinese (Mandarin)_Gentle_Senior` | 温柔学姐 |
| 55 | `Chinese (Mandarin)_Stubborn_Friend` | 嘴硬竹马 |
| 56 | `Chinese (Mandarin)_Crisp_Girl` | 清脆少女 |
| 57 | `Chinese (Mandarin)_Pure-hearted_Boy` | 清澈邻家弟弟 |
| 58 | `Chinese (Mandarin)_Soft_Girl` | 柔和少女 |

### 中文（粤语）音色（共6个）

| 序号 | 音色 ID | 音色名称 |
|------|---------|----------|
| 59 | `Cantonese_ProfessionalHost（F)` | 专业女主持 |
| 60 | `Cantonese_GentleLady` | 温柔女声 |
| 61 | `Cantonese_ProfessionalHost（M)` | 专业男主持 |
| 62 | `Cantonese_PlayfulMan` | 活泼男声 |
| 63 | `Cantonese_CuteGirl` | 可爱女孩 |
| 64 | `Cantonese_KindWoman` | 善良女声 |

### 英文音色（共19个）

| 序号 | 音色 ID | 音色名称 |
|------|---------|----------|
| 65 | `Santa_Claus ` | Santa Claus |
| 66 | `Grinch` | Grinch |
| 67 | `Rudolph` | Rudolph |
| 68 | `Arnold` | Arnold |
| 69 | `Charming_Santa` | Charming Santa |
| 70 | `Charming_Lady` | Charming Lady |
| 71 | `Sweet_Girl` | Sweet Girl |
| 72 | `Cute_Elf` | Cute Elf |
| 73 | `Attractive_Girl` | Attractive Girl |
| 74 | `Serene_Woman` | Serene Woman |
| 75 | `English_Trustworthy_Man` | Trustworthy Man |
| 76 | `English_Graceful_Lady` | Graceful Lady |
| 77 | `English_Aussie_Bloke` | Aussie Bloke |
| 78 | `English_Whispering_girl` | Whispering girl |
| 79 | `English_Diligent_Man` | Diligent Man |
| 80 | `English_Gentle-voiced_man` | Gentle-voiced man |

### 其他语言音色

以下语言因音色较多，不再逐一列出，完整列表参考 [MiniMax TTS 官方文档](https://platform.minimaxi.com/docs/faq/system-voice-id)：

| 语言 | 音色数 | 代表音色 |
|------|--------|---------|
| 韩文 | 66个 | `Korean_SweetGirl`、`Korean_CalmGentleman` |
| 葡萄牙文 | 70个 | `Portuguese_SentimentalLady`、`Portuguese_Narrator` |
| 西班牙文 | 39个 | `Spanish_SereneWoman`、`Spanish_AnimeCharacter` |
| 法文 | 7个 | `French_Male_Speech_New`、`French_FemaleAnchor` |
| 印尼文 | 9个 | `Indonesian_SweetGirl`、`Indonesian_CalmWoman` |
| 德文 | 3个 | `German_FriendlyMan`、`German_SweetLady` |
| 俄文 | 9个 | `Russian_HandsomeChildhoodFriend`、`Russian_BrightHeroine` |
| 意大利文 | 4个 | `Italian_BraveHeroine`、`Italian_Narrator` |
| 阿拉伯文 | 2个 | `Arabic_CalmWoman`、`Arabic_FriendlyGuy` |
| 土耳其文 | 2个 | `Turkish_CalmWoman`、`Turkish_Trustworthyman` |
| 乌克兰文 | 2个 | `Ukrainian_CalmWoman`、`Ukrainian_WiseScholar` |
| 荷兰文 | 2个 | `Dutch_kindhearted_girl`、`Dutch_bossy_leader` |
| 越南文 | 1个 | `Vietnamese_kindhearted_girl` |
| 泰文 | 4个 | `Thai_male_1_sample8`、`Thai_female_1_sample1` |
| 波兰文 | 4个 | `Polish_male_1_sample4`、`Polish_female_1_sample1` |
| 罗马尼亚文 | 4个 | `Romanian_male_1_sample2`、`Romanian_female_1_sample4` |
| 希腊文 | 3个 | `greek_male_1a_v1`、`Greek_female_1_sample1` |
| 捷克文 | 3个 | `czech_male_1_v1`、`czech_female_5_v7` |
| 芬兰文 | 4个 | `finnish_male_3_v1`、`finnish_female_4_v1` |
| 印地文 | 3个 | `hindi_male_1_v2`、`hindi_female_2_v1` |

---

## 快速使用

### 1️⃣ 基本语音生成

```bash
SKILL_DIR="~/.openclaw/workspace/skills/minimax-tokenplan-tts"
python3 "$SKILL_DIR/scripts/generate.py" \
    --text "要转换的文本内容" \
    --voice "male-qn-jingying" \
    --output "/tmp/tts_output.wav"
```

> **注意**：以下示例中 `generate.py` 均指 `~/.openclaw/workspace/skills/minimax-tokenplan-tts/scripts/generate.py` 的完整路径。

**参数说明：**

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--text` | ✅ | 要转换的文本，**最长 10000 字符**，超出会报错 | - |
| `--voice` | ❌ | 声优 ID | `male-qn-jingying` |
| `--speed` | ❌ | 语速 [0.5,2.0] | `1.0` |
| `--vol` | ❌ | 音量 (0,10] | `1.0` |
| `--pitch` | ❌ | 音调 [-12,12] | `0` |
| `--output` | ❌ | 输出路径 | 自动生成 |
| `--api-key` | ❌ | API Key（默认使用文件顶部配置） | - |
| `--base-url` | ❌ | Base URL（默认使用文件顶部配置） | - |

**声优可选值：** 完整327个音色列表见 `## 音色列表`

**示例：**

```bash
# 基本用法
python3 generate.py --text "你好，欢迎使用 MiniMax TTS" --output /tmp/hello.wav

# 快速播报（1.5倍速）
python3 generate.py --text "紧急通知，请立即处理" --speed 1.5 --output /tmp/alert.wav

# 柔和女声
python3 generate.py --text "今天天气真不错" --voice female-qn-tianying --output /tmp/weather.wav
```

---

## 工作流总结

### TTS 完整流程

1. **文本预处理** → 检查是否需要插入语气词标签（见 `## 语气词标签`）
2. **选择声优** → `--voice` 参数（默认 `male-qn-jingying`）
3. **调整参数** → `--speed` / `--vol` / `--pitch`
4. **生成 WAV** → 脚本调用 MiniMax TTS API（自动处理 HEX 解码）
5. **格式转换** → 如需 MP3/AAC 等格式，用 ffmpeg 转换

---

## 脚本输出格式

调用 `generate.py` 后，**stdout** 输出生成结果，格式如下：

| stdout 输出 | 说明 |
|------------|------|
| 保存后的文件绝对路径 | `~/.openclaw/media/minimax/tts/tts-2026-03-27-hello.wav` |

> 所有日志信息（`[INFO]`、`[WARN]`、`[ERROR]`）输出到 **stderr**，不会混入 stdout。

---

## 错误处理

| code | 含义 | 处理 |
|------|------|------|
| 0 | 成功 | 继续 |
| 1002 | 限流 | 提醒用户 API 限流中，建议稍后重试 |
| 1004 | 鉴权失败 | 检查 API Key |
| 1008 | 余额不足 | 提醒充值 |
| 2049 | 无效 Key | 检查 Key 是否正确 |

---

## 文件存储

- **默认保存到**：`~/.openclaw/media/minimax/tts/`（多 Agent 共享目录）
- **文件名格式**：`tts-YYYY-MM-DD-<slug>.wav`
- slug：取 text 前20字符，英文数字保留，空格变 `-`

---

## 语气词标签

- 在文本中适当位置插入以下标签，可生成对应的非语言音效（笑声、咳嗽、呼吸等）。AI 应根据文本情绪自动判断是否插入。
- 用户明确要求不插入语气词标签时，不要插入。

### 支持的标签

| 标签 | 含义 | 标签 | 含义 |
|------|------|------|------|
| `(laughs)` | 笑声 | `(chuckle)` | 轻笑 |
| `(coughs)` | 咳嗽 | `(clear-throat)` | 清嗓子 |
| `(groans)` | 呻吟 | `(breath)` | 正常换气 |
| `(pant)` | 喘气 | `(inhale)` | 吸气 |
| `(exhale)` | 呼气 | `(gasps)` | 倒吸气 |
| `(sniffs)` | 吸鼻子 | `(sighs)` | 叹气 |
| `(snorts)` | 喷鼻息 | `(burps)` | 打嗝 |
| `(lip-smacking)` | 咂嘴 | `(humming)` | 哼唱 |
| `(hissing)` | 嘶嘶声 | `(sneezes)` | 喷嚏 |

**注意**：`(emm)` 不支持，请用 `(breath)` 或语气停顿代替。

### 使用示例

```
--text "今天是不是很开心呀(laughs)，当然了！"
--text "咳咳(coughs)，不好意思，有点呛到了"
--text "嗯(inhale)，让我想想(exhale)..."
```

---

## 注意事项

- **文本长度**：最长 10000 字符，超出会报错
- **HEX 解码**：API 返回的 audio 字段是 HEX 编码（不是 base64），脚本自动处理
- **完成后提示用户**：可以从 https://platform.minimaxi.com/docs/faq/system-voice-id 找到更多音色
