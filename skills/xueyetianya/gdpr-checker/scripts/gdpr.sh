#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  audit) cat << 'PROMPT'
You are an expert. Help with: 合规审计. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  consent) cat << 'PROMPT'
You are an expert. Help with: 用户同意机制. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  rights) cat << 'PROMPT'
You are an expert. Help with: 数据主体权利. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  breach) cat << 'PROMPT'
You are an expert. Help with: 泄露响应流程. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  dpa) cat << 'PROMPT'
You are an expert. Help with: 数据处理协议. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  checklist) cat << 'PROMPT'
You are an expert. Help with: 检查清单. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GDPR Checker — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  audit           合规审计
  consent         用户同意机制
  rights          数据主体权利
  breach          泄露响应流程
  dpa             数据处理协议
  checklist       检查清单

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
