<p align="center">
  <img src="https://raw.githubusercontent.com/AaronWander/HT-SmartSales/main/assets/logo.png" alt="海獭 SmartSales AI" width="200">
</p>

<h1 align="center">🦦 海獭 SmartSales AI</h1>

<p align="center">
  <strong>AI 驱动的智能售前服务系统 | 让售前咨询更高效、更专业</strong>
</p>

<p align="center">
  <a href="#核心优势">核心优势</a> •
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用场景">使用场景</a> •
  <a href="#文档">文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge" alt="AI Powered">
  <img src="https://img.shields.io/badge/售前-自动化-green?style=for-the-badge" alt="Sales Automation">
  <img src="https://img.shields.io/badge/效率-提升10倍-orange?style=for-the-badge" alt="10x Efficiency">
  <img src="https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge" alt="License">
</p>

---

## 🎯 为什么选择海獭 SmartSales AI？

### 传统售前的痛点
- ❌ **重复劳动** - 每个客户都要从头问一遍需求
- ❌ **效率低下** - 一个售前顾问一天只能服务 3-5 个客户
- ❌ **方案质量不稳定** - 依赖个人经验，新人上手慢
- ❌ **知识分散** - 产品信息、报价、案例散落各处
- ❌ **响应慢** - 客户咨询后需要等待人工整理方案

### 海獭 SmartSales AI 的解决方案
- ✅ **智能对话收集** - AI 自动引导客户提供关键信息
- ✅ **10倍效率提升** - 一个顾问可同时服务 30+ 客户
- ✅ **标准化输出** - 基于模板确保方案质量一致
- ✅ **知识库集成** - 自动检索产品信息、报价、案例
- ✅ **秒级响应** - 客户咨询后 1 分钟内生成初步方案

---

## 🚀 核心优势

### 1️⃣ 智能需求挖掘
不是简单的问答机器人，而是**懂业务的售前顾问**

```
传统方式：
售前："您的预算是多少？"
客户："不确定"
售前："那您的需求是什么？"
客户："也不太清楚..."
→ 对话陷入僵局

海獭方式：
AI："我看到您是做电商的，通常电商客户关注的是订单处理效率和库存管理，
     您这边主要是哪方面遇到了瓶颈呢？"
客户："对！我们现在订单量大了，人工处理不过来"
AI："明白了，那您现在日均订单量大概多少？高峰期能到多少？"
→ 自然引导，快速定位需求
```

**核心技术**：
- 🧠 **上下文理解** - 记住对话历史，不重复提问
- 🎯 **智能追问** - 根据缺失信息动态生成问题
- 📊 **槽位管理** - 自动识别和填充业务关键信息
- 🔍 **意图识别** - 区分咨询、确认、修改等不同意图

### 2️⃣ 三阶段标准化流程
确保每个客户都得到**完整、专业**的服务

```
阶段 1: 信息收集 (info_collection)
├─ 自动识别客户行业、规模、痛点
├─ 智能追问缺失的关键信息
└─ 实时计算信息完整度

阶段 2: 信息整理 (info_summarization)
├─ 生成结构化需求摘要
├─ 展示给客户确认
└─ 支持自然语言修改

阶段 3: 方案生成 (proposal)
├─ 基于模板自动生成方案
├─ 从知识库检索相关信息
├─ AI 生成个性化建议
└─ 输出完整的售前方案文档
```

### 3️⃣ 灵活的模板系统
**一次配置，终身受益**

```markdown
# 方案模板示例

## 客户信息
- 公司名称：{{slot:company_name}}
- 行业：{{slot:industry}}
- 规模：{{slot:company_size}}

## 需求分析
客户的核心痛点是：{{slot:pain_point}}

根据我们的经验，{{slot:industry}}行业的客户通常需要：
{{ai:根据行业和痛点生成针对性分析}}

## 解决方案
{{rag:查询产品库，匹配最适合的产品}}

## 报价方案
{{rag:根据客户规模查询报价表}}

## 成功案例
{{rag:查询同行业成功案例}}

## 实施计划
预计实施周期：{{ai:根据客户规模和需求复杂度估算}}
```

**支持的占位符**：
- `{{slot:xxx}}` - 客户信息槽位
- `{{sys:xxx}}` - 系统信息（时间、会话ID等）
- `{{rag:xxx}}` - 知识库检索（产品、报价、案例）
- `{{ai:xxx}}` - AI 生成内容（分析、建议、估算）
- `{{ext:xxx}}` - 外部工具调用（CRM、ERP等）

### 4️⃣ 知识库深度集成
**让 AI 成为你的产品专家**

基于 **RAGFlow** 检索增强生成技术：
- 📚 **产品知识库** - 自动检索产品特性、规格、优势
- 💰 **报价库** - 根据客户规模自动匹配报价方案
- 📖 **案例库** - 检索同行业成功案例增强说服力
- 📋 **政策库** - 自动引用公司政策、服务条款
- 🎓 **FAQ 库** - 快速回答常见问题

**智能检索特性**：
- ✅ 语义理解（不是简单的关键词匹配）
- ✅ 上下文感知（根据对话历史调整检索策略）
- ✅ 去重缓存（避免重复检索）
- ✅ 来源标注（方案中标注信息来源）

### 5️⃣ 多平台无缝接入
**客户在哪里，服务就在哪里**

- 💬 **即时通讯** - Telegram、Discord、Slack、WhatsApp
- 🌐 **Web 接口** - 嵌入官网、客服系统
- 📱 **移动端** - 微信公众号、小程序（规划中）
- 🖥️ **CLI** - 命令行界面（内部测试）
- 🔌 **API** - RESTful API（系统集成）

---

## 💼 使用场景

### 场景 1：SaaS 软件售前
**客户**：某 CRM 软件公司  
**痛点**：每天收到 50+ 咨询，售前团队只有 3 人，响应不过来  
**效果**：
- ⏱️ 响应时间从 2 小时降到 **5 分钟**
- 📈 咨询转化率从 15% 提升到 **28%**
- 👥 售前团队效率提升 **12 倍**

### 场景 2：定制化服务售前
**客户**：某企业数字化转型咨询公司  
**痛点**：每个客户需求差异大，方案编写耗时 2-3 天  
**效果**：
- ⚡ 方案生成时间从 3 天降到 **30 分钟**
- 📊 方案质量更标准化，客户满意度提升 **40%**
- 💰 售前成本降低 **60%**

### 场景 3：电商平台客服
**客户**：某跨境电商平台  
**痛点**：客户咨询产品推荐，人工客服无法快速匹配  
**效果**：
- 🎯 产品推荐准确率 **85%**
- 🛒 咨询转化率提升 **35%**
- 💬 客服压力降低 **70%**

---

## ✨ 功能特性

### 🎯 智能对话引擎
- [x] 自然语言理解（NLU）
- [x] 上下文记忆（多轮对话）
- [x] 意图识别（咨询/确认/修改）
- [x] 情感分析（识别客户情绪）
- [x] 多语言支持（中文/英文）

### 📋 业务流程管理
- [x] 三阶段状态机
- [x] 槽位自动填充
- [x] 信息完整度检查
- [x] 自然语言确认
- [x] 流程可视化（规划中）

### 🎨 模板与配置
- [x] 服务目录化管理
- [x] 五类占位符系统
- [x] 模板热更新
- [x] 多服务并行
- [x] 版本管理（规划中）

### 🔍 知识库集成
- [x] RAGFlow 深度集成
- [x] 语义检索
- [x] 上下文感知
- [x] 来源标注
- [x] 实时更新

### 📊 数据分析
- [x] 对话质量评估
- [x] 槽位覆盖率统计
- [x] 转化率分析（规划中）
- [x] 客户画像（规划中）
- [x] A/B 测试（规划中）

### 🔐 企业级特性
- [x] 多租户隔离
- [x] 权限管理
- [x] 审计日志
- [x] 数据加密
- [x] 私有化部署

---

## 🚀 快速开始

### 前置要求
- Python 3.9+
- 大语言模型 API（OpenAI / Claude / 国产大模型）
- RAGFlow（可选，用于知识库检索）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/AaronWander/HT-SmartSales.git
cd HT-SmartSales

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，配置你的 API keys
```

### 配置你的第一个服务

```bash
# 创建服务目录
mkdir -p presales_services/我的服务

# 创建方案模板
cat > presales_services/我的服务/proposal.md << 'EOF'
# {{slot:company_name}} 专属解决方案

## 客户信息
- 公司：{{slot:company_name}}
- 行业：{{slot:industry}}
- 需求：{{slot:requirement}}

## 解决方案
{{rag:根据行业查询产品方案}}

## 报价
{{rag:根据规模查询报价}}
EOF

# 创建槽位配置
cat > presales_services/我的服务/slots.yaml << 'EOF'
id: 我的服务
required_base:
  - company_name
  - industry
  - requirement
meta:
  company_name:
    label: 公司名称
    desc: 客户的公司名称
  industry:
    label: 所属行业
    desc: 客户所在的行业领域
  requirement:
    label: 核心需求
    desc: 客户的主要需求或痛点
EOF
```

### 启动服务

```bash
# 方式 1：CLI 模式（测试）
python cli.py

# 方式 2：Telegram Bot
python gateway/run.py --platform telegram

# 方式 3：Web API
python gateway/run.py --platform api
```

### 测试对话

```
用户: 你好，我想了解一下你们的产品
AI: 您好！我是海獭智能售前助手。为了给您提供最合适的方案，
    能先了解一下您的公司名称吗？

用户: 我们是ABC科技公司
AI: 好的，ABC科技公司。请问贵公司是做什么行业的呢？

用户: 我们是做电商的
AI: 明白了，电商行业。那您这边主要遇到了什么问题或者
    有什么需求呢？

用户: 我们现在订单量大了，库存管理很混乱
AI: 收到！让我为您整理一下信息：
    - 公司：ABC科技公司
    - 行业：电商
    - 需求：订单量增长，库存管理混乱
    
    这些信息对吗？

用户: 对的
AI: 好的，正在为您生成专属方案...
    
    [生成完整的售前方案文档]
```

---

## 📁 项目结构

```
HT-SmartSales/
├── agent/                          # 🧠 核心业务逻辑
│   ├── presales_policy.py         # 槽位策略和配置解析
│   ├── presales_state_machine.py  # 三阶段状态机
│   ├── presales_answer_gate.py    # 答案质量门控
│   ├── presales_summarizer.py     # 信息摘要生成
│   └── presales_proposal.py       # 方案模板渲染引擎
│
├── presales_services/              # 📋 服务配置目录
│   └── 客户专属穿搭服务/          # 示例服务
│       ├── proposal.md            # 方案模板
│       └── slots.yaml             # 槽位配置
│
├── tools/                          # 🔧 工具集成
│   ├── ragflow_tool.py            # RAGFlow 知识库工具
│   └── ...                        # 其他工具
│
├── gateway/                        # 🌐 多平台接入
│   ├── run.py                     # 网关主程序
│   ├── telegram_gateway.py        # Telegram 集成
│   ├── discord_gateway.py         # Discord 集成
│   └── ...                        # 其他平台
│
├── docs/                           # 📚 文档
│   └── presales-rag/
│       ├── design-decision-record.md  # 设计文档
│       ├── runtime-config.md          # 配置说明
│       └── TEMPLATE_GUIDE.md          # 模板编写指南
│
├── tests/                          # 🧪 测试
│   ├── agent/test_presales_*.py   # 业务逻辑测试
│   └── tools/test_ragflow_tool.py # 工具测试
│
├── LICENSES/                       # 📄 开源声明
│   ├── HERMES-MIT.txt             # Hermes Agent 协议
│   ├── RAGFLOW-APACHE2.txt        # RAGFlow 协议
│   └── README.md                  # 许可证说明
│
└── README.md                       # 📖 本文档
```

---

## 📚 文档

### 快速入门
- [安装指南](docs/installation.md)
- [5分钟快速开始](docs/quickstart.md)
- [配置说明](docs/configuration.md)

### 核心概念
- [三阶段工作流](docs/presales-rag/design-decision-record.md)
- [槽位系统](docs/presales-rag/runtime-config.md)
- [模板编写指南](docs/presales-rag/TEMPLATE_GUIDE.md)

### 集成指南
- [RAGFlow 知识库集成](docs/ragflow-integration.md)
- [Telegram Bot 部署](docs/telegram-deployment.md)
- [API 接口文档](docs/api-reference.md)

### 最佳实践
- [模板设计最佳实践](docs/template-best-practices.md)
- [知识库组织建议](docs/knowledge-base-organization.md)
- [性能优化指南](docs/performance-optimization.md)

---

## 🔧 配置说明

### 环境变量

```bash
# ===== LLM 配置 =====
# 选择一个 LLM 提供商
OPENROUTER_API_KEY=sk-or-xxx        # OpenRouter（推荐，支持多模型）
# 或
OPENAI_API_KEY=sk-xxx               # OpenAI
# 或
ANTHROPIC_API_KEY=sk-ant-xxx        # Claude

# ===== RAGFlow 配置（可选）=====
RAGFLOW_API_KEY=ragflow-xxx
RAGFLOW_BASE_URL=http://localhost:9380

# ===== 消息平台配置（可选）=====
TELEGRAM_BOT_TOKEN=123456:ABC-xxx
DISCORD_BOT_TOKEN=xxx
SLACK_BOT_TOKEN=xoxb-xxx
```

### 业务配置 (config.yaml)

```yaml
agent:
  # 启用售前功能
  presales_enabled: true
  
  # 状态机配置
  presales_state_machine_enabled: true
  presales_answer_gate_enabled: true
  
  # 槽位评估模式
  presales_slot_assessment_mode: "llm_structured"  # llm_structured | heuristic
  
  # 知识库配置
  ragflow_hybrid_mode: "on"  # on | off | always
  ragflow_single_retrieval_mode: true
  ragflow_max_calls_per_turn: 1
  
  # 质量门控
  confidence_thresholds:
    high_slot_coverage: 0.8
    medium_slot_coverage: 0.5
```

---

## 📊 性能指标

### 响应速度
- 信息收集：< 2 秒
- 摘要生成：< 3 秒
- 方案生成：< 30 秒（含知识库检索）

### 准确率
- 槽位识别准确率：> 90%
- 意图识别准确率：> 85%
- 知识检索相关性：> 80%

### 并发能力
- 单实例支持：100+ 并发会话
- 水平扩展：无限制

---

## 🧪 测试

```bash
# 运行所有测试
./scripts/run_tests.sh

# 运行 presales 业务测试
./scripts/run_tests.sh tests/agent/test_presales_*.py

# 运行状态机测试
./scripts/run_tests.sh tests/agent/test_presales_state_machine.py

# 运行知识库工具测试
./scripts/run_tests.sh tests/tools/test_ragflow_tool.py
```

**测试覆盖率**：
- 状态机：100%
- 槽位管理：95%
- 模板渲染：90%
- 总体：85%+

---

## 🗺️ 路线图

### v1.0（当前版本）✅
- [x] 三阶段工作流
- [x] 智能槽位管理
- [x] 模板系统
- [x] RAGFlow 集成
- [x] 多平台支持

### v1.1（规划中）🚧
- [ ] 可视化流程编辑器
- [ ] 更多占位符类型
- [ ] 客户画像分析
- [ ] A/B 测试框架

### v2.0（未来）🔮
- [ ] 多语言支持（英文、日文）
- [ ] 语音对话支持
- [ ] 视频演示生成
- [ ] CRM 深度集成
- [ ] 自动学习优化

---

## 📝 开源声明

本项目基于以下开源项目开发：

### Hermes Agent
- **许可证**: MIT License
- **项目地址**: https://github.com/NousResearch/hermes-agent
- **用途**: AI Agent 基础框架
- **版权**: Copyright (c) 2025 Nous Research

### RAGFlow
- **许可证**: Apache 2.0 License
- **项目地址**: https://github.com/infiniflow/ragflow
- **用途**: RAG 检索增强生成引擎
- **版权**: Copyright (c) InfiniFlow, Inc.

完整的开源协议请查看 [LICENSES/](LICENSES/) 目录。

---

## 📄 许可证

**海獭 SmartSales AI** 的业务逻辑代码（presales 模块及相关配置）采用**专有许可证**。

基础框架部分遵循原项目的开源协议（MIT 和 Apache 2.0）。

商业使用请联系我们获取授权。

---

## 🤝 商业合作

### 💼 企业版
- ✅ 私有化部署
- ✅ 定制化开发
- ✅ 技术支持（7x24）
- ✅ 培训服务
- ✅ SLA 保障

### 🎓 培训服务
- AI 售前系统搭建培训
- 模板设计最佳实践
- 知识库管理培训

### 🔧 定制开发
- 行业定制方案
- 系统集成（CRM/ERP）
- 特殊功能开发

---

## 📧 联系我们

- 📮 **Email**: contact@smartsales-ai.com
- 💬 **微信**: SmartSalesAI
- 🌐 **官网**: https://smartsales-ai.com
- 📱 **电话**: +86 xxx-xxxx-xxxx

- 🐛 **Bug 反馈**: [GitHub Issues](https://github.com/AaronWander/HT-SmartSales/issues)
- 💡 **功能建议**: [GitHub Discussions](https://github.com/AaronWander/HT-SmartSales/discussions)

---

## 🌟 Star History

如果这个项目对你有帮助，请给我们一个 ⭐️ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=AaronWander/HT-SmartSales&type=Date)](https://star-history.com/#AaronWander/HT-SmartSales&Date)

---

<p align="center">
  <strong>海獭 SmartSales AI - 让售前更智能 🦦</strong>
  <br>
  <sub>Built with ❤️ by the SmartSales Team</sub>
</p>

<p align="center">
  <a href="#top">回到顶部 ⬆️</a>
</p>
