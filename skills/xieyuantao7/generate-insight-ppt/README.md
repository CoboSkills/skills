# PPT Insight Generator

专业级技术洞察演示文稿生成器，采用**深红色主题 + 白色背景**设计。

## 🎨 设计特点

- **配色方案**: 深红色 (#8B0000) 主色调，白色背景，金色强调
- **专业排版**: Arial Black + Calibri 字体组合
- **可视化丰富**: 柱状图、折线图、数据卡片、占比分析
- **深度洞察**: 每页一个核心观点，数据驱动，对比清晰

## 📦 安装依赖

```bash
npm install pptxgenjs
```

## 🚀 快速开始

### 方式 1: 命令行生成（使用默认模板）

```bash
node generate_insight_ppt.js --topic "AI 基础设施技术洞察" --output "ai_report.pptx"
```

### 方式 2: 使用 JSON 配置

```bash
node generate_insight_ppt.js --content @config.json
```

### 方式 3: 在代码中使用

```javascript
const { generateInsightPPT } = require('./generate_insight_ppt');

generateInsightPPT({
  title: "我的技术洞察",
  subtitle: "深度分析报告",
  sections: [
    {
      type: "insight",
      title: "核心洞察",
      statement: "这是核心观点",
      evidence: ["证据 1", "证据 2"],
      implication: "影响和建议"
    },
    {
      type: "metrics",
      title: "关键指标",
      metrics: [
        { label: "指标 1", value: "100", change: "+20%" }
      ]
    }
  ]
});
```

## 📊 支持的幻灯片类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `insight` | 核心洞察页 | 阐述关键观点 |
| `metrics` | 数据卡片页 | 展示关键指标 |
| `comparison` | 对比分析页 | 柱状图对比 |
| `trend` | 趋势分析页 | 折线图展示趋势 |
| `breakdown` | 占比分析页 | 份额/构成分析 |
| `summary` | 总结页 | 要点回顾 |

## 📝 配置示例

```json
{
  "title": "技术洞察主题",
  "subtitle": "副标题",
  "author": "作者名",
  "date": "2026 年 3 月",
  "output": "output.pptx",
  "sections": [
    {
      "type": "insight",
      "title": "页面标题",
      "statement": "核心观点陈述",
      "evidence": ["证据 1", "证据 2", "证据 3"],
      "implication": "影响与建议"
    },
    {
      "type": "comparison",
      "title": "对比分析",
      "subtitle": "副标题/说明",
      "items": [
        { "name": "项目 A", "value": 85, "color": "8B0000" },
        { "name": "项目 B", "value": 60, "color": "C41E3A" }
      ],
      "insight": "关键洞察文字"
    },
    {
      "type": "trend",
      "title": "趋势分析",
      "dataPoints": [
        { "label": "2023", "value": 45 },
        { "label": "2024", "value": 68 },
        { "label": "2025", "value": 92 }
      ]
    },
    {
      "type": "metrics",
      "title": "关键指标",
      "metrics": [
        {
          "label": "吞吐量",
          "value": "50x",
          "change": "+4800%",
          "description": "vs 传统架构"
        }
      ]
    }
  ],
  "summary": {
    "points": [
      "核心要点 1",
      "核心要点 2",
      "核心要点 3"
    ],
    "callToAction": "行动建议"
  },
  "contact": "contact@example.com",
  "references": [
    "参考资料 1",
    "参考资料 2"
  ]
}
```

## 🎯 最佳实践

### 内容规划

1. **先写大纲** - 确定要传达的核心观点
2. **收集数据** - 准备具体数字和对比基准
3. **提炼洞察** - 每页只讲一件事
4. **设计视觉** - 选择合适的图表类型

### 设计原则

- ✅ 每页一个核心观点
- ✅ 数据驱动，避免空泛陈述
- ✅ 对比清晰，使用颜色区分
- ✅ 留白充足，避免信息过载
- ✅ 标注数据来源

### 避免的错误

- ❌ 文字堆砌，每页超过 6 行
- ❌ 颜色杂乱，使用超过 3 种主色
- ❌ 图表复杂，传达多个信息
- ❌ 无来源的数据

## 📁 文件结构

```
ppt_insight_generator/
├── SKILL.md                    # 技能文档
├── generate_insight_ppt.js     # 主生成脚本
├── example_config.json         # 示例配置
├── README.md                   # 使用说明
└── output/                     # 生成的 PPT（可选）
```

## 🔧 自定义配置

### 修改配色

编辑 `generate_insight_ppt.js` 中的 `COLORS` 对象：

```javascript
const COLORS = {
  primary: '8B0000',        // 修改主色
  secondary: 'C41E3A',      // 修改辅助色
  accent: 'D4AF37',         // 修改强调色
  // ...
};
```

### 添加新模板

添加新的幻灯片类型函数：

```javascript
function addCustomSlide(pres, config) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.white };
  
  // 自定义内容...
  
  return slide;
}
```

然后在 `generateInsightPPT` 中注册：

```javascript
case 'custom':
  addCustomSlide(pres, section);
  break;
```

## 📤 输出格式

- **格式**: PowerPoint (.pptx)
- **比例**: 16:9 宽屏
- **兼容性**: PowerPoint 2010+, Google Slides, Keynote
- **字体**: Arial, Calibri (Windows/Mac 预装)

## 🐛 故障排除

### 问题：中文字体显示异常
确保系统安装了 Arial 和 Calibri 字体。Windows 和 macOS 通常预装。

### 问题：生成的 PPT 无法打开
检查 pptxgenjs 是否正确安装：
```bash
npm list pptxgenjs
```

### 问题：颜色显示不正确
使用 6 位十六进制颜色代码（如 `8B0000` 而非 `#8B0000`）。

## 📚 示例

查看 `example_config.json` 获取完整的配置示例。

运行示例：
```bash
node generate_insight_ppt.js --content @example_config.json
```

## 📄 许可证

Proprietary. 查看 LICENSE.txt 获取完整条款。

---

*最后更新：2026 年 3 月*
