<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '../stores/config'
import { testConnection, getBackendStatus } from '../api/agent'
import type { ConfigCategory, ConfigItem } from '../types'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const configStore = useConfigStore()

const activeTab = ref<ConfigCategory>('model')
const testing = ref(false)
const testResult = ref<{ success: boolean; message: string } | null>(null)

const tabs = [
  { label: '模型', key: 'model' as ConfigCategory },
  { label: 'CPQ', key: 'cpq' as ConfigCategory },
  { label: 'Agent', key: 'agent' as ConfigCategory },
  { label: '界面', key: 'ui' as ConfigCategory },
  { label: '系统', key: 'system' as ConfigCategory },
]

const currentConfigs = computed(() => {
  return configStore.getConfigsByCategory(activeTab.value)
})

onMounted(async () => {
  if (!configStore.loaded) {
    await configStore.loadConfig()
  }
})

async function handleSave() {
  try {
    await configStore.saveConfig()
    ElMessage.success('配置已保存')
  } catch (err) {
    // 尝试获取后端状态给出更详细的错误信息
    let detail = err instanceof Error ? err.message : String(err)
    const status = await getBackendStatus()
    if (status && !status.running) {
      const errorHint = status.error
        ? `\n后端诊断: ${status.error}`
        : `\n后端进程未运行，请确认 Python (${status.pythonFound}) 已安装并能启动 ${status.backendDir}`
      detail += errorHint
    } else if (status && status.error) {
      detail += `\n后端诊断: ${status.error}`
    }
    ElMessage.error(`保存配置失败: ${detail}`)
  }
}

async function handleReset() {
  try {
    await ElMessageBox.confirm('确定恢复默认配置吗？当前修改将丢失。', '确认', {
      confirmButtonText: '确认恢复',
      cancelButtonText: '取消',
      type: 'warning',
    })
    configStore.resetToDefault()
    ElMessage.success('已恢复默认配置')
  } catch {
    // 用户取消
  }
}

async function handleTestConnection() {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await testConnection()
  } catch (err) {
    testResult.value = {
      success: false,
      message: `测试失败: ${err instanceof Error ? err.message : String(err)}`,
    }
  } finally {
    testing.value = false
  }
}

function handleConfigChange(item: ConfigItem, newValue: string | number | boolean) {
  configStore.updateItem(item.key, newValue)
}

function goBack() {
  router.push('/')
}
</script>

<template>
  <div class="settings-view">
    <!-- Header -->
    <header class="settings-header">
      <div class="header-left">
        <el-button text class="back-btn" @click="goBack">
          <el-icon :size="18">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </el-icon>
        </el-button>
        <h1 class="header-title">设置</h1>
      </div>
      <div class="header-actions">
        <el-button @click="handleReset" :disabled="configStore.saving">恢复默认</el-button>
        <el-button type="primary" @click="handleSave" :loading="configStore.saving">保存配置</el-button>
      </div>
    </header>

    <!-- 加载中 -->
    <div v-if="configStore.loading" class="loading-container">
      <el-icon class="loading-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spin">
          <path d="M12 2V6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 18V22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4.93 4.93L7.76 7.76" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M16.24 16.24L19.07 19.07" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </el-icon>
      <p>加载配置中...</p>
    </div>

    <div v-else class="settings-body">
      <!-- Tabs -->
      <div class="settings-tabs">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </div>
      </div>

      <!-- Tab Content -->
      <div class="settings-content">
        <div class="config-list">
          <div
            v-for="item in currentConfigs"
            :key="item.key"
            class="config-item"
          >
            <div class="config-item-header">
              <label class="config-label">{{ item.label }}</label>
              <span v-if="item.description" class="config-desc">{{ item.description }}</span>
            </div>
            <div class="config-control">
              <!-- Select -->
              <el-select
                v-if="item.type === 'select'"
                :model-value="item.value as string | number"
                :placeholder="item.placeholder"
                class="config-select"
                @update:model-value="(val: string | number) => handleConfigChange(item, val)"
              >
                <el-option
                  v-for="opt in item.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>

              <!-- Input -->
              <el-input
                v-else-if="item.type === 'input'"
                :model-value="item.value as string"
                :placeholder="item.placeholder"
                class="config-input"
                @update:model-value="(val: string) => handleConfigChange(item, val)"
              />

              <!-- Password -->
              <el-input
                v-else-if="item.type === 'password'"
                :model-value="item.value as string"
                :placeholder="item.placeholder"
                type="password"
                show-password
                class="config-input"
                @update:model-value="(val: string) => handleConfigChange(item, val)"
              />

              <!-- Toggle -->
              <el-switch
                v-else-if="item.type === 'toggle'"
                :model-value="item.value as boolean"
                active-color="#2563EB"
                @update:model-value="(val: boolean) => handleConfigChange(item, val)"
              />

              <!-- Number -->
              <el-input-number
                v-else-if="item.type === 'number'"
                :model-value="item.value as number"
                :min="0"
                :max="100000"
                :step="1"
                size="small"
                controls-position="right"
                class="config-number"
                @update:model-value="(val: number) => handleConfigChange(item, val)"
              />
            </div>
          </div>
        </div>

        <!-- 测试连接（仅在 Model 或 CPQ Tab） -->
        <div v-if="activeTab === 'model' || activeTab === 'cpq'" class="test-section">
          <el-divider />
          <div class="test-connection">
            <el-button
              type="default"
              @click="handleTestConnection"
              :loading="testing"
              class="test-btn"
            >
              <el-icon :size="16">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2"/>
                  <path d="M12 16V12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </el-icon>
              <span>测试连接</span>
            </el-button>
            <div
              v-if="testResult"
              class="test-result"
              :class="{ success: testResult.success, fail: !testResult.success }"
            >
              <el-icon :size="16">
                <svg v-if="testResult.success" viewBox="0 0 24 24" fill="none">
                  <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none">
                  <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </el-icon>
              <span>{{ testResult.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #F8FAFC;
}

.settings-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #E2E8F0;
  background-color: #FFFFFF;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748B;
}

.back-btn:hover {
  background-color: #F1F5F9;
  color: #2563EB;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #64748B;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.settings-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.settings-tabs {
  width: 200px;
  padding: 16px 12px;
  border-right: 1px solid #E2E8F0;
  background-color: #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tab-item {
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #475569;
  transition: all 0.15s ease;
  font-weight: 500;
}

.tab-item:hover {
  background-color: #F1F5F9;
  color: #1E293B;
}

.tab-item.active {
  background-color: #EFF6FF;
  color: #2563EB;
  font-weight: 600;
}

.settings-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 8px;
  background-color: #FFFFFF;
  border: 1px solid #F1F5F9;
  transition: border-color 0.15s ease;
}

.config-item:hover {
  border-color: #E2E8F0;
}

.config-item-header {
  flex: 1;
  min-width: 0;
  padding-right: 24px;
}

.config-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 4px;
}

.config-desc {
  display: block;
  font-size: 12px;
  color: #94A3B8;
  line-height: 1.4;
}

.config-control {
  flex-shrink: 0;
}

.config-select {
  width: 200px;
}

.config-input {
  width: 240px;
}

.config-number {
  width: 140px;
}

.test-section {
  margin-top: 20px;
}

.test-connection {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.test-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.test-result {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 8px 16px;
  border-radius: 8px;
}

.test-result.success {
  background-color: #F0FDF4;
  color: #16A34A;
}

.test-result.fail {
  background-color: #FEF2F2;
  color: #DC2626;
}
</style>
