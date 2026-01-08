<template>
  <el-card class="chat-card-full" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">诊断助手</span>
        <div class="agent-selectors">
          <el-select
            :model-value="model"
            size="small"
            style="width: 160px"
            @update:model-value="(v) => emit('update:model', String(v || ''))"
          >
            <el-option label="DeepSeek-V3" value="deepseek-ai/DeepSeek-V3" />
            <el-option label="DeepSeek-R1" value="Pro/deepseek-ai/DeepSeek-R1" />
          </el-select>
        </div>
      </div>
    </template>

    <div class="chat-container">
      <div class="chat-history" :ref="setChatHistoryEl">
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
        <el-button
          v-if="showScrollBottom"
          class="scroll-bottom-btn"
          type="primary"
          circle
          @click="emit('scrollBottom')"
        >
          <el-icon><ArrowDown /></el-icon>
        </el-button>
      </transition>

      <div class="chat-input-area">
        <el-input
          :model-value="inputMsg"
          type="textarea"
          :rows="3"
          placeholder="支持Markdown输入... Enter 发送"
          :disabled="sending"
          @keydown.enter.exact.prevent="emit('send')"
          @update:model-value="(v) => emit('update:inputMsg', String(v || ''))"
        />
        <div class="input-actions">
          <div class="option-checks">
            <el-checkbox
              :model-value="useWebSearch"
              label="搜索"
              size="small"
              @update:model-value="(v) => emit('update:useWebSearch', !!v)"
            />
            <el-checkbox
              :model-value="useClusterOps"
              label="操作"
              size="small"
              @update:model-value="(v) => emit('update:useClusterOps', !!v)"
            />
          </div>
          <div class="button-group">
            <el-button v-if="!sending" type="primary" :disabled="!inputMsg.trim()" @click="emit('send')">
              发送
            </el-button>
            <el-button v-else type="danger" plain @click="emit('stop')">停止</el-button>
            <el-button type="warning" plain :disabled="sending" @click="emit('diagnose')">深度诊断</el-button>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ArrowDown } from "@element-plus/icons-vue";

type Message = { role: "user" | "assistant" | "system"; content: string; reasoning?: string };

defineProps<{
  model: string;
  visibleMessages: Message[];
  showScrollBottom: boolean;
  inputMsg: string;
  sending: boolean;
  useWebSearch: boolean;
  useClusterOps: boolean;
  roleLabel: (r: string) => string;
  setChatHistoryEl: (el: Element | null) => void;
}>();

const emit = defineEmits<{
  (e: "update:model", v: string): void;
  (e: "update:inputMsg", v: string): void;
  (e: "update:useWebSearch", v: boolean): void;
  (e: "update:useClusterOps", v: boolean): void;
  (e: "scrollBottom"): void;
  (e: "send"): void;
  (e: "stop"): void;
  (e: "diagnose"): void;
}>();
</script>

<style scoped>
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 14px;
}
</style>

