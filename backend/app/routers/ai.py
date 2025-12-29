from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel, Field
import os
import json
import uuid

from ..db import get_db
from ..deps.auth import get_current_user
from ..models.system_logs import SystemLog
from ..models.chat import ChatSession, ChatMessage
from ..agents.diagnosis_agent import run_diagnose_and_repair
from ..services.llm import LLMClient
from ..services.ops_tools import openai_tools_schema, tool_web_search


router = APIRouter()


class DiagnoseRepairReq(BaseModel):
    cluster: str | None = Field(None, description="集群UUID")
    node: str | None = Field(None, description="节点主机名")
    timeFrom: str | None = Field(None, description="ISO起始时间")
    keywords: str | None = Field(None, description="关键词")
    auto: bool = Field(True, description="是否允许自动修复")
    maxSteps: int = Field(3, ge=1, le=6, description="最多工具步数")

class ChatReq(BaseModel):
    sessionId: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入")
    stream: bool = Field(False, description="是否使用流式输出")
    context: dict | None = Field(None, description="上下文，包含node, agent, model等")

class HistoryReq(BaseModel):
    sessionId: str

def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None) or "system"


@router.post("/ai/diagnose-repair")
async def diagnose_repair(req: DiagnoseRepairReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # 聚合简要日志上下文（结构化日志）
        filters = []
        if req.node:
            filters.append(SystemLog.host == req.node)
        if req.keywords:
            # 这里简化为 message 包含关键词，实际可扩展 ilike/source/op 等
            filters.append(SystemLog.message.ilike(f"%{req.keywords}%"))
        stmt = select(SystemLog).limit(100).order_by(SystemLog.timestamp.desc())
        for f in filters:
            stmt = stmt.where(f)
        rows = (await db.execute(stmt)).scalars().all()
        ctx_logs = [r.to_dict() for r in rows[:50]]
        context = {"cluster": req.cluster, "node": req.node, "logs": ctx_logs}
        uname = _get_username(user)
        result = await run_diagnose_and_repair(db, uname, context, auto=req.auto, max_steps=req.maxSteps)
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

@router.get("/ai/history")
async def get_history(sessionId: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取会话历史"""
    stmt = select(ChatMessage).where(ChatMessage.session_id == sessionId).order_by(ChatMessage.created_at.asc())
    rows = (await db.execute(stmt)).scalars().all()
    messages = [{"role": r.role, "content": r.content} for r in rows]
    return {"messages": messages}

@router.post("/ai/chat")
async def ai_chat(req: ChatReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # 1. Ensure Session Exists
        session_stmt = select(ChatSession).where(ChatSession.id == req.sessionId)
        session = (await db.execute(session_stmt)).scalars().first()
        if not session:
            session = ChatSession(id=req.sessionId, user_id=getattr(user, "id", None), title=req.message[:20])
            db.add(session)
            await db.commit()
            await db.refresh(session)
        
        # 2. Save User Message
        user_msg = ChatMessage(session_id=req.sessionId, role="user", content=req.message)
        db.add(user_msg)
        await db.commit()

        # 3. Build Context & History for LLM
        system_prompt = "You are a helpful Hadoop diagnostic assistant."
        if req.context:
            if req.context.get("agent"):
                system_prompt += f" Your name is {req.context['agent']}."
            if req.context.get("node"):
                system_prompt += f" You are currently analyzing node: {req.context['node']}."
        
        hist_stmt = select(ChatMessage).where(ChatMessage.session_id == req.sessionId).order_by(ChatMessage.created_at.desc()).limit(20)
        hist_rows = (await db.execute(hist_stmt)).scalars().all()
        hist_rows = hist_rows[::-1] 
        
        messages = [{"role": "system", "content": system_prompt}]
        for r in hist_rows:
            messages.append({"role": r.role, "content": r.content})
        
        # 4. Call LLM
        llm = LLMClient()
        tools = openai_tools_schema()
        chat_tools = [t for t in tools if t["function"]["name"] == "web_search"]
        
        # We always do the first call without streaming to handle tool calls easily
        resp = await llm.chat(messages, tools=chat_tools, stream=False)
        choices = resp.get("choices") or []
        if not choices:
            raise HTTPException(status_code=502, detail="llm_unavailable")
            
        msg = choices[0].get("message") or {}
        tool_calls = msg.get("tool_calls") or []
        
        # Tool Loop
        if tool_calls:
            messages.append(msg)
            for tc in tool_calls:
                fn = tc.get("function") or {}
                name = fn.get("name")
                args_str = fn.get("arguments") or "{}"
                try:
                    args = json.loads(args_str)
                except:
                    args = {}
                
                tool_result = {"error": "unknown_tool"}
                if name == "web_search":
                    tool_result = await tool_web_search(args.get("query"), args.get("max_results", 5))
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "name": name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # After tool calls, we decide whether to stream the final response
            if req.stream:
                return await handle_streaming_chat(llm, messages, req.sessionId, db)
            else:
                resp = await llm.chat(messages, tools=chat_tools, stream=False)
                choices = resp.get("choices") or []
                if not choices:
                     raise HTTPException(status_code=502, detail="llm_unavailable_after_tool")
                msg = choices[0].get("message") or {}
        else:
            # No tool calls initially
            if req.stream:
                # If we want to stream the first response, we need to call it again with stream=True
                # because we already called it with stream=False to check for tool calls.
                # Alternatively, we could have streamed the first call and checked for tool calls in the stream.
                # But for simplicity, we just re-call it.
                return await handle_streaming_chat(llm, messages, req.sessionId, db)
        
        # Normal (non-streaming) response
        reply = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        
        asst_msg = ChatMessage(session_id=req.sessionId, role="assistant", content=reply)
        db.add(asst_msg)
        await db.commit()

        return {"reply": reply, "reasoning": reasoning}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="server_error")

async def handle_streaming_chat(llm: LLMClient, messages: list, session_id: str, db: AsyncSession):
    async def event_generator():
        full_reply = ""
        full_reasoning = ""
        
        # Start streaming from LLM
        stream_gen = await llm.chat(messages, stream=True)
        
        async for chunk in stream_gen:
            choices = chunk.get("choices") or []
            if not choices:
                continue
            
            delta = choices[0].get("delta") or {}
            content = delta.get("content") or ""
            reasoning = delta.get("reasoning_content") or ""
            
            if content:
                full_reply += content
            if reasoning:
                full_reasoning += reasoning
                
            yield f"data: {json.dumps({'content': content, 'reasoning': reasoning}, ensure_ascii=False)}\n\n"
        
        # After stream ends, save to DB
        if full_reply:
            # Note: We need a new session or be careful with the current one 
            # as this runs in a generator which might outlive the request scope
            # but FastAPI handles this correctly if we use the db from depends.
            # However, committed changes in a generator might be tricky.
            # Let's use a fresh session if possible or just commit here.
            try:
                asst_msg = ChatMessage(session_id=session_id, role="assistant", content=full_reply)
                db.add(asst_msg)
                await db.commit()
            except Exception as e:
                print(f"Error saving stream to DB: {e}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
