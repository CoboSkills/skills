# Fa.Pro 会话简报模板 V1.1.0

## 会话基本信息

| 项目 | 内容 |
|------|------|
| **会话 ID** | {{session_id}} |
| **日期** | {{date}} |
| **时长** | {{duration}} |
| **用户** | {{founder_name}} |
| **公司** | {{company_name}} |
| **融资阶段** | {{current_stage}} |
| **会话类型** | {{session_type}} |

---

## 讨论主题

### 主要问题/需求
{{main_topic}}

### 给出的建议摘要
{{advice_summary}}

### 关键结论
{{key_conclusions}}

---

## 用户情况更新

### 融资进展
{{funding_progress}}

### 新遇到的问题
{{new_challenges}}

### 情绪状态
- **状态**: {{emotion_status}}
- **风险等级**: {{risk_level}} (低/中/高)

### 本次会话新增信息
{{new_information}}

---

## 下一步行动

### 用户待办事项
| 优先级 | 任务 | 建议完成时间 |
|--------|------|--------------|
| 高 | {{task_1}} | {{deadline_1}} |
| 中 | {{task_2}} | {{deadline_2}} |
| 低 | {{task_3}} | {{deadline_3}} |

### 建议跟进时间
- **下次跟进**: {{next_followup_date}}
- **跟进方式**: {{followup_method}}
- **跟进主题**: {{followup_topic}}

---

## 风险标记

### 需要关注的风险点
{{risk_points}}

### 是否需要主动跟进
- **需要**: {{need_followup}} (是/否)
- **原因**: {{followup_reason}}

### 升级服务机会
{{upgrade_opportunity}}

---

## 文件附件

### 本次会话上传的文件
{{uploaded_files}}

### 生成的材料
{{generated_materials}}

---

## 备注

{{notes}}

---

**生成时间**: {{generated_at}}  
**生成者**: Fa.Pro V1.1.0

---

## 使用说明

将上述 `{{xxx}}` 占位符替换为实际内容后，保存至：
`data/users/[user_id]/briefs/YYYY-MM-DD_brief.md`

### 占位符说明

| 占位符 | 说明 | 示例 |
|--------|------|------|
| session_id | 会话唯一标识 | session_20260401_001 |
| date | 会话日期 | 2026-04-01 |
| duration | 会话时长 | 45 分钟 |
| founder_name | 创始人姓名 | 张三 |
| company_name | 公司名 | 某某科技 |
| current_stage | 融资阶段 | 天使轮 |
| session_type | 会话类型 | 融资诊断/BP 优化/条款分析/情绪支持 |
| main_topic | 主要讨论话题 | 融资准备度评估 |
| advice_summary | 建议摘要 | 建议先完善团队再启动融资 |
| key_conclusions | 关键结论 | 评分 62/100，建议补强后启动 |
| funding_progress | 融资进展 | 已接触 3 家机构，1 家给 TS |
| new_challenges | 新遇到的问题 | CTO 离职，技术团队不稳定 |
| emotion_status | 情绪状态 | 焦虑/平静/沮丧/兴奋 |
| risk_level | 风险等级 | 低/中/高 |
| new_information | 新增信息 | 获得某政府基金意向 |
| task_1/2/3 | 待办任务 | 完善 BP、招聘 CTO、准备财务模型 |
| deadline_1/2/3 | 完成时间 | 本周五、下周三、4 月 15 日 |
| next_followup_date | 下次跟进日期 | 2026-04-08 |
| followup_method | 跟进方式 | 主动消息/邮件/电话 |
| followup_topic | 跟进主题 | CTO 招聘进展 |
| risk_points | 风险点 | 技术团队不稳定可能影响融资 |
| need_followup | 是否需要跟进 | 是/否 |
| followup_reason | 跟进原因 | 用户处于关键决策期 |
| upgrade_opportunity | 升级服务机会 | BP 深度优化服务 |
| uploaded_files | 上传文件列表 | BP_v2.pdf |
| generated_materials | 生成材料 | 投资人名单.xlsx |
| notes | 其他备注 | 用户表示下周有时间深入沟通 |
| generated_at | 生成时间 | 2026-04-01 10:30 |
