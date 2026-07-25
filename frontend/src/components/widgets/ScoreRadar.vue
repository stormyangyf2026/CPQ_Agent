<template>
  <div class="score-radar" v-if="dimensions.length">
    <div class="radar-header">📊 维度评分雷达</div>
    <div class="radar-bars">
      <div v-for="d in dimensions" :key="d.dimensionCode" class="radar-row">
        <span class="r-name">{{ d.dimensionName }}</span>
        <el-progress :percentage="Number(d.rawScore)" :stroke-width="8"
                     :color="barColor(d.rawScore)" style="flex:1;margin:0 10px" />
        <span class="r-score">{{ d.rawScore }}<small> × {{ d.weight }}%</small></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DimensionScore } from '@/types'
defineProps<{ dimensions: DimensionScore[] }>()
function barColor(s: number) { return s >= 90 ? '#67c23a' : s >= 70 ? '#409eff' : s >= 50 ? '#e6a23c' : '#f56c6c' }
</script>

<style scoped>
.score-radar { border: 1px solid #e4e7ed; border-radius: 8px; padding: 14px; margin: 8px 0; }
.radar-header { font-weight: 600; margin-bottom: 10px; }
.radar-row { display: flex; align-items: center; margin-bottom: 6px; font-size: 13px; }
.r-name { width: 75px; color: #606266; }
.r-score { width: 80px; text-align: right; font-weight: 600; color: #303133; }
</style>
