import os
from typing import Any, Dict, Iterable, List, Optional

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None


class LLMClient:
    """供应商大模型客户端，封装聊天与函数调用。

    - 通过环境变量配置：LLM_PROVIDER/LLM_ENDPOINT/LLM_MODEL/LLM_API_KEY
    - 提供 chat(messages, tools, stream) 接口，返回供应商原始响应字典
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.endpoint = os.getenv("LLM_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.simulate = os.getenv("LLM_SIMULATE", "false").lower() == "true"

    def _headers(self) -> Dict[str, str]:
        """构造 HTTP 请求头。"""
        return {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
        }

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, stream: bool = False) -> Dict[str, Any]:
        """调用供应商聊天接口，支持函数调用工具描述。

        - messages：OpenAI 兼容的消息列表
        - tools：OpenAI 兼容的函数调用工具定义（JSON Schema）
        - stream：是否流式；此处返回一次性结果，SSE/WebSocket 由路由层实现
        """
        if self.simulate or httpx is None:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "模拟输出：检测到错误日志，建议重启或kill相关进程",
                            "tool_calls": [],
                        }
                    }
                ]
            }
        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        with httpx.Client(timeout=30) as client:
            resp = client.post(self.endpoint, headers=self._headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

