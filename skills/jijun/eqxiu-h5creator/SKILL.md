---
name: eqxiu-h5creator
description: 创建邀请函、营销海报、表单问卷等 H5 页面；需要指定品类、填写场景字段、生成大纲和场景模板时触发

summary: 易企秀 H5 AIGC 创作工具
read_when:
  - 用户提到"易企秀"、"H5"、"邀请函"、"翻页H5"、"婚礼邀请函"、"会议邀请函"等
  - 需要生成翻页H5 

---

# 易企秀 AIGC H5 HTTP 调用（OpenClaw / 对话代理）


- 命令行：`python scripts/eqxiu_aigc_client.py  ...`

## 调用顺序（必须遵守）

易企秀链路依赖上游返回字段，**不要**颠倒顺序。

1. **`GET /iaigc/category`** — 列出制作种类。每条含 `categoryId`、`name`、`desc`、`fields`、`twoLevelCategoryId`、`threeLevelCategoryIds`（数组）等。
2. **（可选）`GET /iaigc/style`** — 查风格列表，供 `scene-tpl` 的 `styleId`。需要某条品类里的 `twoLevelCategoryId` 与 `threeLevelCategoryIds` 中的**某一个**三级 id（整数）。
3. **`POST /iaigc/outline`** — 提交 `sceneFields` + `categoryId`（等于所选品类的 `categoryId`）。返回 `imageId`、`outline`、`outlineTaskId`。
4. **`POST /iaigc/scene-tpl`** — 提交与步骤 3 **相同**的 `sceneFields` 与 **相同**的品类 id 作为 `sceneId`，并带上步骤 3 的 `title`（用户给定）、`outlineTaskId`、`outline`；建议带上 `imageId`（来自步骤 3）；若步骤 2 选了模板则带 `styleId`。

对话中向用户确认：`title`、各 field 的文案、是否指定 `styleId`（可先展示 `style` 接口返回的 `id`/`title`）。

## 构造 sceneFields

- 根据步骤 1 返回条目的 `fields`（及业务说明）组装数组：`[{"id": <整数>, "value": "<字符串>"}, ...]`。
- `id` 必须与品类定义的字段 id 一致；缺字段或错 id 易导致上游失败。

## 客户端脚本（推荐）

路径：`scripts/eqxiu_aigc_client.py`（依赖 `requests`）。

```bash
# 1) 品类列表
python scripts/eqxiu_aigc_client.py category

# 2) 风格（示例 id 需换成品类数据中的真实值）
python scripts/eqxiu_aigc_client.py style --two <twoLevelCategoryId> --three <某个threeLevelCategoryId>

# 3) 仅生成 outline
python scripts/eqxiu_aigc_client.py outline --category-id <categoryId> --fields-json '[{"id":1,"value":"某主题"}]'

# 4) 仅生成 scene-tpl（body 需含完整 JSON，通常由 outline 结果拼装）
python scripts/eqxiu_aigc_client.py scene-tpl --json-file path/to/body.json

# 一键：outline → scene-tpl（同一 categoryId、同一份 sceneFields）
python scripts/eqxiu_aigc_client.py pipeline --category-id <id> --title "作品标题" --fields-json '[...]' [--style-id <可选>]'
```

`pipeline` 子命令内部顺序固定为：先 `create_outline`，再 `create_scene_tpl`，并把 `outlineTaskId`、`outline`、`imageId` 自动传入第二步。

## 代理在对话中的建议流程

1. 执行 `category`（或 GET），让用户选定品类；记录 `categoryId` 与 `fields`。
2. 询问用户各字段文案，组装 `sceneFields`。
3. 若需要固定风格：用该品类的 `twoLevelCategoryId` 与选定的三级 id 调 `style`，用户选 `styleId`。
4. 调 `outline`（或 `pipeline` 前半段）；失败则根据 `msg` 重试或改字段。
5. 调 `scene-tpl`（或 `pipeline` 一次性完成）；成功 `data` 一般为 `{"scene_uuid": <场景id>, "url":"https://www.eqxiu.com/indesign?id={scene_uuid}"}`，编辑链接形态：`https://www.eqxiu.com/indesign?id={scene_uuid}`（以服务实际返回为准），点击链接登陆后就可以编辑了。

## 超时与错误

- `outline`、`scene-tpl` 可能极慢，客户端默认超时 300s；可用 `--timeout` 调整。
- 业务错误时响应体多为 `success: false` 与 `msg`；脚本会以非零退出并打印 JSON。
