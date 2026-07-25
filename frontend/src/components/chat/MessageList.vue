<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { useChatStore } from '../../stores/chat'
import MessageBubble from './MessageBubble.vue'

const chatStore = useChatStore()
const listRef = ref<HTMLElement | null>(null)
const autoScroll = ref(true)

const messages = computed(() => chatStore.messages)

// 检测用户是否手动滚动到顶部
function handleScroll() {
  if (!listRef.value) return
  const el = listRef.value
  const threshold = 100
  autoScroll.value = el.scrollHeight - el.scrollTop - el.clientHeight < threshold
}

// 自动滚动到底部
function scrollToBottom() {
  if (!autoScroll.value || !listRef.value) return
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
}

// 监听消息变化自动滚动
watch(
  () => chatStore.messages.length,
  () => scrollToBottom()
)

// 监听当前消息内容变化（流式更新）
watch(
  () => {
    const msgs = chatStore.messages
    if (msgs.length === 0) return ''
    return msgs[msgs.length - 1]?.content || ''
  },
  () => scrollToBottom()
)

// 监听流式状态
watch(
  () => chatStore.isStreaming,
  () => scrollToBottom()
)

onMounted(() => {
  scrollToBottom()
})

function getMessageKey(msg: any, index: number): string {
  return msg.id || `msg-${index}`
}
</script>

<template>
  <div class="message-list" ref="listRef" @scroll="handleScroll">
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#2563EB" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="#2563EB" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="#2563EB" stroke-width="1.5" stroke-linejoin="round"/>
        </svg>
      </div>
      <h2 class="empty-title">CPQ Agent</h2>
      <p class="empty-desc">智能产品推荐报价助手。可以查产品、按需求推荐、查客户、查报价。</p>
      <div class="suggestions">
        <div class="suggestion-item" @click="$emit('suggest', '帮我找一款用于智能水表的锂亚电池，工作温度 -20 到 60 度，要 IP67 防水')">
          <el-icon :size="16" color="#2563EB">
            <svg viewBox="0 0 24 24" fill="none"><path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </el-icon>
          <span>🎯 按需求推荐电池</span>
        </div>
        <div class="suggestion-item" @click="$emit('suggest', 'ER14250-BP-002')">
          <el-icon :size="16" color="#2563EB">
            <svg viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="20" height="8" rx="1" stroke="currentColor" stroke-width="2"/><rect x="2" y="14" width="20" height="8" rx="1" stroke="currentColor" stroke-width="2"/></svg>
          </el-icon>
          <span>🔍 查具体产品</span>
        </div>
        <div class="suggestion-item" @click="$emit('suggest', '帮我查下有没有深圳新能源科技这个客户')">
          <el-icon :size="16" color="#2563EB">
            <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2"/><path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </el-icon>
          <span>👤 查客户</span>
        </div>
      </div>
    </div>

    <div v-else class="messages-container">
      <MessageBubble
        v-for="(msg, index) in messages"
        :key="getMessageKey(msg, index)"
        :message="msg"
      />
    </div>
  </div>
</template>

<script lang="ts">
export default {
  emits: ['suggest'],
}
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  scroll-behavior: smooth;
}

.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background-color: #CBD5E1;
  border-radius: 3px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 20px;
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-title {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #64748B;
  margin: 0 0 32px 0;
  max-width: 360px;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 360px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  background-color: #FFFFFF;
  font-size: 13px;
  color: #334155;
}

.suggestion-item:hover {
  border-color: #2563EB;
  background-color: #EFF6FF;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.1);
}

.messages-container {
  display: flex;
  flex-direction: column;
}
</style>
