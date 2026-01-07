<template>
  <div class="resizer-bar" :class="barClass" @mousedown="start">
    <div class="resizer-handle"></div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount } from "vue";

const props = withDefaults(
  defineProps<{
    container: HTMLElement | null;
    isMobile: boolean;
    modelValue: number;
    maxPercent: number;
    collapseThreshold?: number;
    barClass?: string;
  }>(),
  { collapseThreshold: 5, barClass: "" }
);

const emit = defineEmits<{
  (e: "update:modelValue", v: number): void;
  (e: "dragging", v: boolean): void;
}>();

let isDragging = false;

function computePercent(e: MouseEvent) {
  const containerRect = props.container?.getBoundingClientRect();
  if (!containerRect) return null;
  if (props.isMobile) {
    return ((e.clientY - containerRect.top) / containerRect.height) * 100;
  }
  return ((e.clientX - containerRect.left) / containerRect.width) * 100;
}

function onMove(e: MouseEvent) {
  if (!isDragging) return;
  const next = computePercent(e);
  if (next == null) return;
  if (next < props.collapseThreshold) {
    emit("update:modelValue", 0);
    return;
  }
  if (next < props.maxPercent) {
    emit("update:modelValue", next);
  }
}

function stop() {
  if (!isDragging) return;
  isDragging = false;
  emit("dragging", false);
  document.removeEventListener("mousemove", onMove);
  document.removeEventListener("mouseup", stop);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";
}

function start(e: MouseEvent) {
  if (!props.container) return;
  e.preventDefault();
  isDragging = true;
  emit("dragging", true);
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", stop);
  document.body.style.cursor = props.isMobile ? "row-resize" : "col-resize";
  document.body.style.userSelect = "none";
}

onBeforeUnmount(() => stop());
</script>

<style scoped>
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

@media (max-width: 1024px) {
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
