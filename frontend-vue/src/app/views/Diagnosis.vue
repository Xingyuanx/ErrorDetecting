<template>
  <div class="diagnosis-container" ref="layoutContainer">
    <!-- 展开侧边栏的浮动按钮 -->
    <transition name="el-fade-in">
      <div 
        v-if="isLeftCollapsed" 
        class="expand-trigger" 
        :class="{ 'is-mobile': isMobile }"
        @click="toggleLeftPanel"
      >
        <el-icon><ArrowRight v-if="!isMobile" /><ArrowDown v-else /></el-icon>
      </div>
    </transition>

    <div class="diagnosis-layout" :class="{ 'is-resizing': isResizing }">
      <!-- 左侧面板：包含选择器和日志预览 -->
      <div 
        class="panel-left" 
        :class="{ 'is-collapsed': isLeftCollapsed }"
        :style="isMobile ? { height: leftPanelWidth + '%' } : { width: leftPanelWidth + '%' }"
        ref="leftPanelContainer"
      >
        <div v-if="!isLeftCollapsed" class="left-content-wrapper" :class="{ 'is-resizing-inner': isInnerResizing }">
          <!-- 内部展开按钮 -->
          <transition name="el-fade-in">
            <div 
              v-if="isInnerLeftCollapsed" 
              class="inner-expand-trigger" 
              :class="{ 'is-mobile': isMobile }"
              @click="toggleInnerLeftPanel"
            >
              <el-icon><ArrowRight v-if="!isMobile" /><ArrowDown v-else /></el-icon>
            </div>
          </transition>

          <!-- 集群与节点选择 -->
          <el-card 
            v-if="!isInnerLeftCollapsed"
            class="selection-card-vertical" 
            shadow="never"
            :style="isMobile ? { height: innerLeftWidth + '%' } : { width: innerLeftWidth + '%' }"
          >
            <template #header>
              <div class="card-header">
                <span class="card-title">集群与节点</span>
              </div>
            </template>
            <el-scrollbar>
              <div class="cluster-groups-vertical">
                <div v-for="g in filteredGroups" :key="g.id" class="cluster-group-v">
                  <div class="group-header" @click="toggleGroup(g)">
                    <el-icon class="icon-mr">
                      <ArrowDown v-if="g.open" />
                      <ArrowRight v-else />
                    </el-icon>
                    <span class="group-name">{{ g.name }}</span>
                  </div>
                  <div v-if="g.open" class="node-list-v">
                    <div
                      v-for="n in nodesForGroup(g)"
                      :key="n.name"
                      class="node-item-v"
                      :class="{ 'is-active': selectedNode === n.name }"
                      @click="selectNode(n.name)"
                    >
                      <span class="status-dot icon-mr" :class="statusDot(n)"></span>
                      <span class="node-name">{{ n.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-scrollbar>
          </el-card>

          <!-- 内部拉伸条 -->
          <div v-if="!isInnerLeftCollapsed" class="resizer-bar inner-resizer" @mousedown="startInnerResizing">
            <div class="resizer-handle"></div>
          </div>

          <!-- 日志预览 -->
          <el-card 
            class="log-card-main" 
            shadow="never"
            :style="isMobile ? { height: (isInnerLeftCollapsed ? 100 : (100 - innerLeftWidth)) + '%' } : { width: (isInnerLeftCollapsed ? 100 : (100 - innerLeftWidth)) + '%' }"
          >
            <template #header>
              <div class="card-header">
                <span class="card-title">日志预览</span>
                <el-tag v-if="selectedNode" size="small" type="info">{{ selectedNode }}</el-tag>
              </div>
            </template>
            
            <div v-if="!selectedNode" class="empty-preview">
              请选择节点预览日志
            </div>
            <div v-else class="log-preview-container">
              <div class="filter-bar">
                <el-select v-model="filters.level" placeholder="级别" size="small" clearable style="width: 80px;">
                  <el-option label="INFO" value="info" />
                  <el-option label="WARN" value="warning" />
                  <el-option label="ERROR" value="error" />
                </el-select>
                <el-select v-model="filters.timeRange" placeholder="时间" size="small" clearable style="width: 90px;">
                  <el-option label="1h" value="1h" />
                  <el-option label="6h" value="6h" />
                  <el-option label="24h" value="24h" />
                </el-select>
              </div>
              
              <el-table :data="previewLogs" size="small" stripe height="100%" class="log-table">
                <el-table-column prop="time" label="时间" width="85">
                  <template #default="{ row }">
                    {{ row.time.split("T")[1]?.slice(0, 8) || row.time }}
                  </template>
                </el-table-column>
                <el-table-column prop="level" label="级别" width="70">
                  <template #default="{ row }">
                    <el-tag :type="getLevelType(row.level)" size="small" effect="dark">
                      {{ row.level.charAt(0).toUpperCase() }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="message" label="消息" min-width="150" show-overflow-tooltip />
              </el-table>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 分栏拉伸条 -->
      <div class="resizer-bar" @mousedown="startResizing">
        <div class="resizer-handle"></div>
      </div>

      <!-- 右侧面板：诊断助手 -->
      <div 
        class="panel-right" 
        :style="isMobile ? { height: (100 - leftPanelWidth) + '%' } : { width: (100 - leftPanelWidth) + '%' }"
      >
        <el-card class="chat-card-full" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">诊断助手</span>
              <div class="agent-selectors">
                <el-select v-model="model" size="small" style="width: 160px;">
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
                <div class="chat-role">{{ roleLabel(m.role) }}</div>
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

            <transition name="el-fade-in">
              <el-button v-if="showScrollBottom" class="scroll-bottom-btn" type="primary" circle @click="scrollToBottom(true)">
                <el-icon><ArrowDown /></el-icon>
              </el-button>
            </transition>

            <div class="chat-input-area">
              <el-input
                v-model="inputMsg"
                type="textarea"
                :rows="3"
                placeholder="支持Markdown输入... Enter 发送"
                :disabled="sending"
                @keydown.enter.exact.prevent="send()"
              />
              <div class="input-actions">
                <div class="option-checks">
                  <el-checkbox v-model="useWebSearch" label="搜索" size="small" />
                  <el-checkbox v-model="useClusterOps" label="操作" size="small" />
                </div>
                <div class="button-group">
                  <el-button v-if="!sending" type="primary" @click="send()" :disabled="!inputMsg.trim()">发送</el-button>
                  <el-button v-else type="danger" plain @click="stopGeneration()">停止</el-button>
                  <el-button type="warning" plain @click="diagnose()" :disabled="sending">深度诊断</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { ClusterService } from "../api/cluster.service";
import { NodeService } from "../api/node.service";
import { LogService } from "../api/log.service";
import { DiagnosisService } from "../api/diagnosis.service";
import { useAuthStore } from "../stores/auth";
import { ArrowDown, ArrowRight, Rank } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

// 布局控制
const leftPanelWidth = ref(40); // 左侧百分比
const lastPanelWidth = ref(40); // 记录折叠前的宽度
const isLeftCollapsed = ref(false);
const isInnerLeftCollapsed = ref(false);
const lastInnerLeftWidth = ref(30);
const innerLeftWidth = ref(30); // 左侧内部：集群选择占左侧面板的百分比
const isResizing = ref(false);
const isInnerResizing = ref(false);
const layoutContainer = ref<HTMLElement | null>(null);
const leftPanelContainer = ref<HTMLElement | null>(null);
const isMobile = ref(window.innerWidth <= 1024);

function updateMobileState() {
  isMobile.value = window.innerWidth <= 1024;
}

function startResizing(e: MouseEvent) {
  isResizing.value = true;
  document.addEventListener("mousemove", handleResizing);
  document.addEventListener("mouseup", stopResizing);
  
  document.body.style.cursor = isMobile.value ? "row-resize" : "col-resize";
  document.body.style.userSelect = "none";
}

function handleResizing(e: MouseEvent) {
  if (!isResizing.value || !layoutContainer.value) return;
  const containerRect = layoutContainer.value.getBoundingClientRect();

  if (isMobile.value) {
    const newHeight = ((e.clientY - containerRect.top) / containerRect.height) * 100;
    if (newHeight < 5) {
      leftPanelWidth.value = 0;
      isLeftCollapsed.value = true;
    } else if (newHeight < 80) {
      leftPanelWidth.value = newHeight;
      isLeftCollapsed.value = false;
      lastPanelWidth.value = newHeight;
    }
  } else {
    const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    if (newWidth < 5) {
      leftPanelWidth.value = 0;
      isLeftCollapsed.value = true;
    } else if (newWidth < 80) {
      leftPanelWidth.value = newWidth;
      isLeftCollapsed.value = false;
      lastPanelWidth.value = newWidth;
    }
  }
}

function toggleLeftPanel() {
  if (isLeftCollapsed.value) {
    leftPanelWidth.value = lastPanelWidth.value > 10 ? lastPanelWidth.value : 40;
    isLeftCollapsed.value = false;
  } else {
    lastPanelWidth.value = leftPanelWidth.value;
    leftPanelWidth.value = 0;
    isLeftCollapsed.value = true;
  }
}

function toggleInnerLeftPanel() {
  if (isInnerLeftCollapsed.value) {
    innerLeftWidth.value = lastInnerLeftWidth.value > 10 ? lastInnerLeftWidth.value : 30;
    isInnerLeftCollapsed.value = false;
  } else {
    lastInnerLeftWidth.value = innerLeftWidth.value;
    innerLeftWidth.value = 0;
    isInnerLeftCollapsed.value = true;
  }
}

function stopResizing() {
  isResizing.value = false;
  document.removeEventListener("mousemove", handleResizing);
  document.removeEventListener("mouseup", stopResizing);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";
}

function startInnerResizing(e: MouseEvent) {
  isInnerResizing.value = true;
  document.addEventListener("mousemove", handleInnerResizing);
  document.addEventListener("mouseup", stopInnerResizing);
  
  document.body.style.cursor = isMobile.value ? "row-resize" : "col-resize";
  document.body.style.userSelect = "none";
}

function handleInnerResizing(e: MouseEvent) {
  if (!isInnerResizing.value || !leftPanelContainer.value) return;
  const containerRect = leftPanelContainer.value.getBoundingClientRect();

  if (isMobile.value) {
    const newHeight = ((e.clientY - containerRect.top) / containerRect.height) * 100;
    if (newHeight < 5) {
      innerLeftWidth.value = 0;
      isInnerLeftCollapsed.value = true;
    } else if (newHeight > 5 && newHeight < 90) {
      innerLeftWidth.value = newHeight;
      isInnerLeftCollapsed.value = false;
      lastInnerLeftWidth.value = newHeight;
    }
  } else {
    const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    if (newWidth < 5) {
      innerLeftWidth.value = 0;
      isInnerLeftCollapsed.value = true;
    } else if (newWidth > 5 && newWidth < 90) {
      innerLeftWidth.value = newWidth;
      isInnerLeftCollapsed.value = false;
      lastInnerLeftWidth.value = newWidth;
    }
  }
}

function stopInnerResizing() {
  isInnerResizing.value = false;
  document.removeEventListener("mousemove", handleInnerResizing);
  document.removeEventListener("mouseup", stopInnerResizing);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";
}

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
  window.addEventListener("resize", updateMobileState);
  await loadClusters();
  await loadHistory();
  startRefresh();
  // 如果已经有对话，初始化时置底
  scrollToBottom(false);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateMobileState);
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
  height: calc(100vh - 110px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.diagnosis-layout {
  display: flex;
  height: 100%;
  width: 100%;
  position: relative;
}

.expand-trigger {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  z-index: 100;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s;
}

.expand-trigger:hover {
  width: 32px;
  background: var(--el-color-primary-light-3);
}

.expand-trigger.is-mobile {
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  width: 48px;
  height: 24px;
  border-radius: 0 0 4px 4px;
}

.expand-trigger.is-mobile:hover {
  height: 32px;
  width: 48px;
}

.inner-expand-trigger {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 40px;
  background: var(--el-color-primary-light-3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  z-index: 90;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.inner-expand-trigger:hover {
  width: 26px;
  background: var(--el-color-primary-light-5);
}

.inner-expand-trigger.is-mobile {
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  width: 40px;
  height: 20px;
  border-radius: 0 0 4px 4px;
}

.inner-expand-trigger.is-mobile:hover {
  height: 26px;
  width: 40px;
}

.diagnosis-layout.is-resizing {
  cursor: col-resize;
}

/* 面板通用样式 */
.panel-left, .panel-right {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ease, height 0.3s ease;
}

.panel-left.is-collapsed {
  border: none;
}

.diagnosis-layout.is-resizing .panel-left,
.diagnosis-layout.is-resizing .panel-right {
  transition: none;
}

.left-content-wrapper {
  display: flex;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  overflow: hidden;
}

.left-content-wrapper.is-resizing-inner {
  user-select: none;
}

/* 垂直选择器样式 */
.selection-card-vertical {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
}

.cluster-groups-vertical {
  padding: 8px;
}

.cluster-group-v {
  margin-bottom: 8px;
}

.group-header {
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  color: var(--app-text-primary);
  transition: background 0.2s;
}

.group-header:hover {
  background: var(--el-color-primary-light-9);
}

.node-list-v {
  margin-top: 4px;
  padding-left: 12px;
}

.node-item-v {
  padding: 6px 10px;
  margin: 2px 0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.node-item-v:hover {
  background: var(--app-content-bg);
}

.node-item-v.is-active {
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot-running { background-color: var(--el-color-success); }
.status-dot-warning { background-color: var(--el-color-warning); }
.status-dot-error   { background-color: var(--el-color-danger); }

/* 日志预览主区域 */
.log-card-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
}

/* 拉伸条样式 */
.resizer-bar {
  width: 8px;
  cursor: col-resize;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  z-index: 10;
  flex-shrink: 0;
}

.resizer-bar:hover {
  background: var(--el-color-primary-light-8);
}

.resizer-handle {
  width: 2px;
  height: 40px;
  background: var(--app-border-color);
  border-radius: 1px;
}

.inner-resizer {
  margin: 0 4px;
}

/* 右侧聊天区域 */
.chat-card-full {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  border: none;
  border-left: 1px solid var(--app-border-color);
}

:deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  margin-bottom: 16px;
  word-break: break-word;
}

.scroll-bottom-btn {
  position: absolute;
  right: 20px;
  bottom: 160px;
  z-index: 100;
}

.chat-item {
  margin-bottom: 20px;
}

.chat-role {
  font-size: 12px;
  color: var(--app-text-secondary);
  margin-bottom: 4px;
}

.chat-item-user .chat-role { text-align: right; }

.chat-content {
  padding: 12px;
  border-radius: 8px;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border-color);
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-text {
  white-space: pre-wrap;
}

.chat-item-user .chat-content {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-8);
}

.chat-input-area {
  flex-shrink: 0;
  border-top: 1px solid var(--app-border-color);
  padding-top: 16px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.button-group {
  display: flex;
  gap: 8px;
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
  margin-bottom: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 14px;
}

.icon-mr { margin-right: 6px; }

@media (max-width: 1024px) {
  .diagnosis-layout {
    flex-direction: column;
  }
  .left-content-wrapper {
    flex-direction: column;
  }
  .panel-left, .panel-right {
    width: 100% !important;
    /* 高度由 inline style 动态控制 */
  }
  .resizer-bar {
    width: 100%;
    height: 8px;
    cursor: row-resize;
  }
  .resizer-handle {
    width: 40px;
    height: 2px;
  }
  .inner-resizer {
    margin: 4px 0;
  }
}
</style>
