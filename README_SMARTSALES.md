# 🦦 海獭 SmartSales AI

**智能售前服务系统 - AI 驱动的售前咨询与方案生成平台**

海獭 SmartSales AI 是一款基于大语言模型的智能售前服务系统，通过 AI 对话自动收集客户需求、生成定制化方案，大幅提升售前效率。

---

## ✨ 核心特性

### 🎯 智能需求收集
- **自然对话式交互** - 通过对话自然地收集客户信息
- **智能槽位管理** - 自动识别和填充业务关键信息
- **动态问题生成** - 根据缺失信息智能追问

### 📋 三阶段工作流
1. **信息收集阶段** - 收集客户需求和业务信息
2. **信息整理阶段** - 生成结构化摘要供确认
3. **方案生成阶段** - 基于模板自动生成定制方案

### 🎨 灵活的模板系统
- **服务目录化管理** - 支持多服务并行配置
- **占位符系统** - slot/sys/rag/ai/ext 五类变量
- **知识库集成** - 自动从 RAGFlow 检索相关信息填充方案

### 🔄 多平台支持
- Telegram、Discord、Slack、WhatsApp 等消息平台
- CLI 命令行界面
- Web API 接口

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/AaronWander/HT-SmartSales.git
cd HT-SmartSales

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件，配置 API keys
```

### 配置服务

在 `presales_services/` 目录下创建你的服务：

```
presales_services/
  你的服务名/
    proposal.md    # 方案模板
    slots.yaml     # 槽位配置
```

### 运行

```bash
# 启动 CLI
python cli.py

# 或启动 Gateway（消息平台）
python gateway/run.py
```

---

## 📁 项目结构

```
HT-SmartSales/
├── agent/                      # 核心业务逻辑
│   ├── presales_policy.py     # 槽位策略和配置
│   ├── presales_state_machine.py  # 三阶段状态机
│   ├── presales_answer_gate.py    # 答案质量门控
│   ├── presales_summarizer.py     # 信息摘要生成
│   └── presales_proposal.py       # 方案模板渲染
├── presales_services/         # 服务目录
│   └── 客户专属穿搭服务/
│       ├── proposal.md        # 方案模板示例
│       └── slots.yaml         # 槽位配置示例
├── docs/presales-rag/         # 文档
│   ├── design-decision-record.md
│   ├── runtime-config.md
│   └── TEMPLATE_GUIDE.md
├── tests/                     # 测试
│   ├── agent/test_presales_*.py
│   └── tools/test_ragflow_tool.py
└── LICENSES/                  # 开源协议
    ├── HERMES-MIT.txt
    └── RAGFLOW-APACHE2.txt
```

---

## 🎨 模板系统

### 占位符类型

```markdown
# 方案模板示例

## 客户信息
- 客户姓名：{{slot:customer_name}}
- 联系方式：{{slot:contact}}

## 方案详情
{{rag:产品定价信息}}

## AI 生成内容
{{ai:根据客户需求生成个性化建议}}

## 系统信息
- 生成时间：{{sys:datetime}}
- 会话ID：{{sys:session_id}}
```

详细文档请查看 [TEMPLATE_GUIDE.md](docs/presales-rag/TEMPLATE_GUIDE.md)

---

## 🔧 配置说明

### 环境变量

```bash
# LLM API
OPENROUTER_API_KEY=your_key_here
# 或使用其他提供商
OPENAI_API_KEY=your_key_here

# RAGFlow（可选）
RAGFLOW_API_KEY=your_key_here
RAGFLOW_BASE_URL=http://localhost:9380

# 消息平台（可选）
TELEGRAM_BOT_TOKEN=your_token_here
DISCORD_BOT_TOKEN=your_token_here
```

### 服务配置

编辑 `config.yaml` 中的 presales 配置：

```yaml
agent:
  presales_enabled: true
  presales_state_machine_enabled: true
  presales_answer_gate_enabled: true
```

---

## 📊 工作流程

```
用户输入
   ↓
信息收集阶段 (info_collection)
   ├─ 槽位识别
   ├─ 智能追问
   └─ 覆盖率检查
   ↓
信息整理阶段 (info_summarization)
   ├─ 生成结构化摘要
   ├─ 等待用户确认
   └─ 自然语言确认
   ↓
方案生成阶段 (proposal)
   ├─ 模板渲染
   ├─ RAG 知识检索
   ├─ AI 内容生成
   └─ 输出最终方案
```

---

## 🧪 测试

```bash
# 运行所有测试
./scripts/run_tests.sh

# 运行 presales 测试
./scripts/run_tests.sh tests/agent/test_presales_*.py

# 运行状态机测试
./scripts/run_tests.sh tests/agent/test_presales_state_machine.py
```

---

## 📝 开源声明

本项目基于以下开源项目开发：

- **Hermes Agent** - MIT License
  - 项目地址：https://github.com/NousResearch/hermes-agent
  - 用途：AI Agent 基础框架

- **RAGFlow** - Apache 2.0 License
  - 项目地址：https://github.com/infiniflow/ragflow
  - 用途：RAG 检索增强生成引擎

完整的开源协议请查看 [LICENSES/](LICENSES/) 目录。

---

## 📄 许可证

本项目的业务逻辑代码（presales 模块）采用专有许可证。

基础框架部分遵循原项目的开源协议（MIT 和 Apache 2.0）。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📧 联系方式

- GitHub: https://github.com/AaronWander/HT-SmartSales
- Issues: https://github.com/AaronWander/HT-SmartSales/issues

---

**海獭 SmartSales AI** - 让售前更智能 🦦
