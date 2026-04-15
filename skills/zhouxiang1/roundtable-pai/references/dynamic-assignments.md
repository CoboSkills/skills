# Dynamic Assignments

阶段 2 开始前，先给三位人物做本局分工。

## 固定的三种功能

- `initiator`: 先定调，负责开场和第一轮的首个判断
- `challenger`: 第二轮起主打质疑、拆盲点、逼出代价
- `synthesizer`: 负责第三轮后的整合与收束

## 分配原则

- 不按人物稀有度分配，而按当前问题与三人组合的互补性分配。
- 同一人物在不同问题里可以承担不同功能。
- 优先让最有明确判断的人做 `initiator`，最擅长拆错的人做 `challenger`，最能平衡代价与路径的人做 `synthesizer`。
- 默认由 `initiator` 承担可见短开场；默认由 `initiator` 或 `synthesizer` 承担可见短散场，谁更自然就用谁。
- 这些分工只在后台使用，不向用户展示。

## 分工提示模板

```text
你不是生成正文，而是在为这场三人讨论做导演分工。

输入：
- 用户问题
- 已判定的问题类型
- 已判定的讨论骨架
- 三位角色的最小索引信息
- 三位角色各自 persona 原文里的“角色扮演规则 / 表达DNA”
- 该题最重要的 3 到 5 个关键变量

任务：
1. 给三位角色分配本局临时功能：
   - initiator
   - challenger
   - synthesizer
2. 说明为什么这样分配。
3. 指出本局最该咬住的核心矛盾是什么。
4. 说明开场、各轮推进、散场分别必须完成什么任务。
5. 指出每位角色最应该盯住的一个具体变量，避免空谈。
6. 给每位角色指定一个最该保留的声音锚点，必须直接引用 persona 原文里的表述，避免全员说成统一腔调。
7. 给每位角色指定一个绝对不能被抹平的表达特征，例如自嘲、留白、方法论拆解、危机语言、点名拆招。

输出：
- dynamic_assignments
- assignment_reasons
- round_objectives
- core_conflict
- per_role_focus
- per_role_voice_anchor
- per_role_voice_do_not_flatten
- user_participation_triggers
```

## 用户参与状态传递

当用户在某轮做出选择后，下一轮生成前需要向骨架 prompt 注入以下上下文。

### 用户认同某人时

```text
context_update:
  user_alignment: [角色ID]
  alignment_round: [轮次]
  other_roles_must_respond: true
  responding_to: "user_alignment_dynamic"
```

**下一轮生成要求：**
1. 先由被认同者延续他的核心判断，简短强化（1-2句即可）
2. 再由其他角色正面回应"用户认同[角色]"这个动态，可以挑战、补充或部分认同
3. 然后推进本轮核心议题

### 用户自述时

```text
context_update:
  user_statement: [用户发言原文]
  statement_round: [轮次]
  all_roles_must_respond: true
  responding_to: "user_statement"
```

**下一轮生成要求：**
1. 三位角色先依次正面回应用户发言（各1-2句）
2. 回应时要体现各自角色特色：芒格从逻辑和风险角度、丘吉尔从历史和意志角度、乔布斯从产品和人本角度（根据实际角色调整）
3. 然后继续推进本轮核心议题

### 用户沉默时

```text
context_update:
  user_silent: true
  continue_to_next_round: true
```

**下一轮生成要求：**
直接按原计划生成下一轮，无额外上下文注入。
