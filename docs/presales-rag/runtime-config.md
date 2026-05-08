# Presales 运行时配置与文件位置

本页说明：当你要修改“服务模板（proposal.md）”或“插槽清单（slots.yaml）”时，该改哪些文件、放在哪里、什么时候生效。

## 生效规则

1. 服务目录、模板文件、slot 配置默认在 Hermes 启动时读取。
2. 修改 `proposal.md` 或 `slots.yaml` 后，需要重启 Hermes 才会生效。
3. `~/.hermes/config.yaml` 只负责开启 presales 与运行参数；业务 slot 不写在那里。

## 1. 服务目录结构

当前采用服务目录驱动：

```text
presales_services/
  客户专属穿搭服务/
    proposal.md
    slots.yaml
```

规则：

1. `presales_services/` 是服务总目录。
2. 总目录下每个子目录代表一个服务，目录名就是服务名。
3. 每个服务目录中固定放：
   - `proposal.md`：方案输出模板。
   - `slots.yaml`：该服务需要采集的 slot 清单和元信息。
4. 当前实现先选择扫描到的第一个服务作为 active service；后续可扩展为显式选择服务。

## 2. Slot 清单修改位置

当前服务的 slot 配置文件：

```text
presales_services/客户专属穿搭服务/slots.yaml
```

示例：

```yaml
id: 客户专属穿搭服务
required_base:
  - customer_name
  - height_cm
  - weight_kg
required_for_handoff: []
optional: []
meta:
  customer_name:
    label: 客户姓名
    desc: 客户称呼或姓名（用于方案抬头）
  height_cm:
    label: 身高
    desc: 身高（厘米 cm）
```

字段说明：

- `id`：服务名；通常与服务目录名一致。
- `required_base`：进入信息整理/方案输出前必须补齐的 slot。
- `required_for_handoff`：预留的交付前额外必填项。
- `optional`：可选 slot，不阻塞流程。
- `meta`：slot 元信息，用于结构化评估提示和自动生成追问。
  - `label`：展示给客户看的字段名。
  - `desc`：字段含义，模型会据此生成自然追问。
  - 可选：`priority`、`type`、`overwrite_policy`、`conflict_policy` 等。

## 3. 方案模板修改位置

当前服务模板文件：

```text
presales_services/客户专属穿搭服务/proposal.md
```

模板一级标题会用于推导服务介绍：

```md
# 客户专属穿搭方案
```

系统会将其识别为：

```text
客户专属穿搭服务
```

用户问“你们有什么服务”时，只会介绍服务目录中定义的服务，不会自由扩展其他行业服务。

## 4. 模板占位符约定

模板渲染时如果取不到值，会输出空白，不会乱填。

- `{{slot:<key>}}`：填充已确认的 slot 值。
- `{{sys:<name>}}`：填充系统值。
  - 内置：`date`、`datetime`、`session_id`。
- `{{rag:<query>}}`：模板驱动的 RAG 检索。
  - 可以写固定 query，也可以写条目名。
  - 也支持 `条目名称：{{rag}}`，系统会用条目名称 + 已有 slot 信息生成检索 query。
- `{{ai}}` 或 `{{ai:<instruction>}}`：由模型根据当前条目名、上下文和 slot 信息生成内容。
- `{{ext:<tool> <json_args>}}`：预留外部接口/skills/tool 数据源。

## 5. 运行开关位置

`~/.hermes/config.yaml` 中仍保留运行开关，例如：

```yaml
agent:
  presales_enabled: true
  presales_state_machine_enabled: true
  presales_answer_gate_enabled: true
  presales_slot_assessment_mode: llm_structured
  presales_template_rag_max_calls_per_turn: 4
```

这些是运行参数，不是业务 slot 定义。

## 6. 最小验证

修改模板或 slot 后：

```bash
cd /Users/aaron/Documents/augment-projects/persenal/hermes-agent
./hermes --tui
```

建议先问：

```text
你们有什么服务
```

预期只返回 `presales_services/` 中定义的服务，例如“客户专属穿搭服务”。
