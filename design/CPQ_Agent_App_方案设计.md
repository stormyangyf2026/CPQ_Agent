# CPQ Agent App 方案设计文档

> 项目代号: 005_CPQ_Agent | 版本: v1.0 | 日期: 2026-07-05
> 项目路径: `iCloud/创新万维/0004. platform_dev/005_CPQ_Agent/`

---

## 一、项目目标

构建一个**独立运行的 AI 配单桌面应用**，用户通过自然语言对话完成产品配置、BOM 生成、定价、报价单生成。支持 macOS 和 Windows，与 CPQ App 零代码耦合。

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────┐
│  CPQ Agent App (桌面客户端 / PWA)                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  对话 UI (Vue 3 + Element Plus)                  │   │
│  │  ├─ 流式消息渲染                                 │   │
│  │  ├─ 产品卡片 / BOM 表格 / 方案对比               │   │
│  │  ├─ 配置面板 ⚙️                                   │   │
│  │  └─ 对话历史 / 多会话管理                         │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ SSE stream                             │
│  ┌─────────────▼───────────────────────────────────┐   │
│  │  DeepAgents 运行时 (:58100)                      │   │
│  │  ├─ create_deep_agent()                         │   │
│  │  ├─ tools: search / configure / bom / price      │   │
│  │  ├─ memory: 客户偏好持久化                        │   │
│  │  ├─ skills: 产品知识 / 定价策略                   │   │
│  │  └─ config.yaml → 所有可配置项                    │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ REST API                               │
│                │ Authorization: Bearer {cpq_token}      │
│  ┌─────────────▼───────────────────────────────────┐   │
│  │  CPQ App (:30000) - 不动                        │   │
│  │  search / configure / validate / complete / quote │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 三端关系

| 端 | 端口 | 技术 | 说明 |
|----|------|------|------|
| **CPQ Agent 前端** | 57100 (dev) / 静态文件 | Vue 3 + Vite | 独立 App，零 CPQ Portal 代码 |
| **DeepAgents 后端** | 58100 (dev) | Python + FastAPI | Agent 运行时 |
| **CPQ App** | 30000 (dev) | Spring Boot | 不变，纯 API 调用 |

---

## 三、核心技术选型

| 层 | 技术 | 理由 |
|----|------|------|
| 前端框架 | Vue 3 + Composition API + TypeScript | 团队熟悉，与 CPQ Portal 技术一致 |
| UI 组件库 | Element Plus | 同上 |
| Markdown 渲染 | markdown-it + highlight.js | 轻量，支持表格/代码/链接 |
| 流式通信 | Fetch API + ReadableStream | 原生，无需额外依赖 |
| 状态管理 | Pinia | 管理会话、配置、消息 |
| 打包 | Electron-builder (桌面) / Vite (PWA) | 三端一次构建 |
| Agent 后端 | DeepAgents (LangChain + LangGraph) | MIT 开源，内置全套能力 |
| HTTP 服务 | FastAPI + uvicorn | 异步高性能，SSE 原生支持 |
| 配置管理 | YAML (config.yaml) | 人类可读可编辑 |
| 持久化 | SQLite (会话) + JSON (配置) | 轻量，免安装数据库 |

---

## 四、配置体系设计

### 4.1 配置文件: `config.yaml`

```yaml
# ============================================================
# CPQ Agent App 配置文件
# 位置: <app>/config/config.yaml
# 可通过 App 内「设置」面板修改，也可直接编辑此文件
# ============================================================

# ── 模型配置 ──────────────────────────────────────────────
model:
  # 模型标识（provider:model 格式）
  # 支持: openai:gpt-5.5 | anthropic:claude-sonnet-4-6 | deepseek:deepseek-chat | ollama:llama3
  provider: "deepseek"
  model_name: "deepseek-chat"
  
  # API 配置
  api_key: "${DEEPSEEK_API_KEY}"      # 支持环境变量引用 ${VAR}
  base_url: "https://api.deepseek.com" # 自定义 API 地址（兼容代理/中转）
  
  # 模型参数
  temperature: 0.7
  max_tokens: 4096
  top_p: 0.9

# ── CPQ App 连接配置 ─────────────────────────────────────────
cpq:
  # CPQ App 后端地址（默认与前端同地址，端口 30000）
  base_url: "http://localhost:30000"
  
  # 认证信息
  client_id: "e5cd7e4891bf95d1d19206ce24a7b32e"
  
  # 连接超时（秒）
  timeout: 30
  
  # 重试次数
  max_retries: 3

# ── Agent 行为配置 ──────────────────────────────────────────
agent:
  # 系统提示词（支持模板变量: {cpq_url}）
  system_prompt: |
    你是一个制造业 CPQ（配置-定价-报价）智能助手。
    你的后端系统地址是 {cpq_url}。
    
    职责:
    1. 理解客户需求，推荐匹配的产品配置
    2. 根据 CPQ 约束规则验证配置可行性
    3. 生成 BOM 物料清单和定价
    4. 支持价格反向匹配和方案对比
    5. 生成报价单
    
    行为准则:
    - 推荐配置前先验证规则，不推荐不合规配置
    - 定价时说明基准价、折扣、建议价、最低限价
    - 反向匹配时明确告知替代方案的取舍
    - 生成报价单前请用户确认

  # 最大对话轮次（防止无限循环）
  max_turns: 20
  
  # 是否启用子 Agent（复杂任务委派）
  enable_subagents: true

# ── 记忆与技能 ──────────────────────────────────────────────
memory:
  # 持久记忆存储目录
  storage_path: "./data/memory"
  
  # 用户偏好文件（跨会话持久化）
  preferences_file: "preferences.md"
  
  # 最大记忆文件大小（KB）
  max_file_size_kb: 500

skills:
  # 技能目录
  paths:
    - "./skills/product-search"
    - "./skills/bom-config"
    - "./skills/pricing-rules"

# ── 人机协作 ──────────────────────────────────────────────
human_in_loop:
  # 需要审批的操作
  interrupt_on:
    create_quote: true       # 生成报价单前确认
    send_quote: true          # 发送报价单前确认

# ── 沙箱与权限 ──────────────────────────────────────────────
security:
  # 后端类型: state | filesystem | store | sandbox
  backend: "state"
  
  # 文件系统权限（仅 filesystem 后端生效）
  permissions:
    allow_paths: ["./workspace/**"]
    deny_paths: ["./config/**", "./data/**/*.key"]

# ── 日志与诊断 ──────────────────────────────────────────────
logging:
  level: "info"               # debug | info | warning | error
  file: "./logs/agent.log"
  max_size_mb: 10
  backup_count: 3

# ── 用户界面 ──────────────────────────────────────────────
ui:
  # 语言: zh-CN | en
  language: "zh-CN"
  
  # 主题: light | dark | auto
  theme: "auto"
  
  # 流式输出打字机速度（毫秒/字符，0=即时）
  typewriter_delay_ms: 20
  
  # 消息历史保留天数
  history_retention_days: 30
```

### 4.2 配置优先级

```
环境变量 > config.yaml > 代码默认值
```

敏感信息（API Key）**强制**只能通过环境变量设置，不会写入 config.yaml：

```yaml
# config.yaml 中引用环境变量
api_key: "${DEEPSEEK_API_KEY}"
```

### 4.3 配置入口设计（前端）

App 右上角「⚙️ 设置」按钮 → 配置面板：

```
┌─ 设置 ──────────────────────────────────────────┐
│                                                    │
│  🤖 模型配置                                       │
│  ┌─────────────────────────────────────────────┐  │
│  │ 模型提供者: [deepseek ▼]                    │  │
│  │ 模型名称:   [deepseek-chat ▼]               │  │
│  │ API Key:    [••••••••••••••••]  👁 切换      │  │
│  │ Base URL:   [https://api.deepseek.com    ]   │  │
│  │ Temperature:[====○====] 0.7                  │  │
│  │ Max Tokens: [4096                    ▼]     │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  🔗 CPQ 连接                                       │
│  ┌─────────────────────────────────────────────┐  │
│  │ CPQ 地址:   [http://localhost:30000      ]   │  │
│  │ Client ID:  [e5cd7e4891bf95d1d19206ce...]   │  │
│  │ 超时(秒):   [30                        ]     │  │
│  │              [测试连接] 按钮                  │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  ⚙️ Agent 行为                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │ 最大对话轮次: [20                      ]     │  │
│  │ 启用子Agent:  [✓]                            │  │
│  │ 报价确认:     [✓]                            │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  🎨 界面                                           │
│  ┌─────────────────────────────────────────────┐  │
│  │ 主题: [○ 浅色  ● 深色  ○ 自动]             │  │
│  │ 语言: [中文 ▼]                               │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  📊 系统信息                                       │
│  ┌─────────────────────────────────────────────┐  │
│  │ Agent 状态:  ● 运行中                        │  │
│  │ CPQ 连接:   ● 已连接 (172.16.1.115:30000)   │  │
│  │ 会话数:     3 个活跃                         │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  [恢复默认配置]  [导出配置]  [导入配置]              │
└────────────────────────────────────────────────────┘
```

---

## 五、Agent 后端设计

### 5.1 目录结构

```
backend/
├── agent.py              # Agent 主入口: create_deep_agent()
├── tools.py              # CPQ 工具: search/configure/bom/price/quote
├── server.py             # FastAPI 服务: SSE 端点
├── config.py             # 配置加载器
├── config.yaml           # 默认配置
├── requirements.txt      # Python 依赖
├── skills/               # 技能定义
│   ├── product-search/
│   │   └── SKILL.md
│   ├── bom-config/
│   │   └── SKILL.md
│   └── pricing-rules/
│       └── SKILL.md
├── data/                 # 运行时数据（自动创建）
│   ├── memory/           # 持久化记忆
│   └── sessions/         # 会话存档
└── logs/                 # 日志
```

### 5.2 Skills 技能体系

项目复用已有的 `cpq-agent` Skill，按 DeepAgents 的 [Agent Skills 规范](https://agentskills.io/specification) 组织。

#### 目录结构

```
backend/skills/
├── cpq-agent/                          ← ✅ 已有 Skill（5 文件）
│   ├── SKILL.md                        ← CPQ 全流程工作流
│   ├── references/
│   │   └── cpq-api-reference.md        ← 全部 CPQ API 文档
│   ├── scripts/
│   │   ├── cpq_api.py                  ← CPQ App API 封装（token/get/post）
│   │   └── cost_service.py             ← 成本核算服务
│   └── assets/
│       └── .env.example
├── product-search/                     ← ⏳ 待创建
└── pricing-rules/                      ← ⏳ 待创建
```

#### cpq-agent Skill 已覆盖的工作流

| 流程 | 输入 | 步骤 | 输出 | 状态 |
|------|------|------|------|------|
| **流程1：自然语言配置报价** | "德国客户 HVI-40.0" | 搜索→模型→验证→BOM→定价→展示 | BOM 表 + 报价 | ✅ 已跑通 |
| **流程2：文档驱动配置** | 上传 Excel/PDF 规格书 | 提取参数→匹配→配置→BOM→报价 | 配置 + BOM | 📋 已定义 |
| **流程3：报价单生成** | 完成配置 + CRM 客户 | 创建 header→关联 line→返回 ID | 报价单 ID | ✅ 已测通 |

#### cpq-agent SKILL.md 核心内容

```markdown
---
name: cpq-agent
description: |
  CPQ 智能配置报价助手。支持自然语言驱动的产品搜索、属性配置、
  约束规则验证、BOM展开、定价计算、CRM客户数据查询、报价单生成。
---

触发场景:
- 用户说"帮我配"、"配置产品"、"报价"、"生成BOM"
- 用户上传技术规格文档要求配置
- 用户需要CRM数据（客户、商机）

核心API:
- 搜索产品: GET /cpq/product/model/search
- 加载模型: GET /cpq/configure/model/{modelId}
- 验证选择: POST /cpq/configure/validate
- BOM预览: POST /cpq/configure/bom-preview
- 完整定价: POST /cpq/configure/complete
- CRM客户: GET /cpq/customer/account/list
- 创建报价: POST /cpq/quote/header
```

#### 与 DeepAgents 的集成方式

```python
# agent.py — 加载已有 Skill
agent = create_deep_agent(
    model=config.model_string,
    tools=tools,
    skills=[
        "./backend/skills/cpq-agent",     # ✅ 已有：CPQ 全流程
        "./backend/skills/pricing-rules",  # ⏳ 待建：定价策略知识
    ],
    memory=["/memories/AGENTS.md"],
    system_prompt=config.system_prompt,
)
```

Skill 的渐进式披露机制：
- **启动时**：只加载 Skill 的 `name` 和 `description`（约 50 tokens/skill）
- **用户问产品配置时**：Agent 自动读取 `cpq-agent/SKILL.md` 完整指令
- **需要查 API 细节时**：Agent 读取 `references/cpq-api-reference.md`

#### 已有脚本复用

`scripts/cpq_api.py` 提供完整的 CPQ App HTTP 封装：

```python
# cpq_api.py — 可直接在 tools.py 中 import
from scripts.cpq_api import CPQClient

client = CPQClient(base_url=config.cpq_base_url, client_id=config.cpq_client_id)
token = client.login("admin", "admin123")  # 或通过 runtime context 传递
products = client.get("/cpq/product/model/search", params={"keyword": "HVI"})
```

这 294 行代码包含：OAuth2 登录、Token 自动刷新、GET/POST/PUT 封装、错误处理——全部可复用，不用重写。

### 5.3 工具列表

| 工具 | 调用的 CPQ API | 说明 |
|------|---------------|------|
| `search_product(keyword)` | `GET /cpq/product/model/search` | 产品搜索 |
| `load_model(model_id)` | `GET /cpq/configure/model/{id}` | 加载配置模型 |
| `validate_config(model_id, attrs)` | `POST /cpq/configure/validate` | 规则验证 |
| `generate_bom(model_id, attrs)` | `POST /cpq/configure/bom-preview` | BOM 展开 |
| `complete_pricing(model_id, attrs, qty)` | `POST /cpq/configure/complete` | 完整定价 |
| `get_customers()` | `GET /cpq/customer/account/list` | CRM 客户 |
| `create_quote(data)` | `POST /cpq/quote/header` | 创建报价单 |
| `reverse_match(price, preferences)` | 编排多个 API | **🆕 反向匹配** |
| `compare_solutions(a, b)` | 本地计算 | **🆕 方案对比** |

### 5.4 FastAPI 端点设计

| 端点 | 方法 | 说明 |
|------|------|------|
| `/agent/chat` | POST | 发送消息，返回 SSE 流 |
| `/agent/sessions` | GET | 获取会话列表 |
| `/agent/sessions/{id}` | GET | 获取会话历史 |
| `/agent/sessions/{id}` | DELETE | 删除会话 |
| `/config` | GET | 获取当前配置 |
| `/config` | PUT | 更新配置（触发 Agent 重载） |
| `/config/test-cpq` | POST | 测试 CPQ 连接 |
| `/config/test-model` | POST | 测试模型连接 |
| `/health` | GET | 健康检查 |

### 5.5 SSE 流式响应格式

```
event: message
data: {"type":"thinking","content":"正在搜索产品..."}

event: message
data: {"type":"product_card","model_code":"EVE-HVI-40.0","model_name":"...","price":"39800"}

event: message
data: {"type":"bom","items":[{"code":"CAB-001","name":"柜体总成","qty":1},...]}

event: message
data: {"type":"pricing","base_price":39800,"net_price":39800,"discount":0}

event: done
data: {"turn":3,"tokens":1247}
```

---

## 六、前端设计

### 6.1 目录结构

```
frontend/
├── src/
│   ├── App.vue                  # 根组件
│   ├── main.ts                  # 入口
│   ├── router/index.ts          # 路由
│   ├── stores/                  # Pinia 状态
│   │   ├── chat.ts              # 聊天状态
│   │   └── config.ts            # 配置状态
│   ├── views/
│   │   ├── ChatView.vue         # 聊天主页面
│   │   └── SettingsView.vue     # 设置页面
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatPanel.vue    # 聊天面板容器
│   │   │   ├── MessageBubble.vue # 消息气泡
│   │   │   ├── MessageInput.vue  # 输入框
│   │   │   └── SessionList.vue   # 会话列表
│   │   ├── widgets/
│   │   │   ├── ProductCard.vue   # 产品推荐卡片
│   │   │   ├── BOMTable.vue      # BOM 清单表格
│   │   │   ├── PricingCard.vue   # 报价卡片
│   │   │   ├── ComparePanel.vue  # 方案对比面板
│   │   │   └── ThinkingInline.vue # 思考过程行内显示
│   │   └── settings/
│   │       ├── ModelConfig.vue   # 模型配置表单
│   │       ├── CPQConfig.vue     # CPQ 连接配置
│   │       ├── AgentConfig.vue   # Agent 行为配置
│   │       └── UIConfig.vue      # 界面配置
│   ├── api/
│   │   └── agent.ts             # SSE + REST 封装
│   ├── types/
│   │   └── index.ts             # TypeScript 类型
│   └── assets/
├── package.json
├── vite.config.ts
├── tsconfig.json
└── electron/                    # Electron 打包配置
    └── main.ts
```

### 6.2 路由

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | ChatView | 聊天主页面（默认） |
| `/settings` | SettingsView | 配置页面 |

### 6.3 包方案

```bash
# PWA（推荐先做）
npm run build          # 输出 dist/，直接部署

# Electron 桌面 App
npm run electron:mac   # 输出 .dmg
npm run electron:win   # 输出 .msi/.exe
```

---

## 七、CPQ App 接入地址默认值规则

CPQ App 的 `base_url` 配置项默认值遵循**同主机推断**规则：

```python
# config.py
def get_default_cpq_url() -> str:
    """
    默认 CPQ App 地址 = 当前 App 的 host + 端口 30000
    例如: 
      App 运行在 http://192.168.1.5:57100 
      → 默认 CPQ = http://192.168.1.5:30000
    """
    return "http://localhost:30000"  # 本地开发默认
```

前端 App 通过窗口 URL 自动推断：

```typescript
// 自动推断 CPQ 地址
const currentUrl = window.location
const cpqUrl = `${currentUrl.protocol}//${currentUrl.hostname}:30000`
// 例: 用户部署在 172.16.1.115 → CPQ = http://172.16.1.115:30000
```

用户也可以在设置面板手动修改。

---

## 八、可配置项总结（共 18 项）

| 分类 | 配置项 | 类型 | 默认值 | 前端可配 |
|------|--------|------|--------|---------|
| **模型** | 提供者 | select | deepseek | ✅ |
| **模型** | 模型名称 | select/text | deepseek-chat | ✅ |
| **模型** | API Key | password | 环境变量 | ✅ (只写) |
| **模型** | Base URL | text | https://api.deepseek.com | ✅ |
| **模型** | Temperature | slider | 0.7 | ✅ |
| **模型** | Max Tokens | number | 4096 | ✅ |
| **CPQ** | CPQ 地址 | text | http://localhost:30000 | ✅ |
| **CPQ** | Client ID | text | e5cd7e48... | ✅ |
| **CPQ** | 超时 | number | 30 | ✅ |
| **CPQ** | 重试次数 | number | 3 | ✅ |
| **Agent** | 系统提示词 | textarea | (默认模板) | ✅ |
| **Agent** | 最大轮次 | number | 20 | ✅ |
| **Agent** | 启用子Agent | toggle | true | ✅ |
| **审批** | 报价确认 | toggle | true | ✅ |
| **审批** | 发报价确认 | toggle | true | ✅ |
| **界面** | 主题 | radio | auto | ✅ |
| **界面** | 语言 | select | zh-CN | ✅ |
| **日志** | 日志级别 | select | info | ✅ |

---

## 九、工具全景图

```
┌─────────────────────────────────────────────────────┐
│              CPQ Agent 工具体系 (9 tools)            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  search_product ──→ get_model_detail                │
│         │                    │                      │
│         │         ┌──────────┴──────────┐           │
│         │         │  validate_config    │           │
│         │         └──────────┬──────────┘           │
│         │                    │                      │
│         ├──→ get_bom ←──────┘                      │
│         │        │                                  │
│         ├──→ get_pricing ←──┘                      │
│         │        │                                  │
│         │        └──→ create_quote ←── search_      │
│         │                           customers       │
│         │                                           │
│  ┌──────┴──────┐    ┌──────────────┐               │
│  │ 反向匹配      │    │  方案对比     │               │
│  │ reverse_match│    │  compare_    │               │
│  │ _price       │    │  solutions   │               │
│  │ 预算→推荐     │    │ A vs B→diff  │               │
│  └─────────────┘    └──────────────┘               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 十、开发计划与完成状态

| 阶段 | 内容 | 状态 |
|------|------|------|
| **P0** | 后端: create_deep_agent + 9个工具 + FastAPI | ✅ 完成 |
| **P0** | 配置文件: config.yaml + config.py + 热加载 | ✅ 完成 |
| **P1** | 前端: ChatView + MessageBubble + Sidebar + SSE | ✅ 完成 |
| **P1** | 前端: ProductCard + BOMTable + PricingCard + ComparePanel + ThinkingInline | 🔄 开发中 |
| **P1** | 前端: SettingsView + ModelConfig/CPQConfig/AgentConfig/UIConfig | 🔄 开发中 |
| **P2** | 反向匹配 (reverse_match_price) + 方案对比 (compare_solutions) | ✅ 完成 |
| **P2** | 联调 + 测试 | ✅ 完成 (20/20) |
| **P3** | Electron 打包 + PWA manifest + Service Worker | ✅ 完成 |
| **P3** | 样式打磨 | ⏳ 待前端组件集成后 |

---

## 十一、交付物清单

| 交付物 | 说明 | 状态 |
|--------|------|------|
| `backend/` | DeepAgents Agent + 9 工具 + FastAPI | ✅ |
| `frontend/` | Vue 3 独立前端 (+9组件开发中) | 🔄 |
| `config/config.yaml` | 默认配置文件 (18 可配项) | ✅ |
| `design/` | 4 份设计文档 + 预览 HTML | ✅ |
| `tests/` | 4 份测试文档 + 测试脚本 | ✅ |
| `public/manifest.json` | PWA 配置 | ✅ |
| `public/sw.js` | Service Worker | ✅ |
| `electron/` | Electron main + preload | ✅ |
| `.dmg` (Mac) | macOS 安装包 | ⏳ |
| `.exe` (Win) | Windows 安装包 | ⏳ |

---

## 十二、关键设计决策

| 决策 | 理由 |
|------|------|
| Agent 后端独立部署 | 零耦合 CPQ App，独立扩展 |
| 前端独立 App | 专注对话体验，避免系统耦合 |
| CPQ 地址默认同主机推断 | 降低首次配置成本 |
| 敏感信息只用环境变量 | 安全合规，配置文件可提交 Git |
| YAML 配置文件 | 人类可读写，方便运维 |
| 配置热加载 | 改配置不用重启服务 |
| PWA 优先 | 跨平台零成本，后续加 Electron 壳 |
| SSE 流式响应 | 用户体验好，打字机效果 |
| 子 Agent 可开关 | 简单场景不浪费资源 |
