# State Management — Session 与状态管理

## CDP Session 复用

### 启动 CDP Chrome

```bash
# 启动带 CDP 的 Chrome（Cookie 永久保留）
bash ~/.openclaw/scripts/browser-cdp.sh start

# 查看状态
bash ~/.openclaw/scripts/browser-cdp.sh status

# 停止
bash ~/.openclaw/scripts/browser-cdp.sh stop
```

### 验证 CDP

```bash
curl http://localhost:9222/json/version
```

### 手动启动命令

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir=/Users/study/.openclaw/browser-profile \
  --no-first-run
```

## 目录结构

```
~/.openclaw/
├── browser-profile/              # CDP 主仓（Cookie/登录态永久存储）
│   └── Default/
│       ├── Cookies
│       ├── Local Storage/
│       └── ...
│
└── browser-state/                # 站点级 state 备份
    ├── x_state.json              # X/Twitter 登录态
    ├── xueqiu_state.json         # 雪球登录态
    └── ...
```

## 两种模式

### Persistent Profile（持久化）

**特点**：
- ✅ Cookie 永久保留
- ✅ 手动登录一次，后续复用
- ✅ 不会每次都新开页面

**适用**：
- 需要登录的网站（X/雪球等）
- 需要保持会话状态的任务

### Isolated Profile（隔离）

**特点**：
- ❌ 不保留登录态
- ❌ 每次新开页面

**适用**：
- 公开内容抓取
- 测试任务
- 隐私敏感任务

## agent-browser 使用 CDP

```bash
# 先启动 CDP Chrome
bash ~/.openclaw/scripts/browser-cdp.sh start

# agent-browser 自动检测到 CDP 端口并复用
agent-browser open https://xueqiu.com
```

## 站点级 State 备份

**位置**: `~/.openclaw/browser-state/{domain}.json`

**用途**：
- 备份特定站点的登录态/配置
- 便于迁移和恢复

**示例**：
```json
{
  "domain": "xueqiu.com",
  "cookies": [...],
  "local_storage": {...}
}
```
