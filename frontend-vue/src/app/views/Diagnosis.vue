<template>
  <section class="layout__section">
    <div class="layout__page-header diag-header">
      <div class="diag-title">
        <h2 class="layout__page-title">故障诊断</h2>
      </div>
    </div>
    <div class="diag-layout">
      <aside class="diag-sidebar">
        <div class="diag-filter">
          <form class="diag-filter-grid">
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700"
                >日志级别</label
              >
              <select
                v-model="filters.level"
                class="u-w-full u-p-2 u-border u-rounded u-mt-1"
              >
                <option value="">全部级别</option>
                <option value="debug">DEBUG</option>
                <option value="info">INFO</option>
                <option value="warn">WARN</option>
                <option value="error">ERROR</option>
              </select>
            </div>
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700"
                >来源集群</label
              >
              <select
                v-model="filters.cluster"
                class="u-w-full u-p-2 u-border u-rounded u-mt-1"
              >
                <option value="">全部集群</option>
                <option v-for="c in clusterOptions" :key="c" :value="c">
                  {{ c }}
                </option>
              </select>
            </div>
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700"
                >来源节点</label
              >
              <select
                v-model="filters.node"
                class="u-w-full u-p-2 u-border u-rounded u-mt-1"
              >
                <option value="">全部节点</option>
                <option v-for="n in nodesOptions" :key="n" :value="n">
                  {{ n }}
                </option>
              </select>
            </div>
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700"
                >时间范围</label
              >
              <select
                v-model="filters.timeRange"
                class="u-w-full u-p-2 u-border u-rounded u-mt-1"
              >
                <option value="">全部时间</option>
                <option value="1h">最近1小时</option>
                <option value="6h">最近6小时</option>
                <option value="24h">最近24小时</option>
                <option value="7d">最近7天</option>
              </select>
            </div>
            <div class="filter-actions">
              <button type="button" class="btn btn-link" @click="clearFilters">
                清除筛选
              </button>
            </div>
          </form>
          <div class="u-text-sm u-text-gray-700 u-mt-2">
            {{ filterSummary }}
          </div>
        </div>
        <div class="diag-group" v-for="g in filteredGroups" :key="g.id">
          <button
            class="diag-group-toggle"
            type="button"
            @click="toggleGroup(g)"
          >
            <span
              :class="['chev', g.open ? 'chev--down' : 'chev--right']"
            ></span>
            {{ g.name }}
          </button>
          <ul v-show="g.open" class="diag-node-list">
            <li
              v-for="n in nodesForGroup(g)"
              :key="n.name"
              :class="[
                'diag-node-item',
                selectedNode === n.name ? 'diag-node-item--active' : '',
              ]"
              @click="selectNode(n.name)"
            >
              <span class="status-dot" :class="statusDot(n)"></span>
              {{ n.name }}
            </li>
          </ul>
        </div>
        <div class="diag-tabs">
          <button
            :class="['btn', tab === 'live' ? 'btn--primary' : '']"
            type="button"
            @click="tab = 'live'"
          >
            实时日志
          </button>
          <button
            :class="['btn', tab === 'auto' ? 'btn--primary' : '']"
            type="button"
            @click="tab = 'auto'"
          >
            自动刷新中
          </button>
        </div>
        <div class="diag-tip">请选择集群或节点以显示相关日志</div>
        <article class="layout__card u-mt-2">
          <div class="layout__card-header">
            <h3 class="layout__card-title">故障信息</h3>
          </div>
          <div class="layout__card-body">
            <div class="fault-row">
              <span class="fault-key">故障代码</span
              ><span class="fault-val">{{ fault?.code || "—" }}</span>
            </div>
            <div class="fault-row">
              <span class="fault-key">发生时间</span
              ><span class="fault-val">{{ fault?.time || "—" }}</span>
            </div>
            <div class="fault-row">
              <span class="fault-key">影响范围</span
              ><span class="fault-val">{{ fault?.scope || "—" }}</span>
            </div>
            <div class="u-text-sm u-text-error u-mt-1" v-if="faultErr">
              {{ faultErr }}
            </div>
          </div>
        </article>
      </aside>

      <aside class="diag-preview">
        <article class="layout__card">
          <div class="layout__card-header">
            <h3 class="layout__card-title">日志预览</h3>
          </div>
          <div class="layout__card-body">
            <div v-if="!selectedNode" class="preview-placeholder">
              请选择左侧的集群或节点，预览日志内容
            </div>
            <div v-else>
              <div class="preview-meta">
                当前节点：<strong>{{ selectedNode }}</strong>
              </div>
              <div class="u-overflow-x-auto u-mt-2">
                <table class="dashboard__table">
                  <thead class="dashboard__table-head">
                    <tr>
                      <th>时间</th>
                      <th>级别</th>
                      <th>来源</th>
                      <th>消息</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      class="dashboard__table-row"
                      v-for="l in previewLogs"
                      :key="l.id"
                    >
                      <td>
                        <time :datetime="l.time">{{
                          l.time.split("T")[1] || l.time
                        }}</time>
                      </td>
                      <td class="u-font-medium">{{ l.level.toUpperCase() }}</td>
                      <td>
                        <code>{{ l.source }}</code>
                      </td>
                      <td>{{ l.message }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </article>
      </aside>

      <aside class="diag-assistant">
        <article class="layout__card">
          <div class="layout__card-body">
            <div class="assist-row u-mb-2">
              <div class="assist-field">
                <label class="u-text-sm u-font-medium u-text-gray-700"
                  >智能体</label
                >
                <select
                  v-model="agent"
                  class="u-w-full u-p-2 u-border u-rounded u-mt-1"
                >
                  <option value="诊断智能体">诊断智能体</option>
                </select>
              </div>
              <div class="assist-field">
                <label class="u-text-sm u-font-medium u-text-gray-700"
                  >模型</label
                >
                <select
                  v-model="model"
                  class="u-w-full u-p-2 u-border u-rounded u-mt-1"
                >
                  <option value="deepseek">deepseek</option>
                </select>
              </div>
            </div>
          </div>
          <div class="layout__card-header">
            <h3 class="layout__card-title">对话历史</h3>
          </div>
          <div class="layout__card-body">
            <div class="chat-history" ref="chatHistory">
              <div
                class="chat-item"
                :class="
                  m.role === 'assistant'
                    ? 'chat-item--assistant'
                    : m.role === 'user'
                    ? 'chat-item--user'
                    : ''
                "
                v-for="(m, i) in visibleMessages"
                :key="'msg-' + i"
              >
                <div class="chat-role">{{ roleLabel(m.role) }}</div>
                <div class="chat-text">
                  <details v-if="m.reasoning" class="u-mb-2">
                    <summary>推理过程</summary>
                    <pre style="white-space: pre-wrap">{{ m.reasoning }}</pre>
                  </details>
                  <div>{{ m.content }}</div>
                </div>
              </div>
            </div>
            <textarea
              class="chat-input"
              v-model="inputMsg"
              :disabled="sending"
              placeholder="支持Markdown输入...&#10;Enter 发送，Shift + Enter 换行"
              @keydown.enter.exact.prevent="send()"
            ></textarea>
            <div class="chat-actions">
              <!-- 工具按钮：左对齐，向上弹出菜单 -->
              <div class="tools-dropdown">
                <button
                  type="button"
                  class="btn btn--secondary"
                  @click="showTools = !showTools"
                >
                  工具
                </button>
                <div v-if="showTools" class="tools-menu">
                  <label class="tools-item">
                    <input type="checkbox" v-model="useWebSearch" />
                    <span>联网搜索</span>
                  </label>
                </div>
              </div>

              <button
                type="button"
                class="btn btn--primary"
                :disabled="sending || !inputMsg.trim()"
                @click="send()"
              >
                发送
              </button>
              <button
                type="button"
                class="btn btn--primary u-ml-1"
                :disabled="sending"
                @click="generateReport()"
              >
                生成状态报告
              </button>
            </div>
            <div class="chat-progress">
              <span>{{ sending ? "正在生成回复..." : "就绪" }}</span>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: sending ? '60%' : '0%' }"
                ></div>
              </div>
            </div>
            <!-- 新增：显眼的错误信息提示区域 -->
            <div v-if="err" class="chat-error-alert">
              <span class="chat-error-icon">⚠️</span>
              <div class="chat-error-content">
                <div class="chat-error-title">诊断助手提示</div>
                <div class="chat-error-msg">{{ err }}</div>
              </div>
              <button class="btn-close" @click="err = ''">×</button>
            </div>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch, onMounted, nextTick } from "vue";
import api from "../lib/api";
import { useAuthStore } from "../stores/auth";
const kw = ref("");
const tab = ref<"live" | "auto">("live");
const agent = ref("诊断智能体");
const model = ref("deepseek");
const filters = reactive<{
  level: string;
  cluster: string;
  node: string;
  opType: string;
  sourceId: string;
  timeRange: string;
}>({
  level: "",
  cluster: "",
  node: "",
  opType: "",
  sourceId: "",
  timeRange: "",
});
type Group = {
  id: string;
  uuid: string;
  name: string;
  open: boolean;
  nodes: Array<{ name: string; status: string }>;
  count?: number;
};
const groups = reactive<Group[]>([]);
const loadingSidebar = ref(false);
type FaultInfo = { code: string; time: string; scope: string };
const fault = ref<FaultInfo | null>(null);
const faultErr = ref("");
const selectedNode = ref("");
const clusterOptions = computed(() => groups.map((g) => g.name));
const nodesOptions = computed(() => {
  if (filters.cluster) {
    const g = groups.find((x) => x.name === filters.cluster);
    return g ? g.nodes.map((n) => n.name) : [];
  }
  return groups.flatMap((g) => g.nodes.map((n) => n.name));
});
const filteredGroups = computed(() => {
  const kraw = kw.value.trim().toLowerCase();
  let base = groups.filter(
    (g) => !filters.cluster || g.name === filters.cluster
  );
  if (kraw) {
    base = base.filter(
      (g) =>
        g.name.toLowerCase().includes(kraw) ||
        g.nodes.some((n) => n.name.toLowerCase().includes(kraw))
    );
  }
  if (filters.node) {
    base = base.filter((g) => g.nodes.some((n) => n.name === filters.node));
  }
  return base;
});
function nodesForGroup(g: Group) {
  const k = kw.value.trim().toLowerCase();
  let nodes = g.nodes;
  if (k)
    nodes = nodes.filter(
      (n) =>
        n.name.toLowerCase().includes(k) || g.name.toLowerCase().includes(k)
    );
  if (filters.node) nodes = nodes.filter((n) => n.name === filters.node);
  return nodes;
}
function pad3(n: number) {
  return String(n).padStart(3, "0");
}
async function loadClusters() {
  loadingSidebar.value = true;
  try {
    const r = await api.get("/v1/clusters", {
      headers: auth.token
        ? { Authorization: `Bearer ${auth.token}` }
        : undefined,
    });
    const list = Array.isArray(r.data?.clusters) ? r.data.clusters : [];
    const mapped: Group[] = list
      .map((x: any) => ({
        id: String(x.uuid || x.id || x.host || x.name || ""),
        uuid: String(x.uuid || x.id || ""),
        name: String(x.host || x.name || x.uuid || ""),
        open: false,
        nodes: [],
        count: Number(x.count) || 0,
      }))
      .filter((g) => g.id && g.name);
    groups.splice(0, groups.length, ...mapped);
  } catch (e: any) {
    // 保持现状并在提示区显示错误
    err.value = formatError(e, "集群列表加载失败");
  } finally {
    loadingSidebar.value = false;
  }
}
async function loadNodesFor(clusterUuid: string) {
  const g = groups.find((x) => x.uuid === clusterUuid);
  if (!g) return;
  const clusterName = g.name;
  try {
    const r = await api.get("/v1/nodes", {
      params: { cluster: clusterUuid },
      headers: auth.token
        ? { Authorization: `Bearer ${auth.token}` }
        : undefined,
    });
    const nodes = Array.isArray(r.data?.nodes)
      ? r.data.nodes
          .map((x: any) => ({
            name: String(x?.name || x),
            status: x?.status || "running",
          }))
          .filter((x: any) => x.name)
      : [];
    if (nodes.length) g.nodes = nodes;
    else if ((g.count || 0) > 0)
      g.nodes = Array.from({ length: g.count as number }, (_, i) => ({
        name: `${clusterName}-${pad3(i + 1)}`,
        status: "running",
      }));
  } catch (e: any) {
    if ((g.count || 0) > 0 && g.nodes.length === 0)
      g.nodes = Array.from({ length: g.count as number }, (_, i) => ({
        name: `${clusterName}-${pad3(i + 1)}`,
        status: "running",
      }));
    // 不打断交互，错误显示在提示区
    err.value = formatError(e, "节点列表加载失败");
  }
}
async function toggleGroup(g: Group) {
  g.open = !g.open;
  if (g.open && g.nodes.length === 0) await loadNodesFor(g.uuid);
}
async function loadFaultInfo() {
  faultErr.value = "";
  fault.value = null;
  const params: any = {};
  if (selectedNode.value) params.node = selectedNode.value;
  else if (filters.cluster) {
    const g = groups.find(x => x.name === filters.cluster);
    params.cluster = g ? g.uuid : filters.cluster;
  }
  try {
    const r = await api.get("/v1/faults/summary", {
      params,
      headers: auth.token
        ? { Authorization: `Bearer ${auth.token}` }
        : undefined,
    });
    const d = r?.data?.fault || r?.data?.data || null;
    if (d)
      fault.value = {
        code: String(d.code || ""),
        time: String(d.time || ""),
        scope: String(d.scope || ""),
      };
  } catch (e: any) {
    faultErr.value = formatError(e, "故障信息加载失败");
  }
}
function selectNode(n: string) {
  selectedNode.value = n;
}
function statusDot(n: { name: string; status: string }) {
  if (n.status === "running") return "status-dot--running";
  if (n.status === "warning") return "status-dot--warning";
  if (n.status === "error") return "status-dot--error";
  // fallback for compatibility
  return n.name.includes("003")
    ? "status-dot--error"
    : n.name.includes("002")
    ? "status-dot--warning"
    : "status-dot--running";
}
const previewLogs = ref<
  Array<{
    id: number;
    time: string;
    level: string;
    source: string;
    message: string;
  }>
>([]);
async function loadPreviewLogs() {
  if (!selectedNode.value) {
    previewLogs.value = [];
    return;
  }
  try {
    const params: any = { node: selectedNode.value, size: 50 };
    if (filters.level) params.level = filters.level;
    if (filters.timeRange) {
      const now = Date.now();
      const r = filters.timeRange;
      const span =
        r === "1h"
          ? 60 * 60 * 1000
          : r === "6h"
          ? 6 * 60 * 60 * 1000
          : r === "24h"
          ? 24 * 60 * 60 * 1000
          : r === "7d"
          ? 7 * 24 * 60 * 60 * 1000
          : 0;
      if (span) params.time_from = new Date(now - span).toISOString();
    }
    const r = await api.get("/v1/logs", {
      params,
      headers: auth.token
        ? { Authorization: `Bearer ${auth.token}` }
        : undefined,
    });
    const items = Array.isArray(r.data?.items)
      ? r.data.items
      : Array.isArray(r.data?.logs)
      ? r.data.logs
      : [];
    previewLogs.value = items.map((d: any, i: number) => ({
      id: d.id || i,
      time: d.time || new Date().toISOString(),
      level: String(d.level || "info").toLowerCase(),
      source: String(d.source || d.node || ""),
      message: d.message || "",
    }));
  } catch (e: any) {
    previewLogs.value = [];
  }
}
const auth = useAuthStore();
const messages = ref<
  Array<{
    role: "user" | "assistant" | "system";
    content: string;
    reasoning?: string;
  }>
>([
  { role: "system", content: "欢迎使用多智能体诊断面板" },
  { role: "assistant", content: "请在左侧选择节点并拖入关键日志作为上下文" },
]);
const visibleMessages = computed(() =>
  messages.value.filter((m) => m.role !== "system")
);
const chatHistory = ref<HTMLElement | null>(null);
function scrollToLatest() {
  const el = chatHistory.value;
  if (el) el.scrollTop = el.scrollHeight;
}
const inputMsg = ref("");
const sending = ref(false);
const err = ref("");

// 工具菜单状态
const showTools = ref(false);
const useWebSearch = ref(false);
function sessionIdOf() {
  return selectedNode.value
    ? `diagnosis-${selectedNode.value}`
    : "diagnosis-global";
}
function roleLabel(r: string) {
  return r === "assistant" ? "诊断智能体" : r === "user" ? "我" : "系统";
}
const filterSummary = computed(() => {
  const items: string[] = [];
  if (filters.level) items.push(`级别=${filters.level.toUpperCase()}`);
  if (filters.cluster) items.push(`集群=${filters.cluster}`);
  if (filters.node) items.push(`节点=${filters.node}`);
  if (filters.timeRange) items.push(`时间=${filters.timeRange}`);
  return items.length ? `当前筛选：${items.join("；")}` : "当前筛选：无";
});
function clearFilters() {
  filters.level = "";
  filters.cluster = "";
  filters.node = "";
  filters.opType = "";
  filters.sourceId = "";
  filters.timeRange = "";
}
async function loadHistory() {
  err.value = "";
  try {
    const r = await api.get("/v1/ai/history", {
      params: { sessionId: sessionIdOf() },
      headers: auth.token
        ? { Authorization: `Bearer ${auth.token}` }
        : undefined,
    });
    const list = Array.isArray(r.data?.messages) ? r.data.messages : [];
    messages.value = list.map((m: any) => ({
      role: m.role || "assistant",
      content: String(m.content || ""),
      reasoning: m.reasoning,
    }));
    await nextTick();
    scrollToLatest();
  } catch (e: any) {
    err.value = formatError(e, "历史记录加载失败");
  }
}
async function send() {
  const msg = inputMsg.value.trim();
  if (!msg) return;
  sending.value = true;
  err.value = "";
  const userMsg = { role: "user" as const, content: msg };
  messages.value.push(userMsg);
  
  // 添加一个空的助手消息占位，用于流式填充内容
  const assistantMsg = reactive({ role: "assistant" as const, content: "", reasoning: "" });
  messages.value.push(assistantMsg);
  
  try {
    const response = await fetch("/api/v1/ai/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
      },
      body: JSON.stringify({
        sessionId: sessionIdOf(),
        message: msg,
        stream: true, // 开启流式模式
        context: {
          webSearch: useWebSearch.value,
          agent: agent.value,
          node: selectedNode.value || "",
          model: model.value,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    if (!reader) throw new Error("无法读取响应流");

    inputMsg.value = ""; // 发送成功后清空输入框

    let buffer = "";
    let hasReceivedContent = false;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      // 最后一项可能是不完整的行，留到下一次处理
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data: ")) continue;
        
        const jsonStr = trimmed.slice(6);
        try {
          const data = JSON.parse(jsonStr);
          if (data.content) {
            assistantMsg.content += data.content;
            hasReceivedContent = true;
          }
          if (data.reasoning) {
            assistantMsg.reasoning += data.reasoning;
            hasReceivedContent = true;
          }
          // 实时滚动到底部
          await nextTick();
          scrollToLatest();
        } catch (e) {
          console.error("解析流数据失败", e, jsonStr);
        }
      }
    }

    // 如果流结束了但没有收到任何内容，说明后端可能没有返回有效回复
    if (!hasReceivedContent) {
      err.value = "后端已响应但未返回任何有效诊断内容。可能原因：模型处理超时、当前上下文无相关日志、或后端逻辑异常。";
      messages.value.pop(); // 移除空的占位消息
    }
  } catch (e: any) {
    err.value = formatError(e, "消息发送失败");
    // 如果失败了，移除占位消息
    messages.value.pop();
  } finally {
    sending.value = false;
  }
}
async function generateReport() {
  inputMsg.value =
    inputMsg.value ||
    `请根据当前节点${
      selectedNode.value || "（未选定）"
    }最近关键日志生成一份状态报告（包含症状、影响范围、根因假设与建议）。`;
  await send();
}
onMounted(async () => {
  await loadClusters();
  await loadHistory();
  await loadFaultInfo();
});
watch(selectedNode, () => {
  loadHistory();
  loadFaultInfo();
  loadPreviewLogs();
});
watch(
  () => filters.level,
  () => {
    loadPreviewLogs();
  }
);
watch(
  () => filters.timeRange,
  () => {
    loadPreviewLogs();
  }
);
watch(
  () => filters.cluster,
  () => {
    loadFaultInfo();
  }
);
function formatError(e: any, def: string) {
  const r = e?.response;
  const s = r?.status;
  const st = r?.statusText;
  const d = r?.data;
  const detail = typeof d?.detail === "string" ? d.detail : "";
  const errs = Array.isArray(d?.detail?.errors) ? d.detail.errors : [];
  const msgs: string[] = [];

  if (s) {
    let prefix = `HTTP ${s}`;
    switch (s) {
      case 400: prefix = "请求无效 (Bad Request)"; break;
      case 401: prefix = "会话已过期，请重新登录"; break;
      case 403: prefix = "无权访问该诊断资源"; break;
      case 404: prefix = "诊断服务接口未找到"; break;
      case 500: prefix = "诊断服务器内部故障"; break;
      case 502: prefix = "网关响应异常，诊断后端可能已掉线"; break;
      case 503: prefix = "诊断服务目前无法处理请求"; break;
      case 504: prefix = "诊断请求处理超时"; break;
      default: if (st) prefix += ` ${st}`;
    }
    msgs.push(prefix);
  }

  if (detail) msgs.push(detail);
  if (errs.length)
    msgs.push(
      errs
        .map((x: any) => x?.message || "")
        .filter(Boolean)
        .join("；")
    );
  if (!msgs.length) msgs.push(r ? def : "网络连接异常，请检查后端服务状态");
  return msgs.join(" | ");
}
</script>

<style scoped>
.diag-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.diag-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
.badge {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--active);
  color: var(--text-primary);
  font-size: 12px;
}
.diag-layout {
  display: grid;
  grid-template-columns: var(--diag-sidebar-width, 30%) 1fr var(
      --diag-assistant-width,
      30%
    );
  gap: 16px;
  align-items: stretch;
}
.diag-sidebar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}
.diag-filter {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.diag-filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}
.diag-filter-grid > div {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.diag-filter-grid label {
  margin-bottom: 4px;
}
.diag-sidebar select {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
.filter-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
.diag-group {
  margin-top: 8px;
}
.diag-group-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--hover);
  color: var(--text-primary);
}
.chev {
  width: 0;
  height: 0;
  border-style: solid;
}
.chev--right {
  border-width: 5px 0 5px 8px;
  border-color: transparent transparent transparent var(--text-muted);
}
.chev--down {
  border-width: 8px 5px 0 5px;
  border-color: var(--text-muted) transparent transparent transparent;
}
.diag-node-list {
  list-style: none;
  padding: 8px 4px;
  margin: 0;
}
.diag-node-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  margin-top: 6px;
  cursor: pointer;
}
.diag-node-item:hover {
  background: var(--hover);
}
.diag-node-item--active {
  background: var(--active);
  border-color: var(--accent);
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-dot--running {
  background: #16a34a;
}
.status-dot--warning {
  background: #f59e0b;
}
.status-dot--error {
  background: #dc2626;
}
.diag-tabs {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
.diag-tip {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 12px;
}
.fault-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px dashed var(--border);
}
.fault-row:last-child {
  border-bottom: none;
}
.fault-key {
  color: var(--text-muted);
  font-size: 12px;
}
.fault-val {
  font-weight: 600;
}

.diag-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.diag-preview .layout__card {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}
.diag-preview .layout__card-body {
  flex: 1;
  overflow: auto;
}
.preview-meta {
  color: var(--text-muted);
  font-size: 12px;
}
.preview-placeholder {
  color: var(--text-muted);
  font-size: 14px;
}
.preview-body {
  background: var(--hover);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-top: 8px;
  flex: 1;
}

.diag-assistant {
  display: flex;
  flex-direction: column;
  margin-right: 16px;
}
.diag-assistant .layout__card {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.diag-assistant .layout__card-body {
  flex: 1;
  overflow: auto;
}
.diag-assistant .layout__card-body:first-of-type {
  flex: 0;
  overflow: visible;
  padding-bottom: 8px;
}
.diag-assistant .layout__card-body:last-of-type {
  flex: 1;
  overflow: auto;
}
.assist-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.assist-field {
  display: flex;
  flex-direction: column;
}
.chat-history {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 360px;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding-right: 4px;
}
.chat-item {
  display: flex;
  gap: 8px;
}
.chat-role {
  width: 72px;
  color: var(--text-muted);
}
.chat-text {
  flex: 1;
  background: var(--hover);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 10px;
  max-width: 100%;
  overflow-x: hidden;
  word-break: break-word;
}
.chat-text * {
  word-break: break-word;
  overflow-wrap: anywhere;
}
.chat-history {
  overflow-x: hidden;
}
.chat-item--assistant .chat-text {
  background: var(--hover);
}
.chat-item--user .chat-text {
  background: var(--active);
  border-color: var(--accent);
}
.chat-input {
  width: 100%;
  min-height: 80px;
  margin-top: 8px;
  padding: 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.2s ease;
  background: var(--surface);
}
.chat-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
  background: #fff;
}
.chat-input:disabled {
  background: var(--hover);
  cursor: not-allowed;
  opacity: 0.7;
}
.chat-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.chat-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
  position: relative;
}
.tools-dropdown {
  margin-right: auto;
  position: relative;
}
.tools-menu {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 120px;
  z-index: 100;
}
.tools-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  padding: 4px 8px;
  border-radius: 4px;
}
.tools-item:hover {
  background: var(--hover);
}
.tools-item input {
  margin: 0;
}
.chat-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  color: var(--text-muted);
}
.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--accent);
}

.layout__card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
}
.layout__card-header {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  background: var(--active);
}
.layout__card-title {
  font-size: 14px;
  font-weight: 700;
}
.layout__card-body {
  padding: 12px;
}
.diag-tabs .btn {
  border-radius: 999px;
  padding: 6px 12px;
}
.diag-tabs .btn--primary {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.diag-group-toggle {
  transition: background 120ms ease, border-color 120ms ease;
}
.diag-group-toggle:hover {
  background: var(--active);
  border-color: var(--accent);
}

@media (max-width: 1024px) {
  .diag-layout {
    grid-template-columns: 1fr;
  }
  .diag-assistant {
    margin-right: 0;
  }
}
@media (max-width: 640px) {
  .diag-filter-grid {
    grid-template-columns: 1fr;
  }
  .assist-row {
    grid-template-columns: 1fr;
  }
  .chat-role {
    width: 56px;
  }
}

/* 新增：聊天错误提示框样式 */
.chat-error-alert {
  margin-top: 12px;
  padding: 12px;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  animation: slideIn 0.3s ease-out;
}
.chat-error-icon {
  font-size: 18px;
  line-height: 1;
}
.chat-error-content {
  flex: 1;
}
.chat-error-title {
  font-weight: 600;
  color: #991b1b;
  font-size: 14px;
  margin-bottom: 2px;
}
.chat-error-msg {
  color: #b91c1c;
  font-size: 13px;
  line-height: 1.4;
}
.btn-close {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 20px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}
.btn-close:hover {
  color: #b91c1c;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
