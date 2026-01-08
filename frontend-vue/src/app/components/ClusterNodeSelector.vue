<template>
  <el-card
    class="selection-card-vertical"
    shadow="never"
    :style="isMobile ? { height: percent + '%' } : { width: percent + '%' }"
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
</template>

<script setup lang="ts">
import { ArrowDown, ArrowRight } from "@element-plus/icons-vue";

type NodeItem = { name: string; status: string };
type Group = { id: string; uuid: string; name: string; open: boolean; nodes: NodeItem[]; count?: number };

defineProps<{
  isMobile: boolean;
  percent: number;
  filteredGroups: Group[];
  selectedNode: string;
  nodesForGroup: (g: Group) => NodeItem[];
  toggleGroup: (g: Group) => void | Promise<void>;
  selectNode: (n: string) => void;
  statusDot: (n: NodeItem) => string;
}>();
</script>

<style scoped>
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
</style>

