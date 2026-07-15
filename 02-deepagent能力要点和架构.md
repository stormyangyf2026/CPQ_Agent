# DeepAgents 能力要点与架构

> 基于 LangChain DeepAgents 官方文档 (docs.langchain.com) 整理
> 版本: deepagents latest (2025) | 整理日期: 2026-07-05

---

## 一、整体架构

### 四层能力模型

```
┌──────────────────────────────────────────────────┐
│                create_deep_agent()                │
├──────────────────────────────────────────────────┤
│  Execution Environment      │  Context Management │
│  ├── Tools & MCP            │  ├── Skills         │
│  ├── Virtual Filesystem     │  ├── Memory         │
│  ├── Filesystem Permissions │  ├── Summarization  │
│  └── Code Execution (Shell) │  └── Prompt Caching │
├─────────────────────────────┼────────────────────┤
│  Delegation                 │  Steering           │
│  ├── Subagent Spawning      │  ├── Human-in-loop  │
│  └── Task Planning          │  └── Interrupts      │
└─────────────────────────────┴────────────────────┘
│               LangGraph Runtime                   │
│  (Streaming, Persistence, Checkpointing)          │
└──────────────────────────────────────────────────┘
│               LangChain Core                      │
│  (Tools, Models, Messages)                        │
└──────────────────────────────────────────────────┘
```

### 核心技术栈

| 层 | 职责 |
|----|------|
| **deepagents** | Agent 套件，提供所有内置能力 |
| **LangGraph** | 图运行时：持久化执行、流式传输、人机协作、状态管理 |
| **LangChain** | 核心构建块：工具、模型、消息、中间件 |
| **LangSmith** | 生产部署：追踪、评估、监控、部署 |

---

## 二、八大核心能力

### 1. 执行环境 (Execution Environment)

**工具层**
```python
# 自定义工具（Python 函数）
@tool
def search_orders(user_id: str, status: str) -> str:
    """Search for user orders by status."""
    return ...

# MCP 工具（Model Context Protocol）
agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[mcp_tool_1, mcp_tool_2],
)
```

**虚拟文件系统**
内置工具：`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
- `read_file` 原生支持图片（PNG/JPG/GIF/WEBP），返回多模态内容
- 可插拔后端：内存、磁盘、远程、沙箱

**文件系统权限**
```python
from deepagents import FilesystemPermission

permissions=[
    # 只允许读写 /workspace 目录
    FilesystemPermission(operations=["read","write"], paths=["/workspace/**"], mode="allow"),
    # 拒绝其他所有
    FilesystemPermission(operations=["read","write"], paths=["/**"], mode="deny"),
]
```

**代码执行（沙箱）**
```python
from deepagents.backends import LangSmithSandbox
# 支持 LangSmith, Daytona, E2B, Modal, Runloop 等沙箱
backend = LangSmithSandbox(sandbox=ls_sandbox)
agent = create_deep_agent(model=model, backend=backend)
# Agent 获得 execute 工具，可执行任意 Shell 命令
```

### 2. 上下文工程 (Context Engineering)

| 上下文类型 | 说明 | 作用域 |
|-----------|------|--------|
| **System Prompt** | 自定义 + 内置指导 | 每次运行 |
| **Memory** | `AGENTS.md` 文件，始终在线 | 持久化 |
| **Skills** | 按需加载（渐进式披露） | 任务触发 |
| **Tool Prompts** | 内置工具使用说明 | 工具调用时 |
| **Runtime Context** | 用户 ID、API Key 等 | 每次调用 |
| **Summarization** | 自动压缩历史 | 接近窗口限制时 |
| **Subagent Isolation** | 子 Agent 隔离大量上下文 | 委派时 |

### 3. 子智能体委派 (Subagents)

```python
agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[
        {
            "name": "code-reviewer",
            "description": "Review code for bugs and style issues",
            "system_prompt": "You are a senior code reviewer...",
            "tools": [read_file, grep],
            "model": "anthropic:claude-sonnet-4-6",  # 可不同模型
        },
    ],
)
```

**子 Agent 配置项：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | str | 唯一标识，主 Agent 用此名称调用 |
| `description` | str | 描述，主 Agent 据此决定是否委派 |
| `system_prompt` | str | 子 Agent 专属指令（不继承主 Agent） |
| `tools` | list | 工具（可覆盖、继承或不带） |
| `model` | str/BaseChatModel | 可指定不同模型 |

**何时用子 Agent：**
- ✅ 多步骤任务会污染主 Agent 上下文
- ✅ 需要特殊指令或工具的专业领域
- ✅ 需要不同模型能力的任务
- ❌ 简单的单步骤任务
- ❌ 需要保留中间上下文时

### 4. 持久记忆 (Memory)

```python
# Agent 级记忆（所有用户共享）
agent = create_deep_agent(
    model=model,
    memory=["/memories/AGENTS.md"],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda rt: (rt.server_info.assistant_id,)
            ),
        },
    ),
)

# 用户级记忆（每个用户隔离）
agent = create_deep_agent(
    model=model,
    memory=["/memories/preferences.md"],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda rt: (rt.server_info.user.identity,)
            ),
        },
    ),
)
```

**记忆类型：**

| 类型 | 说明 | 生命周期 |
|------|------|----------|
| **短期记忆** | 对话历史 + 临时文件 | 单个线程（Checkpointer 持久化） |
| **长期记忆** | 跨对话持久化记忆 | StoreBackend（跨线程） |
| **程序记忆 (Skills)** | 可复用的工作流程和最佳实践 | 按需加载 |
| **组织级记忆** | 团队/公司共享的规则和策略 | 只读，应用代码写入 |

### 5. 技能系统 (Skills)

技能目录结构：
```
skills/
└── langgraph-docs/
    ├── SKILL.md          ← YAML frontmatter + 指令
    ├── scripts/          ← 可执行脚本
    ├── references/       ← 参考文档
    └── assets/           ← 模板和静态资源
```

**SKILL.md 格式：**
```markdown
---
name: langgraph-docs
description: Fetch relevant LangGraph documentation.
---

# langgraph-docs

## Instructions

### 1. Fetch the documentation index
Use fetch_url to read https://docs.langchain.com/llms.txt
```

**渐进式披露（三层加载）：**

| 层级 | 加载内容 | 时机 |
|------|---------|------|
| Level 1 | Skill 的 name + description | Agent 启动时 |
| Level 2 | SKILL.md 完整指令 | 技能被激活时 |
| Level 3 | scripts/references/assets | 指令引用时 |

### 6. 人机协作 (Human-in-the-Loop)

```python
agent = create_deep_agent(
    model=model,
    tools=[remove_file, fetch_file, notify_email],
    interrupt_on={
        "remove_file": True,                               # 默认：approve/edit/reject/respond
        "notify_email": {"allowed_decisions": ["approve", "reject"]},  # 仅允许/拒绝
    },
    checkpointer=MemorySaver(),  # 必须！
)
```

**中断模式（Permissions）：**
```python
FilesystemPermission(
    operations=["write"],
    paths=["/secrets/**"],
    mode="interrupt",  # 写入敏感路径前暂停等待审批
)
```

### 7. 中间件系统 (Middleware)

DeepAgents 内置中间件栈（按顺序）：

| 中间件 | 功能 |
|--------|------|
| TodoListMiddleware | 任务规划和跟踪（`write_todos` 工具） |
| FilesystemMiddleware | 文件系统操作（ls, read, write, edit, glob, grep） |
| SubAgentMiddleware | 子 Agent 委派（`task` 工具） |
| SummarizationMiddleware | 上下文自动压缩 |
| HumanInTheLoopMiddleware | 人机协作审批 |
| PatchToolCallsMiddleware | 修复中断后的消息历史 |

**添加自定义中间件：**
```python
agent = create_deep_agent(
    model=model,
    middleware=[MyCustomMiddleware()],  # 追加到默认栈之后
)
```

### 8. 生产部署 (Going to Production)

```
开发阶段（本地）              生产阶段（LangSmith）
┌──────────────┐         ┌──────────────────┐
│ Python 脚本   │  ────→  │ Managed DeepAgent │
│ langgraph dev │         │ langgraph.json    │
│ InMemoryStore│         │ 持久化 Store      │
│ 本地 sandbox  │         │ 远程 Sandbox       │
└──────────────┘         └──────────────────┘
```

**langgraph.json 配置：**
```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./agent.py:agent"
  },
  "env": ".env"
}
```

**生产调用：**
```python
# 每次调用必须带 thread_id 和 context
agent.invoke(
    {"messages": [{"role": "user", "content": "..."}]},
    config={"configurable": {"thread_id": "my-thread-id"}},
    context=Context(user_id="user-123"),
)
```

---

## 三、与 Claude Agent SDK 对比

| 维度 | DeepAgents | Claude Agent SDK |
|------|------------|------------------|
| Agent 位置 | 沙箱内/外均可 | 仅在沙箱内 |
| 执行后端 | 可插拔（本地/虚拟/远程/自定义） | 沙箱本地文件系统 |
| 模型支持 | 任何（100+ 提供者） | 仅 Claude 系列 |
| 多租户 | 内置（范围线程、沙箱、RBAC） | 需自行构建 |
| 部署 | Managed DeepAgent 或自托管 | 自建服务器 |
| 许可证 | MIT | MIT（Claude Code 本身为专有） |

---

## 四、DeepAgents Code (dcode)

终端编码 Agent，类似 Claude Code / Cursor，基于 DeepAgents SDK：

```bash
# 安装
curl -LsSf https://langch.in/dcode | bash

# 使用
dcode --model openai:gpt-5.5
dcode --model anthropic:claude-opus-4-8
```

支持：文件操作、Shell 执行、远程沙箱、网络搜索、任务规划、子 Agent、记忆、MCP 工具、LangSmith 追踪。
