import os
from typing import Any, Dict, Iterable, List, Optional
from dotenv import load_dotenv

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

load_dotenv()

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

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, stream: bool = False) -> Dict[str, Any]:
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
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.endpoint, headers=self._headers(), json=payload)
            resp.raise_for_status()
            return resp.json()
