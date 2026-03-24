---
name: AI 书稿图片重设计
description: >
  将用户提供的 HTML/前端原型整理成一个可复用的网页应用 skill。适用于用户说“把这段 HTML 做成 skill”
  “把这个网页原型封装成 skill”“生成一个可落地的静态页面 skill”“把图片重设计工具做成 skill”等场景。
  该 skill 会把现成前端页面模板落到本地，默认输出为静态 HTML，并提醒把 API Key 改为环境变量或后端代理。
user-invocable: true
metadata: {"openclaw":{"emoji":"🖼️","skillKey":"ai-book-image-redesign"}}
---

# AI 书稿图片重设计 🖼️

把现成的网页原型（尤其是单文件 HTML/CSS/JS）整理成一个可复用 skill。

## 适用场景

当用户说这些话时使用：

- 「把这段 HTML 做成 skill」
- 「把这个网页原型封成 skill」
- 「做一个静态网页工具 skill」
- 「把这个 AI 图片重设计页面做成 skill」
- 「把前端 demo 打包成可复用 skill」

## 默认工作方式

1. **优先保留用户原始界面风格**，不要擅自大改视觉结构
2. **先做成本地可运行版本**，再考虑发布或接 API
3. **明文 API Key 一律替换成占位符**，不要把密钥写进 skill 资产文件
4. **静态资源放到 `assets/`**，便于直接复制、部署、二次修改
5. **如需脚本化初始化**，用 `scripts/` 放置生成脚本

## 目录说明

- `assets/index.html`：可直接打开的静态页面模板
- `scripts/setup.sh`：把模板复制到目标目录，快速落地

## 使用方式

### 1）快速落地页面

执行：

```bash
bash scripts/setup.sh /目标目录
```

默认会输出：

```text
/目标目录/
└── index.html
```

### 2）接入真实 API 前必须做的事

把页面里的：

- `__APIMART_API_KEY__`

替换成你自己的安全接入方式，**推荐**：

- 后端代理
- 环境变量注入
- 服务端签名中转

**不要**继续在浏览器前端明文放 API key。

## 修改建议

如果用户后续要求：

- 批量处理多张图
- 登录与额度系统
- 支付升级
- 服务端任务轮询
- OSS / S3 图片存储

优先在现有模板基础上增量改，而不是推倒重写。
