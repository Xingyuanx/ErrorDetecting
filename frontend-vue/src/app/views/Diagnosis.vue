<template>
  <div class="diagnosis-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">故障诊断</h2>
        <p class="page-subtitle">基于多智能体协作的自动化故障分析与辅助修复</p>
      </div>
    </div>

    <!-- 集群与节点选择 -->
    <el-card class="selection-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">集群与节点选择</span>
        </div>
      </template>
      <el-scrollbar>
        <div class="cluster-groups-wrapper">
          <div v-for="g in filteredGroups" :key="g.id" class="cluster-group">
            <el-button
              :type="g.open ? 'primary' : ''"
              @click="toggleGroup(g)"
              class="cluster-toggle"
            >
              <el-icon class="icon-mr">
                <ArrowDown v-if="g.open" />
                <ArrowRight v-else />
              </el-icon>
              {{ g.name }}
            </el-button>
            <div v-if="g.open" class="node-list">
              <el-button
                v-for="n in nodesForGroup(g)"
                :key="n.name"
                size="small"
                :type="selectedNode === n.name ? 'primary' : ''"
                :plain="selectedNode !== n.name"
                class="node-item"
                @click="selectNode(n.name)"
              >
                <span class="status-dot icon-mr" :class="statusDot(n)"></span>
                {{ n.name }}
              </el-button>
            </div>
          </div>
        </div>
      </el-scrollbar>
      <div class="selection-tip">请选择集群或节点以显示相关日志</div>
    </el-card>

    <el-row :gutter="16" class="main-content">
      <!-- 日志预览 -->
      <el-col :xs="24" :lg="12" class="mb-4-mobile">
        <el-card class="log-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">日志预览</span>
              <el-tag v-if="selectedNode" size="small" type="info">当前节点: {{ selectedNode }}</el-tag>
            </div>
          </template>

          <div v-if="!selectedNode" class="empty-preview">
            请选择集群或节点，预览日志内容
          </div>
          <div v-else class="log-preview-container">
            <div class="filter-bar">
              <el-select v-model="filters.level" placeholder="日志级别" size="small" clearable style="width: 100px;">
                <el-option label="INFO" value="info" />
                <el-option label="WARN" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
              <el-select v-model="filters.timeRange" placeholder="时间范围" size="small" clearable style="width: 120px;">
                <el-option label="最近1小时" value="1h" />
                <el-option label="最近6小时" value="6h" />
                <el-option label="最近24小时" value="24h" />
                <el-option label="最近7天" value="7d" />
              </el-select>
            </div>
            
            <el-table :data="previewLogs" size="small" stripe height="100%" class="log-table" header-cell-class-name="table-header">
              <el-table-column prop="time" label="时间" width="100">
                <template #default="{ row }">
                  {{ row.time.split("T")[1] || row.time }}
                </template>
              </el-table-column>
              <el-table-column prop="level" label="级别" width="80">
                <template #default="{ row }">
                  <el-tag :type="getLevelType(row.level)" size="small" effect="dark">
                    {{ row.level.toUpperCase() }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="source" label="来源" width="120" show-overflow-tooltip class-name="u-hidden-mobile" />
              <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 智能助手 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chat-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">诊断助手</span>
              <div class="agent-selectors">
                <el-select v-model="agent" size="small" style="width: 110px;">
                  <el-option label="诊断智能体" value="诊断智能体" />
                </el-select>
                <el-select v-model="model" size="small" style="width: 180px;">
                  <el-option label="DeepSeek-V3" value="deepseek-ai/DeepSeek-V3" />
                  <el-option label="DeepSeek-R1" value="Pro/deepseek-ai/DeepSeek-R1" />
                </el-select>
              </div>
            </div>
          </template>

          <div class="chat-container">
            <div class="chat-history" ref="chatHistory">
              <div
                v-for="(m, i) in visibleMessages"
                :key="'msg-' + i"
                class="chat-item"
                :class="m.role === 'user' ? 'chat-item-user' : 'chat-item-assistant'"
              >
                <div class="chat-role">
                  {{ roleLabel(m.role) }}
                </div>
                <div class="chat-content">
                  <div v-if="m.reasoning" class="reasoning-container">
                    <el-collapse>
                      <el-collapse-item title="推理过程">
                        <pre class="reasoning-text">{{ m.reasoning }}</pre>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                  <div class="message-text">{{ m.content }}</div>
                </div>
              </div>
            </div>

            <!-- 快速置底按钮 -->
            <transition name="el-fade-in">
              <el-button
                v-if="showScrollBottom"
                class="scroll-bottom-btn"
                type="primary"
                circle
                @click="scrollToBottom(true)"
              >
                <el-icon><ArrowDown /></el-icon>
              </el-button>
            </transition>

            <div v-if="err" class="chat-error">
              <el-alert :title="err" type="error" show-icon @close="err = ''" />
            </div>

            <div class="chat-input-area">
              <el-input
                v-model="inputMsg"
                type="textarea"
                :rows="3"
                placeholder="支持Markdown输入... Enter 发送，Shift + Enter 换行"
                :disabled="sending"
                @keydown.enter.exact.prevent="send()"
              />
              <div class="input-actions">
                <div class="option-checks">
                  <el-checkbox v-model="useWebSearch" label="联网搜索" size="small" />
                  <el-checkbox v-model="useClusterOps" label="集群操作" size="small" />
                </div>
                <div class="button-group">
                  <el-button v-if="!sending" type="primary" @click="send()" :disabled="!inputMsg.trim()">
                    发送
                  </el-button>
                  <el-button v-else type="danger" plain @click="stopGeneration()">
                    停止
                  </el-button>
                  <el-button type="warning" plain @click="diagnose()" :disabled="sending">
                    深度诊断
                  </el-button>
                  <el-button type="info" plain @click="generateReport()" :disabled="sending">
                    状态报告
                  </el-button>
                </div>
              </div>
              <div v-if="sending" class="sending-progress">
                <div class="progress-label">正在生成回复...</div>
                <el-progress :percentage="60" :indeterminate="true" :show-text="false" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { ClusterService } from "../api/cluster.service";
import { NodeService } from "../api/node.service";
import { LogService } from "../api/log.service";
import { DiagnosisService } from "../api/diagnosis.service";
import { useAuthStore } from "../stores/auth";
import { ArrowDown, ArrowRight } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

const kw = ref("");
const agent = ref("诊断智能体");
const model = ref("deepseek-ai/DeepSeek-V3");
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
const selectedNode = ref("");

const selectedClusterUuid = computed(() => {
  if (!selectedNode.value) return "";
  const group = groups.find((g) =>
    g.nodes.some((n) => n.name === selectedNode.value)
  );
  return group ? group.uuid : "";
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
    const list = await ClusterService.list();
    const mapped: Group[] = list
      .map((x: any) => ({
        id: String(x.uuid || x.id || x.host || x.name || ""),
        uuid: String(x.uuid || x.id || ""),
        name: String(x.host || x.name || x.uuid || ""),
        open: false,
        nodes: [],
        count: Number(x.count) || 0,
      }))
      .filter((g: any) => g.id && g.name);
    groups.splice(0, groups.length, ...mapped);
  } catch (e: any) {
    err.value = e.friendlyMessage || formatError(e, "集群列表加载失败");
  } finally {
    loadingSidebar.value = false;
  }
}

async function loadNodesFor(clusterUuid: string) {
  const g = groups.find((x) => x.uuid === clusterUuid);
  if (!g) return;
  const clusterName = g.name;
  try {
    const nodes = await NodeService.listByCluster(clusterUuid);
    const mappedNodes = nodes
          .map((x: any) => ({
            name: String(x?.name || x),
            status: x?.status || "running",
          }))
          .filter((x: any) => x.name);
    if (mappedNodes.length) g.nodes = mappedNodes;
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
    err.value = e.friendlyMessage || formatError(e, "节点列表加载失败");
  }
}

async function toggleGroup(g: Group) {
  g.open = !g.open;
  if (g.open && g.nodes.length === 0) await loadNodesFor(g.uuid);
}

function selectNode(n: string) {
  selectedNode.value = n;
}

function statusDot(n: { name: string; status: string }) {
  if (n.status === "running") return "status-dot-running";
  if (n.status === "warning") return "status-dot-warning";
  if (n.status === "error") return "status-dot-error";
  return n.name.includes("003")
    ? "status-dot-error"
    : n.name.includes("002")
    ? "status-dot-warning"
    : "status-dot-running";
}

function getLevelType(level: string) {
  switch (level.toLowerCase()) {
    case 'error': return 'danger';
    case 'warning':
    case 'warn': return 'warning';
    case 'info': return 'info';
    case 'success': return 'success';
    default: return 'info';
  }
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
    const { items } = await LogService.list(params);
    previewLogs.value = items.map((d: any, i: number) => ({
      id: d.log_id || d.id || i,
      time: d.log_time || d.time || d.timestamp || new Date().toISOString(),
      level: String(d.level || "info").toLowerCase(),
      source: String(d.title || d.source || d.node_host || d.node || d.host || ""),
      message: d.info || d.message || "",
    }));
  } catch (e: any) {
    previewLogs.value = [];
  }
}

let refreshTimer: any = null;
function startRefresh() {
  stopRefresh();
  refreshTimer = setInterval(() => {
    if (selectedNode.value && !sending.value) {
      loadPreviewLogs();
    }
  }, 5000);
}
function stopRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
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
  { role: "assistant", content: "请在左侧选择节点并开始诊断" },
]);

const visibleMessages = computed(() =>
  messages.value.filter((m) => m.role !== "system")
);

const chatHistory = ref<HTMLElement | null>(null);
const showScrollBottom = ref(false);

function handleScroll() {
  if (!chatHistory.value) return;
  const { scrollTop, scrollHeight, clientHeight } = chatHistory.value;
  showScrollBottom.value = scrollHeight - scrollTop - clientHeight > 200;
}

function scrollToBottom(smooth = true) {
  nextTick(() => {
    if (chatHistory.value) {
      chatHistory.value.scrollTo({
        top: chatHistory.value.scrollHeight,
        behavior: smooth ? "smooth" : "auto",
      });
    }
  });
}

function scrollToLatest() {
  scrollToBottom(true);
}

const inputMsg = ref("");
const sending = ref(false);
const err = ref("");
let abortController: AbortController | null = null;

function stopGeneration() {
  if (abortController) {
    abortController.abort();
    abortController = null;
    sending.value = false;
  }
}

const useWebSearch = ref(false);
const useClusterOps = ref(true);

function sessionIdOf() {
  return selectedNode.value
    ? `diagnosis-${selectedNode.value}`
    : "diagnosis-global";
}

function roleLabel(r: string) {
  return r === "assistant" ? "诊断智能体" : r === "user" ? "我" : "系统";
}

async function loadHistory() {
  err.value = "";
  try {
    const r = await DiagnosisService.getHistory(sessionIdOf());
    const list = Array.isArray(r?.messages) ? r.messages : [];
    messages.value = list.map((m: any) => ({
      role: m.role || "assistant",
      content: String(m.content || ""),
      reasoning: m.reasoning || m.reasoning_content,
    }));
    await nextTick();
    scrollToLatest();
  } catch (e: any) {
    err.value = e.friendlyMessage || formatError(e, "历史记录加载失败");
  }
}

async function send() {
  const msg = inputMsg.value.trim();
  if (!msg) return;
  sending.value = true;
  err.value = "";
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
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
      },
      body: JSON.stringify({
        sessionId: sessionIdOf(),
        message: msg,
        stream: true,
        context: {
          webSearch: useWebSearch.value,
          clusterOps: useClusterOps.value,
          agent: agent.value,
          node: selectedNode.value || "",
          cluster: selectedClusterUuid.value || "",
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

    inputMsg.value = "";

    let buffer = "";
    let hasReceivedContent = false;

    while (true) {
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
            assistantMsg.reasoning += (data.reasoning || data.reasoning_content);
            hasReceivedContent = true;
          }
          await nextTick();
          scrollToLatest();
        } catch (e) {
          console.error("解析流数据失败", e, jsonStr);
        }
      }
    }

    if (!hasReceivedContent) {
      err.value = "后端已响应但未返回任何有效诊断内容。";
      messages.value.pop();
    }
  } catch (e: any) {
    if (e.name === 'AbortError') return;
    err.value = e.friendlyMessage || formatError(e, "消息发送失败");
    messages.value.pop();
  } finally {
    sending.value = false;
  }
}

async function diagnose() {
  if (!selectedNode.value) {
    ElMessage.warning("请先在左侧选择一个节点进行诊断");
    return;
  }
  
  const group = groups.find(g => g.nodes.some(n => n.name === selectedNode.value));
  if (!group) {
    ElMessage.error("无法确定节点所属集群");
    return;
  }

  sending.value = true;
  err.value = "";
  
  try {
    const res = await DiagnosisService.diagnoseRepair({
      cluster: group.uuid,
      model: model.value,
      auto: true,
      maxSteps: 3
    });
    
    messages.value.push({
      role: "assistant",
      content: `深度诊断已完成：\n${res.summary || res.message || "诊断完成，请查看报告。"}`
    });
    
    await nextTick();
    scrollToLatest();
  } catch (e: any) {
    err.value = e.friendlyMessage || formatError(e, "深度诊断请求失败");
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

watch(chatHistory, (newVal) => {
  if (newVal) {
    newVal.addEventListener("scroll", handleScroll);
  }
});

onMounted(async () => {
  await loadClusters();
  await loadHistory();
  startRefresh();
  // 如果已经有对话，初始化时置底
  scrollToBottom(false);
});

onUnmounted(() => {
  stopRefresh();
  if (chatHistory.value) {
    chatHistory.value.removeEventListener("scroll", handleScroll);
  }
});

watch(selectedNode, () => {
  loadHistory();
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

function formatError(e: any, def: string) {
  if (e instanceof Error && !(e as any).response) {
    return e.message || "网络请求异常";
  }
  const r = e?.response;
  const s = r?.status;
  const d = r?.data;
  const detail = typeof d?.detail === "string" ? d.detail : "";
  const msgs: string[] = [];
  if (s) msgs.push(`HTTP ${s}`);
  if (detail) msgs.push(detail);
  if (!msgs.length) msgs.push(r ? def : "网络连接异常");
  return msgs.join(" | ");
}
</script>

<style scoped>
.diagnosis-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 120px);
}

/* 桌面端特有样式：固定高度，内部滚动 */
@media (min-width: 1025px) {
  .diagnosis-container {
    height: calc(100vh - 110px); /* 稍微调高一点，增加展示空间 */
    min-height: unset;
    overflow: hidden;
    padding-bottom: 4px;
  }

  .selection-card {
    flex-shrink: 0;
    margin-bottom: 0;
  }

  :deep(.selection-card .el-card__body) {
    padding: 8px 16px;
  }

  .main-content {
    flex: 1;
    min-height: 0;
    margin-bottom: 0 !important;
  }

  .main-content :deep(.el-col) {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* 调整卡片 body，确保内容区撑满 */
  .log-card, .chat-card {
    height: 100%;
    overflow: hidden;
  }
}

@media (max-width: 768px) {
  .diagnosis-container {
    height: auto;
    min-height: unset;
  }
  .mb-4-mobile {
    margin-bottom: 16px;
  }
  .log-card, .chat-card {
    height: 500px !important;
  }
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin: 0;
}

.page-subtitle {
  color: var(--app-text-secondary);
  font-size: 14px;
  margin: 4px 0 0 0;
}

.header-badge {
  font-weight: 500;
}

.selection-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
}

.cluster-groups-wrapper {
  display: flex;
  gap: 16px;
  padding-bottom: 8px;
}

.cluster-group {
  flex-shrink: 0;
}

.cluster-toggle {
  font-weight: 500;
}

.icon-mr {
  margin-right: 8px;
}

.node-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.node-item {
  justify-content: flex-start;
  margin: 0 !important;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot-running { background-color: var(--el-color-success); }
.status-dot-warning { background-color: var(--el-color-warning); }
.status-dot-error   { background-color: var(--el-color-danger); }

.selection-tip {
  font-size: 12px;
  color: var(--app-text-secondary);
  margin-top: 8px;
}

.main-content {
  flex: 1;
  min-height: 0;
}

.log-card, .chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
}

:deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.empty-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--app-text-secondary);
  font-size: 14px;
}

.log-preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.log-table {
  flex: 1;
}

.agent-selectors {
  display: flex;
  gap: 8px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative; /* 为置底按钮提供定位参考 */
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
  padding-right: 4px;
}

.scroll-bottom-btn {
  position: absolute;
  right: 20px;
  bottom: 180px; /* 位于输入框上方 */
  z-index: 10;
  box-shadow: var(--el-box-shadow);
  transition: transform var(--el-transition-duration), opacity var(--el-transition-duration);
}

.scroll-bottom-btn:hover {
  transform: translateY(-2px);
}

.scroll-bottom-btn:active {
  transform: translateY(0);
}

/* 移动端适配：调整按钮位置 */
@media (max-width: 768px) {
  .scroll-bottom-btn {
    right: 15px;
    bottom: 200px;
  }
}

.chat-item {
  margin-bottom: 20px;
}

.chat-role {
  font-size: 12px;
  color: var(--app-text-secondary);
  margin-bottom: 4px;
}

.chat-item-user .chat-role {
  text-align: right;
}

.chat-content {
  padding: 12px;
  border-radius: 8px;
  background-color: var(--app-card-bg);
  border: 1px solid var(--app-border-color);
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.chat-item-user .chat-content {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
}

.reasoning-container {
  margin-bottom: 8px;
}

.reasoning-text {
  font-size: 12px;
  color: var(--app-text-secondary);
  background-color: var(--app-content-bg);
  padding: 8px;
  border-radius: 4px;
  white-space: pre-wrap;
  margin: 0;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-error {
  margin-bottom: 12px;
}

.chat-input-area {
  flex-shrink: 0;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.option-checks {
  display: flex;
  gap: 16px;
}

.button-group {
  display: flex;
  gap: 8px;
}

.sending-progress {
  margin-top: 12px;
}

.progress-label {
  font-size: 12px;
  color: var(--app-text-secondary);
  margin-bottom: 4px;
}

:deep(.table-header) {
  background-color: var(--app-content-bg) !important;
  color: var(--app-text-secondary);
  font-weight: 600;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .agent-selectors {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .agent-selectors :deep(.el-select) {
    flex: 1;
    min-width: 120px;
  }

  .input-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .option-checks {
    width: 100%;
    justify-content: flex-start;
  }

  .button-group {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .button-group .el-button {
    flex: 1;
    margin: 0 !important;
    min-width: 80px;
  }

  .mb-4-mobile {
    margin-bottom: 16px;
  }
}

/* 滚动条美化 */
.chat-history::-webkit-scrollbar {
  width: 6px;
}
.chat-history::-webkit-scrollbar-thumb {
  background-color: var(--app-border-color);
  border-radius: 3px;
}
.chat-history::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>
