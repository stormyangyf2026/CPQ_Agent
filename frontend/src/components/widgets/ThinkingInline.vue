<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  text?: string
}>()

const messages: Record<string, string> = {
  search: '正在搜索产品...',
  pricing: '正在计算定价...',
  analyzing: '正在分析需求...',
  thinking: '正在思考...',
  generating: '正在生成方案...',
}

const displayText = computed(() => {
  if (props.text) return props.text
  return messages.thinking
})
</script>

<template>
  <span class="thinking-inline" aria-label="思考中" role="status">
    <span class="dots">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </span>
    <span class="thinking-text">{{ displayText }}</span>
  </span>
</template>

<style scoped>
.thinking-inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.dots {
  display: inline-flex;
  gap: 3px;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--cpq-primary);
  animation: pulse-dot 1.4s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse-dot {
  0%, 80%, 100% {
    opacity: 0.2;
    transform: scale(0.7);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

.thinking-text {
  font-size: 13px;
  color: var(--cpq-primary);
  font-weight: 500;
}
</style>
