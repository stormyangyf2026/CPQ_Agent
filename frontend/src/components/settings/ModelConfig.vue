<script setup lang="ts">
import { ref, watch } from 'vue'

const modelProviders = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Azure OpenAI', value: 'azure' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'Google Gemini', value: 'gemini' },
  { label: '本地模型', value: 'local' },
]

const props = withDefaults(defineProps<{
  provider?: string
  modelName?: string
  apiKey?: string
  baseUrl?: string
  temperature?: number
}>(), {
  provider: 'openai',
  modelName: 'gpt-4o',
  apiKey: '',
  baseUrl: '',
  temperature: 0.7,
})

const emit = defineEmits<{
  'update:provider': [value: string]
  'update:modelName': [value: string]
  'update:apiKey': [value: string]
  'update:baseUrl': [value: string]
  'update:temperature': [value: number]
}>()

const localProvider = ref(props.provider)
const localModelName = ref(props.modelName)
const localApiKey = ref(props.apiKey)
const localBaseUrl = ref(props.baseUrl)
const localTemperature = ref(props.temperature)
const showKey = ref(false)

watch(localProvider, (v) => emit('update:provider', v))
watch(localModelName, (v) => emit('update:modelName', v))
watch(localApiKey, (v) => emit('update:apiKey', v))
watch(localBaseUrl, (v) => emit('update:baseUrl', v))
watch(localTemperature, (v) => emit('update:temperature', v))
</script>

<template>
  <div class="model-config">
    <div class="config-section-title">模型配置</div>

    <el-form label-position="top" size="default" class="config-form">
      <el-form-item label="模型提供商">
        <el-select v-model="localProvider" class="config-select">
          <el-option
            v-for="p in modelProviders"
            :key="p.value"
            :label="p.label"
            :value="p.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="模型名称">
        <el-input
          v-model="localModelName"
          placeholder="例如: gpt-4o, claude-3-opus"
        />
      </el-form-item>

      <el-form-item label="API Key">
        <el-input
          v-model="localApiKey"
          :type="showKey ? 'text' : 'password'"
          placeholder="输入 API Key"
          show-password
        >
          <template #append>
            <el-button @click="showKey = !showKey">
              {{ showKey ? '隐藏' : '显示' }}
            </el-button>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="Base URL">
        <el-input
          v-model="localBaseUrl"
          placeholder="https://api.openai.com/v1"
        />
      </el-form-item>

      <el-form-item label="Temperature">
        <div class="slider-wrapper">
          <el-slider
            v-model="localTemperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            input-size="small"
          />
          <span class="slider-hint">控制输出的随机性，较低值更确定</span>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.model-config {
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

.config-select {
  width: 100%;
}

.slider-wrapper {
  width: 100%;
}

.slider-wrapper :deep(.el-slider) {
  margin-bottom: 4px;
}

.slider-wrapper :deep(.el-slider__runway) {
  margin: 8px 0;
}

.slider-hint {
  display: block;
  font-size: 12px;
  color: #94A3B8;
  margin-top: 4px;
}
</style>
