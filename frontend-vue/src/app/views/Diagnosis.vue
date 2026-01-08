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
      <SplitPane
        :container="layoutContainer"
        :is-mobile="isMobile"
        :max-percent="80"
        v-model="leftPanelWidth"
        @dragging="(v) => (isResizing = v)"
      >
        <template #first>
          <div
            class="panel-left"
            :class="{ 'is-collapsed': isLeftCollapsed }"
            :style="
              isMobile
                ? { height: leftPanelWidth + '%' }
                : { width: leftPanelWidth + '%' }
            "
            ref="leftPanelContainer"
          >
            <div
              v-if="!isLeftCollapsed"
              class="left-content-wrapper"
              :class="{ 'is-resizing-inner': isInnerResizing }"
            >
              <SplitPane
                :container="leftPanelContainer"
                :is-mobile="isMobile"
                :max-percent="90"
                :resizable="!isInnerLeftCollapsed"
                bar-class="inner-resizer"
                v-model="innerLeftWidth"
                @dragging="(v) => (isInnerResizing = v)"
              >
                <template #first>
                  <transition name="el-fade-in">
                    <div
                      v-if="isInnerLeftCollapsed"
                      class="inner-expand-trigger"
                      :class="{ 'is-mobile': isMobile }"
                      @click="toggleInnerLeftPanel"
                    >
                      <el-icon
                        ><ArrowRight v-if="!isMobile" /><ArrowDown v-else
                      /></el-icon>
                    </div>
                  </transition>

                  <ClusterNodeSelector
                    v-if="!isInnerLeftCollapsed"
                    :is-mobile="isMobile"
                    :percent="innerLeftWidth"
                    :filtered-groups="filteredGroups"
                    :selected-node="selectedNode"
                    :nodes-for-group="nodesForGroup"
                    :toggle-group="toggleGroup"
                    :select-node="selectNode"
                    :status-dot="statusDot"
                  />
                </template>

                <template #second>
                  <el-card
                    class="log-card-main"
                    shadow="never"
                    :style="
                      isMobile
                        ? {
                            height:
                              (isInnerLeftCollapsed
                                ? 100
                                : 100 - innerLeftWidth) + '%',
                          }
                        : {
                            width:
                              (isInnerLeftCollapsed
                                ? 100
                                : 100 - innerLeftWidth) + '%',
                          }
                    "
                  >
                    <template #header>
                      <div class="card-header">
                        <span class="card-title">日志预览</span>
                        <el-tag v-if="selectedNode" size="small" type="info">{{
                          selectedNode
                        }}</el-tag>
                      </div>
                    </template>

                    <LogViewer
                      :node="selectedNode"
                      v-model:level="filters.level"
                      v-model:timeRange="filters.timeRange"
                      :paused="sending"
                    />
                  </el-card>
                </template>
              </SplitPane>
            </div>
          </div>
        </template>

        <template #second>
          <div
            class="panel-right"
            :style="
              isMobile
                ? { height: 100 - leftPanelWidth + '%' }
                : { width: 100 - leftPanelWidth + '%' }
            "
          >
            <DiagnosisChatPanel
              v-model:model="model"
              v-model:inputMsg="inputMsg"
              v-model:useWebSearch="useWebSearch"
              v-model:useClusterOps="useClusterOps"
              :visible-messages="visibleMessages"
              :show-scroll-bottom="showScrollBottom"
              :sending="sending"
              :role-label="roleLabel"
              :set-chat-history-el="setChatHistoryEl"
              @scroll-bottom="scrollToBottom(true)"
              @send="send()"
              @stop="stopGeneration()"
              @diagnose="diagnose()"
            />
          </div>
        </template>
      </SplitPane>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  reactive,
  ref,
  computed,
  watch,
  onMounted,
} from "vue";
import { useAuthStore } from "../stores/auth";
import { ArrowDown, ArrowRight, Rank } from "@element-plus/icons-vue";
import LogViewer from "../components/LogViewer.vue";
import ClusterNodeSelector from "../components/ClusterNodeSelector.vue";
import DiagnosisChatPanel from "../components/DiagnosisChatPanel.vue";
import SplitPane from "../components/SplitPane.vue";
import { useCollapsiblePercent } from "../composables/useCollapsiblePercent";
import { useIsMobile } from "../composables/useIsMobile";
import { useScrollBottomHint } from "../composables/useScrollBottomHint";
import { useClusterTree } from "../composables/useClusterTree";
import { useDiagnosisChat } from "../composables/useDiagnosisChat";
import { formatError } from "../lib/errors";

// 布局控制
const {
  percent: leftPanelWidth,
  collapsed: isLeftCollapsed,
  toggle: toggleLeftPanel,
} = useCollapsiblePercent({
  initialPercent: 40,
  defaultExpandedPercent: 40,
  minRememberPercent: 10,
});
const {
  percent: innerLeftWidth,
  collapsed: isInnerLeftCollapsed,
  toggle: toggleInnerLeftPanel,
} = useCollapsiblePercent({
  initialPercent: 30,
  defaultExpandedPercent: 30,
  minRememberPercent: 10,
});
const isResizing = ref(false);
const isInnerResizing = ref(false);
const layoutContainer = ref<HTMLElement | null>(null);
const leftPanelContainer = ref<HTMLElement | null>(null);
const { isMobile } = useIsMobile(1024);

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

const selectedNode = ref("");
function selectNode(n: string) {
  selectedNode.value = n;
}

const { groups, filteredGroups, nodesForGroup, toggleGroup, statusDot, selectedClusterUuid, loadClusters } =
  useClusterTree({
    kw,
    filters,
    selectedNode,
    setError: (e, def) => {
      err.value = e?.friendlyMessage || formatError(e, def);
    },
  });

const auth = useAuthStore();
const { setEl: setChatHistoryEl, showScrollBottom, scrollToBottom } =
  useScrollBottomHint({ threshold: 200 });

function scrollToLatest() {
  scrollToBottom(true);
}

const err = ref("");
const useWebSearch = ref(false);
const useClusterOps = ref(true);
function roleLabel(r: string) {
  return r === "assistant" ? "诊断智能体" : r === "user" ? "我" : "系统";
}
const {
  messages,
  visibleMessages,
  inputMsg,
  sending,
  stopGeneration,
  loadHistory,
  send,
  diagnose,
  generateReport,
} = useDiagnosisChat({
  authToken: computed(() => auth.token),
  agent,
  model,
  selectedNode,
  selectedClusterUuid,
  groups,
  useWebSearch,
  useClusterOps,
  setError: (e, def) => {
    err.value = e?.friendlyMessage || formatError(e, def);
  },
  clearError: () => {
    err.value = "";
  },
  scrollToLatest,
});

onMounted(async () => {
  await loadClusters();
  await loadHistory();
  // 如果已经有对话，初始化时置底
  scrollToBottom(false);
});

watch(selectedNode, () => {
  loadHistory();
});

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
.panel-left,
.panel-right {
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

.status-dot-running {
  background-color: var(--el-color-success);
}
.status-dot-warning {
  background-color: var(--el-color-warning);
}
.status-dot-error {
  background-color: var(--el-color-danger);
}

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

.chat-item-user .chat-role {
  text-align: right;
}

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

.icon-mr {
  margin-right: 6px;
}

@media (max-width: 1024px) {
  .diagnosis-layout {
    flex-direction: column;
  }
  .left-content-wrapper {
    flex-direction: column;
  }
  .panel-left,
  .panel-right {
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
