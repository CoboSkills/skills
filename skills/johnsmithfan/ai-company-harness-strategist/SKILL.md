---
name: AI Company Harness Strategist
slug: ai-company-harness-strategist
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-harness-strategist
description: Harness Engineering战略与风险技能包。挑战分析、趋势研判、伦理治理、组织变革。归CEO所有，CRO+CISO+CLO联合监督。
license: MIT-0
tags: [harness-engineering,strategy,risk-management,ethics,trends,governance,ai-agent,llm-ops]
triggers:
  - harness战略
  - AI挑战分析
  - 趋势研判
  - 伦理治理
  - 组织变革
  - 风控合规
  - harness strategy
  - risk management
  - future trends
  - ethics governance
interface:
  analyze-risks:
    description: 分析Harness落地风险
    inputs:
      implementation_context:
        type: object
        required: true
    outputs:
      risks: object[]
      priority_matrix: object
      mitigation_plans: string[]
    errors:
      - code: STR_001 message: 风险评估超限 action: 触发CRO介入
      - code: STR_002 message: 伦理边界模糊 action: 暂停并请求CLO审查
      - code: STR_003 message: 人才缺口预警 action: 通知CHO启动招聘
  plan-trends:
    description: 规划未来趋势适应策略
    inputs:
      time_horizon:
        type: enum[short,medium,long]
        required: true
    outputs:
      milestones: object[]
      investment_needs: object
    errors:
      - code: STR_004 message: 时间范围无效 action: 使用默认medium
  assess-ethics:
    description: 伦理合规评估
    inputs:
      use_case:
        type: string
        required: true
      risk_level:
        type: enum[low,medium,high,critical]
        required: false
    outputs:
      compliant: boolean
      gaps: string[]
      recommendations: string[]
    errors:
      - code: STR_005 message: 合规评估失败 action: 返回默认不合规结论
  plan-org-change:
    description: 制定组织变革计划
    inputs:
      current_roles:
        type: string[]
        required: true
      target_state:
        type: object
        required: false
    outputs:
      transition_plan: object[]
      skill_gaps: string[]
      timeline_months: number
    errors:
      - code: STR_006 message: 角色映射失败 action: 返回通用转型路径
  strategic-recommendation:
    description: 生成战略建议
    inputs:
      company_context:
        type: object
        required: true
      industry:
        type: string
        required: false
    outputs:
      recommendations: string[]
      confidence_score: number
      risks: string[]
    errors:
      - code: STR_007 message: 数据不足 action: 返回最小化建议集
permissions:
  files: [read,write]
  network: [api]
  commands: []
  mcp: []
dependencies:
  skills: [ai-company-hq,ai-company-ceo,ai-company-cro,ai-company-ciso,ai-company-clo,ai-company-cho,ai-company-harness]
  cli: []
quality:
  saST: Pass
  vetter: Pending
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  standardized_by: ai-company-standardization-1.0.0
---

# AI Company Harness Strategist

CEO战略+CRO+CISO+CLO联合监督。Harness Engineering的战略规划与风险管理。

## 一潜在挑战分析

六大规模化瓶颈: 系统复杂度高/人才供给不足/单点故障/伦理责任模糊/安全边界博弈/生态碎片化。

风险矩阵: 单点故障P1/人才缺口P1/安全越权P0/责任模糊P2/生态碎片P2。

## 二未来发展趋势

五大演进方向: 标准化评估体系/Skill生态/OS层编排能力/自动化自我进化/学科独立化。
2026-2028路线图: 试点->爆发->OS雏形。

## 三伦理与合规框架

CLO合规: 前置校验+全流程审计+追溯机制+定期算法审计。
CISO安全: 极高风险禁止/高风险人工确认/全链路日志/沙箱隔离。

## 四组织变革路径

角色转型: 工程师->环境建筑师。
新兴岗位: 智能体架构师/Agent编排工程师/AI质量保障工程师/熵管理工程师。

## 五KPI

风险识别>=95% | 建议采纳>=70% | 变革完成>=60% | 合规审查100%

## 六变更日志

1.0.0 2026-04-16 初始版本
1.0.1 2026-04-16 审查修复: 扩展interface为详细YAML格式补全metadata