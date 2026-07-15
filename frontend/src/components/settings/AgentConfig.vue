<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  maxRounds?: number
  enableSubAgent?: boolean
  requireQuoteConfirm?: boolean
}>(), {
  maxRounds: 10,
  enableSubAgent: false,
  requireQuoteConfirm: true,
})

const emit = defineEmits<{
  'update:maxRounds': [value: number]
  'update:enableSubAgent': [value: boolean]
  'update:requireQuoteConfirm': [value: boolean]
}>()

const localMaxRounds = ref(props.maxRounds)
const localEnableSubAgent = ref(props.enableSubAgent)
const localRequireQuoteConfirm = ref(props.requireQuoteConfirm)

watch(localMaxRounds, (v) => emit('update:maxRounds', v))
watch(localEnableSubAgent, (v) => emit('update:enableSubAgent', v))
watch(localRequireQuoteConfirm, (v) => emit('update:requireQuoteConfirm', v))
</script>

<template>
  <div class="agent-config">
    <div class="config-section-title">Agent 行为配置</div>

    <el-form label-position="top" size="default" class="config-form">
      <el-form-item label="最大推理轮次">
        <div class="form-item-with-desc">
          <el-input-number
            v-model="localMaxRounds"
            :min="1"
            :max="50"
            :step="1"
            controls-position="right"
            class="rounds-input"
          />
          <span class="input-hint">Agent 单次任务的最大工具调用轮次，过高会消耗更多 token</span>
        </div>
      </el-form-item>

      <el-form-item label="启用子 Agent">
        <div class="form-item-with-desc">
          <el-switch
            v-model="localEnableSubAgent"
            active-color="#2563EB"
          />
          <span class="input-hint">允许 Agent 在复杂任务中创建子代理并行处理</span>
        </div>
      </el-form-item>

      <el-form-item label="报价确认">
        <div class="form-item-with-desc">
          <el-switch
            v-model="localRequireQuoteConfirm"
            active-color="#2563EB"
          />
          <span class="input-hint">生成报价前需要用户确认，避免误操作</span>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.agent-config {
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

.rounds-input {
  width: 140px;
}

.input-hint {
  font-size: 12px;
  color: #94A3B8;
  line-height: 1.4;
}
</style>
