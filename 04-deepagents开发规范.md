# DeepAgents 开发规范

> 基于 LangChain DeepAgents 官方文档和最佳实践整理
> 版本: deepagents latest (2025) | 整理日期: 2026-07-05

---

## 一、代码组织规范

### 1.1 项目结构

```
my-cpq-agent/
├── agent.py                # Agent 入口，create_deep_agent()
├── tools.py                # 自定义工具函数
├── models.py               # 数据模型（Pydantic）
├── skills/                 # 技能目录
│   ├── product-search/
│   │   └── SKILL.md
│   └── bom-config/
│       └── SKILL.md
├── memories/               # 持久记忆
│   └── AGENTS.md
├── tests/                  # 测试
├── langgraph.json          # 部署配置
├── .env                    # 环境变量
└── pyproject.toml          # 依赖管理
```

### 1.2 工具定义规范

```python
from langchain.tools import tool

# ✅ 正确：有类型注解、有 docstring、有参数说明
@tool(parse_docstring=True)
def search_products(
    keyword: str,
    max_results: int = 5,
    region: str = "EU",
) -> dict:
    """Search for CPQ products by keyword.

    Use this when the user asks about product availability or wants
    to find products matching specific criteria.

    Args:
        keyword: Search term for product name or code
        max_results: Maximum number of results to return (default 5)
        region: Market region filter: 'EU', 'CN', 'US'
    """
    ...

# ❌ 错误：无 docstring，无类型说明
def search_products(k, n=5):
    return ...
```

### 1.3 System Prompt 规范

```python
# ✅ 好：结构清晰，有角色定位、可用工具说明、行为约束
system_prompt = """You are a CPQ (Configure, Price, Quote) assistant for manufacturing.

Your responsibilities:
1. Help users find and configure products
2. Generate Bills of Materials (BOM)
3. Calculate pricing based on configured rules
4. Create quote documents

## Tools available
- `search_product`: Find products by keyword
- `configure_product`: Configure with attributes
- `generate_bom`: Expand BOM from configuration
- `calculate_price`: Apply pricing rules

## Guidelines
- Always validate configuration before generating BOM
- Present pricing with currency and unit breakdown
- Flag any configuration that violates constraints
"""

# ❌ 差：太简短，没有具体指导
system_prompt = "You help with CPQ tasks."
```

### 1.4 子 Agent 定义规范

```python
# ✅ 正确：name 和 description 明确，system_prompt 独立完整
subagents = [
    {
        "name": "configurator",
        "description": "Configure products with attribute selection, rule validation, and BOM generation. Use when the user needs to configure a specific product model.",
        "system_prompt": "You are a CPQ product configurator. You validate attribute selections, check constraint rules, and generate BOMs.",
        "tools": [configure_product, validate_rules],
    },
]

# ❌ 错误：description 太模糊，system_prompt 缺失
subagents = [
    {
        "name": "helper",
        "description": "helps with stuff",
        "system_prompt": "You are helpful.",
    },
]
```

---

## 二、安全规范

### 2.1 权限原则

**规则一：工具是最小权限边界**
- 只给 Agent 完成任务最小必要的工具
- 不给 Agent 不需要的 API 权限

**规则二：文件系统权限显式声明**
```python
# 始终用白名单模式
permissions=[
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/workspace/**"],  # 明确允许的路径
        mode="allow",
    ),
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/**"],            # 最后 deny 兜底
        mode="deny",
    ),
]
```

**规则三：敏感操作需要审批**
```python
interrupt_on={
    "send_email": True,
    "delete_file": True,
    "create_quote": True,
}
```

### 2.2 信任模型

> DeepAgents 遵循 "信任 LLM" 模型。Agent 可以执行其工具允许的任何操作。
> **安全边界应在工具/沙箱层面实施，而不是期望模型自我约束。**

- ✅ 沙箱隔离代码执行
- ✅ 权限规则限制文件访问
- ✅ 人机协作审批敏感操作
- ❌ 不要在 System Prompt 中写"不要删除文件"来期望模型遵守

### 2.3 API 密钥管理

```python
# ✅ 正确：通过环境变量
os.environ["OPENAI_API_KEY"] = "..."

# ✅ 正确：通过 runtime context
@dataclass
class Context:
    user_id: str
    api_key: str  # 从认证系统传入

# ❌ 错误：硬编码
api_key = "sk-1234567890abcdef"  # NEVER DO THIS
```

---

## 三、上下文管理规范

### 3.1 Memory vs Skills 的选择

| 场景 | 使用 | 原因 |
|------|------|------|
| 项目约定、用户偏好 | **Memory** | 每次都需要 |
| 专业工作流程、参考文档 | **Skills** | 只在需要时加载 |
| 组织级策略 | **Memory** (只读) | 全局适用 |
| 某领域的详细操作步骤 | **Skills** (子文件) | 减少上下文 |

```python
# 正确分离
agent = create_deep_agent(
    memory=["/memories/preferences.md"],   # 始终在线
    skills=["/skills/cpq-pricing/"],       # 按需加载
)
```

### 3.2 Skills 的规模和粒度

```
✅ 一个 Skill = 一个工作流/领域
   skills/cpq-pricing/SKILL.md      ← 定价相关
   skills/cpq-config/SKILL.md       ← 配置相关

❌ 一个 Skill = 所有事情
   skills/everything/SKILL.md       ← 太大，加载消耗 Token

✅ 主文件简洁，详细内容放 reference
   SKILL.md  → 核心指令（200-500 words）
   references/rules.md → 详细规则表
```

### 3.3 子 Agent 用于上下文隔离

```python
# 主 Agent 上下文 = 高层协调信息
# 子 Agent 上下文 = 详细的搜索结果/计算过程
# 子 Agent 返回 = 最终结果摘要

# ✅ 好：大量搜索结果在子 Agent 中处理
subagents = [{
    "name": "market-researcher",
    "description": "Search the web and compile findings",
    "system_prompt": "You research and compile findings into a concise report.",
    "tools": [internet_search],
}]

# ❌ 差：主 Agent 直接搜索，上下文被 50 条搜索结果撑爆
# agent = create_deep_agent(tools=[internet_search])  # 可能 OOM
```

---

## 四、Backend 选型规范

### 4.1 默认开发环境

```python
# 开发/测试：StateBackend
agent = create_deep_agent(model=model)  # 默认 StateBackend
# 仅线程作用域，重启后清除
```

### 4.2 需要持久化的场景

```python
# 跨会话记忆：StoreBackend
backend = StoreBackend(
    namespace=lambda rt: (rt.server_info.assistant_id,)
)

# 本地文件：FilesystemBackend
backend = FilesystemBackend(root_dir="/absolute/path/to/project")

# 混合：CompositeBackend（生产推荐）
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(...),
        "/skills/": FilesystemBackend(root_dir="/app/skills"),
    },
)
```

### 4.3 代码执行

```python
# 需要 Shell 执行：沙箱
backend = LangSmithSandbox(sandbox=ls_sandbox)

# 仅文件操作：StateBackend / FilesystemBackend 即可
# 不需要沙箱
```

---

## 五、错误处理规范

### 5.1 工具错误

```python
# ✅ 正确：返回有意义的错误信息
def configure_product(model_id: int, attributes: dict) -> dict:
    try:
        result = cpq_api.configure(model_id, attributes)
        return {"status": "ok", "data": result}
    except CPQError as e:
        return {"status": "error", "message": str(e), "code": e.code}

# ❌ 错误：抛出未处理异常
def configure_product(model_id: int, attributes: dict) -> dict:
    return cpq_api.configure(model_id, attributes)
```

### 5.2 重试中间件

```python
from langchain.agents.middleware import ToolRetryMiddleware, ModelRetryMiddleware

agent = create_deep_agent(
    model=model,
    middleware=[
        ToolRetryMiddleware(max_retries=3),     # 工具调用失败重试
        ModelRetryMiddleware(max_retries=2),     # 模型调用失败重试
    ],
)
```

---

## 六、测试规范

### 6.1 工具单元测试

```python
def test_search_product():
    result = search_product("HVI")
    assert result["status"] == "ok"
    assert len(result["data"]) > 0

def test_configure_product_validation():
    result = configure_product(2091, {"电网标准": "EU_VDE"})
    assert result["validation"]["status"] == "PASS"
```

### 6.2 Agent 集成测试

```python
from langgraph.checkpoint.memory import MemorySaver

def test_agent_basic():
    agent = create_deep_agent(
        model="openai:gpt-5.5",
        tools=[search_product],
    )
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Find HVI products"}]
    })
    assert len(result["messages"]) > 1
```

### 6.3 用 LangSmith 追踪

```python
# 设置环境变量即可自动追踪
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "lsv2_..."

# 所有 Agent 调用自动记录到 LangSmith
```

---

## 七、版本管理规范

### 7.1 依赖锁定

```toml
# pyproject.toml
[project]
dependencies = [
    "deepagents>=0.5.0",
    "langchain>=1.0",
    "langgraph>=0.2",
]
```

### 7.2 Git 忽略

```gitignore
# .gitignore
.env
__pycache__/
*.pyc
.langgraph_api/
```

### 7.3 环境变量

```bash
# .env（不提交到 Git）
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# .env.example（提交到 Git，作为模板）
OPENAI_API_KEY=your-key-here
TAVILY_API_KEY=your-key-here
```

---

## 八、命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| Agent 名称 | kebab-case | `cpq-config-agent` |
| 工具函数 | snake_case | `search_product`, `calculate_price` |
| 子 Agent name | kebab-case | `code-reviewer`, `crm-agent` |
| Skill 目录 | kebab-case | `product-search`, `bom-config` |
| Memory 文件 | UPPER_SNAKE.md | `AGENTS.md`, `PREFERENCES.md` |
| SKILL.md 的 name | kebab-case | `langgraph-docs` |
| 数据模型 | PascalCase | `UserContext`, `QuoteRequest` |
| Backend namespace | tuple | `(assistant_id,)`, `(user_id,)` |

---

## 九、性能规范

### 9.1 减少 Token 消耗

- Skills 用**渐进式披露**：只写简短描述，详细内容在子文件
- Memory 保持**最小化**：只存必须每次加载的信息
- 大数据输出用**子 Agent 隔离**：返回摘要而非原始数据
- 启用 Prompt Caching（受模型支持自动生效）

### 9.2 上下文压缩

```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_deep_agent(
    model=model,
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("tokens", 4000),   # 超过 4000 tokens 触发
            keep=("messages", 20),       # 保留最近 20 条消息
        ),
    ],
)
```

### 9.3 模型调用限制

```python
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware

agent = create_deep_agent(
    model=model,
    middleware=[
        ModelCallLimitMiddleware(max_llm_calls=20),   # 最多 20 次模型调用
        ToolCallLimitMiddleware(max_tool_calls=50),   # 最多 50 次工具调用
    ],
)
```

---

## 十、参考资源

| 资源 | 地址 |
|------|------|
| DeepAgents 官方文档 | https://docs.langchain.com/oss/python/deepagents/overview |
| API Reference | https://reference.langchain.com/python/deepagents/ |
| GitHub 仓库 | https://github.com/langchain-ai/deepagents |
| 示例代码 | https://github.com/langchain-ai/deepagents/tree/main/examples |
| LangChain Skills | https://github.com/langchain-ai/langchain-skills |
| Agent Skills 规范 | https://agentskills.io/specification |
| 社区论坛 | https://forum.langchain.com/ |
