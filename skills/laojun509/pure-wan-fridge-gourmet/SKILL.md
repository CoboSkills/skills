---
name: pure-wan-fridge-gourmet
description: 纯血万相冰箱盲盒 - 基于 Wan2.7/Wan2.1 视觉大模型的烹饪灵感触发器。用户上传冰箱内部照片，Skill 利用万相图像生图像能力，将杂乱冰箱场景语义化提炼并重组为精致创意料理概念图。支持多种菜系（中餐/西餐/日料/法餐/意餐/韩式/泰式/融合）、难易程度（简单/适中/挑战）、烹饪时间（快手/适中/慢炖）等参数定制。适用于快速备餐决策、晚餐创意预演、追求完全合规性的视觉 Skill 示例。使用条件：需要 Wan2.1 API 访问权限（阿里云 DashScope）。
---

# 纯血万相冰箱盲盒 (Pure Wan Fridge Gourmet)

## 合规声明

本项目核心视觉资产（所有生成的图像/视频）及核心语义逻辑处理 **100% 由且仅由 Wan2.1 模型 API 生成**。代码中严格绑定了 `wanx2.1-t2i-plus` 等官方模型标识，绝对未混用、未包含、未调用任何第三方大语言模型或图像生成模型。

## 功能概述

"纯血万相冰箱盲盒"是一个完全基于万相 2.1 视觉大模型构建的极简烹饪灵感触发器。它彻底简化了用户输入，用户只需拿出手机对冰箱内部（或零散食材）拍一张照片并上传。本 Skill 将利用万相强大的图像语义理解与合成能力，直接将 messy 的冰箱内部场景，语义化地"提炼"并"重组"出一道精致的创意料理概念图。

**核心特色：支持多维度参数定制**
- 🌍 **8种菜系**：中餐、西餐、日料、法餐、意餐、韩式、泰式、融合菜
- 📊 **3档难度**：简单快手、适中难度、挑战级
- ⏱️ **3种时长**：快手菜(15分钟)、适中(30-45分钟)、慢炖(1小时+)

这是对万相 2.1 **"化腐朽为神奇"** 视觉生成能力的终极展示。

## 使用场景

- **懒人、打工人的快速备餐决策** - 无需打字输入剩菜清单
- **独居青年的晚餐创意预演** - 在社交媒体分享高颜值料理概念
- **追求完全合规性的开发者** - 单一 API 调用，无 LLM 参与风险
- **烹饪爱好者** - 根据难度和时间规划烹饪方案

## 核心工作流程

本 Skill 采用单一的、高精度的 **"万相 2.1 图像生图像"** 闭环工作流：

### 1. 输入端 (Input)
用户上传冰箱内部的实拍原图，并可选择：
- **菜系风格** (cuisine)
- **难易程度** (difficulty) 
- **烹饪时间** (cooking_time)
- **额外要求** (custom_requirements)

### 2. 处理层 (Wan2.1 Core Processing)
- 调用 Wan2.1 图像生图像（Image-to-Image） API
- **核心技巧**：将输入图片作为图像提示词，结合用户选择的参数构建精准语义提示词
- 自动提取食材语义，忽略冰箱杂乱布局，重组为指定风格的菜品概念

### 3. 输出端 (Output)
向用户展示【高颜值概念菜品图】，包含完整的风格、难度、时间信息。

## 参数说明

### 菜系选择 (--cuisine / -c)

| 参数值 | 中文名 | 风格描述 |
|--------|--------|----------|
| `chinese` | 中式料理 | 传统瓷盘、刀工精细、酱油光泽、葱花点缀 |
| `western` | 西式料理 | 白瓷盘、黄油酱汁、香草装饰、经典摆盘 |
| `japanese` | 日式料理 | 极简摆盘、禅意美学、季节性食材、陶瓷餐具 |
| `french` | 法式料理 | 艺术酱汁、微型蔬菜、白瓷、高级餐厅氛围 |
| `italian` | 意式料理 | 家庭式摆盘、番茄酱汁、木质桌面、温暖光线 |
| `korean` | 韩式料理 | 热盘滋滋、辣椒酱光泽、芝麻点缀、小菜搭配 |
| `thai` | 泰式料理 | 鲜艳热带色彩、椰浆咖喱、青柠辣椒、芭蕉叶 |
| `fusion` | 融合料理 | 东西方技法结合、前卫摆盘、创新搭配 |

### 难易程度 (--difficulty / -d)

| 参数值 | 中文名 | 描述 |
|--------|--------|------|
| `easy` | 简单快手 | 家常烹饪、步骤简单、新手友好 |
| `medium` | 适中难度 | 平衡技术与口味、中等复杂度 |
| `hard` | 挑战级 | 专业厨师水准、分子料理元素、复杂技法 |

### 烹饪时间 (--cooking-time / -t)

| 参数值 | 中文名 | 描述 |
|--------|--------|------|
| `quick` | 快手菜（15分钟内） | 爆炒或生食、新鲜食材、快餐风格 |
| `moderate` | 适中（30-45分钟） | 平衡准备与烹饪、家常菜风格 |
| `slow` | 慢炖/精煮（1小时以上） | 炖煮慢烤、深层风味、周末烹饪 |

## 使用方法

### 方式一：命令行（推荐）

```bash
# 设置环境变量
export WAN_API_KEY="your-wan-api-key"

# 基础用法 - 中式中等难度适中时间
python3 scripts/generate_gourmet.py path/to/fridge_photo.jpg

# 完整参数示例 - 日式简单快手菜
python3 scripts/generate_gourmet.py fridge.jpg \
    --cuisine japanese \
    --difficulty easy \
    --cooking-time quick

# 简写形式
python3 scripts/generate_gourmet.py fridge.jpg -c chinese -d easy -t quick

# 添加自定义要求（如：减脂、不辣、适合宝宝）
python3 scripts/generate_gourmet.py fridge.jpg \
    --cuisine chinese \
    --custom "不要辣，适合减脂期"

# 查询任务状态
python3 scripts/generate_gourmet.py --query <task_id>
```

### 方式二：Python API 调用

```python
from scripts.generate_gourmet import WanFridgeGourmet

# 初始化
gourmet = WanFridgeGourmet()

# 生成中式简单快手菜
result = gourmet.generate(
    image_path="my_fridge.jpg",
    cuisine="chinese",
    difficulty="easy",
    cooking_time="quick",
    custom_requirements="不要辣，少油"
)

print(f"生成的菜品图: {result['image_url']}")
print(f"菜系: {result['cuisine_name']}")
print(f"难度: {result['difficulty_name']}")
print(f"时间: {result['cooking_time_name']}")
```

## 配置说明

### 环境变量

```bash
export WAN_API_KEY="your-dashscope-api-key"
export WAN_API_URL="https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
```

### API 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `model` | `wanx2.1-t2i-plus` | 万相2.1图像生成模型 |
| `size` | `1024*1024` | 输出图片尺寸 |
| `async` | `enable` | 启用异步模式（必须） |

## 依赖安装

```bash
pip install requests
```

## 故障排查

### 图像生成失败
- 检查 API Key 是否正确设置
- 确认 API URL 是否可访问
- 检查网络连接状态

### 生成效果不理想
- 尝试更换 `cuisine` 参数调整菜系风格
- 调整 `difficulty` 参数改变复杂度
- 使用 `custom_requirements` 添加具体要求
- 确保冰箱照片光线充足、食材可见

## 示例输出

输入：杂乱的冰箱内部照片（剩菜、蔬菜、鸡蛋等）

输出参数：
- 菜系：中式料理
- 难度：简单快手
- 时间：15分钟内

输出：精美的中式家常炒菜概念图，保留原食材的语义特征，以专业美食摄影风格呈现。

---

*纯血万相，化腐朽为神奇。*
