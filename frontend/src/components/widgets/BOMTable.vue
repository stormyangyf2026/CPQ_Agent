<script setup lang="ts">
import { ref, computed } from 'vue'

export interface BOMItem {
  code: string
  name: string
  qty: number
  unitPrice: number
  amount: number
  children?: BOMItem[]
}

const props = defineProps<{
  items: BOMItem[]
}>()

const collapsedRows = ref<Set<number>>(new Set())

function toggleRow(index: number) {
  const s = new Set(collapsedRows.value)
  if (s.has(index)) {
    s.delete(index)
  } else {
    s.add(index)
  }
  collapsedRows.value = s
}

function isCollapsed(index: number): boolean {
  return collapsedRows.value.has(index)
}

function hasChildren(item: BOMItem): boolean {
  return !!item.children && item.children.length > 0
}

const totalAmount = computed(() => {
  return props.items.reduce((sum, item) => sum + item.amount, 0)
})

const formattedTotal = computed(() => {
  return `¥${totalAmount.value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
})

function formatMoney(val: number): string {
  return `¥${val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}
</script>

<template>
  <div class="bom-table-wrapper">
    <table class="bom-table" role="table" aria-label="BOM 物料清单">
      <thead>
        <tr>
          <th class="col-expand" style="width: 32px"></th>
          <th class="col-code">物料编码</th>
          <th class="col-name">物料名称</th>
          <th class="col-qty">数量</th>
          <th class="col-price">单价</th>
          <th class="col-amount">金额</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(item, index) in items" :key="item.code + index">
          <tr
            class="bom-row"
            :class="{
              'has-children': hasChildren(item),
              'collapsed': isCollapsed(index),
            }"
          >
            <td class="col-expand">
              <button
                v-if="hasChildren(item)"
                class="expand-btn"
                @click="toggleRow(index)"
                :aria-label="isCollapsed(index) ? '展开明细' : '折叠明细'"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  class="expand-icon"
                  :class="{ rotated: !isCollapsed(index) }"
                >
                  <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </td>
            <td class="col-code">{{ item.code }}</td>
            <td class="col-name">{{ item.name }}</td>
            <td class="col-qty num-cell">{{ item.qty }}</td>
            <td class="col-price num-cell money">{{ formatMoney(item.unitPrice) }}</td>
            <td class="col-amount num-cell money">{{ formatMoney(item.amount) }}</td>
          </tr>
          <!-- 子行 -->
          <tr
            v-if="hasChildren(item) && !isCollapsed(index)"
            class="bom-children-row"
          >
            <td colspan="6">
              <table class="bom-table bom-sub-table">
                <tbody>
                  <tr
                    v-for="(child, ci) in item.children!"
                    :key="child.code + ci"
                    class="bom-row bom-sub-row"
                  >
                    <td class="col-expand" style="width: 32px"></td>
                    <td class="col-code">{{ child.code }}</td>
                    <td class="col-name">{{ child.name }}</td>
                    <td class="col-qty num-cell">{{ child.qty }}</td>
                    <td class="col-price num-cell money">{{ formatMoney(child.unitPrice) }}</td>
                    <td class="col-amount num-cell money">{{ formatMoney(child.amount) }}</td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <!-- 合计 -->
    <div class="bom-total">
      <div class="total-label">合计</div>
      <div class="total-amount">{{ formattedTotal }}</div>
    </div>
  </div>
</template>

<style scoped>
.bom-table-wrapper {
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  overflow: hidden;
  background: #FFFFFF;
}

.bom-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.bom-table thead {
  background-color: #F8FAFC;
}

.bom-table th {
  padding: 10px 12px;
  font-weight: 600;
  color: #475569;
  text-align: left;
  border-bottom: 1px solid #E2E8F0;
  white-space: nowrap;
}

.bom-row {
  border-bottom: 1px solid #F1F5F9;
  transition: background-color 0.1s ease;
}

.bom-row:nth-child(even of :not(.bom-children-row)) {
  background-color: #F8FAFC;
}

.bom-row:nth-child(odd of :not(.bom-children-row)) {
  background-color: #FFFFFF;
}

.bom-row:hover {
  background-color: #EFF6FF !important;
}

.bom-row td {
  padding: 10px 12px;
  color: #334155;
  vertical-align: middle;
}

/* 子表 */
.bom-sub-table {
  border: none;
  margin: 0;
}

.bom-sub-row {
  background-color: #FAFAFA !important;
  font-size: 12px;
}

.bom-sub-row td {
  padding: 6px 12px;
}

.bom-children-row td {
  padding: 0;
}

/* 数字列 */
.num-cell {
  text-align: right;
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
}

.money {
  color: var(--cpq-price);
  font-weight: 600;
}

/* 展开按钮 */
.expand-btn {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #94A3B8;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.expand-btn:hover {
  background-color: #E2E8F0;
  color: #475569;
}

.expand-icon {
  width: 14px;
  height: 14px;
  transition: transform 0.2s ease;
}

.expand-icon.rotated {
  transform: rotate(90deg);
}

.col-expand {
  padding: 0 !important;
  text-align: center !important;
}

/* 合计行 */
.bom-total {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background-color: #F8FAFC;
  border-top: 2px solid #E2E8F0;
}

.total-label {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.total-amount {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 16px;
  font-weight: 700;
  color: var(--cpq-price);
}
</style>
