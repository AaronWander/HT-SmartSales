# Hermes Presales 模板变量与撰写规范

这份文档说明：在 Hermes 的“普通售前对话 -> 信息采集 -> 信息整理确认 -> 方案输出并保存 -> 退出设计流程”中，`proposal.md` 方案模板可以使用的变量类型、写法和注意事项。

## 0. 文件位置

每个服务独立一个目录：

```text
presales_services/<服务名>/
  proposal.md
  slots.yaml
```

示例：

```text
presales_services/客户专属穿搭服务/proposal.md
presales_services/客户专属穿搭服务/slots.yaml
```

修改后重启 Hermes 生效。

## 1. 五种变量类型

模板占位符统一写法：

```text
{{<type>:<payload>}}
```

部分类型允许省略 payload，例如 `{{ai}}`、`{{rag}}`。

### 1) `slot` 客户信息槽位

作用：填充客户已提供并被结构化评估为可用的信息。

```md
客户：{{slot:customer_name}}
预算：{{slot:budget_range}}
```

要求：`slot` key 必须定义在同目录的 `slots.yaml` 中。取不到值时留空。

### 2) `sys` 系统自动生成

作用：填充不需要客户提供、系统可确定的字段。

```md
日期：{{sys:date}}
时间：{{sys:datetime}}
会话：{{sys:session_id}}
```

内置项：

- `date`：当天日期，`YYYY-MM-DD`。
- `datetime`：当前时间，秒精度。
- `session_id`：当前会话 id。

### 3) `rag` 知识库检索

作用：把知识库检索结果填入模板，例如报价、政策、流程、款式知识等。

```md
费用/报价：{{rag}}
退费政策：{{rag:退费政策是什么？}}
版型选择：{{rag}}
```

规则：

- 如果 `rag` 有 payload，系统会结合 payload + 已确认 slot 生成最终检索 query。
- 如果 `rag` 无 payload，系统会取占位符所在行左侧的条目名作为检索意图。
- 检索不到就留空，不编造。
- 方案模板渲染阶段可一次填充多个 `rag` 条目，次数由 `agent.presales_template_rag_max_calls_per_turn` 控制。

### 4) `ai` 模型自行生成

作用：由模型根据条目名、已确认 slot、对话上下文生成非事实性内容，例如总结、风格建议、方案描述。

```md
身材特点简述：{{ai}}
版型选择：{{ai}}
整体建议：{{ai:请生成不超过 120 字的专业建议}}
```

规则：

- `{{ai}}` 会使用所在行/条目名作为生成意图。
- 不应让 `ai` 生成事实字段，例如客户姓名、预算、日期等。
- 事实字段应来自 `slot`、`sys`、`rag` 或 `ext`。

### 5) `ext` 外部接口 / skills / tools

作用：预留外部接口或技能工具数据源，例如库存、排期、内部报价 API。

```md
库存：{{ext:inventory_lookup {"sku":"A001"}}}
```

当前建议：没有明确工具白名单前，业务模板优先使用 `slot/sys/rag/ai`。

## 2. 模板撰写原则

1. 取不到值就留空。
2. 不要把示例值写成真实值。
3. 客户事实信息必须用 `slot`。
4. 日期、会话号等系统信息用 `sys`。
5. 报价、政策、公司知识优先用 `rag`。
6. 风格化表达、总结、建议段落可用 `ai`。
7. 不要把整份模板包在 markdown 代码块里。
8. 表格保持标准 Markdown 表格格式。

## 3. Slot 配置关系

模板中出现的 `{{slot:<key>}}` 应该在同目录 `slots.yaml` 中定义。

例如模板：

```md
| 客户姓名 | {{slot:customer_name}} |
| 身高 | {{slot:height_cm}} cm |
```

对应 `slots.yaml`：

```yaml
required_base:
  - customer_name
  - height_cm
meta:
  customer_name:
    label: 客户姓名
    desc: 客户称呼或姓名
  height_cm:
    label: 身高
    desc: 身高，单位 cm
```

## 4. 最小模板示例

```md
# 客户专属穿搭方案

## 基本信息

| 项目 | 内容 |
|---|---|
| 方案日期 | {{sys:date}} |
| 客户姓名 | {{slot:customer_name}} |

## 已确认信息

| 项目 | 内容 |
|---|---|
| 身高 | {{slot:height_cm}} cm |
| 体重 | {{slot:weight_kg}} kg |
| 偏好风格 | {{slot:style_preferences}} |
| 预算范围 | {{slot:budget_range}} |

## 方案建议

身材特点简述：{{ai}}
版型选择：{{ai}}
费用/报价：{{rag}}
```
