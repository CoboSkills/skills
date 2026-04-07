---
name: jy-news-interpretation
description: |
  基于 MCP 聚源金融数据库生成过去 24 小时的金融资讯热点速报（默认 Markdown 格式，支持 HTML 输出）。覆盖重要金融相关的国内新闻、国外要闻、重要个股公告、三大核心模块，所有信息可溯源、带原始发布时间戳。使用场景：当用户有以下意图时触发，询问近期要闻，询问近期热点，快速了解金融最新动态，解读财经新闻，分析新闻对市场影响，查询个股公告解读，定时生成财经日报。Generate a 24-hour financial news hotspots brief based on the MCP Juyuan Financial Database (default in Markdown format, HTML output supported). It covers three core modules: important domestic financial news, international key headlines, and major individual stock announcements. All information is traceable with original release timestamps. Triggers: user asks about recent news, financial hotspots, market dynamics, news interpretation, stock announcements, or scheduled daily briefs.
metadata:
  openclaw:
    requires:
      bins: ["node", "npm", "mcporter"]
    install:
      - id: install-mcporter
        kind: node
        package: mcporter
        label: Install mcporter via npm
---

# 【SKILL 财经速递】

本技能基于恒生聚源 MCP 金融服务，对近期热点财经新闻进行重要性筛选和深入解读，帮助用户快速理解新闻内容对金融市场、特定行业或具体资产的影响，为用户在金融投资、行业研究等方面提供有价值的信息指引，辅助其做出合理决策。

## 功能范围

1. **24 小时金融热点速报**：自动生成过去 24 小时核心财经新闻、行业要闻、个股公告解读报告
2. **新闻深度解读**：接收任意财经新闻/热点事件，分析其对市场、行业、标的资产的中长期/短期影响
3. **事件溯源与关联分析**：梳理新闻事件时间线，挖掘关联行业、关联标的、历史相似事件
4. **定时任务支持**：支持每日/交易日/每周自动生成财经资讯解读报告
5. **多格式输出**：默认 Markdown 格式，支持 HTML 结构化输出，所有数据带原始时间戳与信息溯源

## 查询建议

- 查询需明确核心主体：新闻关键词、行业名称、股票代码、热点事件名称均可
- 支持时间范围指定：近 24 小时、近 3 天、近一周、交易日等
- 支持需求指定：仅速报、深度解读、影响分析、关联标的查询等
- 所有工具调用统一使用 `query` 作为入参，无需额外参数

## 查询示例

1. 解读过去 24 小时金融市场热点新闻
2. 新能源行业最新政策新闻对市场的影响
3. 贵州茅台最新公告深度解读
4. 美联储加息新闻解读及关联行业分析
5. 每日交易日财经新闻速递

## 环境检查与配置

**每次使用本技能前，必须先检查 mcporter 安装和 MCP 服务配置状态！**

### 步骤 1：检查 mcporter 是否安装

```bash
mcporter --version
```

**如未安装**，按以下流程安装：

```bash
# 1. 通过 npm 全局安装
npm install -g mcporter

# 2. 验证安装
mcporter --version
```

### 步骤 2：检查 MCP 服务配置

```bash
# 列出所有已配置的 MCP 服务
mcporter list
```

**预期输出**（必须包含以下两个服务）：
- jy-financedata-tool
- jy-financedata-api

**如服务未配置**，需要获取 JY_API_KEY 并配置：

1. **获取 JY_API_KEY**：向恒生聚源申请 JY_API_KEY，通过邮箱申请（首次配置需提供，配置一次即可）

   **JY_API_KEY 申请路径**：
   - 申请邮箱：datamap@gildata.com
   - 邮件标题：数据地图 KEY 申请 -XX 公司 - 申请人姓名
   - 正文模板：
     - 姓名：
     - 手机号：
     - 公司/单位全称：
     - 所属部门：
     - 岗位：
     - MCP_KEY 申请用途：
     - Skill 申请列表：
     - 是否需要 Skill 安装包：（是，邮件提供/否，自行下载）
     - 其他补充说明（可选）：

   申请通过后，恒生聚源将默认发送【工具版和接口版】KEY

2. **配置 MCP 服务**：

```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

3. **验证配置**：

```bash
mcporter list
```

输出包含上述两个服务即为配置成功

4. **使用方式**：
```bash
# 基础键值对传参
mcporter call 服务名称。工具 参数=值

# 示例，注意：所有服务工具的入参均为 query
mcporter call jy-financedata-api.StockBelongIndustry query="电子行业 代表性上市公司 龙头股"
```

### 步骤 3：在 OpenClaw 中启用 mcporter（如未配置）

**mcporter 配置文件路径**：
- Windows: `C:\Users\你的用户名\config\mcporter.json`
- Linux/MacOS: `/root/config/mcporter.json`

**OpenClaw 配置文件路径**：
- Windows: `C:\Users\你的用户名\.openclaw\openclaw.json`
- Linux/MacOS: `~/.openclaw/openclaw.json`

**编辑 openclaw.json**，在 skills 部分添加 mcporter 配置：

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "enabled": true,
        "env": {
          "MCPORTER_CONFIG": "C:\\Users\\你的用户名\\config\\mcporter.json"
        }
      }
    }
  }
}
```

**重启 OpenClaw 使配置生效**：

```bash
openclaw gateway restart
```

### 配置检查流程（技能启动时执行）

每次使用本技能时，应先执行以下检查：

```bash
# 1. 检查 mcporter 是否可用
if ! command -v mcporter &> /dev/null; then
    echo "❌ mcporter 未安装，请先执行：npm install -g mcporter"
    exit 1
fi

# 2. 检查 MCP 服务是否配置
mcporter list | grep -E "jy-financedata-tool|jy-financedata-api"
if [ $? -ne 0 ]; then
    echo "❌ 未检测到聚源数据 MCP 服务配置"
    echo "请先配置 JY_API_KEY 并添加 MCP 服务（见环境检查与配置章节）"
    exit 1
fi

# 3. 测试连接
mcporter call jy-financedata-api.getNewsInfo query="测试" --output json
```

## 核心工作流程

流程中的工具调用能够并发调用尽量并发调用提速。

### 步骤 1：用户意图解析

识别用户查询关键词，确定解读类型：热点速报/新闻解读/行业分析/公告研判

### 步骤 2：并行获取基础数据

```bash
# 并行调用两个核心服务
mcporter call jy-financedata-api.getNewsInfo query="用户输入内容" --output json &
mcporter call jy-financedata-tool.analyzeNewsImpact query="用户输入内容" --output json &
wait
```

### 步骤 3：数据清洗与结构化处理

过滤无效信息，提取新闻时间、来源、核心内容、关联标的、影响等级

### 步骤 4：深度解读生成

结合金融领域知识，分析新闻对市场/行业/个股的短期、中长期影响

### 步骤 5：报告输出

生成带溯源、时间戳、关联分析的 Markdown/HTML 解读报告

## 快速开始

### 基础调用命令

```bash
mcporter call 服务名。工具名 query="查询内容"
```

### 常用示例

**1. 24 小时财经热点速报**
```bash
mcporter call jy-financedata-api.get24hHotNews query="过去 24 小时财经热点新闻"
```

**2. 单条新闻深度解读**
```bash
mcporter call jy-financedata-tool.interpretNews query="央行降准新闻解读"
```

**3. 行业新闻影响分析**
```bash
mcporter call jy-financedata-api.analyzeIndustryNews query="半导体行业利好新闻影响"
```

**4. 个股公告查询**
```bash
mcporter call jy-financedata-api.queryStockAnnouncement query="600519.SH 最新公告"
```

**5. 关联标的分析**
```bash
mcporter call jy-financedata-tool.findRelatedStocks query="新能源汽车产业链 关联上市公司"
```

## 输出格式

完整输出格式模板请参考：`references/output-format.md`

### 核心输出结构

```markdown
## 📅 财经日报 | {日期}

### 🔥 热点速览
{10 条新闻标题列表，每条≤20 字}

### 📰 国内要闻
**{新闻标题}**
{摘要，≤150 字}
**📊 数据解析** - {相关历史数据}
**💰 影响测算** - {具体财务影响}
**🔗 影响路径分析** - {自然语言描述传导路径}
**关联标的** - 表格展示

### 🌍 国际动态
**{新闻标题}**
{摘要，≤150 字}
**关联标的** - 表格展示

### 📢 重要公告
**{公司名}：{公告标题}**
{摘要，≤150 字}
**关联标的** - 表格展示

### 📊 市场数据速览
| 品种 | 动态 | 说明 | 数据源 |
|------|------|------|--------|
| {指数/商品} | {涨跌幅} | {说明} | 聚源数据 |
```

## 资源清单

```
~/.openclaw/skills/jy-news-interpretation/
├── SKILL.md                          # 本技能主文件
├── references/                       # 参考文档目录
│   ├── output-format.md              # 完整输出格式模板
│   └── examples.md                   # 使用示例合集
└── .learnings/                       # 技能学习日志
    ├── LEARNINGS.md
    └── ERRORS.md
```

## 限制

### 数据来源仅限恒生聚源 MCP 金融服务，不支持外部数据源
所有数据查询必须通过 `jy-financedata-tool` 或 `jy-financedata-api` 服务获取

### 新闻解读基于已发布的公开资讯，不构成投资建议
解读结果仅供参考，不能作为绝对的投资决策依据

### JY_API_KEY 为用户私有配置，失效后需重新申请配置
API Key 失效或权限变更时，需重新向恒生聚源申请并更新配置

### 定时任务依赖系统环境稳定，异常中断需重复尝试 3 次后报错并提示手动重试
定时任务执行失败时，自动重试 3 次，仍失败则通知用户手动执行

### 所有工具调用入参统一使用 query
所有 MCP 服务工具调用必须使用 `query` 作为唯一入参名

## 数据查询要求

| 数据类型 | 查询内容 | 时间范围 | 服务 | 工具 |
|----------|----------|----------|------|------|
| 热点新闻 | 24 小时财经新闻 | 近 24 小时 | jy-financedata-api | get24hHotNews |
| 新闻解读 | 单条新闻分析 | 指定新闻 | jy-financedata-tool | interpretNews |
| 行业分析 | 行业影响评估 | 近 3 天 | jy-financedata-api | analyzeIndustryNews |
| 个股公告 | 上市公司公告 | 近 7 天 | jy-financedata-api | queryStockAnnouncement |
| 关联标的 | 产业链关联公司 | 实时 | jy-financedata-tool | findRelatedStocks |
| 行情数据 | 股票/指数行情 | 实时 | jy-financedata-api | queryStockQuote |
| 财务数据 | 公司财报数据 | 近 5 年 | jy-financedata-api | queryCompanyFinance |

## 注意事项

### 内容质量
- ✅ 确保新闻内容真实、完整，避免断章取义
- ✅ 标题控制在 20 字以内，摘要控制在 150 字以内
- ✅ 国内与国际新闻避免重复
- ✅ 优先选择对市场有实质影响的新闻

### 合规提示
- ⚠️ 金融市场复杂多变，解读结果仅供参考
- ⚠️ 不能作为绝对的投资决策依据
- ⚠️ 涉及个股分析时需保持客观中立

### 技术实现
- 使用 mcporter 调用 MCP 服务时需处理速率限制
- 建议批量获取数据，避免频繁单次调用
- 遇到 429 错误时遵循 Retry-After 头等待
- 行情数据需标注"可能存在延迟，以交易软件为准"
- **JY_API_KEY 安全提示**：不要在日志或输出中暴露完整的 API Key

## 示例对话

**用户**: 今天有什么重要财经新闻？

**助手**: 
1. 检查环境配置... ✅ mcporter 已安装，MCP 服务已配置
2. 获取 24 小时热点新闻...
3. 查询市场数据...
4. 生成财经日报...

**用户**: 帮我解读一下美联储加息的新闻

**助手**: 
1. 环境检查通过
2. 调用 `jy-financedata-tool.interpretNews query="美联储加息"`
3. 分析影响路径...
4. 生成深度解读报告...

**用户**: 我没有 JY_API_KEY，怎么配置？

**助手**: 
请按以下步骤配置：

1. **获取 API Key**：发送邮件至 datamap@gildata.com 申请
2. **配置 MCP 服务**：
   ```bash
   mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 KEY"
   mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 KEY"
   ```
3. **验证配置**：`mcporter list`

配置完成后即可使用本技能查询金融数据！
