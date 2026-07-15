<script setup lang="ts">
import { computed } from 'vue'

export interface ProductInfo {
  modelCode: string
  name: string
  capacity: string
  price: number
  matchRate: number
  thumbnailUrl?: string
}

const props = defineProps<{
  product: ProductInfo
}>()

const emit = defineEmits<{
  confirm: [product: ProductInfo]
}>()

const matchLevel = computed<'high' | 'medium' | 'low'>(() => {
  if (props.product.matchRate >= 85) return 'high'
  if (props.product.matchRate >= 60) return 'medium'
  return 'low'
})

const matchLabel = computed(() => {
  const map = { high: '高', medium: '中', low: '低' }
  return `${props.product.matchRate}% · ${map[matchLevel.value]}匹配`
})

const formattedPrice = computed(() => {
  return `¥${props.product.price.toLocaleString('zh-CN')}`
})

function handleConfirm() {
  emit('confirm', props.product)
}
</script>

<template>
  <div class="product-card" role="article" :aria-label="`产品: ${product.name}`">
    <div class="card-inner">
      <!-- 图片区 -->
      <div class="image-section">
        <div class="image-placeholder" v-if="!product.thumbnailUrl">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="placeholder-icon">
            <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
            <path d="M21 15L16 10L5 21" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M15 21L21 15L19 13" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
        <img v-else :src="product.thumbnailUrl" :alt="product.name" class="product-image" />
      </div>

      <!-- 信息区 -->
      <div class="info-section">
        <!-- 型号 -->
        <div class="model-code">{{ product.modelCode }}</div>

        <!-- 名称 -->
        <h3 class="product-name">{{ product.name }}</h3>

        <!-- 参数网格 -->
        <div class="params-grid">
          <div class="param-item">
            <span class="param-label">容量</span>
            <span class="param-value">{{ product.capacity }}</span>
          </div>
          <div class="param-item">
            <span class="param-label">匹配度</span>
            <span
              class="match-badge"
              :class="`match-${matchLevel}`"
            >
              {{ matchLabel }}
            </span>
          </div>
        </div>

        <!-- 价格 -->
        <div class="price-section">
          <span class="price-value">{{ formattedPrice }}</span>
        </div>

        <!-- 操作 -->
        <div class="action-section">
          <button class="confirm-btn" @click="handleConfirm">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span>确认选择</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
  max-width: 320px;
}

.product-card:hover {
  border-color: var(--cpq-primary);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
}

.card-inner {
  display: flex;
  flex-direction: column;
}

/* 图片区 */
.image-section {
  width: 100%;
  height: 180px;
  background-color: #F8FAFC;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-placeholder {
  color: #CBD5E1;
}

.placeholder-icon {
  width: 56px;
  height: 56px;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 12px;
}

/* 信息区 */
.info-section {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-code {
  font-size: 11px;
  font-weight: 600;
  color: var(--cpq-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
  line-height: 1.4;
}

/* 参数网格 */
.params-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.param-label {
  font-size: 11px;
  color: #94A3B8;
}

.param-value {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
}

/* 匹配度标签 */
.match-badge {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
  white-space: nowrap;
}

.match-high {
  background-color: #F0FDF4;
  color: var(--cpq-match-high);
}

.match-medium {
  background-color: #FFFBEB;
  color: var(--cpq-match-medium);
}

.match-low {
  background-color: #FEF2F2;
  color: var(--cpq-match-low);
}

/* 价格 */
.price-section {
  padding-top: 4px;
}

.price-value {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 22px;
  font-weight: 700;
  color: var(--cpq-price);
  line-height: 1.2;
}

/* 操作 */
.action-section {
  padding-top: 4px;
}

.confirm-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background-color: var(--cpq-primary);
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.confirm-btn:hover {
  background-color: #1D4ED8;
}

.confirm-btn:active {
  background-color: #1E40AF;
}

.btn-icon {
  width: 16px;
  height: 16px;
}
</style>
