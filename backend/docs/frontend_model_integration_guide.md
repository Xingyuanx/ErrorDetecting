# 前端模型联调指南 (V3 & R1)

本文档旨在指导前端开发人员如何通过 API 调用不同的 LLM 模型（DeepSeek-V3 和 DeepSeek-R1）。

---

## 1. 模型标识符说明

在调用 API 时，请使用以下字符串作为模型标识：

| 模型名称 | 标识符 (API 传参值) | 适用场景 |
| :--- | :--- | :--- |
| **DeepSeek-V3** | `deepseek-ai/DeepSeek-V3` | 普通对话、通用问答、响应速度快。 |
| **DeepSeek-R1** | `Pro/deepseek-ai/DeepSeek-R1` | 复杂逻辑推理、深度故障诊断、代码生成。 |

---

## 2. 接口调用方式

### 2.1 AI 聊天接口 (`/api/v1/ai/chat`)

前端需要在请求体的 `context` 对象中传入 `model` 字段。

#### 请求示例 (TypeScript/Fetch):
```typescript
const response = await fetch('/api/v1/ai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify({
    sessionId: "current-chat-id",
    message: "如何解决 NameNode 处于安全模式？",
    stream: true, // 建议开启流式
    context: {
      model: "Pro/deepseek-ai/DeepSeek-R1", // 切换模型
      agent: "HadoopExpert"
    }
  })
});
```

#### 响应处理 (SSE 流式):
当 `stream: true` 时，响应格式为 SSE (Server-Sent Events)。每一行 `data` 是一个 JSON 字符串，包含 `content` (正文) 和 `reasoning` (思维链，仅 R1 支持)。

```javascript
// 处理逻辑示例
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = new TextDecoder().decode(value);
  const lines = chunk.split('\n');
  lines.forEach(line => {
    if (line.startsWith('data: ')) {
      const { content, reasoning } = JSON.parse(line.slice(6));
      if (reasoning) updateReasoningUI(reasoning); // 更新思考过程 UI
      if (content) updateContentUI(content);       // 更新正文 UI
    }
  });
}
```

---

## 3. 故障诊断与自动修复接口 (`/api/v1/ai/diagnose-repair`)

对于自动诊断任务，模型参数直接放在请求体根部。

#### 请求示例:
```bash
curl -X POST http://localhost:8000/api/v1/ai/diagnose-repair \
-H "Content-Type: application/json" \
-d '{
  "cluster": "cluster-uuid-123",
  "model": "Pro/deepseek-ai/DeepSeek-R1",
  "auto": true,
  "maxSteps": 3
}'
```

---

## 4. 注意事项

1.  **默认模型**: 如果前端不传递 `model` 参数，后端将使用 `.env` 文件中配置的 `LLM_MODEL` (目前默认为 V3)。
2.  **R1 推理过程**: DeepSeek-R1 会输出 `reasoning_content`。前端建议提供一个可折叠的“思考过程”组件，用来展示 `reasoning` 字段的内容，以增强用户体验。
3.  **错误处理**: 若传入无效的模型名称，后端可能会返回 `403` 或 `502` 错误，请前端做好兜底逻辑。
