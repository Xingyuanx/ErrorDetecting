import os
import json
from typing import Any, Dict, Iterable, List, Optional
from dotenv import load_dotenv

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

load_dotenv()

_shared_async_client: Any = None

def _get_async_client() -> Any:
    global _shared_async_client
    if httpx is None:
        return None
    if _shared_async_client is None:
        _shared_async_client = httpx.AsyncClient(
            headers={},
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
            http2=True,
        )
    return _shared_async_client

_DEFAULT_ENDPOINTS: Dict[str, str] = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "siliconflow": "https://api.siliconflow.cn/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
}

_DEFAULT_MODELS: Dict[str, str] = {
    "openai": "gpt-4o-mini",
    "siliconflow": "deepseek-ai/DeepSeek-R1",
    "deepseek": "deepseek-ai/DeepSeek-R1",
}

def _clean_str(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    if (s.startswith("`") and s.endswith("`")) or (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s

def _normalize_endpoint(ep: str) -> str:
    if not ep:
        return ep
    s = _clean_str(ep).rstrip("/")
    if s.endswith("/v1"):
        return s + "/chat/completions"
    if s.endswith("/chat/completions"):
        return s
    return s


class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
        raw_endpoint = os.getenv("LLM_ENDPOINT", "") or _DEFAULT_ENDPOINTS.get(self.provider, _DEFAULT_ENDPOINTS["openai"])
        self.endpoint = _normalize_endpoint(raw_endpoint)
        self.model = _clean_str(os.getenv("LLM_MODEL", _DEFAULT_MODELS.get(self.provider, "gpt-4o-mini")))
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("SILICONFLOW_API_KEY") or ""
        self.api_key = api_key
        self.simulate = os.getenv("LLM_SIMULATE", "false").lower() == "true"
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
        }

    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, stream: bool = False) -> Any:
        if self.simulate or httpx is None:
            if stream:
                async def _sim_stream():
                    yield {"choices": [{"delta": {"content": "模拟流式输出：检测到错误日志，建议重启或kill相关进程"}, "index": 0}]}
                return _sim_stream()
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
        payload: Dict[str, Any] = {"model": self.model, "messages": messages, "stream": stream}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        if stream:
            async def _stream_gen():
                client = _get_async_client()
                async with client.stream("POST", self.endpoint, headers=self._headers(), json=payload, timeout=self.timeout) as resp:
                        resp.raise_for_status()
                        async for line in resp.aiter_lines():
                             if not line or not line.startswith("data: "):
                                 continue
                             data_str = line[6:].strip()
                             if data_str == "[DONE]":
                                 break
                             try:
                                 yield json.loads(data_str)
                             except:
                                 continue
            return _stream_gen()

        client = _get_async_client()
        resp = await client.post(self.endpoint, headers=self._headers(), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
