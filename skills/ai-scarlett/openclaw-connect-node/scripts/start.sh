#!/bin/bash
# OpenClaw Connect Node - 一键启动脚本
# 用法: ./start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查环境变量
if [ -z "$HUB_URL" ] || [ -z "$APP_ID" ] || [ -z "$APP_KEY" ] || [ -z "$APP_TOKEN" ]; then
  echo "❌ 缺少环境变量，请设置以下变量:"
  echo ""
  echo "  export HUB_URL=http://主节点地址:3100"
  echo "  export APP_ID=你的AppID"
  echo "  export APP_KEY=你的Key"
  echo "  export APP_TOKEN=你的Token"
  echo "  export NODE_PORT=3100  # 可选，默认 3100"
  echo ""
  echo "然后重新运行: $0"
  exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
  echo "📦 安装依赖..."
  cd "$SCRIPT_DIR" && npm install
fi

echo "🚀 启动子节点..."
echo "   Hub: $HUB_URL"
echo "   App ID: $APP_ID"
echo "   Port: ${NODE_PORT:-3100}"
echo ""

cd "$SCRIPT_DIR" && npx tsx src/index.ts
