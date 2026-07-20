#!/usr/bin/env python3
"""
CPQ Agent — FastAPI 服务

提供 REST API 端点用于：
- 健康检查
- Agent 对话（SSE 流式）
- 配置管理
- 连接测试
"""

import asyncio
import json
import os
import sys
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import requests
import uvicorn
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field

import tools
from agent import build_agent
from config import Config, load_config, save_config

# ── 全局状态 ──────────────────────────────────────────────

_config: Config | None = None
_agent: Any = None


# ── Pydantic Models ──────────────────────────────────────


class ChatMessage(BaseModel):
    role: str = Field(..., description="角色: user / assistant / system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="对话消息列表")


class LoginConfig(BaseModel):
    username: str = Field(default="admin", description="CPQ 登录用户名")
    password: str = Field(default="admin123", description="CPQ 登录密码")


class UpdateConfigRequest(BaseModel):
    model_config = {"extra": "ignore"}  # 前端可能发送 UI/System 等额外字段

    model_base_url: str | None = Field(default=None, description="模型 API 基础 URL")
    model_api_key: str | None = Field(default=None, description="模型 API Key")
    model_name: str | None = Field(default=None, description="模型名称")
    model_temperature: float | None = Field(default=None, ge=0, le=2, description="模型温度")
    cpq_base_url: str | None = Field(default=None, description="CPQ 服务 URL")
    cpq_client_id: str | None = Field(default=None, description="CPQ 客户端 ID")
    cpq_username: str | None = Field(default=None, description="CPQ 用户名")
    cpq_password: str | None = Field(default=None, description="CPQ 密码")
    agent_max_turns: int | None = Field(default=None, ge=1, le=100, description="最大对话轮次")
    agent_system_prompt: str | None = Field(default=None, description="系统提示")


# ── Agent 生命周期 ──────────────────────────────────────


def init_agent(cfg: Config | None = None) -> Any:
    """初始化或重新加载 Agent"""
    global _config, _agent
    if cfg is not None:
        _config = cfg
    elif _config is None:
        _config = load_config()
    try:
        _agent = build_agent(_config)
        print(f"[server] Agent 已初始化 (model={_config.model.model_name})")
        return _agent
    except Exception as e:
        print(f"[server] Agent 初始化失败: {e}")
        traceback.print_exc()
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """服务生命周期管理"""
    global _config, _agent
    try:
        _config = load_config()
        init_agent(_config)
        port_str = os.environ.get("PORT", "58118")
        print(f"[server] Application startup complete, port {port_str}")
    except Exception as e:
        # Use ascii-safe messages to avoid cp1252 encoding errors on Windows CI
        print(f"[server] WARN: startup exception - {e}")
        traceback.print_exc()
        print("[server] WARN: running in degraded mode (config not loaded, Agent unavailable)")
    yield
    print("[server] Server shutting down")


# ── FastAPI App ──────────────────────────────────────────

app = FastAPI(
    title="CPQ Agent API",
    description="CPQ 智能配置报价助手后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 辅助函数 ──────────────────────────────────────────────


async def sse_stream(agent: Any, messages: list[dict]) -> AsyncGenerator[str, None]:
    """将 agent 流式输出转为 SSE 事件流"""
    try:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        # 转换消息格式
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))

        # 输入状态
        input_state = {"messages": langchain_messages}

        # 发送状态事件
        yield f"event: status\ndata: {json.dumps({'status': 'processing', 'message': '正在处理...'})}\n\n"

        full_response = ""
        async for event in agent.astream_events(
                input_state,
                version="v2",
                config={"recursion_limit": 9999},
            ):
            # 处理 token 流
            if event.get("event") == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", {})
                if hasattr(chunk, "content"):
                    content = chunk.content
                    if content:
                        full_response += content
                        yield f"event: message_delta\ndata: {json.dumps({'content': content})}\n\n"

            # 处理工具调用
            elif event.get("event") == "on_tool_start":
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                yield f"event: status\ndata: {json.dumps({'status': 'tool_call', 'tool': tool_name, 'input': str(tool_input)[:200]})}\n\n"

            elif event.get("event") == "on_tool_end":
                tool_name = event.get("name", "unknown")
                tool_output = event.get("data", {}).get("output", {})
                output_str = str(tool_output)[:200]
                yield f"event: status\ndata: {json.dumps({'status': 'tool_result', 'tool': tool_name, 'output': output_str})}\n\n"

        # 追加完成提示
        completion_suffix = "\n\n✅ **已完成所有工作。** 请问还需要什么帮助？"
        yield f"event: message_delta\ndata: {json.dumps({'content': completion_suffix})}\n\n"
        full_response += completion_suffix

        # 发送完成事件
        yield f"event: done\ndata: {json.dumps({'status': 'completed', 'content': full_response})}\n\n"

    except Exception as e:
        error_msg = f"Agent 处理出错: {str(e)}"
        traceback.print_exc()
        yield f"event: error\ndata: {json.dumps(error_msg)}\n\n"


# ── 端点 ──────────────────────────────────────────────────


@app.get("/health/diagnostics")
async def health_diagnostics():
    """详细诊断信息 — 帮助排查启动和连接问题"""
    import platform
    import sys

    global _config

    config_loaded = _config is not None
    agent_ready = _agent is not None

    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "cwd": os.getcwd(),
        "config_loaded": config_loaded,
        "agent_ready": agent_ready,
        "config": _config.to_dict_safe() if _config else None,
    }


@app.get("/health")
async def health_check():
    """健康检查

    检查 CPQ 服务是否可达和 Agent 是否就绪
    """
    global _config, _agent

    cpq_ok, cpq_msg = tools.health_check()

    agent_ok = _agent is not None
    agent_msg = "Agent 就绪" if agent_ok else "Agent 未初始化"

    overall = cpq_ok and agent_ok

    return {
        "status": "ok" if overall else "degraded",
        "cpq": {"status": "ok" if cpq_ok else "error", "message": cpq_msg},
        "agent": {"status": "ok" if agent_ok else "error", "message": agent_msg},
    }


@app.post("/agent/chat")
async def agent_chat(request: ChatRequest):
    """Agent 对话

    接收用户消息，返回 SSE 流式响应。
    事件类型:
    - message_delta: 流式文本片段
    - status: 状态更新（处理中/工具调用/工具结果）
    - done: 完成事件
    """
    global _agent

    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent 未就绪，请稍后重试")

    messages_dict = [msg.model_dump() for msg in request.messages]
    if not messages_dict:
        raise HTTPException(status_code=400, detail="消息列表不能为空")

    return StreamingResponse(
        sse_stream(_agent, messages_dict),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/config")
async def get_config():
    """获取当前配置（脱敏）"""
    global _config
    if _config is None:
        raise HTTPException(status_code=503, detail="配置未加载")
    return _config.to_dict_safe()


@app.put("/config")
async def update_config(payload: dict = Body(...)):
    """更新配置并重载 Agent

    兼容前端发送的扁平键名（cpq_api_url → cpq_base_url 等）。
    """
    global _config, _agent

    if _config is None:
        _config = load_config()

    # 更新模型配置
    if "model_base_url" in payload and payload["model_base_url"] is not None:
        _config.model.base_url = payload["model_base_url"]
    if "model_api_key" in payload and payload["model_api_key"] is not None:
        _config.model.api_key = payload["model_api_key"]
    if "model_name" in payload and payload["model_name"] is not None:
        _config.model.model_name = payload["model_name"]
    if "model_temperature" in payload and payload["model_temperature"] is not None:
        _config.model.temperature = payload["model_temperature"]

    # 更新 CPQ 配置（兼容前端 cpq_api_url → cpq_base_url, cpq_timeout → cpq.timeout）
    cpq_url = payload.get("cpq_base_url") or payload.get("cpq_api_url")
    if cpq_url is not None:
        _config.cpq.base_url = cpq_url
    if payload.get("cpq_client_id") is not None:
        _config.cpq.client_id = payload["cpq_client_id"]
    if payload.get("cpq_username") is not None:
        _config.cpq.username = payload["cpq_username"]
    if payload.get("cpq_password") not in (None, ""):
        _config.cpq.password = payload["cpq_password"]
    if payload.get("cpq_timeout") is not None:
        _config.cpq.timeout = int(payload["cpq_timeout"])

    # 更新 Agent 配置（兼容前端 agent_max_iterations → agent_max_turns）
    max_turns = payload.get("agent_max_turns") or payload.get("agent_max_iterations")
    if max_turns is not None:
        _config.agent.max_turns = int(max_turns)
    if payload.get("agent_system_prompt") is not None:
        _config.agent.system_prompt = payload["agent_system_prompt"]

    # 持久化到磁盘
    saved = save_config(_config)

    # 重载 Agent
    try:
        init_agent(_config)
        return {
            "status": "ok",
            "message": "配置已更新，Agent 已重载",
            "persisted": saved,
        }
    except Exception as e:
        # 即使 Agent 重载失败，配置也已更新到内存和磁盘
        if saved:
            return {
                "status": "ok",
                "message": f"配置已保存到磁盘，但 Agent 重载失败（{e}）。请重启应用使配置生效。",
                "persisted": True,
                "agent_error": str(e),
            }
        raise HTTPException(status_code=500, detail=f"Agent 重载失败: {e}")


@app.post("/config/test-cpq")
async def test_cpq_connection():
    """测试 CPQ 连接"""
    global _config
    if _config is None:
        raise HTTPException(status_code=503, detail="配置未加载")

    try:
        cfg = _config.cpq
        # 尝试登录
        resp = requests.post(
            f"{cfg.base_url}/auth/login",
            json={
                "username": cfg.username,
                "password": cfg.password,
                "clientId": cfg.client_id,
                "grantType": "password",
                "tenantId": "000000",
            },
            headers={"Content-Type": "application/json"},
            timeout=cfg.timeout,
        )
        if resp.status_code == 200:
            body = resp.json()
            return {
                "status": "ok",
                "message": f"CPQ 连接成功 ({cfg.base_url})",
                "authenticated": True,
            }
        else:
            return {
                "status": "error",
                "message": f"CPQ 返回状态码 {resp.status_code}: {resp.text[:200]}",
            }
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": f"无法连接到 {cfg.base_url}"}
    except Exception as e:
        return {"status": "error", "message": f"连接测试失败: {e}"}


@app.post("/config/test-model")
async def test_model_connection():
    """测试模型连接"""
    global _config
    if _config is None:
        raise HTTPException(status_code=503, detail="配置未加载")

    try:
        cfg = _config.model
        model = ChatDeepSeek(
            model=cfg.model_name,
            api_key=cfg.api_key or os.environ.get("DEEPSEEK_API_KEY", ""),
            base_url=cfg.base_url,
            temperature=cfg.temperature,
            max_tokens=100,
        )
        result = model.invoke([{"role": "user", "content": "回复 OK 表示连接正常"}])
        return {
            "status": "ok",
            "message": f"模型连接成功: {result.content[:100]}",
        }
    except Exception as e:
        return {"status": "error", "message": f"模型连接失败: {e}"}


# ── 入口 ──────────────────────────────────────────────────


def main():
    """启动 FastAPI 服务"""
    port = int(os.environ.get("PORT", "58100"))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"[server] 启动 CPQ Agent 服务: http://{host}:{port}")
    print(f"[server] 文档: http://{host}:{port}/docs")

    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
