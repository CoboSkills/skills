# Fa.Pro 用户画像模板 V1.1.0

```json
{
  "user_id": "{{user_id}}",
  "created_at": "{{created_at}}",
  "updated_at": "{{updated_at}}",
  
  "基本信息": {
    "founder_name": "{{founder_name}}",
    "company_name": "{{company_name}}",
    "sector": "{{sector}}",
    "company_description": "{{company_description}}",
    "location": "{{location}}",
    "website": "{{website}}"
  },
  
  "融资信息": {
    "current_stage": "{{current_stage}}",
    "target_raise": "{{target_raise}}",
    "current_valuation": "{{current_valuation}}",
    "funding_experience": "{{funding_experience}}",
    "investors_contacted": [],
    "ts_received": 0,
    "closed_rounds": []
  },
  
  "配置偏好": {
    "support_style": "{{support_style}}",
    "reminder_frequency": "{{reminder_frequency}}",
    "do_not_disturb": "22:00-08:00",
    "language": "zh-CN"
  },
  
  "会话统计": {
    "session_count": 0,
    "first_session_date": "{{first_session_date}}",
    "last_session_date": "{{last_session_date}}",
    "total_duration_minutes": 0
  },
  
  "文件记录": {
    "bp_uploaded": false,
    "bp_version": "",
    "uploaded_files": [],
    "generated_materials": []
  },
  
  "风险评估": {
    "burnout_risk_score": 0,
    "funding_urgency": "normal",
    "team_stability": "stable",
    "last_emotion_status": "平静"
  },
  
  "服务状态": {
    "version": "free",
    "upgraded_at": null,
    "pro_services_used": []
  },
  
  "备注": "{{notes}}"
}
```

---

## 字段说明

### 基本信息

| 字段 | 说明 | 示例 |
|------|------|------|
| user_id | 用户唯一标识 | user_20260401_001 |
| founder_name | 创始人姓名/花名 | 张三 / Alex |
| company_name | 公司全称 | 某某科技有限公司 |
| sector | 赛道 | SaaS/硬科技/消费/医疗 |
| company_description | 公司简介 | 一句话描述业务 |
| location | 所在地 | 北京/上海/深圳 |
| website | 官网/产品链接 | https://xxx.com |

### 融资信息

| 字段 | 说明 | 示例 |
|------|------|------|
| current_stage | 当前阶段 | 天使轮/Pre-A/A 轮 |
| target_raise | 目标融资金额 | 500 万/1000 万 |
| current_valuation | 当前估值 | 5000 万投前 |
| funding_experience | 融资经验 | 首次/有经验/老司机 |
| investors_contacted | 已接触投资人 | ["红杉", "IDG"] |
| ts_received | 收到 TS 数量 | 0/1/2 |
| closed_rounds | 已完成轮次 | [{"round": "天使", "amount": "300 万", "date": "2025-01"}] |

### 配置偏好

| 字段 | 说明 | 可选值 |
|------|------|--------|
| support_style | 支持风格 | 教练式/朋友式/导师式 |
| reminder_frequency | 提醒频率 | 激进/标准/保守/被动 |
| do_not_disturb | 勿扰时段 | 22:00-08:00 |

### 会话统计

自动更新，用于追踪用户活跃度。

### 文件记录

| 字段 | 说明 |
|------|------|
| bp_uploaded | 是否上传过 BP |
| bp_version | BP 版本号 |
| uploaded_files | 上传文件列表 |
| generated_materials | 生成的材料列表 |

### 风险评估

| 字段 | 说明 | 评分标准 |
|------|------|----------|
| burnout_risk_score | Burnout 风险 | 0-10 分，根据情绪检测 |
| funding_urgency | 融资紧急度 | low/normal/high/urgent |
| team_stability | 团队稳定性 | stable/concerning/unstable |
| last_emotion_status | 最后情绪状态 | 焦虑/沮丧/愤怒/孤独/疲惫/平静/兴奋 |

### 服务状态

| 字段 | 说明 |
|------|------|
| version | 服务版本 | free/pro |
| upgraded_at | 升级时间 | ISO 日期 |
| pro_services_used | 使用的 Pro 服务列表 |

---

## 使用说明

1. 新用户首次对话完成后创建此文件
2. 每次会话后更新 `updated_at` 和相关字段
3. 保存至 `data/users/[user_id]/profile.json`
4. 敏感信息加密存储

---

**模板版本**: V1.1.0  
**更新日期**: 2026-04-01
