---
name: csdn-article-publish
description: 将 Markdown 技术文章通过浏览器自动化发布到 CSDN 博客（编辑器流程、登录校验、审核提示）。适用于「发到 CSDN」「保存到 CSDN 博客」等需求。
---

# CSDN 文章发布（增强版）

## 参考来源

本技能在流程与编辑器入口上参考了 [SkillHub](https://skillhub.tencent.com/) 社区中的 **「CSDN 文章发布」**（`csdn-publish`，ClawHub：`echome123/csdn-publish`）。SkillHub 上同类高热度技能还包括 **Csdn Publisher**（`csdn-publisher`，浏览器自动化 + 扫码登录等）。若需与官方包同步，可在 SkillHub 搜索「CSDN」后安装原技能。

## 文件输出目录

若需将待发布的 Markdown 草稿、截图或附件落在本机固定目录，使用：

**`~/WorkBuddy/csdn-article-publish/`**（与 `skill-config.json` 的 `outputDir` 一致，等价于 `path.join(HOME, 'WorkBuddy', 'csdn-article-publish')`；发布动作仍在 CSDN 网页完成。）

## 何时使用

- 用户明确要求：把文章**发布到 CSDN**、**发到 CSDN 博客**、**同步到 CSDN**。
- 与「仅生成 Markdown」区分：本技能强调**在已登录 CSDN 的前提下**完成浏览器内发布。

## 前置条件

1. **账号**：用户已在 CSDN 开通博客；发布前需**已登录**（若未登录，应引导用户先登录或扫码，勿猜测密码）。
2. **工具**：具备 **浏览器自动化**（如 MCP `browser` / Playwright / Cursor Browser）；下文用 `browser.*` 表示抽象步骤，具体 API 以当前环境为准。
3. **内容**：正文可为 Markdown；标题长度需符合 CSDN 规则（常见为 **5～100** 字符，以页面提示为准）。

## 核心流程（与 SkillHub 原版一致并补充）

### 1. 打开创作页

- 编辑器（博客发布页）示例：

  `https://mp.csdn.net/mp_blog/creation/editor`

- 若链接带 `spm` 等参数可保留，以打开后实际可编辑为准。

### 2. 检查登录

- 使用页面快照（`snapshot` / 可访问性树）判断：
  - 出现登录框、验证码、强制跳转登录 → **停止自动填写**，提示用户登录后再继续。
  - 出现标题输入区、富文本/Markdown 工具栏 → 继续。

### 3. 填写标题

- 在**标题输入框**填入用户给定标题。
- **注意**：SkillHub 示例中曾使用固定 `ref`（如 `e41`）。**页面改版后 ref 会变**，必须以**当前快照**中的 ref 为准，不可硬编码旧 ref。

### 4. 填写正文

- 若编辑器在 **iframe** 内，先聚焦 iframe 内可编辑区域，再输入 **完整 Markdown**。
- 支持代码块、标题、列表等（以 CSDN 编辑器实际支持为准）。

### 5. 发布

- 点击「发布」或等价按钮（同样以**当前快照**定位 ref）。
- 发布后再次快照确认：
  - 成功提示（如「发布成功」「审核中」等）→ 提取或展示文章链接。
  - 链接形态通常类似：`https://blog.csdn.net/{username}/article/details/{id}`

### 6. 结果反馈

- 向用户返回：**可访问的文章 URL**、是否处于**审核中**、以及是否需要用户补充标签/分类（若页面要求）。

## 与本地文件协作

若用户本地已有 Markdown 文件：

1. 用 `Read` 读取文件内容（含 frontmatter 时，标题可用 `title` 或一级标题）。
2. 将标题与正文填入 CSDN 编辑器，再执行发布。

## 错误处理

| 情况 | 处理 |
|------|------|
| 未登录 | 停止自动化，提示用户登录 CSDN |
| 标题过短/过长 | 按页面提示调整字数 |
| 正文为空 | 提示补充内容 |
| ref 找不到 | 重新 snapshot，用新 ref，勿沿用文档中的示例 ref |
| 网络或超时 | 重试或建议用户检查网络 |

## 可选：从 SkillHub 安装原版

若希望使用社区维护的安装包与版本更新，可参考 [SkillHub 安装说明](https://skillhub.cn/install/skillhub.md)，在商店中搜索 **CSDN** 或 `csdn-publish` / `csdn-publisher`。

## 与其它技能协作

- **内容创作**：可先用 `wechat-content-studio`、`wechat-typeset-pro` 等生成或排版 Markdown，再调用本技能发布到 CSDN。
- **多站点抓取**：与「从 CSDN 抓取」不同；本技能方向为**发布到 CSDN**。
