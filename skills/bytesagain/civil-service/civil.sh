#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  shenlun) cat << 'PROMPT'
You are an expert. Help with: 申论写作. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  xingce) cat << 'PROMPT'
You are an expert. Help with: 行测技巧. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  interview) cat << 'PROMPT'
You are an expert. Help with: 面试模拟. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  hotspot) cat << 'PROMPT'
You are an expert. Help with: 时政热点. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  plan) cat << 'PROMPT'
You are an expert. Help with: 备考计划. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  essay) cat << 'PROMPT'
You are an expert. Help with: 大作文模板. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Civil Service Exam — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  shenlun         申论写作
  xingce          行测技巧
  interview       面试模拟
  hotspot         时政热点
  plan            备考计划
  essay           大作文模板

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
