# DeepAgents 开发指南

> 基于 LangChain DeepAgents 官方文档 (docs.langchain.com) 整理
> 版本: deepagents latest (2025) | 整理日期: 2026-07-05

---

## 一、什么是 DeepAgents

DeepAgents 是 LangChain 生态中的 **"Agent 套件 (Agent Harness)"**，提供开箱即用的智能体能力：
任务规划、文件系统上下文管理、子智能体生成、长期记忆、人机协作。

### 在 LangChain 生态中的位置

```
LangChain (核心构建块) → LangGraph (图运行时) → DeepAgents (套件层)
   工具、模型           持久化、流式、中断      规划、文件系统、子Agent
```

| 层级 | 职责 | 何时用 |
|------|------|--------|
| **LangChain** (`create_agent`) | 最小 Agent 工具调用循环 | 简单 Agent、不需要内置能力 |
| **LangGraph** | 自定义工作流图 | 需要自定义编排逻辑 |
| **DeepAgents** (`create_deep_agent`) | 完整套件，内置全部能力 | 复杂多步骤任务 |

### 核心理念

| 原则 | 说明 |
|------|------|
| **Opinionated** | 默认配置针对长周期、多步骤任务调优 |
| **Extensible** | 可覆盖或替换任何组件，无需 fork |
| **Model-agnostic** | 支持任何支持 Tool Calling 的 LLM |
| **Production-ready** | 基于 LangGraph，支持流式、持久化、检查点 |

---

## 二、快速上手

### 安装

```bash
pip install deepagents
# 或
uv add deepagents
```

### 最小示例

```python
from deepagents import create_deep_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
```

### 完整示例：研究型 Agent

```python
from deepagents import create_deep_agent
from tavily import TavilyClient

tavily_client = TavilyClient(api_key="...")

def internet_search(query: str, max_results: int = 5) -> dict:
    """Run a web search"""
    return tavily_client.search(query, max_results=max_results)

research_instructions = """You are an expert researcher.
You have access to an internet search tool.
Conduct thorough research and write a polished report."""

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[internet_search],
    system_prompt=research_instructions,
)
```

### 支持的模型提供者

使用 `provider:model` 格式：

| 提供者 | 格式示例 |
|--------|----------|
| OpenAI | `openai:gpt-5.5` |
| Anthropic | `anthropic:claude-sonnet-4-6` |
| Google | `google_genai:gemini-3.5-flash` |
| OpenRouter | `openrouter:anthropic/claude-sonnet-4-6` |
| Fireworks | `fireworks:accounts/fireworks/models/glm-5p1` |
| Baseten | `baseten:zai-org/GLM-5.2` |
| Ollama (本地) | `ollama:devstral-2` |

---

## 三、完整参数列表

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",     # 模型（provider:model 或 BaseChatModel）
    system_prompt="You are helpful.",         # 系统提示词
    tools=[search, fetch_url],               # 自定义工具
    memory=["./AGENTS.md"],                   # 记忆文件（总是在线）
    skills=["./skills/"],                     # 技能目录（按需加载）
    backend=FilesystemBackend(root_dir="."),  # 文件系统后端
    permissions=[...],                        # 文件系统权限规则
    subagents=[...],                          # 自定义子智能体
    middleware=[...],                          # 额外中间件
    interrupt_on={...},                       # 人机协作配置
    response_format=MySchema,                 # 结构化输出
    state_schema=CustomState,                 # 自定义状态
    context_schema=Context,                   # 运行时上下文
    checkpointer=InMemorySaver(),             # 检查点（持久化）
    store=InMemoryStore(),                    # 长期存储
    debug=False,                              # 调试模式
    name="my-agent",                          # Agent 名称
)
```

---

## 四、模型选择建议

### 官方评估结果

| 模型 | 综合 | 文件操作 | 检索 | 工具使用 | 记忆 | 会话 | 摘要 |
|------|------|---------|------|---------|------|------|------|
| gemini-3.5-flash | **82%** | 100% | 100% | 90% | 54% | 38% | 80% |
| gpt-5.5 | 80% | 92% | 100% | 84% | 64% | 52% | 80% |
| claude-opus-4-7 | 80% | 100% | 100% | 82% | - | 48% | 100% |
| GLM-5.1 (Fireworks) | 81% | 100% | 100% | 87% | - | 33% | 80% |

### 推荐模型

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 复杂推理 + 代码 | claude-opus-4-8 | 100% 文件操作、100% 摘要 |
| 综合平衡 | gemini-3.5-flash | 总体最高分 |
| 性价比 | gpt-5.5 | 记忆和对话表现好 |
| 开源/国内 | GLM-5.2 / Kimi-K2.7 Code | 开源模型最强 |

---

## 五、核心 API

### 创建并调用

```python
# 创建 Agent（返回 CompiledStateGraph）
agent = create_deep_agent(model="openai:gpt-5.5")

# 同步调用
result = agent.invoke({"messages": ["Hello"]})

# 异步调用
result = await agent.ainvoke({"messages": ["Hello"]})

# 流式输出
for chunk in agent.stream({"messages": ["Hello"]}):
    print(chunk)

# 带配置
result = agent.invoke(
    {"messages": ["Hello"]},
    config={"configurable": {"thread_id": "my-thread"}},
    context=MyContext(user_id="123"),
)
```

### 响应格式

```python
from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    key_points: list[str]

agent = create_deep_agent(
    model="openai:gpt-5.5",
    response_format=Summary,
)
```

---

## 六、与现有系统集成

DeepAgents 通过 **Tools** 和 **MCP** 与外部系统集成：

```python
# 方式1：Python 函数作为工具
@tool
def query_cpq_product(keyword: str) -> dict:
    """Search CPQ products by keyword"""
    response = requests.get(f"http://localhost:30000/cpq/product/model/search?keyword={keyword}")
    return response.json()

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[query_cpq_product],
    system_prompt="You are a CPQ configuration agent.",
)
```

---

## 七、相关资源

| 资源 | 地址 |
|------|------|
| 官方文档 | https://docs.langchain.com/oss/python/deepagents/overview |
| GitHub | https://github.com/langchain-ai/deepagents |
| PyPI | https://pypi.org/project/deepagents/ |
| 讨论论坛 | https://forum.langchain.com/c/oss-product-help-lc-and-lg/deep-agents/18 |
| API 参考 | https://reference.langchain.com/python/deepagents/ |
| LangChain Academy | https://academy.langchain.com/ |
