---
name: thinktank-skill-finder
description: ThinkTank Skill Finder. 面向智库研究场景的技能检索与技能包安装。
author: MAMA
metadata:
  openclaw:
    emoji: 🔎
    requires:
      bins: [clawdhub]
---
# ThinkTank Skill Finder v1.0.6

面向智库研究场景的一站式 Skill 发现与安装工具。支持通过 ClawdHub 镜像进行检索与安装，便于中国网络环境使用；既可按需推荐和安装单个 Skill，也可直接安装智库研究核心包，以及学术研究、动态监测、分析建模等增强包。

清单维护说明见：
`~/.openclaw/workspace/skills/thinktank-skill-finder/MAINTENANCE.md`

## 功能

当用户问：

- "有什么 skill 可以做智库研究？"
- "找一个能做行业研究的 skill"
- "有没有画图/报告相关 skill"
- "安装智库研究技能包"

这个 Skill 会帮助搜索 ClawdHub 并推荐相关 Skills。

## 使用方法

### 1. 搜索 Skills

```bash
clawdhub search "<英文检索词>"
```

### 2. 查看详情（含统计数据）

```bash
clawdhub inspect <skill-name>
```

或者直接 API 查询 stats：

```bash
curl "https://clawhub.ai/api/v1/skills/<skill-name>" | jq '.skill.stats'
```

### 3. 安装单个 Skill

```bash
clawdhub install <skill-name> --no-input --registry=https://cn.clawhub-mirror.com
```

### 4. 安装智库研究技能包（按 skills.csv）

```bash
# 列出可用的技能包
python3 ~/.openclaw/workspace/skills/thinktank-skill-finder/scripts/install_bundle.py --list

# 安装核心包
python3 ~/.openclaw/workspace/skills/thinktank-skill-finder/scripts/install_bundle.py thinktank-core

# 安装多个包（自动去重）
python3 ~/.openclaw/workspace/skills/thinktank-skill-finder/scripts/install_bundle.py thinktank-core academic-research-plus
```

### 5. 验证安装

```bash
clawdhub list
或者：
ls ~/.openclaw/workspace/skills/<skill-name>/SKILL.md
```

## 工作流程

```text
场景 A：推荐单个技能
1. 理解用户需求
2. 理解意图并改写为英文检索词
3. 搜索 ClawdHub
4. 列出相关 Skills（含下载量/stars）
5. 推荐最合适的单个 Skill，并提供安装命令
6. 如有需要，补一句引导：如果你后面还会经常做这类任务，我也可以继续帮你配一组相关技能。
7. 用户想配一组相关技能时，转入场景 B；用户只要当前单个 Skill 时，执行安装命令并完成验证

场景 B：安装技能包
1. 识别“安装技能包/全套/bundle”等意图
2. 调用脚本查看可用 bundle：
   python3 ~/.openclaw/workspace/skills/thinktank-skill-finder/scripts/install_bundle.py --list
3. 向用户介绍各个 bundle 的用途和适用场景
4. 等用户明确指定要安装哪几个 bundle
5. 执行安装命令：
   python3 ~/.openclaw/workspace/skills/thinktank-skill-finder/scripts/install_bundle.py <bundle-id>
6. 如果用户需要多个相关领域的能力，可以一次安装多个 bundle（脚本会自动去重）
```

## 输出格式

搜索结果应包含：

- Skill 名称
- 简短描述（中文）
- 下载量
- Stars 数
- 是否已安装

## 示例

**用户**: "找一个能做行业研究的 skill"

**搜索**: `clawdhub search "market research"`

**推荐输出**:

```text
🔎 "行业研究" 结果：

1. market-research-agent
   描述：行业研究、竞品分析和市场规模拆解
   下载：5,433 | Stars: 17 | ❌ 未安装
   → 推荐安装

安装命令: clawdhub install market-research-agent --no-input --registry=https://cn.clawhub-mirror.com
安装后验证: ls ~/.openclaw/workspace/skills/market-research-agent/SKILL.md
```

---

*帮助用户发现需要的智库研究 Skills 🔎*
