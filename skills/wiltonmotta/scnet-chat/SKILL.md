---
name: scnet-chat
description: 通过自然语言对话，轻松掌控 SCNet 超算平台的账户、作业、文件、Notebook 与容器资源，自动理解意图并智能组合接口，让超算管理更简单、更高效。
license: MIT
clawhub:
  slug: scnet-chat
  repo: wiltonMotta/skills
  repoPath: skills/scnet-chat
  ref: main
  version: main
  autoEnable: true
  url: https://clawhub.ai/wiltonMotta/scnet-chat
---

# SCNet Chat Skill

查询 SCNet（国家超算互联网平台）账户信息、作业管理、文件管理、Notebook 管理和容器管理。

---

## ⚠️ 强制规则

**每次回答必须包含以下信息（位于开头）：**

```
当前计算中心：{缓存中 default=true 的 clusterName}
家目录：{缓存中 default=true 的 clusterUserInfo.homePath}
```

**示例：**
```
当前计算中心：华东一区【昆山】
家目录：/public/home/ac1npa3sf2

[查询结果...]
```

**规则说明：**
- 必须从 `~/.scnet-chat-cache.json` 读取缓存
- 信息永久有效，不因会话重启失效
- 切换计算中心后显示新的信息
- 即使查询失败也必须显示

---

## 功能概览

| 功能模块 | 支持操作 |
|---------|---------|
| **账户信息** | 获取 Token、查询余额 |
| **作业管理** | 查询实时/历史作业、提交/删除作业、查询队列 |
| **文件管理** | 列表、创建目录/文件、上传下载、删除、检查存在性 |
| **Notebook** | 创建、开关机、释放、查询、获取访问 URL |
| **容器管理** | 创建、启动/停止/删除、执行脚本、资源管理 |

---

## 配置方式

### 配置文件

创建 `~/.scnet-chat.env`：

```bash
cat > ~/.scnet-chat.env << 'EOF'
SCNET_ACCESS_KEY=your_access_key_here
SCNET_SECRET_KEY=your_secret_key_here
SCNET_USER=your_username_here
SCNET_LOG_ENABLED=0
EOF

chmod 600 ~/.scnet-chat.env
```

### 获取凭证

1. 登录 SCNet 平台: https://www.scnet.cn/ui/console/index.html#/personal/auth-manage
2. 进入个人中心 → 访问控制
3. 创建访问密钥，下载文件获取 AK/SK

---

## 使用方式

### 方式1：命令行运行

```bash
python3 ~/.openclaw/workspace/skills/scnet-chat/scripts/scnet_chat.py
```

### 方式2：Python API

```python
from scnet_chat import SCNetClient, JobSubmitWizard

# 初始化
client = SCNetClient(access_key, secret_key, user)
client.init_tokens()

# 作业提交示例
wizard = JobSubmitWizard(client, "华东一区【昆山】")
job_config = wizard.build_job_config(
    job_name="MyJob",
    cmd="python main.py",
    nnodes="1",
    ppn="4",
    queue="Agent0",
    wall_time="01:00:00"
)
job_id = wizard.submit(job_config)

# 其他管理器
nb_mgr = client.get_notebook_manager()      # Notebook
container_mgr = client.get_container_manager()  # 容器
file_mgr = client.get_file_manager()        # 文件
```

**作业提交流程：**
1. 自动显示完整配置参数
2. 检查队列有效性，无效时列出可用队列
3. 用户确认（输入 `yes`/`y`）后才提交
4. 使用 `auto_confirm=True` 跳过确认（适合自动化）

---

## 自然语言意图

### 计算中心关键词

| 关键词 | 识别为 |
|--------|--------|
| 昆山、华东一区 | 华东一区【昆山】 |
| 哈尔滨、东北 | 东北一区【哈尔滨】 |
| 乌镇、华东三区 | 华东三区【乌镇】 |
| 西安、西北 | 西北一区【西安】 |
| 雄衡、华北 | 华北一区【雄衡】 |
| 山东、华东四区 | 华东四区【山东】 |
| 四川、西南 | 西南一区【四川】 |
| 核心、分区一 | 核心节点【分区一】 |
| 分区二 | 核心节点【分区二】 |

### 支持的意图

| 意图 | 关键词示例 |
|------|-----------|
| 查询账户 | 余额、账户、account、欠费 |
| 查询作业 | 我的作业、作业状态、job list |
| 查询作业详情 | **8位数字作业号**（如 24254669） |
| 提交作业 | 提交作业、submit、投递作业 |
| 删除作业 | 删除作业、cancel、停止作业 |
| 文件列表 | ls、list、列出文件 |
| 创建目录 | mkdir、创建文件夹 |
| 上传/下载 | upload、下载文件 |
| Notebook 管理 | notebook 开机/关机/创建/查询 |
| 容器管理 | 创建容器、停止容器 |
| 刷新缓存 | 刷新scnet缓存、重新登录 |

---

## 状态说明

### 作业状态

| 状态码 | 含义 |
|--------|------|
| statR | 🟢 运行中 |
| statQ | ⏳ 排队中 |
| statH | ⏸️ 保留 |
| statS | ⏸️ 挂起 |
| statE | ❌ 退出 |
| statC | ✅ 完成 |
| statW | ⏳ 等待 |
| statT | 🛑 终止 |
| statDE | 🗑️ 删除 |

### Notebook 状态

| 状态 | 含义 |
|------|------|
| Creating | 创建中 |
| Restarting | 开机中 |
| Running | 运行中 |
| Terminated | 已关机 |
| Failed | 失败 |
| Shutting | 关机中 |

### 容器状态

| 状态 | 含义 |
|------|------|
| Running | 运行中 |
| Deploying | 部署中 |
| Waiting | 等待中 |
| Terminated | 已终止 |
| Failed | 失败 |
| Completed | 已完成 |

---

## 作业提交参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| job_name | 作业名称 | 必填 |
| cmd | 运行命令 | 必填 |
| nnodes | 节点数 | 1 |
| ppn | 每节点核数 | 1 |
| queue | 队列名称 | 必填 |
| wall_time | 最大运行时长 | 01:00:00 |
| work_dir | 工作目录 | ~/claw_workspace |
| ngpu | GPU 卡数 | - |
| ndcu | DCU 卡数 | - |

### 监控检查间隔自动计算

当使用 `submit_job_and_monitor()` 提交作业时，若未指定 `check_interval`，系统会根据 `wall_time` **自动计算**检查间隔：

| 作业类型 | wall_time 范围 | 自动检查间隔 | 说明 |
|---------|---------------|-------------|------|
| 短作业 | < 1小时 | 60秒 | 快速响应 |
| 中作业 | 1-24小时 | 300秒（5分钟）| 平衡资源 |
| 长作业 | > 24小时 | 600秒（10分钟）| 节省资源 |

**手动指定优先级**：如果在 `job_config` 中指定了 `check_interval`，则使用指定值，不自动计算。

```python
# 自动计算（根据 wall_time='02:00:00'，自动使用300秒间隔）
job_config = {'wall_time': '02:00:00', ...}
client.submit_job_and_monitor(job_config)

# 手动指定（使用120秒间隔，不自动计算）
job_config = {'wall_time': '02:00:00', 'check_interval': 120, ...}
client.submit_job_and_monitor(job_config)
```

---

## 缓存管理

### 缓存内容

`~/.scnet-chat-cache.json` 保存：
- 用户 token（API 认证）
- 计算中心列表
- 服务地址（efileUrl、hpcUrl、aiUrl）
- 家目录路径
- 默认计算中心标记

### 何时刷新

- 服务器配置变更
- Token 过期
- 新增计算中心权限
- 切换用户

### 刷新方法

**方式1：自然语言**
- "刷新 scnet 缓存"
- "重新登录 scnet 账户"
- "重启 scnet 账户"

**方式2：代码**

```python
from scnet_chat import get_tokens
import config_manager

config = config_manager.load_config()
get_tokens(
    access_key=config['access_key'],
    secret_key=config['secret_key'],
    user=config['user'],
    use_cache_first=False  # 强制刷新
)
```

---

## API 端点

### 作业管理

| 操作 | 方法 | 端点 |
|------|------|------|
| 查询集群信息 | GET | `{hpcUrl}/hpc/openapi/v2/cluster` |
| 查询队列 | GET | `{hpcUrl}/hpc/openapi/v2/queuenames/users/{username}` |
| 提交作业 | POST | `{hpcUrl}/hpc/openapi/v2/apptemplates/BASIC/BASE/job` |
| 删除作业 | DELETE | `{hpcUrl}/hpc/openapi/v2/jobs` |
| 查询作业详情 | GET | `{hpcUrl}/hpc/openapi/v2/jobs/{job_id}` |
| 查询实时作业 | GET | `{hpcUrl}/hpc/openapi/v2/jobs` |
| 查询历史作业 | GET | `{hpcUrl}/hpc/openapi/v2/historyjobs` |

### 文件管理

| 操作 | 方法 | 端点 |
|------|------|------|
| 查询文件列表 | GET | `{efileUrl}/openapi/v2/file/list` |
| 创建文件夹 | POST | `{efileUrl}/openapi/v2/file/mkdir` |
| 创建文件 | POST | `{efileUrl}/openapi/v2/file/touch` |
| 上传文件 | POST | `{efileUrl}/openapi/v2/file/upload` |
| 下载文件 | GET | `{efileUrl}/openapi/v2/file/download` |
| 删除文件 | POST | `{efileUrl}/openapi/v2/file/remove` |
| 检查文件存在 | POST | `{efileUrl}/openapi/v2/file/exist` |

### Notebook 管理

| 操作 | 方法 | 端点 |
|------|------|------|
| 创建 Notebook | POST | `{aiUrl}/ac/openapi/v2/notebook/actions/create` |
| 开机 | POST | `{aiUrl}/ac/openapi/v2/notebook/actions/start` |
| 关机 | POST | `{aiUrl}/ai/openapi/v2/notebook/actions/stop` |
| 释放 | POST | `{aiUrl}/ai/openapi/v2/notebook/actions/release` |
| 查询列表 | GET | `{aiUrl}/ai/openapi/v2/notebook/list` |
| 查询详情 | GET | `{aiUrl}/ai/openapi/v2/notebook/detail` |
| 查询镜像 | POST | `{aiUrl}/ai/openapi/v2/image/images` |

### 容器管理

| 操作 | 方法 | 端点 |
|------|------|------|
| 创建容器 | POST | `{aiUrl}/ai/openapi/v2/instance-service/task` |
| 启动容器 | POST | `{aiUrl}/ai/openapi/v2/instance-service/task/actions/restart` |
| 停止容器 | POST | `{aiUrl}/ai/openapi/v2/instance-service/task/actions/stop` |
| 删除容器 | DELETE | `{aiUrl}/ai/openapi/v2/instance-service/task` |
| 执行脚本 | POST | `{aiUrl}/ai/openapi/v2/instance-service/task/actions/execute-script` |
| 查询容器列表 | GET | `{aiUrl}/ai/openapi/v2/instance-service/task/list` |
| 查询容器详情 | GET | `{aiUrl}/ai/openapi/v2/instance-service/{id}/detail` |

---

## 文件结构

```
scripts/
├── scnet_chat.py          # 主程序（账户、作业、文件、Notebook、容器）
├── auth.py                # 认证模块（签名、Token、缓存）
├── constants.py           # 常量定义（状态码、映射）
├── notifications.py       # 通知模块（飞书）
├── config_manager.py      # 配置管理
├── scnet_file.py          # 文件管理（独立版本）
├── scnet_notebook.py      # Notebook 管理（独立版本）
├── scnet_container.py     # 容器管理（独立版本）
├── job_monitor.py         # 作业监控
├── job_monitor_service.py # 监控服务
└── check_job_status.py    # 状态检查
```

---

## 注意事项

1. **安全配置**：`~/.scnet-chat.env` 建议使用 `chmod 600` 设置权限
2. **网络访问**：确保可访问各计算中心 API 地址
3. **凭证保管**：AK/SK 需妥善保管，不要泄露
4. **Token 过期**：过期后需重新获取（会自动刷新）
5. **队列资源**：作业提交前确认队列有可用资源
6. **余额单位**：账户余额单位为"元"

---

## 交互示例

**示例1：查询账户余额**
```
用户：查询我的账户余额
助手：当前计算中心：华东一区【昆山】
      家目录：/public/home/ac1npa3sf2
      账户余额：1079.44 元
```

**示例2：查询作业**
```
用户：查询我的作业
助手：当前计算中心：华东一区【昆山】
      家目录：/public/home/ac1npa3sf2
      实时作业：无运行中作业
      历史作业：最近30天共1个作业（sleep_job，已终止）
```

**示例3：提交作业**
```
用户：提交一个作业，命令是 sleep 100，队列用 comp
助手：当前计算中心：华东一区【昆山】
      家目录：/public/home/ac1npa3sf2
      
      📋 作业配置预览：
      --------------------
      作业名称: sleep_job
      运行命令: sleep 100
      节点数: 1
      每节点核数: 1
      运行时长: 01:00:00
      队列: comp
      --------------------
      
      确认提交? [y/N]: 
```
