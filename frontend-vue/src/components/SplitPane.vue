<template>
  <slot name="first"></slot>
  <ResizableBar
    v-if="resizable"
    :container="container"
    :is-mobile="isMobile"
    :max-percent="maxPercent"
    :bar-class="barClass"
    :model-value="modelValue"
    @update:model-value="(v) => emit('update:modelValue', v)"
    @dragging="(v) => emit('dragging', v)"
  />
  <slot name="second"></slot>
</template>

<script setup lang="ts">
import ResizableBar from "./ResizableBar.vue";

withDefaults(
  defineProps<{
    container: HTMLElement | null;
    isMobile: boolean;
    modelValue: number;
    maxPercent: number;
    resizable?: boolean;
    barClass?: string;
  }>(),
  { resizable: true, barClass: "" }
);

const emit = defineEmits<{
  (e: "update:modelValue", v: number): void;
  (e: "dragging", v: boolean): void;
}>();
</script>

