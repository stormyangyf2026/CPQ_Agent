<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  url?: string
  clientId?: string
  username?: string
  password?: string
  timeout?: number
}>(), {
  url: '',
  clientId: '',
  username: 'admin',
  password: '',
  timeout: 30,
})

const emit = defineEmits<{
  'update:url': [value: string]
  'update:clientId': [value: string]
  'update:username': [value: string]
  'update:password': [value: string]
  'update:timeout': [value: number]
  test: []
}>()

const localUrl = ref(props.url)
const localClientId = ref(props.clientId)
const localUsername = ref(props.username)
const localPassword = ref(props.password)
const localTimeout = ref(props.timeout)
const testing = ref(false)

watch(localUrl, (v) => emit('update:url', v))
watch(localClientId, (v) => emit('update:clientId', v))
watch(localUsername, (v) => emit('update:username', v))
watch(localPassword, (v) => emit('update:password', v))
watch(localTimeout, (v) => emit('update:timeout', v))
watch(localTimeout, (v) => emit('update:timeout', v))

function handleTest() {
  testing.value = true
  emit('test')
  // Reset testing state after a short delay (actual result handled externally)
  setTimeout(() => { testing.value = false }, 2000)
}
</script>

<template>
  <div class="cpq-config">
    <div class="config-section-title">CPQ 连接配置</div>

    <el-form label-position="top" size="default" class="config-form">
      <el-form-item label="CPQ API 地址">
        <el-input
          v-model="localUrl"
          placeholder="https://your-cpq-instance.com/api"
        />
      </el-form-item>

      <el-form-item label="Client ID">
        <el-input
          v-model="localClientId"
          placeholder="输入 Client ID"
        />
      </el-form-item>

      <el-form-item label="用户名">
        <el-input
          v-model="localUsername"
          placeholder="CPQ 登录用户名"
        />
        <div class="form-hint">用于获取 Access Token 的登录账号</div>
      </el-form-item>

      <el-form-item label="密码">
        <el-input
          v-model="localPassword"
          type="password"
          placeholder="CPQ 登录密码"
          show-password
        />
        <div class="form-hint">Token 由系统自动获取和续期，密码仅用于首次登录</div>
      </el-form-item>

      <el-form-item label="超时时间 (秒)">
        <el-input-number
          v-model="localTimeout"
          :min="5"
          :max="120"
          :step="5"
          controls-position="right"
          class="timeout-input"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="testing"
          @click="handleTest"
          class="test-btn"
        >
          <template #icon>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;">
              <path d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2"/>
              <path d="M12 16V12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </template>
          <span>测试连接</span>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.cpq-config {
  padding: 0;
}

.config-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E2E8F0;
}

.config-form {
  max-width: 480px;
}

.config-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.config-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  line-height: 1.4;
  padding-bottom: 4px;
}

.timeout-input {
  width: 140px;
}

.test-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
