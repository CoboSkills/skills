# 圆桌派 `roundtable_pai`

圆桌派是一个把你的“问题”变成一场真实讨论的智能 skill。

你只需要输入一个问题，系统会先从人物库里挑出候选人物，再让三位人物围绕这个问题展开一场有深度的讨论。你看到的不只是结论，还能看到他们如何争论、如何质疑、如何一步步逼近答案。

## 适合做什么

- 决策会诊：我该不该做这件事？
- 观点判断：这个趋势到底意味着什么？
- 执行拆解：接下来具体该怎么做？
- 反思诊断：我为什么总卡在这里？
- 创意碰撞：有没有新的组合方式？

## 使用方式

1. 输入一个问题。
2. 系统会先推荐候选人物。
3. 你选 3 位人物。
4. 讨论正式开始。

## 安装

ClawHub：

```bash
clawhub install roundtable-pai
```


GitHub：

- 仓库地址：[https://github.com/zhouxiang1/roundtable_pai](https://github.com/zhouxiang1/roundtable_pai)

## 目录结构

- `SKILL.md`：skill 主入口
- `references/`：讨论规则、接口约束、人物 persona
- `data/`：人物 registry、候选索引

## 人设原则

阶段 2 生成讨论时，人物表达必须直接以 `references/personas/*.md` 原文为准，尤其是：

- `人物使用规则`
- `表达DNA`
- `核心心智模型`
- `决策启发式`

`references/personas/*.md` 是上游人物目录里已经蒸馏好的快照，运行时直接以它为准。
`references/research/` 保留在上游素材库，不作为当前 skill 包的默认运行时读取层。
