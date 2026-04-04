---
name: skill-atlas
version: "2.1.0"

# ── 元数据 ─────────────────────────────────────────────
# 标注优化版本，修复 always 标志和 registry 损坏字段
metadata:
  openclaw:
    always: false          # 修正：按需加载，非核心 always
    autonomous: true        # 允许心跳自主调用（受限，见 limits）
    invoke_scope: "user-confirmed"  # 安装/更新需用户确认

# ── 安装规范 ─────────────────────────────────────────────
# 安装类型：带脚本的技能包，非 instruction-only
install:
  type: skill-package
  version: "2.0.0"
  files:
    - scripts/skill_atlas.py      # 主管理工具（17 个命令）
    - scripts/skill-inspect.py    # 技能审视分析脚本
    - config/scenes.json          # 场景配置（首次运行时自动创建）
    - config/clawhub_skills.md    # ClawHub 热门技能数据库
    - config/daily/              # 每日报告目录
  external_dependencies:
    - skill: skill-vetter
      script: scripts/skill-vetter.py
      note: "安全审查脚本，install/update/cat-add 时强制调用"
  checks:
    - binary: clawhub
      note: "通过 PowerShell 调用，用于搜索/安装/更新技能"
    - binary: python
      note: "运行 skill_atlas.py、skill-inspect.py、skill-vetter.py"
    - binary: powershell
      note: "运行 clawhub CLI 和 PowerShell 脚本"
    - script: scripts/skill-vetter.py
      note: "安全审查脚本，install/update 时强制调用"
      required: true
      source: "skill-vetter 技能"
  steps:
    - copy: "复制包内文件到 WORKSPACE/skills/skill-atlas/"
    - check: "验证 skill-vetter 已安装，scripts/skill-vetter.py 存在"
    - check: "验证 scripts/skill-inspect.py 存在"
    - init: "首次调用时自动创建 config/daily/ 和初始化 scenes.json"
  verify:
    - command: "python WORKSPACE/scripts/skill-inspect.py"
      expect: "输出技能列表，无报错"

# ── 依赖声明 ─────────────────────────────────────────────
requires:
  binaries:
    - name: clawhub
      note: "通过 PowerShell 调用，用于搜索/安装/更新技能"
      required: true
    - name: python
      note: "运行 skill_atlas.py、skill-inspect.py、skill-vetter.py"
      required: true
    - name: powershell
      note: "运行 clawhub CLI 和 PowerShell 脚本"
      required: true
  scripts:
    - path: scripts/skill-vetter.py
      note: "安全审查脚本，install/update/cat-add 时强制调用"
      required: true
      source: "skill-vetter 技能"
    - path: scripts/skill-inspect.py
      note: "技能审视分析脚本"
      required: false
  env:
    - name: OPENCLAW_WORKSPACE
      default: "用户工作区根目录"
      note: "用于定位 skills/、scripts/、config/ 目录"

# ── 权限声明 ─────────────────────────────────────────────
permissions:
  workspace_read:
    - skills/*/SKILL.md
    - skills/*/config/scenes.json
    - skills/*/config/daily/*.md
    - skills/*/scripts/*.py
    - skills/*/scripts/*.ps1
  workspace_write:
    - skills/skill-atlas/config/scenes.json
    - skills/skill-atlas/config/daily/
  external:
    - name: clawhub install
      scope: "仅安装已审查的技能，更新前强制安全审查"
      mode: "interactive"
    - name: clawhub update
      scope: "仅更新已安装的技能，更新前强制安全审查"
      mode: "interactive"
    - name: clawhub search
      scope: "只读操作，不修改任何文件"
      mode: "read-only"
    - name: clawhub list
      scope: "只读操作，获取本地已安装技能列表"
      mode: "read-only"
    - name: clawhub inspect
      scope: "只读操作，获取远程技能元数据"
      mode: "read-only"

# ── 限制声明 ─────────────────────────────────────────────
limits:
  - "不读取 ~/.ssh、~/.aws、~/.config、~/.netrc 等敏感路径和凭据文件"
  - "不访问 MEMORY.md、USER.md、SOUL.md、IDENTITY.md 等身份文件"
  - "不发送凭据或敏感数据到外部服务器"
  - "clawhub install/update 仅影响 skills/ 目录，不修改系统文件"
  - "不执行未经安全审查的外部脚本（curl → 文件、eval、exec 等）"
  - "不请求提权/sudo，不修改 PATH 或系统环境变量"
  - "workspace_write 仅限于 skills/*/config/ 目录"
  - "Autonomous 模式（心跳）禁止执行安装/更新/分类修改，仅允许只读操作"
---

# 🧭 Skill Atlas · 技能图谱

> **让每一个技能各归其位，让每一次搜索有所依依。**

---

## ⚡ 核心功能一览

| 功能 | 说明 |
|------|------|
| 📦 **技能 Inventory** | 核心 / 常驻 / 本地，三层分类 |
| 🔍 **跨平台搜索** | CN / 全球同时搜，按相关性排序 |
| 🔒 **安装安全审查** | 每次安装/更新前必做，自动执行 skill-vetter |
| 📥 **按分类下载** | 选分类 → 检测缺失 → 安全审查 → 安装 |
| 🔔 **版本检测** | 每日检测，列出更新清单等你决定 |
| 📊 **每日报告** | 常驻技能 / 分类技能 / 可更新 / 待确认 |
| 🌟 **自动升降级** | 分类技能用够次数自动升常驻 |
| ⏰ **定时同步** | 每日 07:30 自动执行 |

---

## 🎯 快速上手

```
技能审视              → 查看已安装技能状态
搜索 [关键词]         → 跨平台搜索新技能
安装 [技能名]         → 安全审查后安装
全部更新              → 批量更新所有技能
探索 [分类名]         → 下载该分类下热门技能
备份                  → 生成 .skill_manifest.json
```

## 🔧 管理命令

| 命令 | 说明 |
|------|------|
| `搜索 [关键词]` | 跨平台搜索，优先 CN 镜像 |
| `安装 [技能名]` | 安全审查后安装 |
| `更新 [技能名]` | 安全审查后更新到最新 |
| `全部更新` | 批量安全审查后依次更新 |
| `技能审视` | 分析所有已安装技能 |
| `审查技能 [技能名]` | 手动触发独立审查 |
| `分类创建/启用/禁用` | 自定义分类管理 |
| `添加常驻 / 移除常驻` | 常驻层调整 |
| `当前场景` | 查看当前场景及推荐技能 |
| `查看每日报告` | 查看今日同步报告 |

---

## 🔒 安全审查

每次安装/更新前强制执行，审查等级由 `skill-vetter` 判定：

| 等级 | 行为 |
|------|------|
| 🟢 LOW | 直接安装 |
| 🟡 MEDIUM | 完整审查后安装，报告结果 |
| 🔴 HIGH | 阻止安装，需用户确认 |
| ⛔ EXTREME | 拒绝安装，记录原因 |

### 🚨 RED FLAGS（任何一条 → 直接拒绝）

```
🚫 拒绝安装 IF YOU SEE:
• curl/wget 到未知 URL
• 向外部服务器发送数据
• 请求凭证 / API Key
• 访问 ~/.ssh、~/.aws、~/.config
• 读取 MEMORY.md、USER.md、SOUL.md、IDENTITY.md
• base64 decode、eval()、exec()
• 修改 workspace 外系统文件
• 安装未声明的包
• 代码压缩/加密/混淆
• 请求 sudo/提升权限
```

### 审查输出格式

```
🔒 安全审查报告
═══════════════════════════════════════
Skill: [name]
Source: [ClawHub / GitHub / other]
Author: [username] · ⭐ [stars] · 📥 [downloads]
Version: [version] · Updated: [date]
───────────────────────────────────────
RED FLAGS: [None / 列表]

PERMISSIONS:
• Files: [列表]
• Network: [列表]
• Commands: [列表]
───────────────────────────────────────
RISK LEVEL: 🟢 LOW

VERDICT: ✅ 审查通过，安装中...
═══════════════════════════════════════
```

---

## 🏗️ 技能加载层级

| 层 | 说明 | 加载 |
|----|------|------|
| **核心层** | skill-atlas · proactive-agent · skill-vetter · self-improving | 每次会话必加载（always: true） |
| **常驻层** | 用户常用技能 | 每次会话加载 |
| **分类层** | 按需安装的技能 | 按需加载 |

> ⚠️ 核心层已移除 agent-memory（已卸载，embedding列为占位符无法真正使用）

---

## 🚀 首次启用

```
skill-atlas 初始化完成

  🧭 skill-atlas · 技能图谱
  ─────────────────────────────────────────
  42,000+ 技能 · 三大平台 · 每日自动同步

  三大来源：
  🌐 ClawHub（clawhub.ai）
  🇨🇳 ClawHub CN（mirror-cn.clawhub.com）
  🔧 SkillHub（skillhub.tencent.com）
```

---

## 📂 分类与代表技能

| 分类 | 代表技能 |
|------|----------|
| 🔍 **搜索资讯** | Summarize、Tavily Search、Brave Search |
| 🧠 **记忆/知识** | Elite Longterm Memory、Memory Setup |
| 🤖 **AI 增强** | Proactive Agent、self-improving-agent |
| 🌐 **浏览器自动化** | Agent Browser、Browser Use、Playwright MCP |
| 📁 **文件处理** | Nano Pdf、Word/DOCX、Excel/XLSX |
| ⚡ **自动化** | Automation Workflows、Desktop Control |
| 💼 **工作办公** | Gmail、Notion、Slack |
| 💰 **投资交易** | Polymarket、Stock Analysis |
| 🎨 **创意设计** | Nano Banana Pro、SuperDesign |
| 🌤️ **生活** | Weather、Sonoscli |

---

## ⏰ 定时同步

每日 07:30（Asia/Shanghai）自动执行，包含：

### 版本检测
1. `clawhub list` 获取本地已安装技能及版本
2. `clawhub inspect <slug>` 获取远程最新版本
3. 对比差异，生成 `config/daily/updates_YYYY-MM-DD.md`

### 📊 每日报告

```
## 🏠 常驻技能（N 个）
列表：名称 / 版本 / 下载量 / ⭐

## 📂 分类加载技能（N 个）
列表：名称 / 版本 / 已用次数 / 状态
状态：✅ 正常 / 🟡 可升级 / ❌ 申请取消

## 🔔 可更新技能（N 个）
表格：技能 / 当前版本 / 最新版本

## 📌 待确认事项
- 🔴 有 N 个技能可更新，是否现在更新？
- 🟡 以下分类技能已达 5 次，是否取消加载？
```

### 技能升降级规则

| 触发条件 | 自动操作 | 告知用户 |
|----------|----------|----------|
| 分类技能使用 ≥ 10 次 | 自动升为常驻 | ✅ 告知 |
| 分类技能使用 ≥ 5 次 | 标记「可升级」 | ✅ 询问 |
| 用户申请取消 | 心跳确认后移除 | ✅ 确认 |
| 常驻技能 7 天未用 | 标记可降级 | ✅ 询问 |

---

## 🔍 技能审视报告格式

```
🔍 技能审视报告
═══════════════════════════════════════
共 N 个技能 · 核心 N 个 · 常驻 N 个 · 分类 N 个
───────────────────────────────────────
✅ 正常（N 个）
  • skill-a · v1.0 · 12KB · 核心

⚠️ 部分可用（N 个）
  • skill-c · v1.0 · 45KB
    ⚠️ 缺 binary: summarize

🔴 不可用（N 个）
  • skill-d · v1.0 · 30KB
    🔴 缺 API Key: TAVILY_API_KEY

🔵 自定义修改（N 个）
  • proactive-agent · v3.1.0 · 81KB
    🔵 本地 WAL 协议修改

🔄 可更新（N 个）
  • self-improving-agent · 3.0.10 → 3.0.12
───────────────────────────────────────
📌 建议操作
  • skill-c: 安装 summarize binary
  • skill-d: 设置 API Key 或卸载
═══════════════════════════════════════
```

---

## 📦 自定义分类

```json
{
  "custom_categories": {
    "my-trading": {
      "name": "我的交易套件",
      "description": "交易相关技能合集",
      "enabled": false,
      "skills": ["polymarket", "stock-analysis"],
      "created_at": "2026-04-03"
    }
  }
}
```

| 操作 | 行为 |
|------|------|
| 分类启用 | 所有技能加入常驻层，下次会话加载 |
| 分类禁用 | 所有技能从常驻层移除，文件保留 |
| 分类删除 | 移除分类，技能文件保留 |

---

## 💾 备份与恢复

```bash
# 生成清单（每次安装后执行）
python3 scripts/save_skill_manifest.py

# 出事后一键恢复
python3 scripts/restore_skills.py
```

清单文件：`.skill_manifest.json`（已记录在 MEMORY.md）

---

## ⚙️ 配置文件

| 文件 | 说明 |
|------|------|
| `config/clawhub_skills.md` | 热门技能数据库 |
| `config/scenes.json` | 场景 + 分类 + 常驻技能 + 自定义分类 |
| `config/daily/` | 每日同步增量记录 |
| `scripts/skill-inspect.py` | 技能审视分析脚本 |

---

## ⚠️ 外部依赖风险声明

本技能调用外部 clawhub registry 下载第三方技能，并执行外部 skill-vetter 脚本。

| 外部调用 | 风险等级 | 缓解措施 |
|---------|---------|----------|
| clawhub registry | 中 | 安装前强制 skill-vetter 审查 |
| skill-vetter.py | 中 | 仅读取 skills/ 目录，不访问凭据 |
| clawhub install/update | 高 | 需用户明确确认后执行 |

**Autonomous 模式下（心跳）：**
```
✅ 允许：搜索、审视、备份、查看报告
❌ 禁止：安装、更新、分类修改（需 user-confirmed）
```

## Tip

- CN 镜像优先：避免全球站限速
- 安装/更新前必读目标技能的 SKILL.md：避免"装了不用"
- 清单定期更新：`python3 scripts/save_skill_manifest.py`
- Autonomous 模式禁止执行安装/更新操作
