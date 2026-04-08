name: uapp-event
version: 0.2.0
summary: 友盟 App 自定义事件查询入口 skill，支持事件列表查询、事件统计（触发次数、独立用户数）、参数分析等功能，用于埋点数据分析。支持通过事件名称或显示名称查询事件存在性。

entry: scripts/event.py

## 典型问法与内部意图映射

| 典型问法 | 内部意图（CLI 参数） |
|---------|-------------------|
| "有哪些自定义事件？" | `--list-events` |
| "某个按钮点击了多少次？" | `--query click_button --metric count` |
| "有多少独立用户触发了注册事件？" | `--query register --metric unique_users` |
| "支付事件有哪些参数？" | `--list-params payment` |
| "不同来源渠道的事件分布怎样？" | `--query login --param channel` |
| "事件 xxx 存在吗？" | `--check-event xxx` |
| "显示名称为'开始'的事件存在吗？" | `--check-display "开始"` |

## 支持的查询模式

### 事件存在性检查

| 参数 | 说明 |
|-----|------|
| `--check-event EVENT_NAME` | 通过事件名称检查事件是否存在 |
| `--check-display DISPLAY_NAME` | 通过显示名称检查事件是否存在（对人类更友好） |

### 事件列表查询（分页）

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--list-events` | - | 查询事件列表 |
| `--page` | 1 | 页码 |
| `--per-page` | 50 | 每页数量（最大 100） |
| `--all` | - | 查询全部事件 |

### 事件统计查询

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `--query EVENT_NAME` | - | 指定事件名称 |
| `--metric count` | - | 触发次数 |
| `--metric unique_users` | - | 独立用户数 |
| `--metric all` | all | 综合统计 |

### 参数分析

| 参数 | 说明 |
|-----|------|
| `--list-params EVENT_NAME` | 查询事件参数列表 |
| `--query EVENT_NAME --param PARAM_NAME` | 查询参数值分布 |
| `--param-metric duration` | 查询参数值时长统计 |
| `--param-value VALUE` | 查询特定参数值的趋势 |

## 支持的时间范围

- `yesterday`: 昨天
- `last_7_days`: 过去7天（默认）
- `last_30_days`: 过去30天
- `yyyy-mm-dd`: 指定日期

## 调用示例

### 事件存在性检查

```bash
# 通过事件名称检查
python3 scripts/event.py --check-event "app_start" --app "MyApp"

# 通过显示名称检查（对人类更友好）
python3 scripts/event.py --check-display "开始" --app "MyApp"

# JSON 输出
python3 scripts/event.py --check-display "开始" --app "MyApp" --json
```

### 事件列表查询

```bash
# 查询事件列表（默认第1页，每页50条）
python3 scripts/event.py --list-events --app "MyApp"

# 分页查询
python3 scripts/event.py --list-events --page 2 --per-page 20 --app "MyApp"

# 查询全部事件
python3 scripts/event.py --list-events --all --app "MyApp"
```

### 事件统计查询

```bash
# 查询事件触发次数
python3 scripts/event.py --query "click_button" --metric count --app "MyApp"

# 查询独立用户数
python3 scripts/event.py --query "click_button" --metric unique_users --app "MyApp"

# 综合统计（默认）
python3 scripts/event.py --query "click_button" --app "MyApp"

# 指定时间范围
python3 scripts/event.py --query "click_button" --range last_30_days --app "MyApp"
```

### 参数分析

```bash
# 查询事件参数列表
python3 scripts/event.py --list-params "click_button" --app "MyApp"

# 查询参数值分布
python3 scripts/event.py --query "click_button" --param "button_id" --app "MyApp"

# 查询参数值时长统计
python3 scripts/event.py --query "click_button" --param "button_id" --param-metric duration --app "MyApp"
```

### JSON 输出

添加 `--json` 参数获取结构化数据：

```bash
python3 scripts/event.py --list-events --app "MyApp" --json
python3 scripts/event.py --query "click_button" --app "MyApp" --json
```

## 配置方式

1. `--config /path/to/umeng-config.json`: 显式指定配置文件
2. `export UMENG_CONFIG_PATH=/path/to/umeng-config.json`: 环境变量
3. 在当前目录创建 `umeng-config.json`: 默认查找

配置文件格式参见项目根目录 `umeng-config.json` 示例。

## 注意事项

1. **分页限制**：事件列表默认每页 50 条，最大 100 条，避免大数据量查询
2. **eventId 映射**：参数列表查询需要 eventId，脚本会自动从事件列表中解析
3. **事件名称匹配**：支持精确匹配和忽略大小写匹配
4. **显示名称查询**：`--check-display` 通过中文显示名称查询，对人类更友好
5. **输出截断规则**：
   - 事件列表：事件名称超过32字符、显示名称超过64字符会被截断并追加 `...`
   - 参数列表：参数名称超过32字符、显示名称超过64字符会被截断并追加 `...`
   - 单个事件/参数查询：完整显示，不做截断
   - JSON 输出（`--json`）：完整显示，不做截断
