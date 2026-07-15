# DeepAgents 实践指南

> 基于 LangChain DeepAgents 官方文档 (docs.langchain.com) 整理
> 版本: deepagents latest (2025) | 整理日期: 2026-07-05

---

## 一、构建 CPQ Agent 的典型场景

### 场景 1：简单 Agent（无文件系统、无子 Agent）

适用于单步查询、API 透传。

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

def search_product(keyword: str) -> dict:
    """Search CPQ product by keyword"""
    response = requests.get(
        f"http://localhost:30000/cpq/product/model/search?keyword={keyword}",
        headers={"clientid": "e5cd7e...", "Authorization": f"Bearer {token}"}
    )
    return response.json()

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search_product],
    system_prompt="You are a CPQ product configurator.",
)
```

### 场景 2：带文件系统的 Agent（BOM 生成和存储）

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

def configure_product(model_id: int, attributes: dict) -> dict:
    """Configure a product with given attributes and return BOM."""
    ...

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[configure_product],
    system_prompt="""You are a CPQ configuration agent.
    After generating a BOM, save it to /boms/bom-{model_id}.md for future reference.""",
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/boms/": StoreBackend(namespace=lambda rt: ("cpq-boms",)),
        },
    ),
)
```

### 场景 3：多步骤 CPQ 工作流（子 Agent 委派）

```python
agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search_product, get_customer, create_quote],
    system_prompt="""You are a CPQ sales assistant.
    For complex configurations, delegate to the configurator subagent.
    For customer data, delegate to the CRM subagent.""",
    subagents=[
        {
            "name": "configurator",
            "description": "Configure products with rules validation and BOM generation",
            "system_prompt": "You are a product configurator...",
            "tools": [configure_product, validate_rules, generate_bom],
        },
        {
            "name": "crm-agent",
            "description": "Look up customer accounts and opportunities",
            "system_prompt": "You are a CRM lookup agent...",
            "tools": [get_customer, get_opportunity],
        },
    ],
)
```

### 场景 4：带审批的报价流程（人机协作）

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[calculate_price, send_quote, approve_discount],
    interrupt_on={
        "send_quote": True,            # 发报价前需要审批
        "approve_discount": {          # 超 20% 折扣需要审批
            "allowed_decisions": ["approve", "reject"]
        },
    },
    checkpointer=MemorySaver(),
)
```

### 场景 5：CPQ Agent 带技能

```python
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[search_product, get_cost, calculate_price],
    memory=["/memories/AGENTS.md"],     # 持久化偏好
    skills=["/skills/cpq-pricing/"],    # 定价知识技能
    system_prompt="You are a CPQ pricing assistant.",
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda rt: (rt.server_info.assistant_id,)
            ),
            "/skills/": StoreBackend(
                namespace=lambda rt: (rt.server_info.assistant_id,)
            ),
        },
    ),
)
```

---

## 二、Backend 选型指南

| Backend | 适用场景 | 特点 |
|---------|---------|------|
| **StateBackend** (默认) | 单会话临时文件 | 线程作用域，通过检查点持久化 |
| **FilesystemBackend** | 本地开发，访问真实文件 | 绝对路径根目录 |
| **StoreBackend** | 跨会话持久化记忆 | 适合长期记忆、用户偏好 |
| **CompositeBackend** | 混合路由 | 不同路径路由到不同后端 |
| **Sandbox** | 代码执行（安全隔离） | 额外 Shell 执行能力 |
| **LocalShellBackend** | 开发环境直接执行 | 无隔离，仅开发用 |
| **ContextHubBackend** | 从 Hub 加载文件 | 无需单独配置 Store |

### 推荐组合：CPQ 生产环境

```python
backend = CompositeBackend(
    default=StateBackend(),               # 临时文件 = 会话作用域
    routes={
        "/memories/": StoreBackend(        # 持久记忆
            namespace=lambda rt: (rt.server_info.assistant_id,)
        ),
        "/boms/": StoreBackend(            # BOM 归档
            namespace=lambda rt: (rt.server_info.assistant_id,)
        ),
        "/skills/": FilesystemBackend(      # 技能从磁盘加载
            root_dir="/app/skills"
        ),
    },
)
```

---

## 三、Skills 编写实践

### 目录结构

```
cpq-skills/
├── product-search/
│   └── SKILL.md
├── bom-config/
│   ├── SKILL.md
│   └── references/
│       └── material-mapping.md
└── pricing-rules/
    ├── SKILL.md
    └── references/
        └── product-line-rules.md
```

### product-search/SKILL.md 示例

```markdown
---
name: product-search
description: Search and recommend CPQ products for German market energy storage.
---

# product-search

## When to use
When a customer asks about energy storage products, especially for European markets.

## Instructions

### 1. Search products
Use the `search_product` tool with relevant keywords:
- German market: "HVI", "VDE", "high voltage"
- Budget: "LVI", "low voltage"

### 2. Compare options
Present 2-3 options with kWh, price, and key differentiators.

### 3. Recommend
Recommend the best fit with reasoning.
German customers typically need VDE certification and high-voltage systems.
```

### bom-config/SKILL.md 示例

```markdown
---
name: bom-config
description: Generate and validate Bills of Materials for configured products.
---

# bom-config

## When to use
After a product configuration is complete. Use to generate BOM and validate material requirements.

## Instructions

### 1. Load BOM
Use `generate_bom` tool with the model ID and selected attributes.

### 2. Validate
Check all required materials are present and quantities are correct.
Reference `references/material-mapping.md` for material code mappings.

### 3. Cost analysis
For each line item, estimate cost based on the latest material pricing.
Flag items with unusual cost that may need review.
```

---

## 四、Permissions 权限策略

### 常见模式

**只读 Agent：**
```python
permissions=[
    FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
]
```

**隔离工作区：**
```python
permissions=[
    FilesystemPermission(operations=["read","write"], paths=["/workspace/**"], mode="allow"),
    FilesystemPermission(operations=["read","write"], paths=["/**"], mode="deny"),
]
```

**保护敏感文件：**
```python
permissions=[
    FilesystemPermission(operations=["read","write"], paths=["/workspace/.env", "/secrets/**"], mode="deny"),
    FilesystemPermission(operations=["read","write"], paths=["/workspace/**"], mode="allow"),
    FilesystemPermission(operations=["read","write"], paths=["/**"], mode="deny"),
]
```

**写入前审批：**
```python
permissions=[
    FilesystemPermission(operations=["write"], paths=["/secrets/**"], mode="interrupt"),
]
# 需配合 checkpointer
checkpointer=InMemorySaver()
```

---

## 五、生产环境关键检查清单

### 调用参数

- [ ] 每次调用传入 `thread_id`（保持会话连续性）
- [ ] 每次调用传入 `context`（用户 ID、权限等运行时参数）
- [ ] 使用 `context_schema` 定义 context 数据结构

### 持久化

- [ ] Checkpointer 配置（生产建议 LangSmith 托管，开发用 InMemorySaver）
- [ ] Store 配置（长期记忆跨线程持久化）
- [ ] Memories 和 Skills 路由到正确的 Backend

### 安全

- [ ] Permissions 规则覆盖所有文件路径
- [ ] 敏感工具设置 `interrupt_on`
- [ ] 沙箱隔离代码执行
- [ ] API 密钥通过环境变量或 context 传入，不硬编码

### 可观测

- [ ] LangSmith 追踪启用
- [ ] LangSmith Engine 监控

### 部署

- [ ] `langgraph.json` 配置正确
- [ ] `.env` 文件包含所有必需环境变量
- [ ] 测试 `langgraph dev` 可运行

---

## 六、示例：CPQ Agent 生产部署文件

### agent.py
```python
from dataclasses import dataclass
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

@dataclass
class Context:
    user_id: str
    tenant_id: str = "000000"

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search_product, configure_product, generate_bom, calculate_price],
    memory=["/memories/AGENTS.md"],
    skills=["/skills/"],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(namespace=lambda rt: (rt.server_info.assistant_id,)),
            "/skills/": StoreBackend(namespace=lambda rt: (rt.server_info.assistant_id,)),
        },
    ),
    interrupt_on={"send_quote": True},
    system_prompt="You are a CPQ (Configure, Price, Quote) assistant for manufacturing.",
    context_schema=Context,
)
```

### langgraph.json
```json
{
  "dependencies": ["."],
  "graphs": {
    "cpq-agent": "./agent.py:agent"
  },
  "env": ".env"
}
```

### .env
```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...
```
