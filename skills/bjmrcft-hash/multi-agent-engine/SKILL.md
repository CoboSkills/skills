---
name: multi-agent-orchestrator
description: 多代理编排引擎 - 目标驱动的深度研究与项目协作系统。支持任务分解、分支执行、验证审核、返工迭代、智能决策。遵循第一性原理，实现主代理与分支代理的双向通信。触发词：多代理、multi-agent、代理编排、深度研究、目标分解、任务委派、工作流、agent orchestrate、multi agent
---

# 多代理编排引擎 v7.0 (Multi-Agent Orchestrator)

> **v7.0 变更**: 环境验证系统 + 模型特征自定义覆盖 + 版本检查 + 第三方部署文档

## 环境依赖

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| OpenClaw | **2026.3.x+** | 需要 `sessions_spawn`、`subagents`、`sessions_send` API |
| Node.js | 20.x+ | ES Module 支持 |
| 操作系统 | Windows / macOS / Linux | 路径自动适配（`USERPROFILE` / `HOME`） |

**启动前检查**：`多代理 check_env` — 验证 OpenClaw 版本和工具可用性

## 第三方部署说明

### 兼容性保证
- ✅ **路径无关**：所有路径通过 `process.env.USERPROFILE || process.env.HOME` 动态计算
- ✅ **配置驱动**：模型池、代理配置、角色映射均从外部 JSON 读取，无硬编码
- ✅ **跨平台**：纯 Node.js + `path` 模块，Windows/macOS/Linux 兼容
- ✅ **模型自适应**：自动扫描 `openclaw.json` 中的 providers + fallbacks

### 自定义规则（可选）

在 workspace 根目录创建 `.model-selector-rules.json` 覆盖启发式推断：

```json
{
  "traits": {
    "your-provider/special-model": ["analysis", "research"],
    "another-provider/code-model": ["coding"]
  },
  "tiers": {
    "your-provider/paid-model": "standard",
    "your-provider/free-model": "free"
  },
  "boost": {
    "your-provider/premium-model": 20
  }
}
```

### 不降级策略

本系统**不提供降级方案**。如果环境检查失败（`check_env` 返回错误），说明 OpenClaw 版本过低或缺少必需 API，必须升级 OpenClaw 到 2026.3.x+ 才能使用。

## 概述

目标驱动的深度研究与项目协作系统，通过 `sessions_spawn` 实现多代理并行执行。

```
提纲确认 → 复杂度评估 → 路由 → plan → 并行执行 → 收集验证 → 重试/降级 → Critic审核 → 聚合 → 完成
```

## 🔴 铁律（不可违反）

1. **质量优先**：质量 > 速度。未经用户明确确认，不得以任何理由降低标准、裁剪流程、省略审核
2. **流程不可跳跃**：6 个 Phase 必须按顺序执行，Critic 审核为强制门禁，不可跳过
3. **看板强制输出**：每个阶段完成后必须调用看板函数并展示给用户
4. **聚合不可省略**：即使 100% 成功也必须执行聚合

## 核心能力

- **📋 提纲确认门**（v6 新增）——用户提交目标后，主代理先生成研究提纲，用户确认后才启动协同流程
- **复杂度路由**：简单任务直接完成，中等任务主代理+验证，复杂任务完整多代理并行
- **异构模型分配**：按角色+复杂度自动选择最优模型，同批次不重复
- **增强重试**：区分 6 种错误类型（超时/API错误/空输出/文件缺失/质量不合格/崩溃），针对性重试
- **双看板系统**（v6 新增）——计划看板（Plan）+ 执行看板（Execution），含调用模型/Tokens/文件验证
- **降级协议**：60%成功→主代理补做，30%→重试，<30%→全接管
- **返工机制**：Critic 审核不通过时，自动触发子代理返工循环
- **输出分层**（v6 新增）——按「研究任务/版本/交付物」三级目录隔离，不同任务互不干扰
- **归档清理**：工作流完成后一键归档产出物 + 清理临时文件

## 快速开始

### 一键启动

```
多代理 run --goal "研究人工智能在医疗领域的应用前景"
```

### 模型配置（首次使用必做）

```
多代理 setup                   # 查看当前配置
多代理 setup_recommended       # 查看基于模型库的推荐配置
多代理 setup_confirm           # 确认并保存推荐配置
```

### 高级命令
```
多代理 check_env               # 检查 OpenClaw 版本和工具可用性（首次启动必做）
多代理 thinking_capabilities   # 查看模型 Thinking 支持矩阵
多代理 check_changes           # 检测模型池变更
```

### 分步执行

```
多代理 plan --goal "目标"       # 生成 JSON 执行计划
多代理 dashboard                # 查看任务看板
多代理 model_pool               # 查看可用模型池
多代理 archive --workflow_id X  # 归档产出物
```

## 执行流程

```
用户提交目标
  ↓
Phase 0: 提纲确认 ← 展示研究提纲 → 用户确认/修改/取消
  ↓
Phase 1: plan → 生成执行计划 + 计划看板
  ↓
Phase 2: spawn → 并行启动子代理 → yield 等待
  ↓
Phase 3: collect → 检查文件 → 评估 → 降级/继续
  ↓
Phase 4: critic → Critic 审核 → 通过/返工
  ↓
Phase 5: aggregate → 融合为 FINAL_REPORT.md
  ↓
Phase 6: finalize → 输出执行摘要
```

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    主代理 (Coordinator)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ 提纲确认  │  │ 结果验证  │  │ 降级补做  │  │ 聚合  │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
└────────┬────────────────────────────────────────────────┘
         │ sessions_spawn
  ┌──────▼──────┐ ┌───────────┐ ┌───────────┐ ┌─────────┐
  │  Research   │ │ Technical │ │ Strategy  │ │ Critic  │
  │  _Analyst   │ │ Specialist│ │ _Analyst  │ │ (独立)  │
  └─────────────┘ └───────────┘ └───────────┘ └─────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
         shared/researches/{slug}_{date}/v{n}/
```

## 输出目录结构

```
shared/
├── boards/                          # 看板 JSON
│   ├── wf_xxx_plan.json
│   └── wf_xxx_exec.json
├── researches/                      # 按研究任务隔离
│   ├── ev-overseas_20260403/       # ← 任务A
│   │   ├── v1/                      #   第一轮
│   │   │   ├── Research_Analyst_report.md
│   │   │   ├── Technical_Specialist_report.md
│   │   │   ├── Strategy_Analyst_report.md
│   │   │   └── Critic_report.md
│   │   ├── v2/                      #   返工轮
│   │   │   ├── Research_Analyst_report_v2.md
│   │   │   └── ...
│   │   └── final/                   #   最终交付物
│   │       └── FINAL_REPORT.md
│   └── ai-healthcare_20260405/     # ← 任务B（完全隔离）
└── archive/                          # 归档目录
```

## 命令速查

| 命令 | 说明 |
|------|------|
| `plan --goal "X"` | 生成 JSON 执行计划 + 看板 |
| `run --goal "X"` | 生成执行计划 + 文本指南 |
| `dashboard [--workflow_id X]` | 查看任务看板 |
| `model_pool` | 查看可用模型池 |
| `diagnose --result "X"` | 诊断失败原因 |
| `archive --workflow_id X` | 归档产出物 |
| `clean [--dry_run true]` | 清理临时文件 |
| `archive_and_clean --workflow_id X` | 一键归档+清理 |

**代理管理：** `list` / `create` / `template --type research|technical|critical|coordinator|advocate|developer`

**工作流：** `workflow_list`

**验证/聚合/决策：** `validate` / `aggregate` / `decide` / `generate_prompt` / `generate_feedback`

## 与 OpenClaw 工具的配合

本技能提供配置、验证、聚合、决策等能力，实际的代理执行使用 OpenClaw 内置工具：

```
# 创建子代理（主代理的核心调用）
sessions_spawn --task "子任务描述" --runtime subagent --mode run

# 查看子代理状态
subagents --action list

# 向子代理发送消息
sessions_send --sessionKey "xxx" --message "指令"
```

## 配置存储

- 代理配置: `.multi-agent-profiles.json`
- 工作流状态: `.multi-agent-workflows.json`

## 详细文档

- **运行时操作协议**：见 [references/protocols.md](references/protocols.md)（提纲确认、复杂度评估、超时预设、降级协议、看板体系、分层目录等完整规范）
