# AI 工具后端联调指南 (联网搜索)

本文档旨在指导后端开发人员如何对接前端「故障诊断」面板中的 AI 工具功能（联网搜索）。

## 1. 接口信息

- **接口地址**: `/api/v1/ai/chat`
- **请求方法**: `POST`
- **认证方式**: `Bearer Token` (Header: `Authorization`)

## 2. 请求格式 (Request Payload)

前端会发送一个 JSON 对象，包含当前的消息内容以及工具配置上下文。

```json
{
  "sessionId": "string", // 会话 ID，用于维持上下文 (如 diagnosis-node-001)
  "message": "string", // 用户输入的当前问题内容
  "context": {
    "node": "string", // 当前选中的节点名称 (可选)
    "agent": "string", // 选中的智能体名称 (如 "诊断智能体")
    "model": "string", // 选中的模型名称 (如 "deepseek")
    "webSearch": true // 是否开启【联网搜索】功能
  }
}
```

### 字段说明

- `webSearch`: 当此项为 `true` 时，后端应先调用搜索引擎（如 Google/Bing API 或内建搜索插件）获取实时信息，再将其作为上下文喂给 LLM。

## 3. 响应格式 (Response Body)

后端应返回 AI 的回复内容。如果模型支持，可以返回推理过程。

```json
{
  "reply": "string", // AI 最终生成的回答 (支持 Markdown)
  "reasoning": "string" // [可选] AI 的思维链/推理过程，前端会自动以折叠框形式展示
}
```

## 4. 后端实现建议 (Python/FastAPI 示例)

后端需要更新 `ChatReq` 模型以接收 `context` 字段，并在调用大模型服务时透传这些参数。

```python
class ChatContext(BaseModel):
    node: str | None = None
    agent: str | None = None
    model: str | None = None
    webSearch: bool = False

class ChatReq(BaseModel):
    sessionId: str
    message: str
    context: ChatContext

@router.post("/ai/chat")
async def ai_chat(req: ChatReq):
    # 1. 如果 webSearch 为 True，在此处执行联网搜索逻辑
    search_results = ""
    if req.context.webSearch:
        search_results = await perform_web_search(req.message)

    # 2. 调用 LLM
    llm_response = await llm_client.chat(
        prompt=req.message,
        system_context=f"Node: {req.context.node}, Search: {search_results}"
    )

    return {
        "reply": llm_response.content,
        "reasoning": llm_response.reasoning # 即使前端没请求，后端也可根据模型能力返回推理内容
    }
```

## 5. 注意事项

- **超时处理**: 开启 `webSearch` 后，LLM 的响应时间会显著增加，请确保后端 API 的超时时间设置合理（建议 60s 以上）。
- **流式输出**: 目前前端采用的是非流式交互，如果后续需要改为流式输出，请另行约定 SSE 协议。
