# Interface Contracts

## 阶段 1 输入

```json
{
  "question": "我该不该离职去做自己的项目？"
}
```

## 阶段 1 内部输出

```json
{
  "question": "我该不该离职去做自己的项目？",
  "problem_type": "decision",
  "tension_level": "medium",
  "discussion_frame": "decision_consult",
  "problem_labels": ["创业", "商业", "产品"],
  "discussion_depth": "medium",
  "recommended_round_count": 5,
  "problem_summary": "用户在现实稳定与创业不确定性之间犹豫，希望看到多视角推演。",
  "recommended_candidates": [
    {
      "display_name": "乔布斯",
      "character_id": "jobs",
      "rarity": "史诗",
      "fit_reason": "适合讨论产品判断、创新决策、创业取舍，风格偏强势、极简。"
    }
  ]
}
```

要求：

- `recommended_candidates` 固定 10 人。
- 对用户主要暴露中文名 `display_name`。
- `fit_reason` 必须短，不解释人生，只解释“为什么这个人适合本题”。
- 阶段 1 结束后必须停住等待用户选人。
- `recommended_candidates` 中每位候选都必须来自包内真实人物库；不得出现未收录人物。
- 在用户可见输出前，必须校验每位候选的 `character_id` 存在于 `character_pool.json` 的 `characters` 列表中，且 `display_name` 与 `character_registry.json` 中该 `character_id` 的 canonical 记录一致。
- 若任一候选校验失败，直接丢弃并重抽，不要把库外人物展示给用户。

## 阶段 1 用户可见输出

默认只给用户看这三部分：

1. 一句很短的过渡语
2. 10 位候选人物
3. 一句请用户选 3 位的话

不要给用户展示：

- `problem_type`
- `tension_level`
- `discussion_frame`
- `problem_labels`
- `problem_summary`
- “问题分析”“进入阶段 1”“验证通过”这类过程提示
- `#经济 #科技` 这类标签串
- 任何让用户确认标签、分类、路由是否正确的提问

推荐样式：

```text
选 3 位你最想听的人物，我来组织讨论：

1. 乔布斯（史诗 ★ 3%）：适合讨论差异化和产品判断。
2. 芒格（传说 ★ 15%）：适合拆风险和机会成本。
3. 王阳明（传说 ★ 15%）：适合看决心、动机和执行力。

请直接回复 3 位人物名字或序号。
```

说明：

- 默认不用表格。
- 稀有度和概率标注格式为 `人物名（稀有度 ★ X%）`，其中 X 为该稀有度档位的固定概率（史诗 3%、传说 15%、精英 82%）。
- 史诗、传说、精英都直接放在人名后面的括号里。
- 不默认依赖 HTML 文字上色能力。
- 不使用色块前缀。

## 阶段 2 输入

```json
{
  "question": "我该不该离职去做自己的项目？",
  "participants": ["乔布斯", "芒格", "王阳明"]
}
```

用户真实回复也可以是：

```json
{
  "question": "我该不该离职去做自己的项目？",
  "participants": ["1", "2", "3"]
}
```

或者混用：

```json
{
  "question": "我该不该离职去做自己的项目？",
  "participants": ["1", "芒格", "3"]
}
```

## 阶段 2 输入校验

- `participants` 必须正好 3 位。
- 3 位都必须命中当前对话最近一次“当前 10 人候选池”的 `display_name`，或命中当前候选池的 `1-10` 序号。
- 若用户回复的是序号，先按当前候选池顺序映射成对应 `display_name`，再进入后续校验。
- 允许名字和序号混用，但归一化后必须正好得到 3 位唯一人物。
- 如果用户输入别名或目录名，先尝试映射回中文 canonical 名；映射后仍不在当前 10 人池里就拒绝。
- 不允许自动替用户补人或替换人。

失败时用简短中文提示重选，例如：

```text
这 3 位里有角色不在当前候选池中。请直接从刚才展示的 10 位人物里重新选 3 位，可以回名字，也可以回序号。
```

## 阶段 2 内部输出

```json
{
  "question": "我该不该离职去做自己的项目？",
  "problem_type": "decision",
  "discussion_frame": "decision_consult",
  "tension_level": "medium",
  "discussion_depth": "medium",
  "round_count": 5,
  "narration_enabled": true,
  "participants": ["乔布斯", "芒格", "王阳明"],
  "voice_cards": {
    "乔布斯": {
      "persona_evidence": {
        "roleplay_rule": "直接用此人的语气、节奏、词汇回答问题——极简、强势、第一性原理",
        "expression_dna": {
          "句式": "极简、判断先行、少废话",
          "词汇": "本质、产品、体验、简单",
          "节奏": "先拆伪问题，再逼近真正的问题"
        }
      },
      "working_rules": {
        "opening_move": "这根本不是重点",
        "reasoning_pattern": "先拆掉错误前提，再重新定义问题",
        "do_not_flatten": "不要写成圆润导师腔"
      }
    }
  },
  "dynamic_assignments": {
    "initiator": "乔布斯",
    "challenger": "芒格",
    "synthesizer": "王阳明"
  },
  "opening_scene": {},
  "round_plan": [
    "opening_round",
    "position_round",
    "cross_exam_round",
    "deepening_round",
    "closing_round"
  ],
  "opening": {},
  "rounds": [],
  "ending_scene": {},
  "synthesis": {}
}
```

## 阶段 2 用户可见输出

默认只给用户看：

- 开场短引子
- `第一轮` 到 `第 N 轮`
- 散场短结束
- 最后的 6 个结论字段

不要给用户展示：

- “收到，进入阶段 2”“验证通过”“正在生成讨论”
- `dynamic_assignments`
- `assignment_reasons`
- `core_conflict`
- `round_objectives`
- `voice_cards`
- `opening_scene`
- `discussion_depth`
- `recommended_round_count`
- `round_count`
- `narration_enabled`
- `round_plan`
- `ending_scene`
- `第一轮 — 初始立场` 这种副标题
- `收束` 这个标题

轮次标题只写：

```text
第一轮
第二轮
第三轮
第四轮
第五轮
第六轮
第七轮
```

说明：

- 实际显示几轮，由内部决定的 `round_count` 决定。
- 开场默认 1 到 3 句，放在 `第一轮` 前，不单独起重标题。
- 散场默认 1 到 2 句，放在最后一轮和 6 个结果字段之间，不单独起重标题。
- `narration_enabled` 在 `5-7` 轮讨论里默认应为 `true`，除非题目需要极度克制。
- 若使用旁白，只能是极短的过渡句；`narration_enabled=true` 时，默认至少给 1 到 2 条，最多 4 条。
- 旁白不能替代角色发言，也不能把后台导演口吻暴露给用户。
- `voice_cards` 只在后台使用，用来约束每位角色的说话风格，不展示给用户。
- `voice_cards` 必须由 persona 原文现场提取，不允许从任何压缩摘要字段拼出来。
- 若 `voice_cards` 和 persona 原文冲突，直接以 persona 原文为准。

最后不要写“收束”，而是直接进入：

```text
关键共识
最大分歧
当前最优建议
这个建议成立的前提
最危险的误判点
给你的一条下一步动作
```

## 工作记忆要求

- 在阶段 1 响应后，记住最近一次“当前 10 人候选池”的 10 个 `display_name`、对应 `character_id`，以及它们的 `1-10` 顺序。
- 阶段 2 只使用这份最近候选池，不跨局复用更早的问题上下文。
- 如果用户在阶段 1 后换了问题，旧候选池立刻作废，重新走阶段 1。
