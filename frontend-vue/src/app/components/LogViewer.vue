<template>
  <div class="log-viewer">
    <div v-if="!node" class="empty-preview">请选择节点预览日志</div>
    <div v-else class="log-preview-container">
      <div class="filter-bar">
        <el-select
          :model-value="level"
          placeholder="级别"
          size="small"
          clearable
          style="width: 80px"
          @update:model-value="(v) => emit('update:level', String(v || ''))"
        >
          <el-option label="INFO" value="info" />
          <el-option label="WARN" value="warning" />
          <el-option label="ERROR" value="error" />
        </el-select>
        <el-select
          :model-value="timeRange"
          placeholder="时间"
          size="small"
          clearable
          style="width: 90px"
          @update:model-value="(v) => emit('update:timeRange', String(v || ''))"
        >
          <el-option label="1h" value="1h" />
          <el-option label="6h" value="6h" />
          <el-option label="24h" value="24h" />
        </el-select>
      </div>

      <div class="log-list-wrapper">
        <div class="log-list-head">
          <div class="cell time">时间</div>
          <div class="cell level">级别</div>
          <div class="cell msg">消息</div>
        </div>

        <div ref="viewportEl" class="log-viewport" @scroll="onScroll">
          <div class="log-spacer" :style="{ height: totalHeight + 'px' }"></div>
          <div
            class="log-items"
            :style="{ transform: `translateY(${offsetY}px)` }"
          >
            <div v-for="row in visibleLogs" :key="row.id" class="log-row">
              <div class="cell time">
                {{ row.time.split("T")[1]?.slice(0, 8) || row.time }}
              </div>
              <div class="cell level">
                <el-tag
                  :type="getLevelType(row.level)"
                  size="small"
                  effect="dark"
                >
                  {{ row.level.charAt(0).toUpperCase() }}
                </el-tag>
              </div>
              <div class="cell msg" :title="row.message">{{ row.message }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { LogService } from "../api/log.service";

type LogItem = {
  id: number | string;
  time: string;
  level: string;
  source: string;
  message: string;
};

const props = withDefaults(
  defineProps<{
    node: string;
    level: string;
    timeRange: string;
    paused?: boolean;
    size?: number;
    pollMs?: number;
  }>(),
  { paused: false, size: 50, pollMs: 5000 }
);

const emit = defineEmits<{
  (e: "update:level", v: string): void;
  (e: "update:timeRange", v: string): void;
}>();

const logs = ref<LogItem[]>([]);
const viewportEl = ref<HTMLDivElement | null>(null);
const scrollTop = ref(0);
const viewportHeight = ref(0);
const rowHeight = 34;
const overscan = 8;
let timer: any = null;
let ro: ResizeObserver | null = null;

function onScroll() {
  if (!viewportEl.value) return;
  scrollTop.value = viewportEl.value.scrollTop;
}

const totalHeight = computed(() => logs.value.length * rowHeight);

const startIndex = computed(() => {
  const base = Math.floor(scrollTop.value / rowHeight);
  return Math.max(0, base - overscan);
});

const endIndex = computed(() => {
  const count = Math.ceil(viewportHeight.value / rowHeight) + overscan * 2;
  return Math.min(logs.value.length, startIndex.value + count);
});

const offsetY = computed(() => startIndex.value * rowHeight);
const visibleLogs = computed(() =>
  logs.value.slice(startIndex.value, endIndex.value)
);

function getLevelType(level: string) {
  switch (level.toLowerCase()) {
    case "error":
      return "danger";
    case "warning":
    case "warn":
      return "warning";
    case "info":
      return "info";
    case "success":
      return "success";
    default:
      return "info";
  }
}

async function loadLogs() {
  if (!props.node) {
    logs.value = [];
    return;
  }
  try {
    const params: any = { node: props.node, size: props.size };
    if (props.level) params.level = props.level;
    if (props.timeRange) {
      const now = Date.now();
      const r = props.timeRange;
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
    logs.value = (items || []).map((d: any, i: number) => ({
      id: d.log_id || d.id || i,
      time: d.log_time || d.time || d.timestamp || new Date().toISOString(),
      level: String(d.level || "info").toLowerCase(),
      source: String(
        d.title || d.source || d.node_host || d.node || d.host || ""
      ),
      message: d.info || d.message || "",
    }));
  } catch {
    logs.value = [];
  }
}

function startPoll() {
  stopPoll();
  timer = setInterval(() => {
    if (props.node && !props.paused) loadLogs();
  }, props.pollMs);
}

function stopPoll() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

watch(
  () => [props.node, props.level, props.timeRange],
  () => {
    loadLogs();
    if (viewportEl.value) viewportEl.value.scrollTop = 0;
  },
  { immediate: true }
);

onMounted(() => {
  if (viewportEl.value) viewportHeight.value = viewportEl.value.clientHeight;
  ro = new ResizeObserver(() => {
    if (viewportEl.value) viewportHeight.value = viewportEl.value.clientHeight;
  });
  if (viewportEl.value) ro.observe(viewportEl.value);
  startPoll();
});

onBeforeUnmount(() => {
  stopPoll();
  if (ro && viewportEl.value) ro.unobserve(viewportEl.value);
  ro = null;
});
</script>

<style scoped>
.log-viewer {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.log-list-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--app-border-color);
  border-radius: 6px;
}

.log-list-head {
  display: grid;
  grid-template-columns: 90px 80px 1fr;
  gap: 8px;
  padding: 8px 10px;
  font-size: 12px;
  color: var(--app-text-secondary);
  border-bottom: 1px solid var(--app-border-color);
  background: var(--app-card-bg);
}

.log-viewport {
  position: relative;
  flex: 1;
  overflow: auto;
}

.log-spacer {
  width: 1px;
  opacity: 0;
}

.log-items {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.log-row {
  height: 34px;
  display: grid;
  grid-template-columns: 90px 80px 1fr;
  gap: 8px;
  padding: 0 10px;
  align-items: center;
  font-size: 12px;
  border-bottom: 1px solid var(--app-border-color);
}

.cell.msg {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
