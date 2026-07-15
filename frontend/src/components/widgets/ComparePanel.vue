<script setup lang="ts">
import { computed } from 'vue'

export interface ComparisonDiff {
  field: string
  label: string
  type: 'added' | 'removed' | 'changed'
  valueA: string
  valueB: string
}

export interface ComparisonResult {
  solutionA: {
    label: string
    specs: Record<string, string>
  }
  solutionB: {
    label: string
    specs: Record<string, string>
  }
  differences: ComparisonDiff[]
  recommendation: string
}

const props = defineProps<{
  comparison: ComparisonResult
}>()

const diffTypeClass = (type: string) => {
  return `diff-${type}`
}

const specEntriesA = computed(() =>
  Object.entries(props.comparison.solutionA.specs)
)

const specEntriesB = computed(() =>
  Object.entries(props.comparison.solutionB.specs)
)

const specLabels: Record<string, string> = {
  modelCode: '型号',
  name: '名称',
  capacity: '容量',
  price: '价格',
  matchRate: '匹配度',
  warranty: '质保',
  delivery: '交期',
}
</script>

<template>
  <div class="compare-panel">
    <!-- 标题 -->
    <div class="compare-header">
      <span class="compare-title">方案对比</span>
    </div>

    <!-- 方案标签 -->
    <div class="solution-labels">
      <div class="label-a">{{ comparison.solutionA.label }}</div>
      <div class="label-vs">VS</div>
      <div class="label-b">{{ comparison.solutionB.label }}</div>
    </div>

    <!-- A|B 双列对比 -->
    <div class="compare-grid">
      <!-- 表头行 -->
      <div class="grid-row grid-header">
        <div class="grid-cell cell-field">参数</div>
        <div class="grid-cell cell-a">方案A</div>
        <div class="grid-cell cell-b">方案B</div>
      </div>

      <template v-for="diff in comparison.differences" :key="diff.field">
        <div
          class="grid-row"
          :class="diffTypeClass(diff.type)"
        >
          <div class="grid-cell cell-field">
            <span class="field-label">{{ diff.label || specLabels[diff.field] || diff.field }}</span>
            <span class="diff-indicator" :class="diffTypeClass(diff.type)">
              {{ diff.type === 'added' ? '新增' : diff.type === 'removed' ? '减少' : '变更' }}
            </span>
          </div>
          <div class="grid-cell cell-a">{{ diff.valueA || '-' }}</div>
          <div class="grid-cell cell-b">{{ diff.valueB || '-' }}</div>
        </div>
      </template>

      <!-- 无差异的完整参数 -->
      <template v-for="[key, valA] in specEntriesA" :key="key">
        <template v-if="!comparison.differences.some(d => d.field === key)">
          <div class="grid-row no-diff">
            <div class="grid-cell cell-field">
              {{ specLabels[key] || key }}
            </div>
            <div class="grid-cell cell-a">{{ valA }}</div>
            <div class="grid-cell cell-b">{{ specEntriesB.find(([k]) => k === key)?.[1] || '-' }}</div>
          </div>
        </template>
      </template>
    </div>

    <!-- 推荐结论 -->
    <div class="recommendation-section">
      <div class="recommendation-header">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="rec-icon">
          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor"/>
        </svg>
        <span>推荐结论</span>
      </div>
      <div class="recommendation-body">
        {{ comparison.recommendation }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.compare-panel {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
}

.compare-header {
  padding: 12px 16px;
  border-bottom: 1px solid #F1F5F9;
}

.compare-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

/* 方案标签 */
.solution-labels {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: #F8FAFC;
  border-bottom: 1px solid #E2E8F0;
}

.label-a,
.label-b {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 6px;
}

.label-a {
  background-color: #EFF6FF;
  color: var(--cpq-primary);
}

.label-b {
  background-color: #F0FDF4;
  color: var(--cpq-match-high);
}

.label-vs {
  font-size: 12px;
  font-weight: 600;
  color: #94A3B8;
}

/* 对比网格 */
.compare-grid {
  display: flex;
  flex-direction: column;
}

.grid-header {
  background-color: #F8FAFC;
  border-bottom: 1px solid #E2E8F0;
  font-weight: 600;
  font-size: 12px;
  color: #64748B;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-bottom: 1px solid #F1F5F9;
  transition: background-color 0.1s ease;
}

.grid-row:last-child {
  border-bottom: none;
}

.grid-cell {
  padding: 10px 12px;
  font-size: 13px;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 6px;
}

.cell-field {
  font-weight: 500;
  color: #475569;
  flex-wrap: wrap;
}

.cell-a,
.cell-b {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}

/* 差异指示器 */
.diff-indicator {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 4px;
  white-space: nowrap;
}

.diff-added {
  background-color: #F0FDF4;
}

.diff-added .diff-indicator {
  background-color: #DCFCE7;
  color: var(--cpq-diff-added);
}

.diff-added .cell-a,
.diff-added .cell-b {
  color: var(--cpq-diff-added);
  font-weight: 600;
}

.diff-removed {
  background-color: #FEF2F2;
}

.diff-removed .diff-indicator {
  background-color: #FEE2E2;
  color: var(--cpq-diff-removed);
}

.diff-removed .cell-a,
.diff-removed .cell-b {
  color: var(--cpq-diff-removed);
  font-weight: 600;
}

.diff-changed {
  background-color: #FFFBEB;
}

.diff-changed .diff-indicator {
  background-color: #FEF3C7;
  color: var(--cpq-diff-changed);
}

.diff-changed .cell-a,
.diff-changed .cell-b {
  color: var(--cpq-diff-changed);
  font-weight: 600;
}

.no-diff {
  background-color: #FFFFFF;
}

/* 推荐结论 */
.recommendation-section {
  padding: 16px;
  border-top: 1px solid #E2E8F0;
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF9E7 100%);
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.rec-icon {
  width: 16px;
  height: 16px;
  color: #F59E0B;
}

.recommendation-header span {
  font-size: 14px;
  font-weight: 600;
  color: #92400E;
}

.recommendation-body {
  font-size: 13px;
  color: #78350F;
  line-height: 1.6;
}
</style>
