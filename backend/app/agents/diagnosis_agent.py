from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..services.llm import LLMClient
from ..services.ops_tools import openai_tools_schema, tool_read_log, tool_kill_process, tool_reboot_node


async def run_diagnose_and_repair(db: AsyncSession, operator: str, context: Dict[str, Any], auto: bool = True, max_steps: int = 3) -> Dict[str, Any]:
    """单智能体：根据日志上下文诊断并自动修复（Function Calling）。

    - context：包含 cluster/node/logs 等关键信息
    - auto：是否允许自动执行工具（默认允许）
    - max_steps：最多工具调用步数
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
        resp = llm.chat(messages, tools=tools, stream=False)
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
            elif name == "kill_process":
                result = await tool_kill_process(db, operator, args.get("node"), int(args.get("pid")), int(args.get("signal", 9)), args.get("sshUser"))
            elif name == "reboot_node":
                result = await tool_reboot_node(db, operator, args.get("node"), args.get("sshUser"))
            else:
                result = {"error": "unknown_tool"}
            actions.append({"name": name, "args": args, "result": result})
            messages.append({"role": "tool", "content": str(result), "name": name})
    return {"rootCause": root_cause, "actions": actions, "residualRisk": residual_risk}

