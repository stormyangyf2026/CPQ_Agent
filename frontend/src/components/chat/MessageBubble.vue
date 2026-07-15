<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import type { Message } from '../../types'
import { renderMarkdown } from '../../utils/markdown'
import ThinkingInline from '../widgets/ThinkingInline.vue'

const props = defineProps<{
  message: Message
}>()

const isUser = computed(() => props.message.role === 'user')
const isStreaming = computed(() => props.message.status === 'streaming')
const isError = computed(() => props.message.status === 'error')
const isThinking = computed(() => props.message.role === 'thinking')

const renderedContent = ref('')

function updateRenderedContent() {
  if (props.message.content) {
    renderedContent.value = renderMarkdown(props.message.content)
  } else if (isStreaming.value) {
    renderedContent.value = ''
  }
}

onMounted(() => {
  updateRenderedContent()
})

watch(
  () => props.message.content,
  () => {
    updateRenderedContent()
  }
)

function formatTime(isoStr: string): string {
  try {
    const date = new Date(isoStr)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}
</script>

<template>
  <!-- Thinking 消息 -->
  <div v-if="isThinking" class="thinking-message">
    <ThinkingInline :text="message.content" />
  </div>
  
  <div v-else class="message-bubble" :class="{ 'is-user': isUser, 'is-error': isError, 'is-streaming': isStreaming }">
    <div class="message-avatar">
      <div class="avatar-icon" :class="{ 'user-avatar': isUser, 'agent-avatar': !isUser }">
        <svg v-if="isUser" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <div class="message-content">
      <div class="message-sender">{{ isUser ? '你' : 'CPQ Agent' }}</div>
      <div class="message-body" :class="{ 'user-body': isUser, 'agent-body': !isUser, 'error-body': isError }">
        <!-- 流式加载中且内容为空时显示思考动画 -->
        <div v-if="isStreaming && !message.content" class="thinking-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <!-- Markdown 渲染内容 -->
        <div v-else-if="renderedContent" class="markdown-body" v-html="renderedContent"></div>
        <!-- 错误消息 -->
        <div v-else-if="isError" class="error-text">{{ message.content }}</div>
        <!-- 普通文本回退 -->
        <div v-else class="text-content">{{ message.content }}</div>
      </div>
      <div class="message-time">{{ formatTime(message.createdAt) }}</div>
    </div>
  </div>
</template>

<style scoped>
.message-bubble {
  display: flex;
  gap: 10px;
  padding: 12px 0;
  max-width: 100%;
}

.message-bubble.is-user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  background-color: #2563EB;
  color: white;
}

.agent-avatar {
  background-color: #F1F5F9;
  color: #2563EB;
  border: 1px solid #E2E8F0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 80%;
}

.message-bubble.is-user .message-content {
  align-items: flex-end;
}

.message-sender {
  font-size: 12px;
  color: #64748B;
  font-weight: 500;
  padding: 0 4px;
}

.message-body {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
  overflow-wrap: break-word;
}

.user-body {
  background-color: #DBEAFE;
  color: #1E293B;
  border-bottom-right-radius: 4px;
}

.agent-body {
  background-color: #FFFFFF;
  color: #1E293B;
  border: 1px solid #E2E8F0;
  border-bottom-left-radius: 4px;
}

.error-body {
  background-color: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FECACA;
}

.message-time {
  font-size: 11px;
  color: #94A3B8;
  padding: 0 4px;
}

/* 思考动画 */
.thinking-dots {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 4px 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #94A3B8;
  animation: pulse 1.4s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

.error-text {
  color: #DC2626;
}

.text-content {
  white-space: pre-wrap;
}

/* Markdown 样式 */
.markdown-body :deep(pre) {
  background-color: #1E293B;
  color: #E2E8F0;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
  margin: 8px 0;
}

.markdown-body :deep(code) {
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 13px;
}

.markdown-body :deep(p code) {
  background-color: #F1F5F9;
  color: #2563EB;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.markdown-body :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 16px 0 8px 0;
  color: #1E293B;
}

.markdown-body :deep(p) {
  margin: 6px 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

.markdown-body :deep(li) {
  margin: 3px 0;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid #2563EB;
  padding-left: 12px;
  color: #64748B;
  margin: 8px 0;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #E2E8F0;
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background-color: #F8FAFC;
  font-weight: 600;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid #E2E8F0;
  margin: 16px 0;
}

.markdown-body :deep(a) {
  color: #2563EB;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
}
</style>
.thinking-message { padding: 6px 16px; opacity: 0.7; }
