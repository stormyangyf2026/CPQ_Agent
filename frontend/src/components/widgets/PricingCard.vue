<script setup lang="ts">
import { computed } from 'vue'

export interface PricingInfo {
  basePrice: number
  salePrice: number
  discount: number     // 折扣率，如 0.15 表示 85 折
  minPrice: number
}

const props = defineProps<{
  pricing: PricingInfo
}>()

const emit = defineEmits<{
  'create-quote': []
  'adjust-price': []
}>()

const formattedBase = computed(() =>
  `¥${props.pricing.basePrice.toLocaleString('zh-CN')}`
)

const formattedSale = computed(() =>
  `¥${props.pricing.salePrice.toLocaleString('zh-CN')}`
)

const formattedMin = computed(() =>
  `¥${props.pricing.minPrice.toLocaleString('zh-CN')}`
)

const discountPercent = computed(() => {
  return `${Math.round(props.pricing.discount * 100)}%`
})

const savedAmount = computed(() => {
  return props.pricing.basePrice - props.pricing.salePrice
})

const formattedSaved = computed(() =>
  `¥${savedAmount.value.toLocaleString('zh-CN')}`
)
</script>

<template>
  <div class="pricing-card">
    <!-- 报价金额 -->
    <div class="price-header">
      <div class="price-label">报价金额</div>
      <div class="sale-price">{{ formattedSale }}</div>
      <div class="base-price-row">
        <span class="base-price">{{ formattedBase }}</span>
      </div>
    </div>

    <!-- 折扣信息 -->
    <div class="discount-section">
      <div class="discount-item">
        <span class="discount-label">折扣率</span>
        <span class="discount-value">{{ discountPercent }} OFF</span>
      </div>
      <div class="discount-item">
        <span class="discount-label">节省金额</span>
        <span class="discount-value saved">{{ formattedSaved }}</span>
      </div>
      <div class="discount-item">
        <span class="discount-label">底价</span>
        <span class="discount-value min">{{ formattedMin }}</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-section">
      <button class="btn btn-primary" @click="emit('create-quote')">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
          <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12 18V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9 15H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>生成报价单</span>
      </button>
      <button class="btn btn-secondary" @click="emit('adjust-price')">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
          <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2"/>
          <path d="M12 8V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>调整价格</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.pricing-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
  max-width: 360px;
}

/* 价格头部 */
.price-header {
  padding: 20px;
  text-align: center;
  background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F1F5F9;
}

.price-label {
  font-size: 12px;
  color: #94A3B8;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sale-price {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 28px;
  font-weight: 700;
  color: var(--cpq-price);
  line-height: 1.2;
}

.base-price-row {
  margin-top: 6px;
}

.base-price {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 14px;
  color: #94A3B8;
  text-decoration: line-through;
}

/* 折扣信息 */
.discount-section {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.discount-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.discount-label {
  font-size: 13px;
  color: #64748B;
}

.discount-value {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--cpq-match-high);
}

.discount-value.saved {
  color: var(--cpq-match-high);
}

.discount-value.min {
  color: var(--cpq-match-medium);
}

/* 操作按钮 */
.action-section {
  padding: 12px 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background-color: var(--cpq-primary);
  color: #FFFFFF;
  border-color: var(--cpq-primary);
}

.btn-primary:hover {
  background-color: #1D4ED8;
}

.btn-secondary {
  background-color: #FFFFFF;
  color: #475569;
  border-color: #E2E8F0;
}

.btn-secondary:hover {
  background-color: #F8FAFC;
  border-color: #CBD5E1;
  color: #1E293B;
}
</style>
