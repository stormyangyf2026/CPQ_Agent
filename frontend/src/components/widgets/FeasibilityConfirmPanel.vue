<template>
  <div class="confirm-panel" :class="'panel-' + state.status.toLowerCase()">
    <div class="confirm-header">
      <span class="confirm-title">📋 工艺确认单</span>
      <el-tag :type="statusTagType" size="small">{{ statusText }}</el-tag>
    </div>

    <div class="confirm-info">
      <div class="info-item">
        <span class="info-label">审批编号</span>
        <span class="info-value">#{{ state.recordId || state.chainId }}</span>
      </div>
      <div class="info-item" v-if="state.modelCode">
        <span class="info-label">产品型号</span>
        <span class="info-value">{{ state.modelCode }} {{ state.modelName || '' }}</span>
      </div>
    </div>

    <div class="requirement-section" v-if="state.requirementText">
      <span class="info-label">客户需求</span>
      <p class="requirement-text">{{ state.requirementText }}</p>
    </div>

    <div class="confirm-actions" v-if="state.chainId">
      <a :href="`${cpqAppUrl}/approval/${state.chainId}`" target="_blank" class="detail-link">查看审批详情 →</a>
    </div>

    <div class="replacement-section" v-if="state.replacedModelCode">
      <div class="replacement-header">🔄 工艺推荐替代产品</div>
      <div class="replacement-body">
        <div class="repl-item">
          <span class="repl-label">原推荐</span>
          <span class="repl-value muted">{{ state.replacedModelCode }}</span>
          <span class="repl-value muted name">{{ state.replacedModelName || '' }}</span>
        </div>
        <div class="repl-arrow">↓ 替代为</div>
        <div class="repl-item">
          <span class="repl-label">替代产品</span>
          <span class="repl-value highlight">{{ state.modelCode }}</span>
          <span class="repl-value highlight name">{{ state.modelName || '' }}</span>
        </div>
        <div class="repl-item reason" v-if="state.replacedReason">
          <span class="repl-label">推荐理由</span>
          <span class="repl-value">{{ state.replacedReason }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted, onUnmounted } from 'vue'
import type { ProcessConfirm } from '@/types'
import { useChatStore } from '../../stores/chat'

const props = defineProps<{ data: ProcessConfirm }>()
const chatStore = useChatStore()
const agentApiUrl = import.meta.env.VITE_AGENT_API_URL || 'http://localhost:58100'
const cpqAppUrl = import.meta.env.VITE_CPQ_APP_URL || 'http://localhost:3000'

const state = reactive({ ...props.data })
const pollCount = ref(0)
let timer: ReturnType<typeof setInterval> | null = null
const notified = reactive({ confirmed: false, replaced: false })

const statusText = computed(() => {
  if (state.replacedModelCode) return '待确认替代'
  switch (state.status) {
    case 'PENDING': return '审核中'
    case 'CONFIRMED': return '已确认'
    case 'REJECTED': return '已驳回'
    default: return state.status
  }
})

const statusTagType = computed(() => {
  if (state.replacedModelCode) return 'warning'
  switch (state.status) {
    case 'CONFIRMED': return 'success'
    case 'PENDING': return 'warning'
    case 'REJECTED': return 'danger'
    default: return 'info'
  }
})

onMounted(() => {
  if (state.status === 'PENDING') {
    timer = setInterval(async () => {
      pollCount.value++
      try {
        const res = await fetch(`${agentApiUrl}/agent/status/${state.resultId}`)
        const json = await res.json()

        // ★ 替代出现 → 发新消息
        if (json.replacedModelCode && !notified.replaced) {
          notified.replaced = true
          chatStore.addMessage('assistant',
            `🔄 工艺工程师推荐了替代产品 ${json.replacedModelCode}，理由：${json.replacedReason || '无'}。\n请在对话框中输入"接受替代"确认，或输入"坚持原选"维持原推荐。`
          )
        }

        // ★ 状态变为 CONFIRMED → 发新消息
        if (json.status === 'CONFIRMED' && !notified.confirmed) {
          notified.confirmed = true
          const mc = json.modelCode || state.modelCode || ''
          chatStore.addMessage('assistant',
            `✅ 工艺确认已通过，产品 ${mc} 可交付。\n需要创建报价吗？如需，请提供客户名称和采购数量。`
          )
          if (timer) { clearInterval(timer); timer = null }
        }

        // 更新卡片数据
        if (json.status && json.status !== 'PENDING') {
          Object.assign(state, json)
        }
        if (json.replacedModelCode) {
          state.replacedModelCode = json.replacedModelCode
          state.replacedModelName = json.replacedModelName || ''
          state.replacedReason = json.replacedReason || state.replacedReason
          state.modelCode = json.modelCode || state.modelCode
          state.modelName = json.modelName || state.modelName
        }
      } catch { /* 忽略 */ }
    }, 5000)
  }
})

onUnmounted(() => { if (timer) { clearInterval(timer); timer = null } })
</script>

<style scoped>
.confirm-panel { border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden; margin: 12px 0; background: #fff; }
.confirm-panel.panel-pending { border-left: 3px solid #e6a23c; }
.confirm-panel.panel-confirmed { border-left: 3px solid #67c23a; }
.confirm-panel.panel-rejected { border-left: 3px solid #f56c6c; }

.confirm-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background: #fafbfc; border-bottom: 1px solid #ebeef5; }
.confirm-title { font-weight: 600; font-size: 14px; }

.confirm-info { padding: 10px 14px; display: flex; gap: 24px; border-bottom: 1px solid #f5f5f5; }
.info-item { display: flex; flex-direction: column; gap: 2px; }
.info-label { font-size: 11px; color: #909399; }
.info-value { font-size: 13px; color: #303133; font-weight: 500; }

.requirement-section { padding: 10px 14px; border-bottom: 1px solid #f5f5f5; }
.requirement-text { margin: 4px 0 0; font-size: 12px; color: #606266; white-space: pre-wrap; line-height: 1.6; }

.replacement-section { margin: 0 14px; padding: 12px; background: #fef7e0; border: 1px solid #fde3a7; border-radius: 6px; }
.replacement-header { font-size: 13px; font-weight: 600; color: #b88206; margin-bottom: 8px; }
.replacement-body { display: flex; flex-direction: column; gap: 4px; }
.repl-item { display: flex; gap: 8px; font-size: 12px; align-items: baseline; flex-wrap: wrap; }
.repl-label { color: #909399; min-width: 52px; flex-shrink: 0; }
.repl-value { color: #303133; }
.repl-value.name { font-size: 11px; color: #909399; margin-left: 4px; }
.repl-value.muted { color: #909399; text-decoration: line-through; }
.repl-value.muted.name { color: #c0c4cc; text-decoration: line-through; font-size: 11px; }
.repl-value.highlight { color: #1A73E8; font-weight: 600; }
.repl-value.highlight.name { color: #1A73E8; font-weight: 400; font-size: 11px; }
.repl-arrow { text-align: center; color: #b88206; font-size: 13px; padding: 2px 0; }
.repl-item.reason { border-top: 1px dashed #fde3a7; padding-top: 6px; margin-top: 2px; }
.confirm-actions { padding: 6px 14px; border-top: 1px solid #ebeef5; }
.detail-link { font-size: 12px; color: #409eff; text-decoration: none; }
.detail-link:hover { text-decoration: underline; }
</style>
