<template>
  <div class="quote-card">
    <div class="quote-header">
      <span class="quote-title">📄 报价单</span>
      <span class="quote-no">{{ data.quoteNo }}</span>
    </div>
    <div class="quote-body">
      <table class="quote-table">
        <tr><th>产品</th><td>{{ data.modelCode }} {{ data.modelName }}</td></tr>
        <tr><th>数量</th><td>{{ data.quantity.toLocaleString() }} 个</td></tr>
        <tr><th>单价</th><td>¥{{ data.unitPrice.toFixed(2) }}</td></tr>
        <tr><th>总额</th><td class="total">¥{{ data.totalPrice.toLocaleString() }}</td></tr>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuoteCreated } from '@/types'
defineProps<{ data: QuoteCreated }>()
</script>

<style scoped>
.quote-card { border: 1px solid #c6e0b3; border-left: 3px solid #67c23a; border-radius: 8px; overflow: hidden; margin: 12px 0; background: #f0f9eb; }
.quote-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #e6f5db; border-bottom: 1px solid #c6e0b3; }
.quote-title { font-weight: 600; font-size: 14px; color: #3d7a1c; }
.quote-no { font-size: 12px; color: #67c23a; font-family: monospace; }
.quote-body { padding: 10px 14px; }
.quote-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.quote-table th { text-align: left; color: #909399; width: 50px; padding: 4px 0; font-weight: 400; }
.quote-table td { color: #303133; padding: 4px 0; }
.quote-table .total { font-weight: 700; color: #f56c6c; font-size: 14px; }
</style>
