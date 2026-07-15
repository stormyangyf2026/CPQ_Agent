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
      <p class="empty-desc">智能配置报价助手，帮你快速生成产品配置和报价方案</p>
      <div class="suggestions">
        <div class="suggestion-item" @click="$emit('suggest', '帮我创建一个新的产品配置')">
          <el-icon :size="16" color="#2563EB">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 5H7C6.46957 5 5.96086 5.21071 5.58579 5.58579C5.21071 5.96086 5 6.46957 5 7V19C5 19.5304 5.21071 20.0391 5.58579 20.4142C5.96086 20.7893 6.46957 21 7 21H17C17.5304 21 18.0391 20.7893 18.4142 20.4142C18.7893 20.0391 19 19.5304 19 19V7C19 6.46957 18.7893 5.96086 18.4142 5.58579C18.0391 5.21071 17.5304 5 17 5H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 5C9 4.46957 9.21071 3.96086 9.58579 3.58579C9.96086 3.21071 10.4696 3 11 3H13C13.5304 3 14.0391 3.21071 14.4142 3.58579C14.7893 3.96086 15 4.46957 15 5C15 5.53043 14.7893 6.03914 14.4142 6.41421C14.0391 6.78929 13.5304 7 13 7H11C10.4696 7 9.96086 6.78929 9.58579 6.41421C9.21071 6.03914 9 5.53043 9 5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </el-icon>
          <span>创建一个新的产品配置</span>
        </div>
        <div class="suggestion-item" @click="$emit('suggest', '为我生成一份报价方案')">
          <el-icon :size="16" color="#2563EB">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 18V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 15H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </el-icon>
          <span>生成一份报价方案</span>
        </div>
        <div class="suggestion-item" @click="$emit('suggest', '解析这份配置数据')">
          <el-icon :size="16" color="#2563EB">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 16V20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 20H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 4H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 8C4 7.46957 4.21071 6.96086 4.58579 6.58579C4.96086 6.21071 5.46957 6 6 6H18C18.5304 6 19.0391 6.21071 19.4142 6.58579C19.7893 6.96086 20 7.46957 20 8V16C20 16.5304 19.7893 17.0391 19.4142 17.4142C19.0391 17.7893 18.5304 18 18 18H6C5.46957 18 4.96086 17.7893 4.58579 17.4142C4.21071 17.0391 4 16.5304 4 16V8Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 12H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </el-icon>
          <span>解析配置数据</span>
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
