/**
 * 多代理编排引擎 (Multi-Agent Orchestrator)
 * 完整的目标驱动深度研究与项目协作系统
 * 
 * 功能模块：
 * 1. 代理配置管理 - 角色、职责、协议定义
 * 2. 工作流引擎 - 流程编排、状态管理
 * 3. 验证器 - 产出质量检查
 * 4. 聚合器 - 结果汇总融合
 * 5. 通信总线 - 代理间通信协议
 * 6. 决策引擎 - 智能决策与人工介入
 */

import fs from "fs";
import path from "path";

// ===== 核心模块 =====
import {
  buildSpawnParams, buildParallelSpawnParams, collectResults,
  validateAgentOutput, aggregateResults, buildCriticTask,
  buildExecutionPlan, saveExecutionPlan, loadExecutionPlan,
  // 分层目录
  buildOutputDirs, buildOutputPath,
  // 看板系统
  createPlanBoard, createExecBoard, updateExecBoard, loadExecBoard, formatExecBoard,
  // 重试 + 降级
  selectModel, selectBatchModels,
  diagnoseFailure, buildRetrySpawn, assessDegradation, buildDegradationPlan,
  ErrorType, DegradationLevel,
  // 归档清理
  archiveWorkflow, cleanShared, generateFinalSummary, archiveAndClean,
  // 环境验证
  validateEnvironment
} from './lib/executor.js';

import { getModelPoolInfo } from './lib/modelSelector.js';
import {
  detectPoolChanges, recommendRoleConfig,
  loadRoleConfig, saveRoleConfig, patchRoleConfig,
  needsSetup, generateSetupPrompt,
  checkForModelChanges,
  formatRecommendationReport, formatChangeNotification,
  buildRoleSpawnParams, ensureThinkingEnabled
} from './lib/modelAdaptation.js';
import {
  checkModelThinking, selectThinkingLevel, degradeThinking,
  verifyThinkingExecution, setUserOverride,
  getCapabilitiesSummary, formatCapabilitiesTable
} from './lib/thinkingCapabilities.js';

import { 
  VALIDATION_RULESETS, validate, formatValidationReport 
} from './lib/validator.js';
import { 
  AGGREGATION_TEMPLATES, aggregate, formatAggregation 
} from './lib/aggregator.js';
import { 
  COMMUNICATION_PROTOCOLS,
  generateAgentPrompt, generateFeedbackPrompt
} from './lib/communication.js';

// ===================== 配置存储 =====================

const CONFIG_DIR = path.join(process.env.USERPROFILE || process.env.HOME, ".openclaw", "workspace");
const PROFILES_FILE = path.join(CONFIG_DIR, ".multi-agent-profiles.json");
const WORKFLOWS_FILE = path.join(CONFIG_DIR, ".multi-agent-workflows.json");
const HISTORY_FILE = path.join(CONFIG_DIR, ".multi-agent-history.json");

function loadJSON(filepath, defaultVal = {}) {
  try {
    if (!fs.existsSync(filepath)) {
      fs.mkdirSync(path.dirname(filepath), { recursive: true });
      fs.writeFileSync(filepath, JSON.stringify(defaultVal, null, 2), "utf-8");
      return defaultVal;
    }
    return JSON.parse(fs.readFileSync(filepath, "utf-8"));
  } catch { return defaultVal; }
}

function saveJSON(filepath, data) {
  const backup = filepath + ".bak";
  if (fs.existsSync(filepath)) fs.copyFileSync(filepath, backup);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2), "utf-8");
}

// ===================== 命令处理器 =====================

const commands = {
  // ========== 环境检查 ==========
  
  check_env: () => {
    const result = validateEnvironment();
    let output = `🔍 多代理环境检查\n${'═'.repeat(50)}\n\n`;
    
    output += `📌 OpenClaw 版本: ${result.version}\n`;
    output += `📌 运行环境: ${result.isAgentRuntime ? 'Agent 模式' : 'CLI 模式'}\n\n`;
    
    if (result.errors.length > 0) {
      output += `❌ 错误 (${result.errors.length}):\n`;
      for (const e of result.errors) output += `  - ${e}\n`;
      output += '\n';
    }
    
    if (result.warnings.length > 0) {
      output += `⚠️ 注意:\n`;
      for (const w of result.warnings) output += `  ${w}\n\n`;
    }
    
    const status = result.valid ? '✅ 环境验证通过，可在 Agent 环境中执行多代理任务' : '❌ 环境不满足要求，请修复后重试';
    output += `${status}\n`;
    return output;
  },

  // ========== 系统初始化 ==========
  
  init: (params) => {
    const config = loadJSON(PROFILES_FILE, { agents: [] });
    const agents = config.agents || [];
    
    if (agents.length === 0) {
      return "⚠️ 没有配置任何代理。请先使用 `多代理 create` 或 `多代理 template` 创建代理配置。";
    }
    
    const created = [];
    const existed = [];
    
    for (const agent of agents) {
      const agentWorkspace = path.join(CONFIG_DIR, 'agents', agent.name);
      if (fs.existsSync(agentWorkspace)) {
        existed.push(agent.name);
      } else {
        fs.mkdirSync(agentWorkspace, { recursive: true });
        created.push(agent.name);
      }
    }
    
    let output = `🏗️ 多代理系统初始化\n${'═'.repeat(50)}\n\n`;
    
    if (created.length > 0) {
      output += `✅ 已创建永久工作区 (${created.length} 个):\n`;
      for (const name of created) {
        output += `   📁 agents/${name}/\n`;
      }
      output += '\n';
    }
    
    if (existed.length > 0) {
      output += `ℹ️ 已存在工作区 (${existed.length} 个):\n`;
      for (const name of existed) {
        output += `   📁 agents/${name}/\n`;
      }
      output += '\n';
    }
    
    output += `💡 使用说明:\n`;
    output += `   • 永久工作区用于存放各代理的历史研究会话子目录\n`;
    output += `   • 每次研究任务会自动创建 {简写}_{时间戳} 子目录\n`;
    output += `   • 归档时仅清理 shared/，agents/ 永久保留\n`;
    
    return output;
  },

  // ========== 代理配置管理 ==========
  
  list: (params) => {
    const config = loadJSON(PROFILES_FILE, { agents: [] });
    let agents = config.agents || [];
    if (params.keyword) {
      const kw = params.keyword.toLowerCase();
      agents = agents.filter(a => 
        a.name.toLowerCase().includes(kw) ||
        (a.description || "").toLowerCase().includes(kw) ||
        (a.capabilities || []).some(c => c.toLowerCase().includes(kw))
      );
    }
    if (agents.length === 0) return "📋 当前没有代理配置。使用 `多代理 create` 或 `多代理 template` 创建。";
    
    let output = `📋 代理配置列表 (共 ${agents.length} 个)\n${'─'.repeat(50)}\n`;
    for (const a of agents) {
      output += `\n🔹 ${a.name}\n`;
      output += `   描述: ${a.description}\n`;
      output += `   能力: ${(a.capabilities || []).join(', ')}\n`;
      output += `   输出: ${a.output_format || 'markdown'} | 协议: ${a.protocol || 'HTTP'}\n`;
      output += `   工具: ${(a.tools || []).join(', ')}\n`;
    }
    return output;
  },

  create: (params) => {
    if (!params.name) return "❌ 缺少 --name 参数";
    const config = loadJSON(PROFILES_FILE, { agents: [] });
    if (config.agents.find(a => a.name === params.name)) {
      return `❌ 代理 "${params.name}" 已存在`;
    }
    const agent = {
      name: params.name,
      description: params.description || "",
      capabilities: Array.isArray(params.capabilities) ? params.capabilities : 
                    (params.capabilities || "").split(",").map(s => s.trim()).filter(Boolean),
      output_format: params.output_format || "markdown",
      protocol: params.protocol || "HTTP",
      tools: Array.isArray(params.tools) ? params.tools : 
             (params.tools || "").split(",").map(s => s.trim()).filter(Boolean),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    config.agents.push(agent);
    saveJSON(PROFILES_FILE, config);
    return `✅ 已创建代理配置: ${agent.name}`;
  },

  edit: (params) => {
    if (!params.name || !params.field) return "❌ 缺少 --name 或 --field 参数";
    const config = loadJSON(PROFILES_FILE, { agents: [] });
    const agent = config.agents.find(a => a.name === params.name);
    if (!agent) return `❌ 代理 "${params.name}" 不存在`;
    
    const editable = ["description", "capabilities", "output_format", "protocol", "tools"];
    if (!editable.includes(params.field)) return `❌ 不可编辑字段 "${params.field}"`;
    
    if (["capabilities", "tools"].includes(params.field)) {
      agent[params.field] = Array.isArray(params.value) ? params.value : 
                           params.value.split(",").map(s => s.trim());
    } else {
      agent[params.field] = params.value;
    }
    agent.updated_at = new Date().toISOString();
    saveJSON(PROFILES_FILE, config);
    return `✅ 已更新 "${params.name}" 的 ${params.field}`;
  },

  delete: (params) => {
    if (!params.name) return "❌ 缺少 --name 参数";
    const config = loadJSON(PROFILES_FILE, { agents: [] });
    const idx = config.agents.findIndex(a => a.name === params.name);
    if (idx === -1) return `❌ 代理 "${params.name}" 不存在`;
    config.agents.splice(idx, 1);
    saveJSON(PROFILES_FILE, config);
    return `✅ 已删除代理配置: ${params.name}`;
  },

  search: (params) => {
    if (!params.keyword) return "❌ 缺少 --keyword 参数";
    return commands.list(params);
  },

  template: (params) => {
    const TEMPLATES = {
      research: { name: 'Research_Analyst', description: '负责深入研究和数据分析', capabilities: ['文献检索','数据分析','报告撰写','信息综合'], output_format: 'research_report.md', tools: ['web_search','web_fetch','workspace.read','workspace.write'] },
      technical: { name: 'Tech_Analyst', description: '负责技术可行性分析和架构设计', capabilities: ['编程','架构设计','技术评估','代码审查'], output_format: 'technical_report.md', tools: ['workspace.read','workspace.write','exec'] },
      critical: { name: 'Critical_Reviewer', description: '以批判性思维从多维度评估成果', capabilities: ['批判性分析','逻辑推理','质量评估','风险识别'], output_format: 'critical_review.md', tools: ['workspace.read'] },
      coordinator: { name: 'Coordinator', description: '协调多个子代理的工作', capabilities: ['任务分解','进度跟踪','结果汇总','决策制定'], output_format: 'coordination_report.md', tools: ['sessions_spawn','sessions_send','subagents','workspace.read','workspace.write'] },
      advocate: { name: 'Advocate', description: '为某一观点提供有力论证', capabilities: ['论证构建','证据收集','说服表达'], output_format: 'argument_report.md', tools: ['web_search','workspace.read'] },
      developer: { name: 'Developer', description: '负责代码实现和技术开发', capabilities: ['编程','调试','测试','文档'], output_format: 'code', tools: ['workspace.read','workspace.write','exec'] }
    };
    if (!params.type) return `❌ 缺少 --type 参数，可用: ${Object.keys(TEMPLATES).join(', ')}`;
    const tmpl = TEMPLATES[params.type];
    if (!tmpl) return `❌ 未知模板 "${params.type}"，可用: ${Object.keys(TEMPLATES).join(', ')}`;
    return commands.create(tmpl);
  },

  // ========== 工作流管理（兼容层）==========
  // 注：新版执行引擎使用 buildExecutionPlan + sessions_spawn 驱动
  // 以下命令保留用于向后兼容，但不再依赖旧的 workflow.js 状态机

  workflow_list: () => {
    return `🔄 可用工作流模板\n${'─'.repeat(50)}\n` +
      `\n🔹 deep_research: 深度研究流程\n` +
      `   分解 → 并行执行 → 收集验证 → Critic审核 → 聚合 → 终稿\n`;
  },

  // ========== 验证器 ==========

  validate: (params) => {
    if (!params.result || !params.ruleset) return "❌ 缺少 --result 或 --ruleset 参数";
    try {
      const result = validate(params.result, params.ruleset, { goal: params.goal });
      return formatValidationReport(result);
    } catch (e) {
      return `❌ ${e.message}`;
    }
  },

  validation_rulesets: () => {
    let output = `📋 可用验证规则集\n${'─'.repeat(50)}\n`;
    for (const [key, rs] of Object.entries(VALIDATION_RULESETS)) {
      output += `\n🔹 ${key}: ${rs.name}\n`;
      output += `   通过阈值: ${Math.round(rs.pass_threshold * 100)}%\n`;
      output += `   规则: ${rs.rules.map(r => r.name).join(', ')}\n`;
    }
    return output;
  },

  // ========== 聚合器 ==========

  aggregate: (params) => {
    if (!params.template) return "❌ 缺少 --template 参数";
    try {
      const results = params.results || [];
      const aggregated = aggregate(results, params.template, params.goal);
      return formatAggregation(aggregated);
    } catch (e) {
      return `❌ ${e.message}`;
    }
  },

  aggregation_templates: () => {
    let output = `📊 可用聚合模板\n${'─'.repeat(50)}\n`;
    for (const [key, tmpl] of Object.entries(AGGREGATION_TEMPLATES)) {
      output += `\n🔹 ${key}: ${tmpl.name}\n`;
      output += `   策略: ${tmpl.strategy}\n`;
      if (tmpl.sections) {
        output += `   章节: ${tmpl.sections.map(s => s.name).join(', ')}\n`;
      }
    }
    return output;
  },

  // ========== 通信协议 ==========

  protocols: () => {
    let output = `📡 可用通信协议\n${'─'.repeat(50)}\n`;
    for (const [key, proto] of Object.entries(COMMUNICATION_PROTOCOLS)) {
      output += `\n🔹 ${key}: ${proto.name}\n`;
      output += `   ${proto.description}\n`;
      output += `   超时: ${proto.timeout_minutes} 分钟\n`;
    }
    return output;
  },

  generate_prompt: (params) => {
    if (!params.agent || !params.task) return "❌ 缺少 --agent 或 --task 参数";
    const agent = typeof params.agent === 'string' ? JSON.parse(params.agent) : params.agent;
    const task = typeof params.task === 'string' ? { description: params.task } : params.task;
    return generateAgentPrompt(agent, task, params.protocol || 'standard_task', params.context || {});
  },

  generate_feedback: (params) => {
    if (!params.task || !params.validation || !params.agent) return "❌ 缺少必要参数";
    return generateFeedbackPrompt(params.task, params.validation, params.agent);
  },

  // ========== 任务看板 ==========

  dashboard: (params) => {
    const execBoard = loadExecBoard(params.workflow_id);
    if (execBoard) {
      return formatExecBoard(execBoard);
    }
    return '📊 当前没有活跃的任务看板。执行多代理任务后自动生成。';
  },

  // ========== 模型池信息 ==========

  model_pool: () => {
    const info = getModelPoolInfo();
    let output = `🧠 模型能力矩阵\n${'═'.repeat(50)}\n\n`;

    for (const [pool, models] of Object.entries(info)) {
      const label = {
        analysis: '📐 深度分析池',
        research: '🔍 搜索研究池',
        critic: '🔍 批判审核池',
        coding: '💻 代码开发池',
        fallback: '🪂 兜底免费池'
      }[pool] || pool;

      output += `${label}:\n`;
      for (const m of models) {
        output += `  • ${m}\n`;
      }
      output += '\n';
    }

    output += `💡 使用方式:\n`;
    output += `  异构模型分配由 modelSelector.js 自动处理\n`;
    output += `  主代理在 buildSpawnParams 时自动选择最优模型\n`;
    output += `  同一批次确保模型不重复（异构博弈）\n`;

    return output;
  },

  // ========== 失败诊断 ==========

  diagnose: (params) => {
    if (!params.error && !params.output_file && !params.tokens) {
      return '❌ 缺少 --error、--output_file 或 --tokens 参数';
    }

    const result = {
      outputFile: params.output_file || null,
      tokensUsed: parseInt(params.tokens) || 0,
      error: params.error || null,
      status: params.status || 'failed'
    };

    const diagnosis = diagnoseFailure(result);
    let output = `🔬 失败诊断报告\n${'═'.repeat(50)}\n\n`;
    output += `📌 错误类型: ${diagnosis.errorType}\n`;
    output += `📝 详情: ${diagnosis.detail}\n`;
    output += `🔧 重试策略: ${diagnosis.strategy.description}\n`;
    output += `   最大重试: ${diagnosis.strategy.maxRetries} 次\n`;
    output += `   超时倍率: ${diagnosis.strategy.timeoutMultiplier}x\n`;
    output += `   换模型: ${diagnosis.strategy.switchModel ? '是' : '否'}\n`;

    return output;
  },

  // ========== 归档清理 ==========

  archive: (params) => {
    const workflow = {
      id: params.workflow_id || `wf_${Date.now()}`,
      goal: params.goal || '未指定',
      template: params.template || 'deep_research',
    };

    const result = archiveWorkflow(workflow);
    let output = `📦 工作流已归档\n${'═'.repeat(50)}\n`;
    output += `📁 归档路径: ${result.archivePath.replace(CONFIG_DIR, '~/.openclaw/workspace')}\n`;
    output += `📄 文件数: ${result.fileCount}\n`;
    output += `💾 总大小: ${Math.round(result.totalSize / 1024)} KB\n`;
    output += `\n${result.summary}\n`;
    return output;
  },

  clean: (params) => {
    const dryRun = params.dry_run === true || params.dry_run === 'true';
    const result = cleanShared({ dryRun });

    let output = `${dryRun ? '🔍 预览清理' : '🧹 已清理 shared/ 目录'}\n${'═'.repeat(50)}\n`;
    output += `📄 文件数: ${result.deleted}\n`;
    output += `💾 释放空间: ${result.freed} KB\n`;

    if (result.files.length > 0) {
      output += `\n文件清单:\n`;
      for (const f of result.files.slice(0, 20)) {
        output += `  ${dryRun ? '⬜' : '🗑️'} ${f}\n`;
      }
      if (result.files.length > 20) {
        output += `  ... 还有 ${result.files.length - 20} 个文件\n`;
      }
    }

    if (dryRun) {
      output += `\n💡 执行 clean（不加 dry_run）实际清理`;
    }

    return output;
  },

  archive_and_clean: (params) => {
    const workflow = {
      id: params.workflow_id || `wf_${Date.now()}`,
      goal: params.goal || '未指定',
      template: params.template || 'deep_research',
    };
    const result = archiveAndClean(workflow);

    let output = result.summary;
    output += `\n🧹 已清理 ${result.cleanResult.deleted} 个临时文件`;
    output += `（释放 ${result.cleanResult.freed} KB）\n`;
    return output;
  },

  // ========== 生成执行计划（结构化 JSON，供 AI 代理驱动）==========

  plan: (params) => {
    if (!params.goal) return "❌ 缺少 --goal 参数";
    const template = params.template || 'deep_research';

    // 1. 生成分层目录
    const directories = buildOutputDirs(
      { slug: (params.goal || 'research').replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, '-').slice(0, 50) },
      parseInt(params.version) || 1
    );

    // 2. 构建执行计划
    const workflow = {
      id: `wf_${Date.now().toString(36)}`,
      name: template,
      goal: params.goal,
      complexity: params.complexity || 'complex',
      route: params.route || 'full',
      phases: [
        { id: 'parallel', name: '并行执行', type: 'parallel' },
        { id: 'critic', name: '批判性审核', type: 'critical_agent' },
        { id: 'aggregate', name: '聚合输出', type: 'main_agent' },
        { id: 'finalize', name: '终稿生成', type: 'main_agent' }
      ]
    };

    // 3. 加载代理配置（修复：plan 命令必须加载 profiles，否则 spawns 为空）
    const profilesData = loadJSON(PROFILES_FILE, { agents: [] });
    const profiles = {};
    if (profilesData.agents && Array.isArray(profilesData.agents)) {
      for (const agent of profilesData.agents) {
        profiles[agent.name] = { ...agent, workspace: path.join(CONFIG_DIR, 'agents', agent.name) };
      }
    }

    // 4. 生成执行计划
    const plan = buildExecutionPlan(workflow, profiles);
    const planPath = saveExecutionPlan(plan, path.join(directories.versionDir, 'execution_plan.json'));

    // 5. 创建计划看板
    const planBoard = createPlanBoard(workflow, plan.phases, directories);

    // 6. 返回 JSON（AI 代理解析后按步骤调用 sessions_spawn）
    return JSON.stringify(plan, null, 2);
  },

  // ========== 完整执行（一键启动，返回文本指南）==========

  run: (params) => {
    if (!params.goal) return "❌ 缺少 --goal 参数";

    // 生成分层目录
    const directories = buildOutputDirs(
      { slug: (params.goal || 'research').replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, '-').slice(0, 50) },
      parseInt(params.version) || 1
    );

    const workflow = {
      id: `wf_${Date.now().toString(36)}`,
      name: params.template || 'deep_research',
      goal: params.goal,
      complexity: params.complexity || 'complex',
      route: params.route || 'full',
      phases: [
        { id: 'parallel', name: '并行执行', type: 'parallel' },
        { id: 'critic', name: '批判性审核', type: 'critical_agent' },
        { id: 'aggregate', name: '聚合输出', type: 'main_agent' },
        { id: 'finalize', name: '终稿生成', type: 'main_agent' }
      ]
    };

    // 加载代理配置
    const profilesData = loadJSON(PROFILES_FILE, { agents: [] });
    const profiles = {};
    if (profilesData.agents && Array.isArray(profilesData.agents)) {
      for (const agent of profilesData.agents) {
        profiles[agent.name] = { ...agent, workspace: path.join(CONFIG_DIR, 'agents', agent.name) };
      }
    }

    // 生成执行计划
    const plan = buildExecutionPlan(workflow, profiles);
    const planPath = saveExecutionPlan(plan, path.join(directories.versionDir, 'execution_plan.json'));

    // 创建看板
    createPlanBoard(workflow, plan.phases, directories);

    // 返回文本指南
    let guide = `🚀 多代理编排 - 执行指南\n${'═'.repeat(50)}\n\n`;
    guide += `📌 目标: ${params.goal}\n`;
    guide += `🔄 工作流: ${workflow.name}\n`;
    guide += `🆔 实例ID: ${workflow.id}\n`;
    guide += `🌐 输出语言: zh-CN\n`;
    guide += `💾 执行计划: ${planPath}\n\n`;

    guide += `📋 阶段流程:\n`;
    for (const phase of plan.phases) {
      const icon = phase.type === 'parallel' ? '⚡' : phase.type === 'critical_agent' ? '🔍' : '🧠';
      guide += `  ${icon} ${phase.name} (${phase.type})`;
      if (phase.spawns && phase.spawns.length > 0) {
        guide += ` → 并行启动 ${phase.spawns.length} 个子代理`;
      }
      guide += `\n`;
    }

    guide += `\n💡 AI 代理使用方式:\n`;
    guide += `  1. 调用 "多代理 plan --goal ..." 获取结构化执行计划\n`;
    guide += `  2. 按 phases 顺序执行：\n`;
    guide += `     - main_agent 阶段：AI 代理自行处理\n`;
    guide += `     - parallel 阶段：使用 spawns[] 参数调用 sessions_spawn\n`;
    guide += `     - critical_agent 阶段：读取聚合结果，生成审核任务\n`;
    guide += `  3. 每阶段完成后读取输出目录下的结果文件\n`;
    guide += `  4. 调用 validate / aggregate 完成质量检查和汇总\n`;
    
    return guide;
  },

  // ========== 快速演示（使用执行引擎）==========

  run_demo: (params) => {
    const goal = params.goal || "研究人工智能在医疗领域的应用前景与局限性";

    // 生成分层目录
    const directories = buildOutputDirs(
      { slug: 'demo-research' },
      1
    );

    const workflow = {
      id: `wf_${Date.now().toString(36)}`,
      name: 'deep_research',
      goal: goal,
      complexity: 'complex',
      route: 'full',
      phases: [
        { id: 'parallel', name: '并行执行', type: 'parallel' },
        { id: 'critic', name: '批判性审核', type: 'critical_agent' },
        { id: 'aggregate', name: '聚合输出', type: 'main_agent' },
        { id: 'finalize', name: '终稿生成', type: 'main_agent' }
      ]
    };

    // 加载代理配置
    const profilesData = loadJSON(PROFILES_FILE, { agents: [] });
    const profiles = {};
    if (profilesData.agents && Array.isArray(profilesData.agents)) {
      for (const agent of profilesData.agents) {
        profiles[agent.name] = { ...agent, workspace: path.join(CONFIG_DIR, 'agents', agent.name) };
      }
    }

    // 生成执行计划
    const plan = buildExecutionPlan(workflow, profiles);
    const planPath = saveExecutionPlan(plan, path.join(directories.versionDir, 'execution_plan.json'));

    // 创建看板
    createPlanBoard(workflow, plan.phases, directories);

    // 返回执行信息
    return `✅ 演示工作流已创建 (ID: ${workflow.id})\n` +
           `📌 目标: ${goal}\n` +
           `💾 执行计划: ${planPath}\n` +
           `🚀 使用 '多代理 plan --goal ...' 获取结构化计划，AI 代理按计划驱动 sessions_spawn`;
  },

  // ========== 模型适配 & Thinking 管理 ==========

  setup: (params) => {
    // 检查首次设置
    if (!loadRoleConfig()) {
      const prompt = generateSetupPrompt();
      if (!prompt.userPrompt) {
        return '⚠️ 未检测到可用模型，请先配置模型提供商';
      }
      return JSON.stringify({
        type: 'setup_required',
        prompt: prompt.userPrompt
      }, null, 2);
    }

    const config = loadRoleConfig();
    let output = '✅ 多代理角色-模型配置（已确认）\n';
    output += '═'.repeat(50) + '\n';
    output += `版本: ${config.version} | 确认时间: ${config.confirmedAt}\n\n`;

    for (const role of ['coordinator', 'critic', 'worker']) {
      const conf = config[role];
      if (conf?.primary) {
        const caps = checkModelThinking(conf.primary);
        output += `${role}: ${conf.primary.split('/').pop()}\n`;
        output += `  Thinking: ${caps.supportsThinking ? conf.thinking || caps.defaultMode : '❌ 不支持'}\n`;
        if (conf.fallbackChain?.length) {
          output += `  Fallback: ${conf.fallbackChain.join(' → ')}\n`;
        }
        output += '\n';
      }
    }

    return output + '💡 如需重新配置: `多代理 setup_recommended`';
  },

  setup_recommended: (params) => {
    const recommendation = recommendRoleConfig();
    if (!recommendation.config) {
      return '⚠️ 未检测到可用模型，请先配置模型提供商';
    }
    return formatRecommendationReport(recommendation);
  },

  setup_confirm: (params) => {
    const recommendation = recommendRoleConfig();
    if (!recommendation.config) {
      return '❌ 无法生成推荐配置';
    }
    saveRoleConfig(recommendation.config);
    return `✅ 已确认角色-模型配置（版本 ${recommendation.config.version || 1}）\n` +
      formatRecommendationReport(recommendation);
  },

  thinking_capabilities: (params) => {
    return formatCapabilitiesTable();
  },

  thinking_override: (params) => {
    if (!params.model_id) return '❌ 缺少 --model_id 参数';
    const supports = params.supports !== 'false' && params.supports !== false;
    const modes = params.modes
      ? (typeof params.modes === 'string' ? params.modes.split(',').map(s => s.trim()) : params.modes)
      : (supports ? ['low', 'medium', 'high'] : []);

    setUserOverride(params.model_id, {
      supportsThinking: supports,
      thinkingModes: modes,
      defaultMode: params.default_mode || modes[0] || 'off',
      confidence: 1.0,
      reason: params.reason || '用户手动设置'
    });

    return `✅ 已更新 ${params.model_id} 的 thinking 能力\n` +
      `  支持: ${supports ? '是' : '否'}\n` +
      `  模式: ${modes.join('/') || '不适用'}\n` +
      `  默认: ${params.default_mode || modes[0] || 'off'}`;
  },

  check_changes: (params) => {
    const result = checkForModelChanges();
    let output = '📡 模型池变更检测\n' + '═'.repeat(50) + '\n\n';
    output += `动作: ${result.action}\n`;
    output += `变更: ${result.change.summary}\n\n`;

    if (result.setupPrompt) {
      output += '🆕 首次使用！\n';
      output += JSON.stringify(result.setupPrompt, null, 2);
    } else if (result.action === 'auto_adapt') {
      output += `🤖 自动适配: ${result.log}\n`;
    } else if (result.action === 'notify_user') {
      output += formatChangeNotification(result.change) + '\n\n';
      if (result.recommendation) {
        output += '🎯 新推荐配置:\n';
        output += formatRecommendationReport(result.recommendation);
      }
    } else {
      output += '✅ 模型池稳定，无需操作';
    }

    return output;
  },

  // ========== 帮助 ==========

  help: () => {
    return `📖 多代理编排引擎 - 命令帮助\n${'═'.repeat(50)}

🔧 环境检查:
  check_env               检查 OpenClaw 版本和工具可用性

📋 代理配置管理:
  list                    列出所有代理配置
  create --name X         创建新代理配置
  edit --name X --field Y --value Z  编辑代理配置
  delete --name X         删除代理配置
  search --keyword X      搜索代理配置
  template --type X       使用模板创建 (research/technical/critical/coordinator/advocate/developer)

🔄 工作流模板:
  workflow_list           列出可用工作流模板

✅ 验证器:
  validate --result X --ruleset Y  验证产出质量
  validation_rulesets     列出可用验证规则集

📊 聚合器:
  aggregate --template X  聚合分支结果
  aggregation_templates   列出可用聚合模板

📡 通信:
  protocols               列出可用通信协议
  generate_prompt         生成子代理任务提示词
  generate_feedback       生成返工反馈提示词

🧠 模型与看板:
  model_pool              查看模型能力矩阵
  dashboard               查看看板（执行中可用）
  diagnose --error X      诊断子代理失败原因

🎯 角色-模型配置:
  setup                   查看当前角色-模型配置
  setup_recommended       查看推荐配置（基于当前模型库）
  setup_confirm           确认并保存推荐配置
  thinking_capabilities   查看各模型的 thinking 支持能力
  thinking_override       手动设置模型的 thinking 能力
  check_changes           检查模型池变更

📦 归档清理:
  archive                 归档工作流产出物
  clean [--dry_run]       清理 shared/ 临时文件
  archive_and_clean       一键归档 + 清理

🚀 一键启动:
  run --goal "目标描述"        获取完整执行指南 + 执行计划
  plan --goal "目标描述"       获取结构化执行计划 (JSON)
  run_demo [--goal "X"]        快速演示工作流

💡 AI 代理执行流程:
  1. plan → 获取 JSON 执行计划
  2. 按 phases 顺序，用 spawns[] 参数调用 sessions_spawn
  3. 读取 shared/final/ 下结果 → validate → aggregate → 最终报告
  `;
  }
};

// ===================== 主入口 =====================

export async function run(params) {
  const action = params.action || params.command || (params.goal ? 'run' : 'help');
  
  if (commands[action]) {
    return commands[action](params);
  }
  
  return `❌ 未知命令 "${action}"。输入 "多代理 help" 查看可用命令。`;
}

