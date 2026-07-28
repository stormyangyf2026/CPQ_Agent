#!/usr/bin/env python3
"""CPQ Agent — FastAPI + DeepAgents SSE 流式"""

import json, os, sys, traceback, glob, tempfile, shutil
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator
import requests, uvicorn
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel
import tools
from agent import build_agent, SYSTEM_PROMPT
from config import Config, load_config, save_config

_config: Config | None = None
_agent: Any = None

SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sessions")

def _session_path(client_id: str, session_id: str) -> str:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return os.path.join(SESSIONS_DIR, f"{client_id}_{session_id}.json")

def _save_session(client_id: str, session_id: str, messages: list[dict], title: str = ""):
    """原子写入会话文件"""
    data = {
        "id": session_id, "clientId": client_id, "title": title or "新对话",
        "messages": messages, "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    fp = _session_path(client_id, session_id)
    tmp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=SESSIONS_DIR, delete=False, suffix=".json")
    try:
        json.dump(data, tmp, ensure_ascii=False, default=str)
        tmp.flush(); os.fsync(tmp.fileno())
        tmp.close()
        os.replace(tmp.name, fp)
    except Exception:
        if os.path.exists(tmp.name): os.unlink(tmp.name)

def _load_session(client_id: str, session_id: str) -> dict | None:
    fp = _session_path(client_id, session_id)
    if not os.path.exists(fp): return None
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)

def _list_sessions(client_id: str) -> list[dict]:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    sessions = []
    for fp in glob.glob(os.path.join(SESSIONS_DIR, f"{client_id}_*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                d = json.load(f)
            sessions.append({
                "id": d.get("id"), "title": d.get("title", "新对话"),
                "updatedAt": d.get("updatedAt", ""), "messageCount": len(d.get("messages", []))
            })
        except: pass
    sessions.sort(key=lambda s: s["updatedAt"], reverse=True)
    return sessions

def _delete_session(client_id: str, session_id: str) -> bool:
    fp = _session_path(client_id, session_id)
    if os.path.exists(fp):
        os.unlink(fp)
        return True
    return False

class ChatMessage(BaseModel): role: str; content: str
class ChatRequest(BaseModel): messages: list[ChatMessage]; sessionId: str = ""; clientId: str = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _config, _agent
    _config = load_config()
    tools.set_cpq_config(_config.cpq)
    import cpq_api; cpq_api.CPQ_URL = _config.cpq.base_url
    _agent = build_agent(_config)
    print(f"[server] Agent ready, CPQ={_config.cpq.base_url}")
    yield

app = FastAPI(title="CPQ Agent", version="3.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

def _extract_tool_data(output) -> dict | None:
    """鲁棒提取 ToolMessage 中的 dict 数据，兼容 DeepAgents/LangChain 各版本 output 格式"""
    if output is None:
        return None
    if isinstance(output, dict):
        return output
    if isinstance(output, (list, tuple)) and len(output) > 0:
        # 可能是 content blocks: [{"text": "...", "type": "text"}]
        first = output[0]
        if isinstance(first, dict):
            if 'text' in first:
                return _extract_tool_data(first['text'])
            return first
        return _extract_tool_data(first)
    if isinstance(output, str):
        try:
            return json.loads(output)
        except (json.JSONDecodeError, TypeError):
            return None
    # ToolMessage 对象
    if hasattr(output, 'content'):
        return _extract_tool_data(output.content)
    # 最后尝试直接转 dict
    try:
        return dict(output)
    except (TypeError, ValueError):
        return None


async def sse_stream(messages: list[dict], session_id: str = "", client_id: str = "") -> AsyncGenerator[str, None]:
    """DeepAgents 流式 → SSE"""
    tools.set_current_session(session_id)
    langchain_msgs = []
    for m in messages:
        content = m.get("content", "")
        if m.get("role") == "assistant" and not content.strip():
            continue  # 跳过前端空占位
        if m.get("role") == "system":
            langchain_msgs.append(SystemMessage(content=content))
        elif m.get("role") == "assistant":
            langchain_msgs.append(AIMessage(content=content))
        else:
            langchain_msgs.append(HumanMessage(content=content))

    # DeepAgent build_agent 已传入 system_prompt，不再重复插入


    yield f"event: status\ndata: {json.dumps({'status': 'processing', 'message': '分析中...'})}\n\n"

    full = ""
    match_sent = False  # ★ 单次LLM调用中只发一次产品卡片（用户要求重匹配会启动新流，天然允许）
    try:
        async for event in _agent.astream_events({"messages": langchain_msgs}, version="v2",
                                                  config={"recursion_limit": 9999}):
            kind = event.get("event", "")
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", {})
                if hasattr(chunk, "content") and chunk.content:
                    full += chunk.content
                    yield f"event: message_delta\ndata: {json.dumps({'content': chunk.content})}\n\n"
            elif kind == "on_tool_start":
                name = event.get("name", "")
                yield f"event: status\ndata: {json.dumps({'status': 'tool_call', 'tool': name})}\n\n"
            elif kind == "on_tool_end":
                name = event.get("name", "")
                output = event.get("data", {}).get("output", {})

                # ★ 鲁棒提取 ToolMessage → dict（兼容多版本 DeepAgents/LangChain）
                tool_data = _extract_tool_data(output)
                if tool_data is None:
                    print(f"[server] WARN: 无法解析工具输出 tool={name} output_type={type(output).__name__}")

                yield f"event: status\ndata: {json.dumps({'status': 'tool_result', 'tool': name})}\n\n"

                # match_product → 结构化卡片事件（只发一次，防止LLM重复调用）
                if name == "match_product" and isinstance(tool_data, dict) and not match_sent:
                    recs = tool_data.get("recommendations", [])
                    if recs:
                        match_sent = True
                        yield f"event: match_result\ndata: {json.dumps({'resultId': tool_data.get('resultId'), 'sessionId': tool_data.get('sessionId'), 'threshold': tool_data.get('threshold',70), 'thresholdPassed': tool_data.get('thresholdPassed',False), 'suggestDiy': tool_data.get('suggestDiy',False), 'totalScored': tool_data.get('totalScored',0), 'recommendations': recs[:10]}, ensure_ascii=False)}\n\n"

                # submit_feasibility_confirm / select_product / confirm_replacement → 工艺确认卡片事件
                if name in ("submit_feasibility_confirm", "select_product", "confirm_replacement") and isinstance(tool_data, dict):
                    yield f"event: process_confirm\ndata: {json.dumps(tool_data, ensure_ascii=False)}\n\n"
    except Exception as e:
        traceback.print_exc()
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"
    # ★ 保存会话到文件（只保存完整消息，跳过空占位和流式中的消息）
    if client_id and session_id:
        try:
            clean_msgs = []
            for m in messages + [{"role": "assistant", "content": full, "id": session_id + "-last", "status": "done", "createdAt": datetime.now(timezone.utc).isoformat()}]:
                if m.get("role") == "assistant" and not m.get("content", "").strip():
                    continue  # 跳过空占位
                if m.get("status") == "streaming":
                    m = {**m, "status": "done"}
                clean_msgs.append(m)
            title = ""
            for m in clean_msgs:
                if m.get("role") == "user" and m.get("content"):
                    title = m["content"][:30]
                    break
            _save_session(client_id, session_id, clean_msgs, title)
        except Exception:
            pass


@app.post("/agent/chat")
async def agent_chat(req: ChatRequest):
    msgs = [m.model_dump() for m in req.messages]
    if not msgs: raise HTTPException(400)
    return StreamingResponse(sse_stream(msgs, req.sessionId, req.clientId), media_type="text/event-stream",
        headers={"Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"})

@app.post("/agent/confirm")
async def agent_confirm(data: dict = Body(...)):
    """前端直接提交工艺确认，绕过LLM"""
    try:
        result_id = data.get("resultId")
        model_id = data.get("modelId")
        if not result_id or not model_id:
            raise HTTPException(400, "缺少 resultId 或 modelId")
        result = tools.submit_feasibility_confirm.func(int(result_id), int(model_id), "CONFIRM")
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/agent/status/{resultId}")
async def agent_status(resultId: int):
    """轮询工艺确认状态，供 FeasibilityConfirmPanel 使用"""
    try:
        import cpq_api
        status = cpq_api.get_process_status(resultId)
        return status
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.get("/health")
async def health():
    ok, msg = tools.health_check()
    return {"status":"ok" if ok else "degraded","cpq":{"status":"ok" if ok else "error","message":msg},"agent":{"status":"ok","message":"DeepAgents"}}

@app.get("/config")
async def get_config():
    if not _config: raise HTTPException(503)
    return _config.to_dict_safe()

@app.put("/config")
async def update_config(payload: dict = Body(...)):
    global _config, _agent
    if not _config: _config = load_config()
    for k, v in payload.items():
        if v is None: continue
        if k.startswith("model_"): setattr(_config.model, k[6:], v)
        elif k.startswith("cpq_"): setattr(_config.cpq, k[4:], v)
        elif k.startswith("agent_"): setattr(_config.agent, k[6:], v)
    save_config(_config)
    _agent = build_agent(_config)
    return {"status":"ok"}

# ── 会话管理 ────────────────────────────────────────────

@app.get("/sessions")
async def list_sessions(clientId: str = Query("")):
    if not clientId: return []
    return _list_sessions(clientId)

@app.get("/sessions/{sessionId}")
async def get_session(sessionId: str, clientId: str = Query("")):
    if not clientId: raise HTTPException(400, "clientId is required")
    data = _load_session(clientId, sessionId)
    if not data: raise HTTPException(404, "会话不存在")
    return data

@app.delete("/sessions/{sessionId}")
async def remove_session(sessionId: str, clientId: str = Query("")):
    if not clientId: raise HTTPException(400, "clientId is required")
    if not _delete_session(clientId, sessionId): raise HTTPException(404, "会话不存在")
    return {"status": "ok"}

def main():
    port = int(os.environ.get("PORT","58100"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
