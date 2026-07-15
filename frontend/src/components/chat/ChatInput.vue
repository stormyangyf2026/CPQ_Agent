<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'

const props = defineProps<{
  disabled: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  send: [text: string]
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function autoResize() {
  nextTick(() => {
    const el = textareaRef.value
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 200) + 'px'
    }
  })
}

function handleInput() {
  autoResize()
}

function handleKeydown(event: KeyboardEvent) {
  // Shift+Enter 换行，Enter 发送
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handleSend() {
  const text = inputText.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  inputText.value = ''
  autoResize()
}

function handlePaste(_event: ClipboardEvent) {
  // 默认处理即可
}

// 暴露聚焦方法
function focus() {
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

defineExpose({ focus })

watch(
  () => props.disabled,
  (val) => {
    if (!val) {
      focus()
    }
  }
)
</script>

<template>
  <div class="chat-input">
    <div class="input-container">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="input-textarea"
        :placeholder="placeholder || '输入消息...（Enter 发送，Shift+Enter 换行）'"
        :disabled="disabled"
        rows="1"
        @input="handleInput"
        @keydown="handleKeydown"
        @paste="handlePaste"
      ></textarea>
      <el-button
        class="send-btn"
        type="primary"
        :disabled="disabled || !inputText.trim()"
        @click="handleSend"
        :icon="false"
      >
        <el-icon :size="18">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </el-icon>
      </el-button>
    </div>
    <div class="input-footer">
      <span class="hint-text">Enter 发送 · Shift+Enter 换行</span>
      <span v-if="disabled" class="streaming-indicator">
        <span class="streaming-dot"></span>
        Agent 正在回复...
      </span>
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  padding: 12px 24px 16px;
  border-top: 1px solid #E2E8F0;
  background-color: #FFFFFF;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 8px 8px 8px 16px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.input-container:focus-within {
  border-color: #2563EB;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input-textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.5;
  color: #1E293B;
  resize: none;
  min-height: 24px;
  max-height: 200px;
  font-family: inherit;
  padding: 0;
}

.input-textarea::placeholder {
  color: #94A3B8;
}

.input-textarea:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn.is-disabled {
  background-color: #CBD5E1;
  border-color: #CBD5E1;
}

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 4px 0;
}

.hint-text {
  font-size: 11px;
  color: #94A3B8;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #2563EB;
}

.streaming-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #2563EB;
  animation: streamingPulse 1.2s ease-in-out infinite;
}

@keyframes streamingPulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}
</style>
