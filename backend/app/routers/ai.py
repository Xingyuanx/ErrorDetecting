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
from ..models.hadoop_logs import HadoopLog
from ..models.chat import ChatSession, ChatMessage
from ..agents.diagnosis_agent import run_diagnose_and_repair
from ..services.llm import LLMClient
from ..services.ops_tools import openai_tools_schema, tool_web_search, tool_start_cluster, tool_stop_cluster, tool_read_log, tool_read_cluster_log, tool_detect_cluster_faults, tool_run_cluster_command


router = APIRouter()


class DiagnoseRepairReq(BaseModel):
    cluster: str | None = Field(None, description="集群UUID")
    node: str | None = Field(None, description="节点主机名")
    timeFrom: str | None = Field(None, description="ISO起始时间")
    keywords: str | None = Field(None, description="关键词")
    auto: bool = Field(True, description="是否允许自动修复")
    maxSteps: int = Field(3, ge=1, le=6, description="最多工具步数")
    model: str | None = Field(None, description="使用的模型")

class ChatReq(BaseModel):
    sessionId: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入")
    stream: bool = Field(False, description="是否使用流式输出")
    context: dict | None = Field(None, description="上下文，包含node, agent, model等")

class HistoryReq(BaseModel):
    sessionId: str

def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None) or "system"

def _get_internal_session_id(user, session_id: str) -> str:
    uname = _get_username(user)
    return f"{uname}:{session_id}"


@router.post("/ai/diagnose-repair")
async def diagnose_repair(req: DiagnoseRepairReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # 聚合简要日志上下文（结构化日志）
        filters = []
        if req.node:
            filters.append(HadoopLog.node_host == req.node)
        if req.keywords:
            # 这里简化为 info 包含关键词
            filters.append(HadoopLog.info.ilike(f"%{req.keywords}%"))
        stmt = select(HadoopLog).limit(100).order_by(HadoopLog.log_time.desc())
        for f in filters:
            stmt = stmt.where(f)
        rows = (await db.execute(stmt)).scalars().all()
        ctx_logs = [r.to_dict() for r in rows[:50]]
        context = {"cluster": req.cluster, "node": req.node, "logs": ctx_logs}
        uname = _get_username(user)
        result = await run_diagnose_and_repair(db, uname, context, auto=req.auto, max_steps=req.maxSteps, model=req.model)
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

@router.get("/ai/history")
async def get_history(sessionId: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取会话历史"""
    internal_id = _get_internal_session_id(user, sessionId)
    stmt = select(ChatMessage).where(ChatMessage.session_id == internal_id).order_by(ChatMessage.created_at.asc())
    rows = (await db.execute(stmt)).scalars().all()
    messages = [{"role": r.role, "content": r.content} for r in rows]
    return {"messages": messages}

@router.post("/ai/chat")
async def ai_chat(req: ChatReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        internal_id = _get_internal_session_id(user, req.sessionId)
        user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
        
        session_stmt = select(ChatSession).where(ChatSession.id == internal_id)
        session = (await db.execute(session_stmt)).scalars().first()
        if not session:
            session = ChatSession(id=internal_id, user_id=user_id, title=req.message[:20])
            db.add(session)

        system_prompt = (
            "你是 Hadoop 运维诊断助手。输出中文，优先给出根因、影响范围、证据与建议。"
            "当用户询问“故障/异常/报错/不可用/打不开/任务失败”等问题时，优先调用 detect_cluster_faults；"
            "必要时再用 read_cluster_log 补充读取对应组件日志。"
            "当用户询问进程/端口/资源/版本等日常运维信息时，优先调用 run_cluster_command（例如 jps/df/free/hdfs_report/yarn_node_list）。"
        )
        if req.context:
            if req.context.get("agent"):
                system_prompt += f" Your name is {req.context['agent']}."
            if req.context.get("node"):
                system_prompt += f" You are currently analyzing node: {req.context['node']}."
        
        hist_stmt = select(ChatMessage).where(ChatMessage.session_id == internal_id).order_by(ChatMessage.created_at.desc()).limit(12)
        hist_rows = (await db.execute(hist_stmt)).scalars().all()
        hist_rows = hist_rows[::-1] 
        
        messages = [{"role": "system", "content": system_prompt}]
        for r in hist_rows:
            messages.append({"role": r.role, "content": r.content})
        messages.append({"role": "user", "content": req.message})
        
        user_msg = ChatMessage(session_id=internal_id, role="user", content=req.message)
        db.add(user_msg)

        llm = LLMClient()
        target_model = req.context.get("model") if req.context else None
        
        # 默认加载所有可用运维工具
        chat_tools = openai_tools_schema()
        
        if req.stream:
            # 流式暂不支持工具调用后的二次生成（为了简化），如果检测到可能需要工具，先走非流式
            # 或者这里可以根据需求调整，目前先保持非流式处理工具逻辑
            pass

        resp = await llm.chat(messages, tools=chat_tools, stream=False, model=target_model)
        choices = resp.get("choices") or []
        if not choices:
            raise HTTPException(status_code=502, detail="llm_unavailable")
        msg = choices[0].get("message") or {}
        tool_calls = msg.get("tool_calls") or []
        
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
                uname = _get_username(user)
                if name == "web_search":
                    tool_result = await tool_web_search(args.get("query"), args.get("max_results", 5))
                elif name == "start_cluster":
                    tool_result = await tool_start_cluster(db, uname, args.get("cluster_uuid"))
                elif name == "stop_cluster":
                    tool_result = await tool_stop_cluster(db, uname, args.get("cluster_uuid"))
                elif name == "read_log":
                    tool_result = await tool_read_log(db, uname, args.get("node"), args.get("path"), int(args.get("lines", 200)), args.get("pattern"), args.get("sshUser"))
                elif name == "read_cluster_log":
                    tool_result = await tool_read_cluster_log(
                        db, 
                        uname, 
                        args.get("cluster_uuid"), 
                        args.get("log_type"), 
                        args.get("node_hostname"), 
                        int(args.get("lines", 100))
                    )
                elif name == "detect_cluster_faults":
                    tool_result = await tool_detect_cluster_faults(
                        db,
                        uname,
                        args.get("cluster_uuid"),
                        args.get("components"),
                        args.get("node_hostname"),
                        int(args.get("lines", 200)),
                    )
                elif name == "run_cluster_command":
                    tool_result = await tool_run_cluster_command(
                        db,
                        uname,
                        args.get("cluster_uuid"),
                        args.get("command_key"),
                        args.get("target"),
                        args.get("node_hostname"),
                        int(args.get("timeout", 30)),
                        int(args.get("limit_nodes", 20)),
                    )
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "name": name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            if req.stream:
                return await handle_streaming_chat(llm, messages, internal_id, db, tools=chat_tools, model=target_model)
            else:
                resp = await llm.chat(messages, tools=chat_tools, stream=False, model=target_model)
                choices = resp.get("choices") or []
                if not choices:
                    raise HTTPException(status_code=502, detail="llm_unavailable_after_tool")
                msg = choices[0].get("message") or {}
        else:
            if req.stream:
                return await handle_streaming_chat(llm, messages, internal_id, db, tools=chat_tools, model=target_model)
        
        reply = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        
        asst_msg = ChatMessage(session_id=internal_id, role="assistant", content=reply)
        db.add(asst_msg)
        await db.commit()

        return {"reply": reply, "reasoning": reasoning}

    except HTTPException:
        raise
    except Exception as e:
        print(f"AI Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"server_error: {str(e)}")

async def handle_streaming_chat(llm: LLMClient, messages: list, session_id: str, db: AsyncSession, tools=None, model: str = None):
    async def event_generator():
        full_reply = ""
        full_reasoning = ""
        
        try:
            stream_gen = await llm.chat(messages, tools=tools, stream=True, model=model)
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
        finally:
            try:
                if full_reply:
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
