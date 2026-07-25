<template>
  <div class="match-result-card">
    <div v-if="!data || !data.recommendations?.length" class="empty-state">
      <el-empty description="标品库未找到高匹配产品">
        <p class="diy-hint">建议调整需求条件，或前往 <a :href="cpqApiUrl" target="_blank">CPQ系统</a> 走非标定制流程</p>
      </el-empty>
    </div>
    <div v-else class="result-list">
      <div class="result-header">
        <span class="result-title">📋 匹配推荐 Top{{ data.recommendations.length }}</span>
        <el-tag :type="data.thresholdPassed ? 'success' : 'warning'" size="small">
          阈值 {{ data.threshold }}分 · {{ data.totalScored }}款达标
        </el-tag>
      </div>

      <div v-for="item in data.recommendations" :key="item.rank" class="product-card"
           :class="{ 'top-match': item.rank <= 3 }">
        <!-- 标题行：排名 + 型号 + 评分 -->
        <div class="card-header">
          <span class="rank-badge" :class="'rank-' + item.rank">#{{ item.rank }}</span>
          <div class="product-image" v-if="item.imageUrl">
            <img :src="item.imageUrl" :alt="item.modelCode" />
          </div>
          <div class="product-image placeholder" v-else>
            <svg viewBox="0 0 48 48" fill="none"><rect width="48" height="48" rx="8" fill="#f0f5ff"/><text x="24" y="28" text-anchor="middle" font-size="16">📦</text></svg>
          </div>
          <span class="card-title">{{ item.modelCode }} {{ item.modelName }}</span>
          <el-tag :type="scoreType(item.totalScore)" size="small" class="score-tag">
            {{ item.totalScore }}分
          </el-tag>
        </div>

        <!-- 维度匹配表格 -->
        <div class="dim-table-wrap" v-if="item.dimensionScores?.length">
          <table class="dim-table">
            <thead>
              <tr><th>维度</th><th>客户需求</th><th>产品属性</th><th>是否满足</th></tr>
            </thead>
            <tbody>
              <tr v-for="ds in item.dimensionScores" :key="ds.dimensionCode"
                  :class="{ 'row-ok': !ds.difference, 'row-warn': ds.difference }">
                <td>{{ ds.dimensionName }}</td>
                <td>{{ extractReq(ds) }}</td>
                <td>{{ extractProd(ds) }}</td>
                <td>
                  <span v-if="!ds.difference" class="tag-ok">✅ 满足</span>
                  <span v-else class="tag-warn">⚠️ {{ ds.difference }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 报价 + AI理由 -->
        <div class="info-row">
          <span class="price">💰 ¥{{ item.basePrice || item.priceRange?.min }}</span>
          <span class="moq">📦 起订量: {{ item.moq }}</span>
          <span class="lead-time">🚚 交期: {{ item.leadTimeDays }}天</span>
        </div>
        <div class="ai-reason">🤖 {{ item.aiReason }}</div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { MatchResult, DimensionScore } from '@/types'

defineProps<{ data: MatchResult }>()
const cpqApiUrl = import.meta.env.VITE_CPQ_API_URL || 'http://localhost:30000'

function scoreType(score: number) {
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  return 'danger'
}

function extractReq(ds: DimensionScore): string {
  const d = ds.detail || ''
  const m = d.match(/需求[:\s]*([^，vs]+)/)
  return m ? m[1].trim() : '-'
}

function extractProd(ds: DimensionScore): string {
  const d = ds.detail || ''
  const m = d.match(/产品[:\s]*([^)]+)/)
  return m ? m[1].trim() : '-'
}
</script>

<style scoped>
.match-result-card { margin: 12px 0; }
.result-list { }
.result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.result-title { font-weight: 600; font-size: 15px; }

.product-card { border: 1px solid #e4e7ed; border-radius: 8px; padding: 14px; margin-bottom: 10px; background: #fff; }
.top-match { border-color: #409eff; }

.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.rank-badge { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; font-size: 12px; font-weight: 700; color: #fff; }
.rank-1 { background: #f56c6c; } .rank-2 { background: #e6a23c; } .rank-3 { background: #409eff; }
.rank-badge:not(.rank-1):not(.rank-2):not(.rank-3) { background: #909399; }

.product-image { width: 40px; height: 40px; border-radius: 6px; overflow: hidden; flex-shrink: 0; }
.product-image img { width: 100%; height: 100%; object-fit: cover; }
.product-image.placeholder { background: #f0f5ff; display: flex; align-items: center; justify-content: center; }

.card-title { font-weight: 700; font-size: 14px; color: #303133; }
.score-tag { margin-left: auto; }

/* 维度表格 */
.dim-table-wrap { overflow-x: auto; margin-bottom: 8px; }
.dim-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.dim-table th { background: #f5f7fa; padding: 6px 8px; text-align: left; font-weight: 600; border-bottom: 2px solid #e4e7ed; }
.dim-table td { padding: 5px 8px; border-bottom: 1px solid #ebeef5; }
.row-ok { }
.row-warn { background: #fef0f0; }
.tag-ok { color: #67c23a; font-weight: 600; }
.tag-warn { color: #e6a23c; font-size: 11px; }

.info-row { display: flex; gap: 16px; font-size: 12px; color: #606266; margin-bottom: 4px; }
.price { font-weight: 600; color: #f56c6c; }
.ai-reason { font-size: 12px; color: #909399; font-style: italic; margin-bottom: 4px; }

.empty-state { padding: 24px; }
.diy-hint { color: #909399; font-size: 13px; margin-top: 8px; }
</style>
