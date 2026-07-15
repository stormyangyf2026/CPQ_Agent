<script setup lang="ts">
import { ref, watch } from 'vue'

const themeOptions = [
  { label: '浅色', value: 'light' },
  { label: '深色', value: 'dark' },
  { label: '跟随系统', value: 'system' },
]

const langOptions = [
  { label: '中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
  { label: '日本語', value: 'ja-JP' },
]

const props = withDefaults(defineProps<{
  theme?: string
  language?: string
}>(), {
  theme: 'light',
  language: 'zh-CN',
})

const emit = defineEmits<{
  'update:theme': [value: string]
  'update:language': [value: string]
}>()

const localTheme = ref(props.theme)
const localLanguage = ref(props.language)

watch(localTheme, (v) => emit('update:theme', v))
watch(localLanguage, (v) => emit('update:language', v))
</script>

<template>
  <div class="ui-config">
    <div class="config-section-title">界面配置</div>

    <el-form label-position="top" size="default" class="config-form">
      <el-form-item label="主题">
        <div class="form-item-with-desc">
          <el-radio-group v-model="localTheme">
            <el-radio-button
              v-for="opt in themeOptions"
              :key="opt.value"
              :value="opt.value"
              :label="opt.value"
            >
              <template #default>
                <span class="radio-content">
                  <!-- 主题图标 -->
                  <svg v-if="opt.value === 'light'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="radio-icon">
                    <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M12 1V3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M12 21V23" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M4.22 4.22L5.64 5.64" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M18.36 18.36L19.78 19.78" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M1 12H3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M21 12H23" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M4.22 19.78L5.64 18.36" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M18.36 5.64L19.78 4.22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  <svg v-else-if="opt.value === 'dark'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="radio-icon">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="radio-icon">
                    <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M12 1V3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M12 21V23" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M4.22 4.22L5.64 5.64" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M18.36 18.36L19.78 19.78" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M1 12H3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M21 12H23" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M4.22 19.78L5.64 18.36" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M18.36 5.64L19.78 4.22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  <span>{{ opt.label }}</span>
                </span>
              </template>
            </el-radio-button>
          </el-radio-group>
        </div>
      </el-form-item>

      <el-form-item label="语言">
        <el-select v-model="localLanguage" class="lang-select">
          <el-option
            v-for="opt in langOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.ui-config {
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

.form-item-with-desc {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.radio-content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.radio-icon {
  width: 16px;
  height: 16px;
}

.lang-select {
  width: 200px;
}
</style>
