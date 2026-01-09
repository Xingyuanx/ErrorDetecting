# AI 诊断流式输出后端联调指南

本文档旨在指导后端开发人员如何对接前端「故障诊断」面板中的 AI 流式输出功能。该功能允许 AI 回复以打字机效果逐块显示，提升用户体验。

## 1. 接口变更概要

- **接口地址**: `/api/v1/ai/chat`
- **请求方法**: `POST`
- **核心变更**: 
    1. 请求体新增 `stream: true` 字段。
    2. 响应类型变为 `text/event-stream` (SSE)。

## 2. 请求格式 (Request Payload)

前端在发起对话时会明确要求流式输出：

```json
{
  "sessionId": "string",
  "message": "string",
  "stream": true, // 关键字段：告知后端使用流式响应
  "context": {
    "node": "string",
    "agent": "string",
    "model": "string",
    "webSearch": boolean
  }
}
```

## 3. 响应协议 (SSE 协议规范)

后端应使用标准 **Server-Sent Events (SSE)** 协议返回数据。

### 响应头 (Headers)
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

### 数据格式 (Data Format)
每一行数据必须以 `data: ` 开头，并包含一个 JSON 字符串。

```text
data: {"content": "正在", "reasoning": ""}
data: {"content": "分析", "reasoning": ""}
data: {"content": "日志", "reasoning": "用户询问了故障原因..."}
data: {"content": "...", "reasoning": "..."}
```

- **`content`**: AI 生成的正文内容片段（追加模式）。
- **`reasoning`**: AI 的推理过程片段（可选，追加模式）。

### 结束标志
流结束时，后端应关闭连接。

## 4. 后端实现参考 (Python/FastAPI 示例)

后端需要将原有的普通返回改为生成器模式。

```python
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

@router.post("/ai/chat")
async def ai_chat(req: ChatReq):
    if not req.stream:
        # 保留原有的非流式逻辑
        return await handle_normal_chat(req)

    async def event_generator():
        # 模拟调用 LLM 的流式接口
        async for chunk in llm_client.chat_stream(req.message):
            # 构造 SSE 格式
            yield f"data: {json.dumps({'content': chunk.content, 'reasoning': chunk.reasoning})}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

## 5. 联调注意事项

1. **JSON 转义**: 确保 `data: ` 后面的 JSON 字符串经过正确转义（特别是换行符和引号）。
2. **缓冲禁用**: 如果后端使用了 Nginx 等代理，请确保禁用了响应缓冲（`X-Accel-Buffering: no`），否则流式效果会被缓存。
3. **空消息处理**: 前端会自动处理 `content` 为空的情况，但建议每条 `data` 至少包含一个有效字段。
4. **异常处理**: 如果流传输中途报错，后端应发送一个包含错误信息的 JSON（例如 `{"error": "..."}`）并断开连接。
