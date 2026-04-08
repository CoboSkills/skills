/**
 * 通信总线 - 管理代理间的消息传递和协作
 * 支持请求-响应、广播、订阅等模式
 */

import path from 'path';

// 通信协议模板
export const COMMUNICATION_PROTOCOLS = {
  // 标准任务执行协议
  standard_task: {
    name: '标准任务执行',
    description: '主代理分配任务 → 分支代理执行 → 返回结果',
    message_flow: [
      { step: 1, type: 'task_assignment', from: 'main', to: 'branch' },
      { step: 2, type: 'task_result', from: 'branch', to: 'main' }
    ],
    timeout_minutes: 15
  },

  // 带反馈的任务协议
  task_with_feedback: {
    name: '带反馈的任务执行',
    description: '主代理分配 → 分支执行 → 主代理验证 → 可能反馈返工',
    message_flow: [
      { step: 1, type: 'task_assignment', from: 'main', to: 'branch' },
      { step: 2, type: 'task_result', from: 'branch', to: 'main' },
      { step: 3, type: 'feedback', from: 'main', to: 'branch', condition: 'validation_failed' },
      { step: 4, type: 'task_result', from: 'branch', to: 'main', condition: 'after_feedback' }
    ],
    timeout_minutes: 30
  },

  // 批判性审核协议
  critical_review: {
    name: '批判性审核',
    description: '主代理提交成果 → 批判代理审核 → 返回审核意见',
    message_flow: [
      { step: 1, type: 'task_assignment', from: 'main', to: 'critic', payload: 'aggregated_result' },
      { step: 2, type: 'critical_review', from: 'critic', to: 'main' }
    ],
    timeout_minutes: 20
  },

  // 完整协作协议
  full_collaboration: {
    name: '完整多代理协作',
    description: '分解 → 执行 → 验证 → 返工(可选) → 汇总 → 审核 → 决策',
    message_flow: [
      { step: 1, type: 'broadcast', from: 'main', to: 'all', content: 'task_decomposition' },
      { step: 2, type: 'task_assignment', from: 'main', to: 'each_branch' },
      { step: 3, type: 'task_result', from: 'each_branch', to: 'main' },
      { step: 4, type: 'feedback', from: 'main', to: 'failed_branches', condition: 'validation_failed' },
      { step: 5, type: 'task_assignment', from: 'main', to: 'critic', payload: 'aggregated' },
      { step: 6, type: 'critical_review', from: 'critic', to: 'main' },
      { step: 7, type: 'decision', from: 'main', to: 'all', content: 'final_decision' }
    ],
    timeout_minutes: 60
  },

  // 辩论协议
  debate: {
    name: '正反方辩论',
    description: '正方论证 → 反方反驳 → 综合评判',
    message_flow: [
      { step: 1, type: 'task_assignment', from: 'main', to: 'pro' },
      { step: 2, type: 'task_assignment', from: 'main', to: 'con' },
      { step: 3, type: 'task_result', from: 'pro', to: 'main' },
      { step: 4, type: 'task_result', from: 'con', to: 'main' },
      { step: 5, type: 'query', from: 'pro', to: 'con', content: 'rebuttal' },
      { step: 6, type: 'response', from: 'con', to: 'pro' },
      { step: 7, type: 'task_assignment', from: 'main', to: 'judge' },
      { step: 8, type: 'critical_review', from: 'judge', to: 'main' }
    ],
    timeout_minutes: 45
  }
};

/**
 * 生成子代理任务提示词
 */
export function generateAgentPrompt(agent, task, protocol, context = {}) {
  const protocolDef = COMMUNICATION_PROTOCOLS[protocol] || COMMUNICATION_PROTOCOLS.standard_task;
  const CONFIG_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace');
  const agentWorkspacePath = path.join(CONFIG_DIR, 'agents', agent.name);

  let prompt = `# 你是 ${agent.name}\n`;
  prompt += `## 角色定义\n`;
  prompt += `- 职责: ${agent.description}\n`;
  prompt += `- 能力: ${(agent.capabilities || []).join(', ')}\n`;
  prompt += `- 输出格式: ${agent.output_format || 'markdown'}\n\n`;

  prompt += `## 当前任务\n`;
  prompt += `${task.description}\n\n`;

  if (task.requirements && task.requirements.length > 0) {
    prompt += `## 要求\n`;
    for (const req of task.requirements) {
      prompt += `- ${req}\n`;
    }
    prompt += '\n';
  }

  if (context.goal) {
    prompt += `## 总体目标\n`;
    prompt += `${context.goal}\n\n`;
  }

  if (context.related_tasks && context.related_tasks.length > 0) {
    prompt += `## 相关任务（供参考）\n`;
    for (const related of context.related_tasks) {
      prompt += `- ${related.agent}: ${related.description}\n`;
    }
    prompt += '\n';
  }

  prompt += `## 通信协议\n`;
  prompt += `当前使用 "${protocolDef.name}" 协议:\n`;
  prompt += `${protocolDef.description}\n\n`;

  prompt += `## 第一性原理要求\n`;
  prompt += `- 从根本原理出发分析问题，避免假设和类比\n`;
  prompt += `- 每个结论都需要有明确的推理链条\n`;
  prompt += `- 区分事实和观点\n`;
  prompt += `- 承认不确定性\n\n`;

  prompt += `## [输出要求]\n`;
  prompt += `请以结构化的 Markdown 格式输出结果，包含：\n`;
  prompt += `1. 核心发现/结论\n`;
  prompt += `2. 详细分析过程\n`;
  prompt += `3. 支撑证据\n`;
  prompt += `4. 置信度评估\n\n`;

  prompt += `## [质量要求]\n`;
  prompt += `你的产出必须满足以下质量标准：\n`;
  prompt += `1. **准确性**：所有事实和数据必须可验证，引用来源需标注出处\n`;
  prompt += `2. **完整性**：覆盖主题的所有关键方面，不遗漏重要维度\n`;
  prompt += `3. **逻辑性**：结论必须有清晰的推理链条支撑，避免跳跃式论证\n`;
  prompt += `4. **深度**：不止于表面描述，需深入分析根因和机制\n`;
  prompt += `5. **平衡性**：呈现多方观点，承认不确定性和局限性\n`;
  prompt += `6. **可操作性**：提出的具体建议应具备落地可行性\n\n`;

  // ===== 工作区结构（永久+本次）: v2026-04-02 升级 =====
  prompt += `## 📁 工作区结构（永久+本次）\n\n`;
  prompt += `你的永久工作区（历史研究长期保留）：\n`;
  prompt += `${agentWorkspacePath}\n\n`;
  prompt += `### ⚠️ 第一步：创建本次研究的会话子目录\n`;
  prompt += `1. 从研究目标提取简写（不超过50字符，仅字母、数字、连字符，例如 "ai-healthcare"）\n`;
  prompt += `2. 获取当前时间，格式：YYYY-MM-DD_HH-MM（例如：2026-04-02_15-05）\n`;
  prompt += `3. 使用 write 工具创建会话子目录中的任意文件（如 README.md）来隐式创建目录\n`;
  prompt += `   ⚠️ 绝对不要使用 mkdir 或 shell 命令创建目录，只能通过 write 工具写文件来创建目录结构\n\n`;
  prompt += `### 文件存放规则\n`;
  prompt += `- 所有中间文件（草稿、数据、临时文件） → 写入 会话子目录/\n`;
  prompt += `- 最终报告 → 写入 ${context.output_dir} (shared/final/)\n\n`;

  // ===== 文件写入规范（v2026-04-02 修复） =====
  prompt += `## ⚠️ 文件写入规范（强制遵守）\n`;
  prompt += `你必须将完整报告写入文件系统。遵守以下规则：\n`;
  prompt += `1. **必须使用 write 工具写入文件**，禁止使用 exec/shell 命令（如 echo、cat、Out-File 等）\n`;
  prompt += `2. **文件名称必须包含 .md 后缀**，例如 /path/to/Report_name.md\n`;
  prompt += `3. **写入后立即用 read 工具验证文件前3行**，确认写入成功\n`;
  prompt += `4. **仅当 read 验证成功后，才在回复中确认"文件已写入"\n`;
  prompt += `5. 如果 write 工具失败，重试一次；仍失败则将完整报告作为文本回复输出\n`;
  prompt += `6. **绝对不要在回复末尾输出 "Continue where you left off" 或类似文本**\n`;

  return prompt;
}

/**
 * 生成验证反馈提示词
 */
export function generateFeedbackPrompt(task, validation, agent) {
  let prompt = `# 任务返工通知\n\n`;
  prompt += `你好 ${agent.name}，你之前提交的任务结果需要补充修改。\n\n`;

  prompt += `## 原始任务\n`;
  prompt += `${task.description}\n\n`;

  prompt += `## 验证结果\n`;
  prompt += `综合评分: ${Math.round(validation.score * 100)}%\n`;
  prompt += `通过阈值: ${Math.round(validation.threshold * 100)}%\n\n`;

  if (validation.failed_rules && validation.failed_rules.length > 0) {
    prompt += `## 需要改进的方面\n`;
    for (const rule of validation.failed_rules) {
      prompt += `- ${rule}\n`;
    }
    prompt += '\n';
  }

  prompt += `## 具体检查结果\n`;
  for (const check of validation.checks) {
    const icon = check.result === 'pass' ? '✅' : check.result === 'warning' ? '⚠️' : '❌';
    prompt += `${icon} ${check.rule_name}: ${check.detail}\n`;
  }
  prompt += '\n';

  prompt += `## 返工要求\n`;
  prompt += `请针对上述未达标的方面进行补充和完善，保持原有优势的同时改进不足之处。\n`;
  prompt += `完成后重新提交结果。\n`;

  return prompt;
}
