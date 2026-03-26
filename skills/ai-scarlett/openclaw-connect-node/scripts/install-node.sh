#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════
# OpenClaw Connect Node - 一键安装脚本 (跨平台)
# ═══════════════════════════════════════════════════════════
#
# 用法 (从 Hub 管理后台复制安装命令):
#   bash install-node.sh \
#     --hub-url http://49.232.250.180:3100 \
#     --app-id oc-xxxxxx \
#     --app-key xxxxxxxx \
#     --token xxxxxxxx \
#     --node-name "深圳节点"
#
# 可选参数:
#   --port 3200          监听端口 (默认 3100)
#   --install-dir /path  安装目录 (默认 /opt/openclaw-node 或 ~/openclaw-node)
#   --no-daemon          不创建守护进程服务
#
# 支持平台:
#   Linux   → systemd 守护
#   macOS   → launchd plist 守护
#   Windows (MSYS/Git Bash/Cygwin) / 其他 → pm2 守护
# ═══════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info()  { echo -e "${CYAN}[i]${NC} $1"; }

# ─── 自动检测操作系统 ────────────────────────────────────
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
  Linux*)              DAEMON_TYPE="systemd" ;;
  Darwin*)             DAEMON_TYPE="launchd" ;;
  MINGW*|MSYS*|CYGWIN*) DAEMON_TYPE="pm2" ;;
  *)                   DAEMON_TYPE="pm2" ;;
esac

# ─── 默认值 ──────────────────────────────────────────────
HUB_URL=""
APP_ID=""
APP_KEY=""
APP_TOKEN=""
NODE_NAME="$(hostname)"
NODE_PORT=3100
SETUP_DAEMON=true

# 默认安装目录: Linux 用 /opt, macOS/Windows 用 ~/openclaw-node
if [ "$DAEMON_TYPE" = "systemd" ]; then
  INSTALL_DIR="/opt/openclaw-node"
else
  INSTALL_DIR="$HOME/openclaw-node"
fi

# ─── 解析参数 ────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hub-url)     HUB_URL="$2"; shift 2 ;;
    --app-id)      APP_ID="$2"; shift 2 ;;
    --app-key)     APP_KEY="$2"; shift 2 ;;
    --token)       APP_TOKEN="$2"; shift 2 ;;
    --node-name)   NODE_NAME="$2"; shift 2 ;;
    --port)        NODE_PORT="$2"; shift 2 ;;
    --install-dir) INSTALL_DIR="$2"; shift 2 ;;
    --no-systemd)  SETUP_DAEMON=false; shift ;;
    --no-daemon)   SETUP_DAEMON=false; shift ;;
    *) err "未知参数: $1" ;;
  esac
done

# ─── 参数校验 ────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "   🦞 OpenClaw Connect Node 安装程序"
echo "═══════════════════════════════════════════════════"
echo ""

[ -z "$HUB_URL" ]   && err "缺少 --hub-url 参数"
[ -z "$APP_ID" ]     && err "缺少 --app-id 参数"
[ -z "$APP_KEY" ]    && err "缺少 --app-key 参数"
[ -z "$APP_TOKEN" ]  && err "缺少 --token 参数"

info "操作系统:  $OS_TYPE ($DAEMON_TYPE)"
info "Hub 地址:  $HUB_URL"
info "App ID:    $APP_ID"
info "节点名称:  $NODE_NAME"
info "监听端口:  $NODE_PORT"
info "安装目录:  $INSTALL_DIR"
echo ""

# ─── 环境检查 ────────────────────────────────────────────
info "检查运行环境..."

# Root 权限检查 - 仅 Linux systemd 需要
if [ "$EUID" -ne 0 ] && [ "$DAEMON_TYPE" = "systemd" ] && [ "$SETUP_DAEMON" = true ]; then
  err "Linux systemd 需要 root 权限。请使用 sudo 运行，或添加 --no-daemon 跳过。"
fi

# Node.js 检查
if command -v node &>/dev/null; then
  NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
  if [ "$NODE_VER" -lt 18 ]; then
    warn "Node.js 版本过低 ($(node -v))，需要 >= 18"
    if [ "$DAEMON_TYPE" = "systemd" ]; then
      info "正在安装 Node.js 22..."
      curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs
    elif [ "$DAEMON_TYPE" = "launchd" ]; then
      info "请使用 brew 或 nvm 升级 Node.js >= 18"
      info "  brew install node@22  或  nvm install 22"
      err "Node.js 版本过低，请升级后重试。"
    else
      err "Node.js 版本过低 ($(node -v))，请升级到 >= 18 后重试。"
    fi
  else
    log "Node.js $(node -v) ✓"
  fi
else
  if [ "$DAEMON_TYPE" = "systemd" ]; then
    info "未检测到 Node.js，正在安装..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs
    log "Node.js $(node -v) 已安装"
  else
    err "未检测到 Node.js，请先安装 Node.js >= 18。"
  fi
fi

# npm/npx 检查
command -v npx &>/dev/null || err "npx 未找到，请确保 Node.js 安装正确"
log "npx ✓"

# 端口检查
if command -v ss &>/dev/null; then
  if ss -tlnp | grep -q ":${NODE_PORT} "; then
    warn "端口 ${NODE_PORT} 已被占用！"
    warn "请使用 --port 指定其他端口，或先停止占用端口的进程"
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
  fi
elif command -v lsof &>/dev/null; then
  if lsof -iTCP:${NODE_PORT} -sTCP:LISTEN &>/dev/null; then
    warn "端口 ${NODE_PORT} 已被占用！"
    warn "请使用 --port 指定其他端口，或先停止占用端口的进程"
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
  fi
fi

# ─── 安装 ────────────────────────────────────────────────
info "准备安装目录..."
mkdir -p "$INSTALL_DIR"

# 检查是否已有代码（用户手动上传的场景）
if [ -f "$INSTALL_DIR/src/index.ts" ]; then
  log "检测到已有代码，跳过复制"
else
  # 从当前 skill 目录复制
  SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
  if [ -f "$SKILL_DIR/scripts/src/index.ts" ]; then
    COPY_SRC="$SKILL_DIR/scripts"
  elif [ -f "$SKILL_DIR/src/index.ts" ]; then
    COPY_SRC="$SKILL_DIR"
  else
    COPY_SRC=""
  fi

  if [ -n "$COPY_SRC" ]; then
    info "从技能目录复制代码..."
    cp -r "$COPY_SRC/"* "$INSTALL_DIR/" 2>/dev/null || true
    if [ -d "$COPY_SRC/src" ]; then
      cp -r "$COPY_SRC/src" "$INSTALL_DIR/src"
    fi
    # 复制前端
    ASSET_DIR="$(dirname "$SKILL_DIR")/assets/frontend-dist"
    if [ -d "$ASSET_DIR" ]; then
      mkdir -p "$INSTALL_DIR/frontend-dist"
      cp -r "$ASSET_DIR/"* "$INSTALL_DIR/frontend-dist/"
    fi
    log "代码已复制到 $INSTALL_DIR"
  else
    err "未找到 Node 源代码。请确保在技能目录下运行，或手动将代码放到 $INSTALL_DIR"
  fi
fi

# ─── 安装依赖 ────────────────────────────────────────────
info "安装 Node.js 依赖..."
cd "$INSTALL_DIR"
if [ ! -f "package.json" ]; then
  [ -f scripts/package.json ] && cp scripts/package.json .
fi
npm install --production 2>&1 | tail -3
log "依赖安装完成"

# ─── 生成 .env 配置 ──────────────────────────────────────
info "生成配置文件..."
cat > "$INSTALL_DIR/.env" << ENVEOF
# ═══════════════════════════════════════════════════
# OpenClaw Connect Node 配置
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# ═══════════════════════════════════════════════════

# Hub 主节点地址
HUB_URL=${HUB_URL}

# 节点认证凭证 (从 Hub 管理后台获取)
APP_ID=${APP_ID}
APP_KEY=${APP_KEY}
APP_TOKEN=${APP_TOKEN}

# 节点设置
NODE_NAME=${NODE_NAME}
NODE_PORT=${NODE_PORT}

# 数据目录
DATA_DIR=${INSTALL_DIR}/data

# 运行环境
NODE_ENV=production

# 守护进程类型 (systemd / launchd / pm2)
DAEMON_TYPE=${DAEMON_TYPE}
ENVEOF

chmod 600 "$INSTALL_DIR/.env"
log "配置文件已生成: $INSTALL_DIR/.env"

# ─── 创建数据目录 ────────────────────────────────────────
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/logs"

# ─── 守护进程配置 ────────────────────────────────────────
if [ "$SETUP_DAEMON" = true ]; then

  case "$DAEMON_TYPE" in
    # ─── Linux: systemd ────────────────────────────────
    systemd)
      info "配置 systemd 守护进程..."

      cat > /etc/systemd/system/openclaw-node.service << SVCEOF
[Unit]
Description=OpenClaw Connect Node
Documentation=https://github.com/nicepkg/openclaw
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
EnvironmentFile=${INSTALL_DIR}/.env
ExecStart=$(which npx) tsx src/index.ts
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=5

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw-node

# 资源限制
LimitNOFILE=65535
MemoryMax=2G
CPUQuota=80%

# 安全
NoNewPrivileges=false
ProtectSystem=false

[Install]
WantedBy=multi-user.target
SVCEOF

      systemctl daemon-reload
      systemctl enable openclaw-node
      log "systemd 服务已创建并启用"
      ;;

    # ─── macOS: launchd ──────────────────────────────────
    launchd)
      info "配置 launchd 守护进程..."

      PLIST_DIR="$HOME/Library/LaunchAgents"
      PLIST_PATH="$PLIST_DIR/com.openclaw.node.plist"
      mkdir -p "$PLIST_DIR"

      NPX_PATH="$(which npx)"

      cat > "$PLIST_PATH" << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.node</string>
    <key>ProgramArguments</key>
    <array>
        <string>${NPX_PATH}</string>
        <string>tsx</string>
        <string>${INSTALL_DIR}/src/index.ts</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${INSTALL_DIR}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HUB_URL</key>
        <string>${HUB_URL}</string>
        <key>APP_ID</key>
        <string>${APP_ID}</string>
        <key>APP_KEY</key>
        <string>${APP_KEY}</string>
        <key>APP_TOKEN</key>
        <string>${APP_TOKEN}</string>
        <key>NODE_NAME</key>
        <string>${NODE_NAME}</string>
        <key>NODE_PORT</key>
        <string>${NODE_PORT}</string>
        <key>NODE_ENV</key>
        <string>production</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${INSTALL_DIR}/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${INSTALL_DIR}/logs/stderr.log</string>
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
PLISTEOF

      log "launchd plist 已创建: $PLIST_PATH"
      ;;

    # ─── Windows/其他: pm2 ───────────────────────────────
    pm2)
      info "配置 pm2 守护进程..."

      # 自动安装 pm2
      if ! command -v pm2 &>/dev/null; then
        info "安装 pm2..."
        npm install -g pm2 2>/dev/null || { warn "全局安装 pm2 失败，尝试 npx"; }
      fi

      # 生成 ecosystem 配置
      cat > "$INSTALL_DIR/ecosystem.config.js" << PMEOF
module.exports = {
  apps: [{
    name: 'openclaw-node',
    script: 'npx',
    args: 'tsx src/index.ts',
    cwd: '${INSTALL_DIR}',
    env: {
      HUB_URL: '${HUB_URL}',
      APP_ID: '${APP_ID}',
      APP_KEY: '${APP_KEY}',
      APP_TOKEN: '${APP_TOKEN}',
      NODE_NAME: '${NODE_NAME}',
      NODE_PORT: '${NODE_PORT}',
      NODE_ENV: 'production',
    },
    autorestart: true,
    max_restarts: 10,
    restart_delay: 10000,
    max_memory_restart: '2G',
    log_file: '${INSTALL_DIR}/logs/combined.log',
    error_file: '${INSTALL_DIR}/logs/error.log',
    out_file: '${INSTALL_DIR}/logs/out.log',
  }]
};
PMEOF

      log "pm2 ecosystem 配置已生成: $INSTALL_DIR/ecosystem.config.js"
      ;;
  esac

fi

# ─── 管理命令 ────────────────────────────────────────────
info "创建管理命令..."

# 确定管理命令安装路径
if [ "$DAEMON_TYPE" = "systemd" ]; then
  CMD_PATH="/usr/local/bin/openclaw-node"
else
  # macOS / Windows: 安装到用户可写路径
  if [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin" 2>/dev/null; then
    CMD_PATH="$HOME/.local/bin/openclaw-node"
  elif [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    CMD_PATH="/usr/local/bin/openclaw-node"
  else
    CMD_PATH="$INSTALL_DIR/openclaw-node"
  fi
fi

cat > "$CMD_PATH" << 'CMDEOF'
#!/bin/bash
INSTALL_DIR="INSTALL_DIR_PLACEHOLDER"

# 读取 DAEMON_TYPE
if [ -f "$INSTALL_DIR/.env" ]; then
  DAEMON_TYPE=$(grep '^DAEMON_TYPE=' "$INSTALL_DIR/.env" | cut -d= -f2)
fi
DAEMON_TYPE="${DAEMON_TYPE:-systemd}"

# 读取端口
PORT=$(grep '^NODE_PORT=' "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2 || echo 3100)

health_check() {
  HEALTH=$(curl -s --max-time 3 "http://localhost:${PORT}/api/health" 2>/dev/null)
  if [ -n "$HEALTH" ]; then
    echo "🏥 健康检查:"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
  fi
}

case "${1:-help}" in
  start)
    case "$DAEMON_TYPE" in
      systemd) systemctl start openclaw-node ;;
      launchd) launchctl load "$HOME/Library/LaunchAgents/com.openclaw.node.plist" 2>/dev/null ;;
      pm2)     pm2 start openclaw-node 2>/dev/null || pm2 start "$INSTALL_DIR/ecosystem.config.js" ;;
    esac
    echo "✅ 节点已启动"
    ;;
  stop)
    case "$DAEMON_TYPE" in
      systemd) systemctl stop openclaw-node ;;
      launchd) launchctl unload "$HOME/Library/LaunchAgents/com.openclaw.node.plist" 2>/dev/null ;;
      pm2)     pm2 stop openclaw-node ;;
    esac
    echo "⏹️  节点已停止"
    ;;
  restart)
    case "$DAEMON_TYPE" in
      systemd) systemctl restart openclaw-node ;;
      launchd)
        launchctl unload "$HOME/Library/LaunchAgents/com.openclaw.node.plist" 2>/dev/null
        launchctl load "$HOME/Library/LaunchAgents/com.openclaw.node.plist"
        ;;
      pm2) pm2 restart openclaw-node ;;
    esac
    echo "🔄 节点已重启"
    ;;
  status)
    case "$DAEMON_TYPE" in
      systemd)
        systemctl status openclaw-node --no-pager
        ;;
      launchd)
        echo "📋 launchd 服务状态:"
        launchctl list | head -1
        launchctl list | grep openclaw || echo "  (未运行)"
        echo ""
        echo "📋 进程状态:"
        ps aux | grep "openclaw-node\|tsx.*index.ts" | grep -v grep || echo "  (无相关进程)"
        ;;
      pm2)
        pm2 describe openclaw-node 2>/dev/null || echo "  (pm2 中未找到 openclaw-node)"
        ;;
    esac
    echo ""
    health_check
    ;;
  logs)
    case "$DAEMON_TYPE" in
      systemd) journalctl -u openclaw-node -f --no-pager ${@:2} ;;
      launchd) tail -f "$INSTALL_DIR/logs/stdout.log" ;;
      pm2)     pm2 logs openclaw-node ;;
    esac
    ;;
  logs-tail)
    case "$DAEMON_TYPE" in
      systemd) journalctl -u openclaw-node --no-pager -n ${2:-50} ;;
      launchd) tail -n ${2:-50} "$INSTALL_DIR/logs/stdout.log" ;;
      pm2)     pm2 logs openclaw-node --lines ${2:-50} --nostream ;;
    esac
    ;;
  config)
    echo "📄 配置文件: $INSTALL_DIR/.env"
    echo "─────────────────────────────────"
    sed 's/\(APP_KEY=\).*/\1***/' "$INSTALL_DIR/.env" | sed 's/\(APP_TOKEN=\).*/\1***/'
    ;;
  edit-config)
    ${EDITOR:-nano} "$INSTALL_DIR/.env"
    echo "💡 修改配置后需要重启: openclaw-node restart"
    ;;
  update)
    echo "🔄 更新中..."
    cd "$INSTALL_DIR"
    if [ -d ".git" ]; then
      git pull
    else
      echo "⚠️  非 git 安装，请手动更新代码到 $INSTALL_DIR"
    fi
    npm install --production 2>&1 | tail -3
    "$0" restart
    echo "✅ 更新完成并已重启"
    ;;
  uninstall)
    read -p "⚠️  确定要卸载 OpenClaw Node？数据不会删除。(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      case "$DAEMON_TYPE" in
        systemd)
          systemctl stop openclaw-node 2>/dev/null
          systemctl disable openclaw-node 2>/dev/null
          rm -f /etc/systemd/system/openclaw-node.service
          systemctl daemon-reload
          ;;
        launchd)
          launchctl unload "$HOME/Library/LaunchAgents/com.openclaw.node.plist" 2>/dev/null
          rm -f "$HOME/Library/LaunchAgents/com.openclaw.node.plist"
          ;;
        pm2)
          pm2 stop openclaw-node 2>/dev/null
          pm2 delete openclaw-node 2>/dev/null
          pm2 save 2>/dev/null
          ;;
      esac
      SELF_PATH="$(realpath "$0" 2>/dev/null || echo "$0")"
      rm -f "$SELF_PATH"
      echo "✅ 已卸载。数据目录 $INSTALL_DIR 已保留。"
    fi
    ;;
  *)
    echo "🦞 OpenClaw Connect Node 管理工具"
    echo ""
    echo "用法: openclaw-node <命令>"
    echo ""
    echo "命令:"
    echo "  start        启动节点"
    echo "  stop         停止节点"
    echo "  restart      重启节点"
    echo "  status       查看状态 + 健康检查"
    echo "  logs         实时日志 (Ctrl+C 退出)"
    echo "  logs-tail N  查看最近 N 条日志"
    echo "  config       查看配置"
    echo "  edit-config  编辑配置"
    echo "  update       更新代码并重启"
    echo "  uninstall    卸载节点"
    echo ""
    echo "安装目录: $INSTALL_DIR"
    echo "守护类型: $DAEMON_TYPE"
    ;;
esac
CMDEOF

# 替换安装目录占位符
sed -i "s|INSTALL_DIR_PLACEHOLDER|${INSTALL_DIR}|g" "$CMD_PATH"
chmod +x "$CMD_PATH"
log "管理命令已创建: $CMD_PATH"

# 检查 PATH 是否包含命令路径
CMD_DIR="$(dirname "$CMD_PATH")"
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$CMD_DIR"; then
  warn "管理命令路径 $CMD_DIR 不在 PATH 中"
  warn "请添加到 shell 配置: export PATH=\"$CMD_DIR:\$PATH\""
fi

# ─── 启动服务 ────────────────────────────────────────────
if [ "$SETUP_DAEMON" = true ]; then
  info "启动节点服务..."

  case "$DAEMON_TYPE" in
    systemd)
      systemctl start openclaw-node
      ;;
    launchd)
      launchctl load "$PLIST_PATH"
      ;;
    pm2)
      pm2 start "$INSTALL_DIR/ecosystem.config.js"
      pm2 save
      pm2 startup 2>/dev/null || true
      ;;
  esac

  sleep 3

  # 验证启动状态
  case "$DAEMON_TYPE" in
    systemd)
      if systemctl is-active --quiet openclaw-node; then
        log "节点服务已启动"
      else
        warn "节点启动可能失败，查看日志: openclaw-node logs"
      fi
      ;;
    launchd)
      if ps aux | grep -v grep | grep -q "tsx.*index.ts"; then
        log "节点服务已启动"
      else
        warn "节点启动可能失败，查看日志: openclaw-node logs"
      fi
      ;;
    pm2)
      if pm2 describe openclaw-node 2>/dev/null | grep -q "online"; then
        log "节点服务已启动"
      else
        warn "节点启动可能失败，查看日志: openclaw-node logs"
      fi
      ;;
  esac
fi

# ─── 完成 ────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "   🦞 OpenClaw Connect Node 安装完成！"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  📍 安装目录:  $INSTALL_DIR"
echo "  📄 配置文件:  $INSTALL_DIR/.env"
echo "  🔗 Hub 地址:  $HUB_URL"
echo "  🏷️  节点名称:  $NODE_NAME"
echo "  🌐 本地端口:  $NODE_PORT"

# 尝试获取本机 IP
LOCAL_IP=""
if command -v hostname &>/dev/null; then
  LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [ -z "$LOCAL_IP" ] && command -v ipconfig &>/dev/null; then
  LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null)
fi
if [ -n "$LOCAL_IP" ]; then
  echo "  🔗 管理界面:  http://${LOCAL_IP}:${NODE_PORT}"
fi

echo ""

# 平台特定提示
case "$DAEMON_TYPE" in
  systemd)
    echo "  🐧 守护方式:  systemd (自动重启 + 开机启动)"
    ;;
  launchd)
    echo "  🍎 守护方式:  launchd (KeepAlive + RunAtLoad)"
    ;;
  pm2)
    echo "  📦 守护方式:  pm2 (autorestart + 内存限制重启)"
    ;;
esac

echo ""
echo "  管理命令:"
echo "    openclaw-node status    查看状态"
echo "    openclaw-node logs      查看日志"
echo "    openclaw-node restart   重启节点"
echo "    openclaw-node config    查看配置"
echo "    openclaw-node uninstall 卸载"

if [ "$DAEMON_TYPE" = "pm2" ]; then
  echo ""
  echo "  pm2 命令 (可选):"
  echo "    pm2 status              查看所有 pm2 进程"
  echo "    pm2 logs openclaw-node  查看日志"
fi

echo ""
