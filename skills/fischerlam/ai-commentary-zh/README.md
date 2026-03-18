# ai-commentary-zh

[![ClawHub Skill](https://img.shields.io/badge/ClawHub-Skill-blueviolet)](https://clawhub.io)
[![Version](https://img.shields.io/badge/version-1.0.8-blue)](SKILL.md)

> **AI 解说**
> 中文场景版，由 Sparki 提供能力。
>
> Powered by [Sparki](https://sparki.io).

## 这个 Skill 做什么

这个 skill 是 Sparki AI 视频工作流的中文场景入口。

- 上传视频文件
- 根据场景创建 AI 处理任务
- 轮询直到处理完成
- 返回结果下载链接

## 适合这些需求
- “做成解说视频风格”
- “让它更像 commentary”
- “做成更有讲解感的版本”
- “让结构更像解说 / explainers”

## 快速开始

```bash
export SPARKI_API_KEY="sk_live_your_key_here"
export SPARKI_API_BASE="https://business-agent-api.sparki.io/api/v1"
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "25" "做成更强的 commentary / 解说型节奏" "9:16")
echo "$RESULT_URL"
```
