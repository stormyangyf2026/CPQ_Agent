<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useChatStore } from '../stores/chat'
import MessageList from '../components/chat/MessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'

const route = useRoute()
const chatStore = useChatStore()

// 如果路由指定了 sessionId，加载该会话
if (route.params.sessionId) {
  const sessionId = route.params.sessionId as string
  if (sessionId !== chatStore.currentSession.id) {
    chatStore.switchSession(sessionId)
  }
}

function handleSend(text: string) {
  chatStore.sendMessage(text)
}

function handleSuggest(text: string) {
  chatStore.sendMessage(text)
}
</script>

<template>
  <div class="chat-view">
    <!-- Header -->
    <header class="chat-header">
      <div class="header-left">
        <h1 class="header-title">{{ chatStore.currentSession.title }}</h1>
      </div>
      <div class="header-right">
        <el-tooltip content="新对话" placement="bottom">
          <el-button text class="header-btn" @click="chatStore.newSession()">
            <el-icon :size="18">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </header>

    <!-- 加载中 -->
    <div v-if="chatStore.loading" class="loading-container">
      <el-icon class="loading-icon" :size="32">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spin">
          <path d="M12 2V6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 18V22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4.93 4.93L7.76 7.76" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16.24 16.24L19.07 19.07" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M2 12H6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M18 12H22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4.93 19.07L7.76 16.24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16.24 7.76L19.07 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </el-icon>
      <p class="loading-text">加载中...</p>
    </div>

    <!-- 消息列表 -->
    <MessageList
      v-else
      @suggest="handleSuggest"
    />

    <!-- 输入区域 -->
    <ChatInput
      ref="chatInputRef"
      :disabled="chatStore.isStreaming"
      @send="handleSend"
    />
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #FFFFFF;
}

.chat-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #E2E8F0;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
}

.header-btn:hover {
  background-color: #F1F5F9;
  color: #2563EB;
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.loading-icon {
  color: #2563EB;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #64748B;
  font-size: 14px;
  margin: 0;
}
</style>
