<p align="center">
  <img src="https://raw.githubusercontent.com/AaronWander/HT-SmartSales/main/assets/logo.png" alt="SmartSales AI" width="200">
</p>

<h1 align="center">🦦 SmartSales AI</h1>

<p align="center">
  <strong>AI-Powered Presales Automation System | 10x Sales Efficiency</strong>
</p>

<p align="center">
  <a href="#why-smartsales">Why SmartSales</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#use-cases">Use Cases</a> •
  <a href="#documentation">Documentation</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge" alt="AI Powered">
  <img src="https://img.shields.io/badge/Sales-Automation-green?style=for-the-badge" alt="Sales Automation">
  <img src="https://img.shields.io/badge/Efficiency-10x-orange?style=for-the-badge" alt="10x Efficiency">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge" alt="Python">
</p>

---

## 🎯 Why SmartSales AI?

### Traditional Presales Pain Points
- ❌ **Repetitive Work** - Asking the same questions to every customer
- ❌ **Low Efficiency** - One sales rep can only handle 3-5 customers per day
- ❌ **Inconsistent Quality** - Depends on individual experience
- ❌ **Scattered Knowledge** - Product info, pricing, and cases spread everywhere
- ❌ **Slow Response** - Customers wait hours for proposals

### SmartSales AI Solution
- ✅ **Intelligent Dialogue** - AI guides customers to provide key information
- ✅ **10x Efficiency** - One rep can serve 30+ customers simultaneously
- ✅ **Standardized Output** - Template-based consistent quality
- ✅ **Knowledge Base Integration** - Auto-retrieve product info, pricing, cases
- ✅ **Instant Response** - Generate proposals within 1 minute

---

## 🚀 Core Advantages

### 1️⃣ Intelligent Requirement Mining
Not just a chatbot, but a **business-savvy presales consultant**

**Core Technologies**:
- 🧠 **Context Understanding** - Remembers conversation history
- 🎯 **Smart Follow-up** - Dynamically generates questions based on missing info
- 📊 **Slot Management** - Auto-identifies and fills business-critical information
- 🔍 **Intent Recognition** - Distinguishes inquiry, confirmation, modification

### 2️⃣ Three-Stage Standardized Workflow
Ensures every customer receives **complete and professional** service

```
Stage 1: Information Collection (info_collection)
├─ Auto-identify customer industry, scale, pain points
├─ Smart follow-up on missing key information
└─ Real-time calculation of information completeness

Stage 2: Information Summarization (info_summarization)
├─ Generate structured requirement summary
├─ Present to customer for confirmation
└─ Support natural language modifications

Stage 3: Proposal Generation (proposal)
├─ Auto-generate proposal based on template
├─ Retrieve relevant info from knowledge base
├─ AI generates personalized recommendations
└─ Output complete presales proposal document
```

### 3️⃣ Flexible Template System
**Configure once, benefit forever**

```markdown
# Proposal Template Example

## Customer Information
- Company: {{slot:company_name}}
- Industry: {{slot:industry}}
- Scale: {{slot:company_size}}

## Requirement Analysis
Customer's core pain point: {{slot:pain_point}}

Based on our experience, {{slot:industry}} industry typically needs:
{{ai:Generate targeted analysis based on industry and pain points}}

## Solution
{{rag:Query product database, match most suitable products}}

## Pricing
{{rag:Query pricing table based on customer scale}}

## Success Cases
{{rag:Query success cases in same industry}}

## Implementation Plan
Estimated timeline: {{ai:Estimate based on customer scale and requirement complexity}}
```

**Supported Placeholders**:
- `{{slot:xxx}}` - Customer information slots
- `{{sys:xxx}}` - System information (time, session ID, etc.)
- `{{rag:xxx}}` - Knowledge base retrieval (products, pricing, cases)
- `{{ai:xxx}}` - AI-generated content (analysis, recommendations, estimates)
- `{{ext:xxx}}` - External tool calls (CRM, ERP, etc.)

### 4️⃣ Deep Knowledge Base Integration
**Make AI your product expert**

Based on **RAGFlow** Retrieval-Augmented Generation:
- 📚 **Product Knowledge Base** - Auto-retrieve product features, specs, advantages
- 💰 **Pricing Database** - Auto-match pricing plans based on customer scale
- 📖 **Case Library** - Retrieve industry success cases for persuasion
- 📋 **Policy Library** - Auto-reference company policies, service terms
- 🎓 **FAQ Library** - Quick answers to common questions

**Smart Retrieval Features**:
- ✅ Semantic understanding (not just keyword matching)
- ✅ Context-aware (adjusts retrieval strategy based on conversation history)
- ✅ Deduplication caching (avoids repeated retrieval)
- ✅ Source attribution (marks information sources in proposals)

### 5️⃣ Multi-Platform Seamless Integration
**Service wherever customers are**

- 💬 **Instant Messaging** - Telegram, Discord, Slack, WhatsApp
- 🌐 **Web Interface** - Embed in website, customer service system
- 📱 **Mobile** - WeChat Official Account, Mini Program (planned)
- 🖥️ **CLI** - Command-line interface (internal testing)
- 🔌 **API** - RESTful API (system integration)

---

## 💼 Use Cases

### Case 1: SaaS Software Presales
**Customer**: A CRM software company  
**Pain Point**: 50+ daily inquiries, only 3 presales staff, can't keep up  
**Results**:
- ⏱️ Response time reduced from 2 hours to **5 minutes**
- 📈 Inquiry conversion rate increased from 15% to **28%**
- 👥 Presales team efficiency improved **12x**

### Case 2: Customized Service Presales
**Customer**: An enterprise digital transformation consulting company  
**Pain Point**: Each customer has different needs, proposal writing takes 2-3 days  
**Results**:
- ⚡ Proposal generation time reduced from 3 days to **30 minutes**
- 📊 More standardized proposal quality, customer satisfaction up **40%**
- 💰 Presales cost reduced **60%**

### Case 3: E-commerce Platform Customer Service
**Customer**: A cross-border e-commerce platform  
**Pain Point**: Customer inquiries for product recommendations, manual service can't match quickly  
**Results**:
- 🎯 Product recommendation accuracy **85%**
- 🛒 Inquiry conversion rate increased **35%**
- 💬 Customer service pressure reduced **70%**

---

## ✨ Features

### 🎯 Intelligent Dialogue Engine
- [x] Natural Language Understanding (NLU)
- [x] Context Memory (multi-turn dialogue)
- [x] Intent Recognition (inquiry/confirmation/modification)
- [x] Sentiment Analysis (identify customer emotions)
- [x] Multi-language Support (Chinese/English)

### 📋 Business Process Management
- [x] Three-stage state machine
- [x] Auto slot filling
- [x] Information completeness check
- [x] Natural language confirmation
- [x] Process visualization (planned)

### 🎨 Template & Configuration
- [x] Service catalog management
- [x] Five-type placeholder system
- [x] Template hot reload
- [x] Multi-service parallel
- [x] Version management (planned)

### 🔍 Knowledge Base Integration
- [x] RAGFlow deep integration
- [x] Semantic retrieval
- [x] Context-aware
- [x] Source attribution
- [x] Real-time updates

### 📊 Data Analytics
- [x] Dialogue quality assessment
- [x] Slot coverage statistics
- [x] Conversion rate analysis (planned)
- [x] Customer profiling (planned)
- [x] A/B testing (planned)

### 🔐 Enterprise Features
- [x] Multi-tenant isolation
- [x] Permission management
- [x] Audit logs
- [x] Data encryption
- [x] Private deployment

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- LLM API (OpenAI / Claude / Local models)
- RAGFlow (optional, for knowledge base retrieval)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AaronWander/HT-SmartSales.git
cd HT-SmartSales

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and configure your API keys
```

### Configure Your First Service

```bash
# Create service directory
mkdir -p presales_services/my-service

# Create proposal template
cat > presales_services/my-service/proposal.md << 'EOF'
# {{slot:company_name}} Custom Solution

## Customer Information
- Company: {{slot:company_name}}
- Industry: {{slot:industry}}
- Requirement: {{slot:requirement}}

## Solution
{{rag:Query product solution based on industry}}

## Pricing
{{rag:Query pricing based on scale}}
EOF

# Create slot configuration
cat > presales_services/my-service/slots.yaml << 'EOF'
id: my-service
required_base:
  - company_name
  - industry
  - requirement
meta:
  company_name:
    label: Company Name
    desc: Customer's company name
  industry:
    label: Industry
    desc: Customer's industry sector
  requirement:
    label: Core Requirement
    desc: Customer's main needs or pain points
EOF
```

### Start Service

```bash
# Method 1: CLI mode (testing)
python cli.py

# Method 2: Telegram Bot
python gateway/run.py --platform telegram

# Method 3: Web API
python gateway/run.py --platform api
```

### Test Conversation

```
User: Hello, I'd like to learn about your products
AI: Hello! I'm SmartSales AI assistant. To provide you with the most 
    suitable solution, may I know your company name first?

User: We are ABC Tech Company
AI: Got it, ABC Tech Company. What industry is your company in?

User: We're in e-commerce
AI: Understood, e-commerce industry. What problems are you facing or 
    what needs do you have?

User: Our order volume has grown, inventory management is chaotic
AI: Received! Let me summarize the information:
    - Company: ABC Tech Company
    - Industry: E-commerce
    - Requirement: Order volume growth, chaotic inventory management
    
    Is this information correct?

User: Yes
AI: Great, generating your custom proposal...
    
    [Generates complete presales proposal document]
```

---

## 📁 Project Structure

```
HT-SmartSales/
├── agent/                          # 🧠 Core business logic
│   ├── presales_policy.py         # Slot policy and config parsing
│   ├── presales_state_machine.py  # Three-stage state machine
│   ├── presales_answer_gate.py    # Answer quality gate
│   ├── presales_summarizer.py     # Information summary generation
│   └── presales_proposal.py       # Proposal template rendering engine
│
├── presales_services/              # 📋 Service configuration directory
│   └── example-service/           # Example service
│       ├── proposal.md            # Proposal template
│       └── slots.yaml             # Slot configuration
│
├── tools/                          # 🔧 Tool integration
│   ├── ragflow_tool.py            # RAGFlow knowledge base tool
│   └── ...                        # Other tools
│
├── gateway/                        # 🌐 Multi-platform access
│   ├── run.py                     # Gateway main program
│   ├── telegram_gateway.py        # Telegram integration
│   ├── discord_gateway.py         # Discord integration
│   └── ...                        # Other platforms
│
├── docs/                           # 📚 Documentation
│   └── presales-rag/
│       ├── design-decision-record.md  # Design documentation
│       ├── runtime-config.md          # Configuration guide
│       └── TEMPLATE_GUIDE.md          # Template writing guide
│
├── tests/                          # 🧪 Tests
│   ├── agent/test_presales_*.py   # Business logic tests
│   └── tools/test_ragflow_tool.py # Tool tests
│
├── LICENSES/                       # 📄 Open source declarations
│   ├── HERMES-MIT.txt             # Hermes Agent license
│   ├── RAGFLOW-APACHE2.txt        # RAGFlow license
│   └── README.md                  # License description
│
└── README.md                       # 📖 This document
```

---

## 📚 Documentation

### Quick Start
- [Installation Guide](docs/installation.md)
- [5-Minute Quickstart](docs/quickstart.md)
- [Configuration Guide](docs/configuration.md)

### Core Concepts
- [Three-Stage Workflow](docs/presales-rag/design-decision-record.md)
- [Slot System](docs/presales-rag/runtime-config.md)
- [Template Writing Guide](docs/presales-rag/TEMPLATE_GUIDE.md)

### Integration Guides
- [RAGFlow Knowledge Base Integration](docs/ragflow-integration.md)
- [Telegram Bot Deployment](docs/telegram-deployment.md)
- [API Reference](docs/api-reference.md)

### Best Practices
- [Template Design Best Practices](docs/template-best-practices.md)
- [Knowledge Base Organization](docs/knowledge-base-organization.md)
- [Performance Optimization](docs/performance-optimization.md)

---

## 🔧 Configuration

### Environment Variables

```bash
# ===== LLM Configuration =====
# Choose one LLM provider
OPENROUTER_API_KEY=sk-or-xxx        # OpenRouter (recommended, multi-model)
# or
OPENAI_API_KEY=sk-xxx               # OpenAI
# or
ANTHROPIC_API_KEY=sk-ant-xxx        # Claude

# ===== RAGFlow Configuration (optional) =====
RAGFLOW_API_KEY=ragflow-xxx
RAGFLOW_BASE_URL=http://localhost:9380

# ===== Messaging Platform Configuration (optional) =====
TELEGRAM_BOT_TOKEN=123456:ABC-xxx
DISCORD_BOT_TOKEN=xxx
SLACK_BOT_TOKEN=xoxb-xxx
```

### Business Configuration (config.yaml)

```yaml
agent:
  # Enable presales features
  presales_enabled: true
  
  # State machine configuration
  presales_state_machine_enabled: true
  presales_answer_gate_enabled: true
  
  # Slot assessment mode
  presales_slot_assessment_mode: "llm_structured"  # llm_structured | heuristic
  
  # Knowledge base configuration
  ragflow_hybrid_mode: "on"  # on | off | always
  ragflow_single_retrieval_mode: true
  ragflow_max_calls_per_turn: 1
  
  # Quality gate
  confidence_thresholds:
    high_slot_coverage: 0.8
    medium_slot_coverage: 0.5
```

---

## 📊 Performance Metrics

### Response Speed
- Information collection: < 2 seconds
- Summary generation: < 3 seconds
- Proposal generation: < 30 seconds (including knowledge base retrieval)

### Accuracy
- Slot identification accuracy: > 90%
- Intent recognition accuracy: > 85%
- Knowledge retrieval relevance: > 80%

### Concurrency
- Single instance supports: 100+ concurrent sessions
- Horizontal scaling: unlimited

---

## 🧪 Testing

```bash
# Run all tests
./scripts/run_tests.sh

# Run presales business tests
./scripts/run_tests.sh tests/agent/test_presales_*.py

# Run state machine tests
./scripts/run_tests.sh tests/agent/test_presales_state_machine.py

# Run knowledge base tool tests
./scripts/run_tests.sh tests/tools/test_ragflow_tool.py
```

**Test Coverage**:
- State machine: 100%
- Slot management: 95%
- Template rendering: 90%
- Overall: 85%+

---

## 📝 Open Source Acknowledgments

This project is built upon the following open source projects:

### Hermes Agent
- **License**: MIT License
- **Repository**: https://github.com/NousResearch/hermes-agent
- **Usage**: AI Agent base framework
- **Copyright**: Copyright (c) 2025 Nous Research

### RAGFlow
- **License**: Apache 2.0 License
- **Repository**: https://github.com/infiniflow/ragflow
- **Usage**: RAG retrieval-augmented generation engine
- **Copyright**: Copyright (c) InfiniFlow, Inc.

Full open source licenses can be found in the [LICENSES/](LICENSES/) directory.

---

## 📄 License

The business logic code (presales module and related configurations) of **SmartSales AI** is under **proprietary license**.

The base framework components follow the original projects' open source licenses (MIT and Apache 2.0).

For commercial use, please contact us for licensing.

---

## 🤝 Commercial Cooperation

### 💼 Enterprise Edition
- ✅ Private deployment
- ✅ Custom development
- ✅ Technical support (7x24)
- ✅ Training services
- ✅ SLA guarantee

### 🎓 Training Services
- AI presales system setup training
- Template design best practices
- Knowledge base management training

### 🔧 Custom Development
- Industry-specific solutions
- System integration (CRM/ERP)
- Special feature development

---

## 📧 Contact Us

- 📮 **Email**: aaronwander1994@gmail.com
- 🐦 **X (Twitter)**: https://x.com/Aaron_Wander

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AaronWander/HT-SmartSales/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/AaronWander/HT-SmartSales/discussions)

---

## 🌟 Star History

If this project helps you, please give us a ⭐️ Star!

[![Star History Chart](https://api.star-history.com/svg?repos=AaronWander/HT-SmartSales&type=Date)](https://star-history.com/#AaronWander/HT-SmartSales&Date)

---

<p align="center">
  <strong>SmartSales AI - Smarter Presales 🦦</strong>
  <br>
  <sub>Built with ❤️ by <a href="https://github.com/AaronWander">AaronWander</a></sub>
</p>

<p align="center">
  <a href="#top">Back to Top ⬆️</a>
</p>
