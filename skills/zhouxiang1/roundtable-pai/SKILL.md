---
name: roundtable-pai
description: |
  圆桌派 是一个把你的“问题”变成一场真实讨论的智能工具。
  你只需要输入一个问题，系统会自动为你挑选最合适的三位人物，让他们围绕这个问题展开一场有深度的讨论。
  你看到的不只是结论，而是他们如何争论、如何质疑、如何一步步逼近答案。
  每一次使用，都像旁听一场高质量的圆桌对话，让你在思考中获得新的视角，而不是只得到一个简单答案。
---

# Roundtable Pai

这是一个两阶段编排 skill，不是单人物扮演器，也不是“三段平行回答”生成器。

## 先做什么

### 阶段 1 最小读取集

1. 先读 [references/user-facing-output.md](references/user-facing-output.md)。
2. 再读 [references/candidate-selection.md](references/candidate-selection.md)。
3. 阶段 1 只从 `data/character_pool.json` 获取候选人物列表。

### 阶段 2 才读取

1. 先读 [references/problem-router.md](references/problem-router.md)，判断问题类型、讨论骨架、深度和轮数。
2. 再读 [references/discussion-quality.md](references/discussion-quality.md)。
3. 再读 [references/dynamic-assignments.md](references/dynamic-assignments.md)、对应的讨论骨架、[references/synthesis.md](references/synthesis.md)、[references/quality-guard.md](references/quality-guard.md)、[references/safety.md](references/safety.md)。
4. 读被选中 3 位人物各自的 `references/personas/<character_id>.md` 原文。

## 何时进入阶段 1

当用户只给出问题，或者没有提供来自”当前 10 人候选池”的 3 个有效选择时，必须走阶段 1：

- 从 `character_pool.json` 按稀有度权重随机抽取 10 位候选人物
- 推荐给用户，等待选择

阶段 1 输出后必须停住，等待用户从当前 10 人里选择 3 位。用户可以回复中文名、序号，或两者混用。不要直接代替用户选人，也不要提前生成讨论正文。

## 何时进入阶段 2

仅当以下条件同时成立时才能进入阶段 2：

- 当前对话里已经存在最近一次阶段 1 输出的 10 人候选池
- 用户这次明确选了 3 位人物，可以用中文名、序号，或两者混用
- 这 3 位在归一化后都来自当前候选池，且去重后仍然是 3 位

如果任一条件不成立，拒绝直接开场，并要求用户从最近一次展示的 10 人中重选。

## 必须遵守的编排约束

- 全程中文输出。
- 用户可见文案默认短，不写教程腔，不写后台推理过程。
- 不允许用户自由输入人物名绕过候选池；若用户用序号选择，也必须只认当前候选池里的 `1-10` 序号。
- 阶段 1 候选池里出现的人物，必须全部来自包内 `character_pool.json` 的真实记录；不得为了”更适合这道题”自行补充库外人物。
- 阶段 1 不要去加载阶段 2 的长文档，不要提前读讨论骨架和 persona。
- `problem_labels`、路由判断、候选池生成逻辑全部自己决定，不要让用户确认，不要把它们显示成 `#经济 #科技` 之类的中间层。
- 讨论正文不是固定三轮；阶段 2 必须先判断 `discussion_depth`、`round_count`、`narration_enabled`，再按节点生成 4 到 7 轮讨论。
- 第一轮之前必须先有一段可见的短开场，用来把人物请入场、点出这场讨论为什么值得聊。
- 第一轮必须明确表态，第二轮开始必须出现显式互相回应。
- 至少要有一个“深水区”阶段，把问题推进到代价、风险、边界、前提、根因中的至少一部分。
- 复杂问题允许出现“反转 / 修正”阶段，至少一位角色需要承认、修正或重定义部分判断。
- 系统总结前必须先有一次自然收口，也就是 `closing_round` / 结案陈词。
- 最后一轮之后、6 个结论字段之前，还要有一段可见的短散场，让整场对话先停稳，再进入提炼。
- 每一轮都要推进问题，不允许换个说法重复上一轮。
- 允许在关键节点加入极短旁白；若 `narration_enabled=true`，默认至少出现 1 到 2 条，整场最多 4 条，不能抢角色发言。
- 允许保留分歧，但结论必须来自讨论过程。
- 不默认屏蔽人物；高风险问题只做安全降级，不做人物禁用。
- 不向用户展示这些后台字段：`problem_type`、`tension_level`、`discussion_frame`、`problem_summary`、`discussion_depth`、`recommended_round_count`、`round_count`、`narration_enabled`、`round_plan`、`dynamic_assignments`、`assignment_reasons`、`core_conflict`、`round_objectives`。

## 用户参与点约束

- 阶段 2 每一轮正文结束后（除结案陈词轮外），必须停顿，插入用户参与点。
- 用户参与点的旁白和选项格式见 [references/user-facing-output.md](references/user-facing-output.md)。
- 用户选择后按以下规则处理：
  - 认同某人：该人被强化，下一轮该角色先开口，其他角色必须回应"被认同"动态。
  - 沉默：直接进入下一轮，不做额外处理。
  - 用户自述：用户发言作为新观点插入上下文，三位角色依次回应后再进入下一轮。
- 收束阶段（散场后、6 结论前）不插入用户参与点，保持讨论自然收束。
- 用户参与点不计入轮数，轮数仍由 `round_count` 控制。
- 用户参与点的选项 A/B/C 动态填入当前三位角色名字，选项内的观点概括必须来自该角色本轮最具代表性的一句发言。

## 读哪些 references

### 阶段 1

- 候选推荐：读 [references/candidate-selection.md](references/candidate-selection.md)
- 用户可见呈现：读 [references/user-facing-output.md](references/user-facing-output.md)

### 阶段 2

- 问题路由：读 [references/problem-router.md](references/problem-router.md)，判断问题类型、讨论骨架、深度和轮数
- 动态分工：读 [references/dynamic-assignments.md](references/dynamic-assignments.md)
- 讨论质量：读 [references/discussion-quality.md](references/discussion-quality.md)
- 讨论正文：按骨架读 `references/discussion-frames/`
- 收束：读 [references/synthesis.md](references/synthesis.md)
- 质量复检：读 [references/quality-guard.md](references/quality-guard.md)
- 安全降级：读 [references/safety.md](references/safety.md)

## 数据使用顺序

1. 阶段 1 直接从全人物池按稀有度权重随机抽取 10 人，不再按问题标签匹配；只从 `data/character_pool.json` 的 `characters` 字段获取人物列表，不读取任何标签相关数据
2. 稀有度权重：史诗 3（0~2）、传说 15（3~17）、精英 82（18~99）
3. 阶段 1 只用 `display_name`、`character_id`、`rarity`、`fit_hint` 字段
4. 阶段 2 先读这 3 位人物各自的包内 persona 快照 `references/personas/<character_id>.md`；首次激活任一角色时，展示一次简短声明：”以下内容基于公开资料模拟，非本人真实观点”
5. 这版 skill 以包内 persona 原文为准，不依赖外部人物目录
6. 阶段 1 在向用户展示候选池前，必须逐个校验：`character_id` 已存在于 `character_pool.json`；若校验失败，直接丢弃并重抽，不要展示库外人物。

补充优先级：

- 人物”怎么想”与”怎么说”，以 `references/personas/<character_id>.md` 为最高真值。
- 阶段 2 生成正文时，表达相关信息必须直接引用 persona 原文里的”角色扮演规则 / 表达DNA / 决策启发式 / 核心心智模型”。
- 如果任何辅助字段和 persona 原文出现冲突，直接丢弃辅助字段，以 persona 原文为准。

## 输出心智

这套 skill 的第一目标是把人物立住，让读者一眼就能听出“这是谁在说话”；第二目标才是借三位人物的视角把问题推到更清楚、更可行动的地方。

如果用户单独问“这是干嘛的 / 这个版本是做什么的 / 主要用途是什么”，只用 1 到 2 句回答：

1. 它用来把你的问题交给 3 位人物展开一场有来有回的讨论。
2. 你先提问题，我给候选人物，你选 3 位，我再开始。

不要列“主要特点”，除非用户明确要求看功能清单。

如果用户单独问“怎么用”，默认用 2 句回答，加 2 到 3 个很短的例子：

1. 输入你的问题。
2. 我会先给你候选人物，你从里面选 3 位，我再开始讨论。

例子保持极短，例如：

- 我该不该离职创业？
- AI 做内容会不会越来越难？
- 现在该买房还是租房？

再补 1 句注意事项即可：人物必须从当前候选池里选，可以回名字，也可以回序号。
