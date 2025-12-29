# AI 诊断流式输出后端联调指南

本文档旨在指导前端开发人员如何对接后端「故障诊断」面板中的 AI 流式输出功能。该功能基于 SSE (Server-Sent Events) 协议，允许 AI 回复以打字机效果逐块显示，提升用户体验。

## 1. 接口基本信息

- **接口地址**: `/api/v1/ai/chat`
- **请求方法**: `POST`
- **认证方式**: Bearer Token (在 Header 中携带 `Authorization: Bearer <your_token>`)
- **核心变更**: 
    1. 请求体需设置 `"stream": true`。
    2. 响应类型为 `text/event-stream`。

## 2. 请求格式 (Request Payload)

前端发起对话时的 JSON 结构：

```json
{
  "sessionId": "string", // 会话唯一标识
  "message": "string",   // 用户输入内容
  "stream": true,        // 必须为 true 以开启流式模式
  "context": {           // 可选：上下文信息
    "node": "string",    // 正在分析的节点名
    "agent": "string"    // 助手名称
  }
}
```

## 3. 响应协议 (SSE 规范)

后端通过流式输出分块返回数据。每一行数据必须以 `data: ` 开头，并包含一个 JSON 字符串。

### 响应头 (Headers)
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

### 数据分块格式 (Data Format)
每一条 `data` 都是增量片段：

```text
data: {"content": "正在", "reasoning": ""}
data: {"content": "分析", "reasoning": ""}
data: {"content": "日志", "reasoning": "用户询问了故障原因..."}
data: {"content": "...", "reasoning": "..."}
```

- **`content`**: AI 生成的正文内容片段（追加模式）。
- **`reasoning`**: AI 的推理过程片段（DeepSeek R1 模型专用，追加模式）。

## 4. 前端对接建议 (JavaScript 示例)

由于 `POST` 请求无法直接使用原生 `EventSource`，建议使用 `fetch` 的 `ReadableStream`：

```javascript
async function startChatStream(payload) {
  const response = await fetch('/api/v1/ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.substring(6);
        try {
          const data = JSON.parse(jsonStr);
          // 更新 UI：将 data.content 追加到正文，data.reasoning 追加到推理区
          updateUI(data.content, data.reasoning);
        } catch (e) {
          console.error("Error parsing SSE data", e);
        }
      }
    }
  }
}
```

## 5. 注意事项

1. **追加显示**: `content` 和 `reasoning` 返回的是**增量**，前端需使用 `+=` 拼接字符串。
2. **推理区展示**: DeepSeek R1 会输出推理过程（`reasoning`），建议在 UI 上专门开辟一个“思考过程”区域展示。
3. **异常处理**: 如果流中断或返回非 200 状态码，请及时给用户报错提示。
4. **结束标志**: 当流读取完毕（`done: true`）时，表示对话结束。
