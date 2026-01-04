from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..services.llm import LLMClient
from ..services.ops_tools import openai_tools_schema, tool_read_log, tool_start_cluster, tool_stop_cluster


async def run_diagnose_and_repair(db: AsyncSession, operator: str, context: Dict[str, Any], auto: bool = True, max_steps: int = 3, model: Optional[str] = None) -> Dict[str, Any]:
    """单智能体：根据日志上下文诊断并自动修复（Function Calling）。

    - context：包含 cluster/node/logs 等关键信息
    - auto：是否允许自动执行工具（默认允许）
    - max_steps：最多工具调用步数
    - model：指定的模型名称
    返回：根因、动作列表与结果、剩余风险
    """
    llm = LLMClient()
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": "你是Hadoop运维诊断专家。你只能调用提供的函数来读取日志或修复。输出中文，优先给出根因、影响范围与修复建议。",
        },
        {
            "role": "user",
            "content": f"上下文: {context}",
        },
    ]
    tools = openai_tools_schema()
    actions: List[Dict[str, Any]] = []
    root_cause = None
    residual_risk = "medium"

    for step in range(max_steps):
        resp = await llm.chat(messages, tools=tools, stream=False, model=model)
        choice = (resp.get("choices") or [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            root_cause = msg.get("content")
            break
        if not auto:
            break
        for tc in tool_calls:
            fn = (tc.get("function") or {})
            name = fn.get("name")
            args = fn.get("arguments") or {}
            result: Dict[str, Any]
            if name == "read_log":
                result = await tool_read_log(db, operator, args.get("node"), args.get("path"), int(args.get("lines", 200)), args.get("pattern"), args.get("sshUser"))
            elif name == "start_cluster":
                result = await tool_start_cluster(db, operator, args.get("cluster_uuid"))
            elif name == "stop_cluster":
                result = await tool_stop_cluster(db, operator, args.get("cluster_uuid"))
            else:
                result = {"error": "unknown_tool"}
            actions.append({"name": name, "args": args, "result": result})
            messages.append({"role": "tool", "content": str(result), "name": name})
    return {"rootCause": root_cause, "actions": actions, "residualRisk": residual_risk}

