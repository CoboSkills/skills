---
name: openclaw-connect-node
description: OpenClaw Connect Enterprise 子节点。将当前 OpenClaw 实例注册为远程 Hub 的子节点，通过 appId/key/token 三重验证绑定。提供本地管理界面（任务查看、记忆管理、系统监控）。子节点只能看自己的数据，所有被主节点控制的数据不可操作。当用户说"连接主节点"、"注册子节点"、"启动 node"、"加入 Hub"时触发。
allowed-tools: Bash(npm:*) Bash(npx:*) Bash(openclaw:*) Bash(curl:*) Bash(systemctl:*) Read Write
---

# OpenClaw Connect Node — 子节点技能

将当前 OpenClaw 实例作为子节点连接到远程 Hub 主节点。

## 架构

```
Hub (主节点 :3100)              Node (子节点 :3100)
├── /admin    主控台            ├── /         子节点管理 UI
├── /api/*    Hub API           ├── /api/*    子节点 API
└── 节点/任务/Agent 管理        └── 只看自己的数据
```

## 安装方式

### 方式一：一键安装（推荐）

从 Hub 管理后台「节点管理 → 创建节点」获取安装命令，在子节点服务器上执行：

```bash
bash install-node.sh \
  --hub-url http://主节点地址:3100 \
  --app-id oc-xxxxxx \
  --app-key xxxxxxxx \
  --token xxxxxxxx \
  --node-name "节点名称"
```

可选参数：
- `--port 3200` — 监听端口（默认 3100）
- `--install-dir /opt/openclaw-node` — 安装目录
- `--no-systemd` — 不创建 systemd 守护进程

安装脚本会自动完成：
1. ✅ 环境检查（Node.js >= 18，自动安装）
2. ✅ 代码部署 + 依赖安装
3. ✅ 生成 `.env` 配置文件（凭证安全存储）
4. ✅ 创建 systemd 服务（挂了自动重启，开机自动启动）
5. ✅ 创建 `openclaw-node` 管理命令
6. ✅ 启动服务

### 方式二：手动安装

```bash
# 1. 复制代码到目标目录
cp -r <skill_directory>/scripts /opt/openclaw-node
cp -r <skill_directory>/assets/frontend-dist /opt/openclaw-node/frontend-dist

# 2. 安装依赖
cd /opt/openclaw-node && npm install

# 3. 创建配置
cat > /opt/openclaw-node/.env << EOF
HUB_URL=http://主节点地址:3100
APP_ID=你的AppID
APP_KEY=你的Key
APP_TOKEN=你的Token
NODE_NAME=节点名称
NODE_PORT=3100
EOF

# 4. 启动
cd /opt/openclaw-node && npx tsx src/index.ts
```

## 管理命令

安装后可使用 `openclaw-node` 命令管理节点：

| 命令 | 说明 |
|------|------|
| `openclaw-node start` | 启动节点 |
| `openclaw-node stop` | 停止节点 |
| `openclaw-node restart` | 重启节点 |
| `openclaw-node status` | 查看状态 + 健康检查 |
| `openclaw-node logs` | 实时日志 |
| `openclaw-node logs-tail 50` | 最近 50 条日志 |
| `openclaw-node config` | 查看配置（敏感信息隐藏） |
| `openclaw-node edit-config` | 编辑配置 |
| `openclaw-node update` | 更新代码并重启 |
| `openclaw-node uninstall` | 卸载节点 |

## systemd 守护

安装脚本自动配置 systemd 服务：

- **自动重启**：进程挂掉 10 秒后自动重启
- **开机自启**：服务器重启后自动启动
- **资源限制**：内存上限 2G，CPU 上限 80%
- **频率保护**：60 秒内最多重启 5 次

## 连接机制

- 启动时通过 `appId + key + token` 三重验证向 Hub 注册
- 注册成功获得 `nodeId` + `sessionToken`
- 每 10 秒发送心跳（CPU/内存/磁盘）
- 每 30 秒从 Hub 同步任务
- 每 60 秒从 Hub 同步技能
- 断线自动重连（指数退避，最大间隔 5 分钟）

## 子节点权限

| 操作 | 权限 |
|------|------|
| 查看分配的任务 | ✅ 只读 |
| 标记任务开始/完成/失败 | ✅ 报告给 Hub |
| 本地记忆管理 | ✅ 可增删改 |
| 查看技能列表 | ✅ 只读 |
| 系统监控 | ✅ 本地数据 |
| 管理其他节点 | ❌ 无权限 |
| Agent/审批/规则管理 | ❌ 无权限 |

## 环境变量

| 变量 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `HUB_URL` | ✅ | Hub 主节点地址 | — |
| `APP_ID` | ✅ | 节点 App ID | — |
| `APP_KEY` | ✅ | 节点密钥 | — |
| `APP_TOKEN` | ✅ | 节点令牌 | — |
| `NODE_NAME` | — | 节点显示名称 | hostname |
| `NODE_PORT` | — | 监听端口 | 3100 |
| `DATA_DIR` | — | 数据存储目录 | ./data |

## 故障排查

| 问题 | 排查 |
|------|------|
| 注册失败 403 | `openclaw-node config` 检查凭证是否正确 |
| 心跳失败 | 检查网络连通性：`curl -s $HUB_URL/api/health` |
| 进程反复重启 | `openclaw-node logs-tail 50` 查看错误日志 |
| 任务为空 | 确认 Hub 已将任务分配到此节点 |
| 端口冲突 | `openclaw-node edit-config` 修改端口后重启 |
| 内存不足 | 检查服务器内存，调整 systemd MemoryMax |

## 卸载

```bash
openclaw-node uninstall
# 或手动:
systemctl stop openclaw-node && systemctl disable openclaw-node
rm /etc/systemd/system/openclaw-node.service && systemctl daemon-reload
rm /usr/local/bin/openclaw-node
```
