from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel, Field
import os

from ..db import get_db
from ..deps.auth import get_current_user
from ..models.system_logs import SystemLog
from ..agents.diagnosis_agent import run_diagnose_and_repair
from ..services.llm import LLMClient


router = APIRouter()


class DiagnoseRepairReq(BaseModel):
    cluster: str | None = Field(None, description="集群UUID")
    node: str | None = Field(None, description="节点主机名")
    timeFrom: str | None = Field(None, description="ISO起始时间")
    keywords: str | None = Field(None, description="关键词")
    auto: bool = Field(True, description="是否允许自动修复")
    maxSteps: int = Field(3, ge=1, le=6, description="最多工具步数")

class ChatReq(BaseModel):
    messages: list[dict] = Field(..., description="对话消息列表，形如[{role:'system'|'user'|'assistant', content:'...'}]")


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

@router.post("/ai/chat")
async def ai_chat(req: ChatReq, user=Depends(get_current_user)):
    try:
        llm = LLMClient()
        resp = await llm.chat(req.messages, tools=None, stream=False)
        choices = resp.get("choices") or []
        if not choices:
            raise HTTPException(status_code=502, detail="llm_unavailable")
        msg = choices[0].get("message") or {}
        reply = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        return {"reply": reply, "reasoning": reasoning}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
