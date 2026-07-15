#!/usr/bin/env python3
"""
CPQ Agent — DeepAgents Agent 实例

使用 DeepAgents 框架的 create_deep_agent 创建 CPQ 智能配置报价助手。
从 config 加载所有参数。
"""

import os
from typing import Any

from deepagents import create_deep_agent
from langchain_deepseek import ChatDeepSeek

from config import Config
from tools import (
    search_product,
    get_model_detail,
    validate_configuration,
    get_bom,
    get_pricing,
    search_customers,
    create_quote,
    reverse_match_price,
    compare_solutions,
    set_cpq_config,
)

# ── 默认系统提示 ──────────────────────────────────────────

DEFAULT_SYSTEM_PROMPT = """你是一个制造业 CPQ（配置-定价-报价）智能助手。

## 你的职责
1. **理解客户需求** — 从用户的自然语言描述中提取产品需求、属性偏好、数量
2. **产品搜索与推荐** — 使用 search_product 搜索匹配的产品型号
3. **产品配置** — 使用 get_model_detail 查看产品的可配置属性，引导用户逐步选择
4. **配置验证** — 使用 validate_configuration 验证选择的配置是否合规
5. **BOM 展开** — 使用 get_bom 生成物料清单
6. **定价计算** — 使用 get_pricing 计算完整定价（基准价、折扣、建议价、最低限价）
7. **客户查询** — 使用 search_customers 搜索 CRM 客户
8. **报价单生成** — 使用 create_quote 创建报价单
9. **价格反向匹配** — 使用 reverse_match_price 根据客户预算推荐最佳方案
10. **方案对比** — 使用 compare_solutions 对比两个产品配置的差异

## CPQ 工作流
### 流程一：自然语言配置报价
1. 从用户输入提取：产品关键词、属性偏好、数量
2. 使用 search_product 搜索产品
3. 使用 get_model_detail 加载产品配置模型（属性列表）
4. 引导用户选择属性，使用 validate_configuration 验证每次选择
5. 使用 get_bom 展开 BOM 清单
6. 使用 get_pricing 计算定价
7. 格式化输出结果

### 流程二：报价单生成
1. 完成配置后，使用 search_customers 查找客户
2. 确认客户信息和报价行项
3. 使用 create_quote 创建报价单
4. 返回报价单 ID

### 流程三：价格反向匹配
1. 用户提供预算上限（如"预算2.5万"）
2. 使用 reverse_match_price 工具，传入 target_price 和需求关键词
3. 工具自动搜索产品、获取定价、排序推荐
4. 向用户展示：匹配状态、最佳方案、预算内选项、超预算选项
5. 如果没有完全匹配，说明差距和建议的降配方案

### 流程四：方案对比
1. 用户有两个候选产品（如 HVI 和 LVI 系列）
2. 使用 compare_solutions 工具，传入两个产品的 modelId
3. 工具自动获取两个产品的详情、BOM、定价
4. 向用户展示：基本参数对比表、价格差异、推荐结论

## 行为准则
- **始终先验证再报价** — 推荐配置前使用 validate_configuration 验证
- **定价透明** — 说明基准价、折扣率、建议价、最低限价
- **用户确认** — 生成报价单前先让用户确认
- **属性引导** — 如果产品有多个可配置属性，逐步引导用户选择

## 完成标志
**强制规则：每次回复的末尾必须加上下面这一行，不能遗漏，不能在该行后加任何其他内容：**

✅ **已完成所有工作。** 请问还需要什么帮助？

## 输出格式
配置完成后，使用结构化方式呈现：

### 📋 配置结果
- 产品名称、型号编码
- 数量
- 属性列表（属性=值）
- 验证状态（✅ PASS / ⚠️ 警告 / 🛑 冲突）

### 📦 BOM 清单
物料编码 | 名称 | 数量 | 单位

### 💰 报价
- 基准价
- 折扣率/金额
- 建议售价
- 最低限价"""


def build_agent(config: Config) -> Any:
    """根据配置构建 DeepAgents Agent

    Args:
        config: CPQ Agent 配置

    Returns:
        CompiledStateGraph: DeepAgents agent 实例
    """
    # 设置 CPQ 配置到 tools 模块
    set_cpq_config(config.cpq)

    # 初始化 ChatDeepSeek 模型
    model = ChatDeepSeek(
        model=config.model.model_name,
        api_key=config.model.api_key or os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url=config.model.base_url,
        temperature=config.model.temperature,
        max_tokens=config.model.max_tokens,
        top_p=config.model.top_p,
    )

    # 系统提示
    system_prompt = config.agent.system_prompt or DEFAULT_SYSTEM_PROMPT

    # 工具列表
    tools = [
        search_product,
        get_model_detail,
        validate_configuration,
        get_bom,
        get_pricing,
        search_customers,
        create_quote,
        reverse_match_price,
        compare_solutions,
    ]

    # 构建 Agent
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        skills=config.skills.paths if config.skills.paths else None,
        backend=None,  # 使用默认的 StateBackend
        name="cpq-agent",
    )

    return agent
