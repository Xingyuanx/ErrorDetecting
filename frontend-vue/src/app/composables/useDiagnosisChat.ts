import { computed, nextTick, reactive, ref, type Ref } from "vue";
import type { ClusterGroup } from "./useClusterTree";
import { DiagnosisService } from "../api/diagnosis.service";
import { ElMessage } from "element-plus";

type Message = { role: "user" | "assistant" | "system"; content: string; reasoning?: string };

export function useDiagnosisChat(options: {
  authToken: Ref<string | null>;
  agent: Ref<string>;
  model: Ref<string>;
  selectedNode: Ref<string>;
  selectedClusterUuid: Ref<string>;
  groups: ClusterGroup[];
  useWebSearch: Ref<boolean>;
  useClusterOps: Ref<boolean>;
  setError: (e: any, def: string) => void;
  clearError: () => void;
  scrollToLatest: () => void;
}) {
  const messages = ref<Message[]>([
    { role: "system", content: "欢迎使用多智能体诊断面板" },
    { role: "assistant", content: "请在左侧选择节点并开始诊断" },
  ]);
  const visibleMessages = computed(() => messages.value.filter((m) => m.role !== "system"));

  const inputMsg = ref("");
  const sending = ref(false);
  let abortController: AbortController | null = null;

  function stopGeneration() {
    if (abortController) {
      abortController.abort();
      abortController = null;
      sending.value = false;
    }
  }

  function sessionIdOf() {
    return options.selectedNode.value ? `diagnosis-${options.selectedNode.value}` : "diagnosis-global";
  }

  async function loadHistory() {
    options.clearError();
    try {
      const r = await DiagnosisService.getHistory(sessionIdOf());
      const list = Array.isArray(r?.messages) ? r.messages : [];
      messages.value = list.map((m: any) => ({
        role: m.role || "assistant",
        content: String(m.content || ""),
        reasoning: m.reasoning || m.reasoning_content,
      }));
      await nextTick();
      options.scrollToLatest();
    } catch (e: any) {
      options.setError(e, "历史记录加载失败");
    }
  }

  async function send() {
    const msg = inputMsg.value.trim();
    if (!msg) return;
    sending.value = true;
    options.clearError();
    abortController = new AbortController();

    const userMsg = { role: "user" as const, content: msg };
    messages.value.push(userMsg);

    const assistantMsg = reactive({ role: "assistant" as const, content: "", reasoning: "" });
    messages.value.push(assistantMsg);

    try {
      const response = await fetch("/api/v1/ai/chat", {
        method: "POST",
        signal: abortController.signal,
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "Cache-Control": "no-cache",
          ...(options.authToken.value ? { Authorization: `Bearer ${options.authToken.value}` } : {}),
        },
        body: JSON.stringify({
          sessionId: sessionIdOf(),
          message: msg,
          stream: true,
          context: {
            webSearch: options.useWebSearch.value,
            clusterOps: options.useClusterOps.value,
            agent: options.agent.value,
            node: options.selectedNode.value || "",
            cluster: options.selectedClusterUuid.value || "",
            model: options.model.value,
          },
        }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error("无法读取响应流");

      inputMsg.value = "";

      let buffer = "";
      let hasReceivedContent = false;

      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;

          const jsonStr = trimmed.slice(6);
          if (jsonStr === "[DONE]") break;

          try {
            const data = JSON.parse(jsonStr);
            const text = data.content || data.reply || data.message || "";
            if (text) {
              assistantMsg.content += text;
              hasReceivedContent = true;
            }
            if (data.reasoning || data.reasoning_content) {
              assistantMsg.reasoning += data.reasoning || data.reasoning_content;
              hasReceivedContent = true;
            }
            await nextTick();
            options.scrollToLatest();
          } catch (e) {
            console.error("解析流数据失败", e, jsonStr);
          }
        }
      }

      if (!hasReceivedContent) {
        options.setError({ friendlyMessage: "后端已响应但未返回任何有效诊断内容。" }, "消息发送失败");
        messages.value.pop();
      }
    } catch (e: any) {
      if (e.name === "AbortError") return;
      options.setError(e, "消息发送失败");
      messages.value.pop();
    } finally {
      sending.value = false;
    }
  }

  async function diagnose() {
    if (!options.selectedNode.value) {
      ElMessage.warning("请先在左侧选择一个节点进行诊断");
      return;
    }

    const group = options.groups.find((g) => g.nodes.some((n) => n.name === options.selectedNode.value));
    if (!group) {
      ElMessage.error("无法确定节点所属集群");
      return;
    }

    sending.value = true;
    options.clearError();

    try {
      const res = await DiagnosisService.diagnoseRepair({
        cluster: group.uuid,
        model: options.model.value,
        auto: true,
        maxSteps: 3,
      });

      messages.value.push({
        role: "assistant",
        content: `深度诊断已完成：\n${res.summary || res.message || "诊断完成，请查看报告。"}`,
      });

      await nextTick();
      options.scrollToLatest();
    } catch (e: any) {
      options.setError(e, "深度诊断请求失败");
    } finally {
      sending.value = false;
    }
  }

  async function generateReport() {
    inputMsg.value =
      inputMsg.value ||
      `请根据当前节点${options.selectedNode.value || "（未选定）"}最近关键日志生成一份状态报告（包含症状、影响范围、根因假设与建议）。`;
    await send();
  }

  return {
    messages,
    visibleMessages,
    inputMsg,
    sending,
    stopGeneration,
    loadHistory,
    send,
    diagnose,
    generateReport,
  };
}
