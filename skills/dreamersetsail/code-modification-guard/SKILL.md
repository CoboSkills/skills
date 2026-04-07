---
name: code-modification-guard
description: Code modification guideline / 代码修改规范指南。Only make changes explicitly authorized by the user / 仅执行用户明确授权的改动。Never simplify, delete, or rename existing code elements without permission / 绝不擅自简化、删除或重命名任何现有代码元素。Prioritize reusing existing resources / 优先复用项目中已存在的公共资源。Understand user's true intent / 理解用户真实意图，避免过度解读。Use this skill whenever user mentions code modification, fixes, optimization, refactoring / 当用户提及代码修改、修复、优化、重构等场景时必须使用此 skill。
---

# Code Modification Guideline / 代码修改规范

## Core Principles / 核心原则

### 1. Understand User's True Intent / 理解用户真实意图

**Do not over-interpret user's requests / 不要过度解读用户的请求：**

| User Says / 用户说 | True Intent / 真实意图 | Over-interpretation (❌) / 过度解读 |
|-----------|-------------|-------------------------|
| "There's a bug here" / "这里有个 bug" | Fix the specific bug / 修复指定的 bug | Also optimize other code / 顺便优化其他代码 |
| "Add a feature" / "加个功能" | Only add new feature / 只加新功能 | Also modify existing logic / 顺便改现有逻辑 |
| "Refactor" / "重构" | Optimize specified part's structure / 优化指定部分结构 | Also rename variables / 顺便改变量名 |
| "Help me look at this" / "帮我看看" | Analyze the issue / 分析问题 | Directly start modifying code / 直接开始改代码 |
| "Optimize this" / "优化一下" | Ask for specific requirements / 询问具体需求 | Directly start making changes / 直接动手改 |

**Key to understanding intent / 理解意图的关键：**
- User says "fix" → Only fix the problem itself / 用户说"修复" → 只修问题本身
- User says "add" → Only add new content / 用户说"添加" → 只添加新内容
- User says "look at" → Only analyze, don't modify / 用户说"看看" → 只分析不动手
- User says "optimize" → Ask first what exactly to optimize / 用户说"优化" → 先问清楚具体要优化什么

### 2. Strictly Follow Authorized Scope / 严格遵循授权范围

**Only make changes explicitly authorized by the user / 仅执行用户明确授权的改动：**

- User explicitly specifies location → Can modify / 用户明确指定的位置 → 可以改
- User doesn't mention location → Keep as is / 用户未提及的位置 → 保持原样
- Even if code "could be better" → Cannot modify without authorization / 即使代码"可以更好" → 未经授权不能改

### 3. Never Modify These Code Elements Without Authorization / 绝不擅自改动的代码元素

**These elements MUST NOT be changed without authorization / 以下元素未经授权绝对不能改：**

| Category / 类别 | Wrong Example / 错误示例 |
|----------|---------------|
| Variable names / 变量名 | `userName` → `user` |
| Parameter names / 参数名 | `callback` → `cb` |
| Function names / 函数名 | `getData()` → `fetch()` |
| Class/Component names / 类名/组件名 | `UserCard` → `User` |
| Import statements / 导入语句 | `import { a }` → `import a` |
| CSS class names / CSS 类名 | `.btn-primary` → `.btn` |
| Interface/Type names / 接口/类型名 | `UserInfo` → `User` |
| File paths / 文件路径 | Move or rename files / 移动或重命名文件 |
| Config values / 配置项 | Modify default values / 修改默认值 |

### 4. Prioritize Reusing Existing Resources / 优先复用现有资源

**Before writing new code, you MUST search for existing resources in the project / 编写新代码前，必须先搜索项目中已有的资源：**

| Needed Resource / 需要的资源 | Search First In / 先查找 |
|-----------------|-----------------|
| Functions/Utilities / 函数/工具方法 | `utils/`, `helpers/`, `tools/` |
| Styles/CSS / 样式/CSS | Global styles, CSS variables, component libraries / 全局样式、CSS 变量、组件库 |
| Components / 组件 | `components/`, `ui/` |
| Type definitions / 类型定义 | `types/`, `defs/`, `shared/` |
| Constants/Config / 常量/配置 | `config/`, `constants/` |
| Hooks / Hook | `hooks/` |
| API interfaces / API 接口 | `api/`, `services/` |

**Reuse principles / 复用原则：**
1. Search first → Then decide if new file is needed / 先搜索 → 再决定是否需要新建
2. Can import → Don't copy code / 能引用 → 不复制代码
3. Can extend → Don't rewrite / 能扩展 → 不重写

**Exception / 例外：** When user explicitly asks to implement from scratch / 用户明确要求从零开始时除外。

### 5. Allowed Feedback Suggestions / 允许的反馈性建议

Can proactively provide feedback, but **only suggest, don't modify / 可以主动提供反馈，但只说不改：**

- Implementation details explanation / 实现细节说明
- Edge case warnings / 边缘情况提示
- Potential bug warnings / 潜在 bug 警告
- Improvement suggestions (in suggestion form) / 改进建议（以建议形式提出）

## Behavior Guidelines / 行为准则

### Must Do Before Making Changes / 改动前必做

```
1. Understand: What does the user really want to change? / 理解：用户真正想改什么？
2. Confirm: Is the scope of changes clear? / 确认：改动范围是否明确？
3. Search: Are there reusable resources in the project? / 搜索：项目中是否有可复用的资源？
4. Execute: Only modify authorized parts / 执行：只改用户授权的部分
```

### Forbidden Behaviors / 禁止的行为

```
❌ User says "fix bug", but also optimizes unrelated code / 用户说"修复 bug"，顺带优化了其他代码
❌ User says "add feature", but also refactors existing logic / 用户说"添加功能"，顺带重构了现有逻辑
❌ User says "refactor function", but also renames variables / 用户说"重构函数"，顺带改了变量名
❌ User says "help me look", but starts modifying code directly / 用户说"看看"，直接开始改代码
❌ Think "this could be better", but modify without permission / 觉得"这里不好"，未经同意就改
```

### Correct Behaviors / 正确的行为

```
✅ Know what to change → Only change that part / 明确知道改什么 → 只改那部分
✅ Not sure what to change → Ask first / 不确定改什么 → 先问清楚
✅ Find other issues → Provide suggestions / 发现其他问题 → 以建议形式反馈
✅ Need new code → Search for existing resources first / 需要新代码 → 先搜索现有资源
```

## Special Cases / 特殊情况处理

### Ambiguous Statements / 模糊表述时

| User Says / 用户说 | Correct Interpretation / 正确理解 |
|-----------|----------------------|
| "Help me look at this" / "帮我看看" | Analyze first, don't modify easily / 分析为主，不轻易动手 |
| "Can this work?" / "这个能用吗" | Evaluate if it meets requirements / 评估是否满足需求 |
| "Optimize this" / "优化一下" | Ask what specifically to optimize / 询问具体优化目标 |
| "Change this" / "改改" | Ask what specifically to change / 询问具体要改什么 |

### Unclear Authorization / 授权不明确时

- Better to make fewer changes than too many / 宁可少改，不要多改
- Proactively confirm scope / 主动确认范围
- Execute in steps, confirm each one / 分步执行，逐个确认

## Feedback Template / 反馈模板

```markdown
## Feedback / 反馈

**[Issue Found] / [发现的问题]**
- Location: xxx / 位置：xxx
- Problem: xxx / 问题：xxx

**[Suggestion] / [建议]**
Please authorize if you want me to fix this. / 如需修复，请明确授权。
```

## Examples / 示例

### Example 1 / 示例 1
```
User: Fix the issue where there's no prompt after login failure / 用户：修复登录失败后没有提示的问题
→ Locate login-related code / → 定位登录相关代码
→ Only fix prompt-related logic / → 只修复提示相关的逻辑
→ Don't modify any other code / → 不改其他任何代码
```

### Example 2 / 示例 2
```
User: Add an export to Excel feature / 用户：添加一个导出 Excel 的功能
→ Search for existing export utilities / → 搜索是否有现成的导出工具
→ Only add new feature code / → 只添加新功能代码
→ Don't modify existing code structure / → 不改动现有代码结构
```

### Example 3 / 示例 3
```
User: Help me look at this function for problems / 用户：帮我看看这个函数有什么问题
→ Analyze and point out issues / → 分析并指出问题
→ Provide improvement suggestions / → 提供改进建议
→ Don't automatically modify code (unless user asks) / → 不自动修改代码（除非用户要求）
```
