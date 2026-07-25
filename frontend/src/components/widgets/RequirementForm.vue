<template>
  <div class="req-form">
    <div class="form-header">📝 快捷需求填写</div>
    <el-form :model="form" label-width="90px" size="small" @submit.prevent="handleSubmit">
      <el-form-item label="产品线">
        <el-select v-model="form.categoryId" placeholder="选择产品线" style="width:100%">
          <el-option label="锂亚 ER电池 (507)" :value="507" />
          <el-option label="锂锰 CR电池 (508)" :value="508" />
        </el-select>
      </el-form-item>
      <el-form-item label="用途场景">
        <el-input v-model="form.usageType" placeholder="如: 智能水表、安防" />
      </el-form-item>
      <el-form-item label="温度范围">
        <el-input v-model="form.tempMin" placeholder="最低℃" style="width:45%" />
        <span style="margin:0 4px">~</span>
        <el-input v-model="form.tempMax" placeholder="最高℃" style="width:45%" />
      </el-form-item>
      <el-form-item label="防护等级">
        <el-select v-model="form.sealLevel" placeholder="选择" style="width:100%">
          <el-option label="IP54" value="IP54" />
          <el-option label="IP65" value="IP65" />
          <el-option label="IP67" value="IP67" />
          <el-option label="IP68" value="IP68" />
          <el-option label="无要求" value="NONE" />
        </el-select>
      </el-form-item>
      <el-form-item label="期望寿命">
        <el-input-number v-model="form.lifeCycleYears" :min="1" :max="20" placeholder="年" style="width:100%" />
      </el-form-item>
      <el-form-item label="认证要求">
        <el-checkbox-group v-model="form.certifications">
          <el-checkbox label="CE">CE</el-checkbox>
          <el-checkbox label="RoHS">RoHS</el-checkbox>
          <el-checkbox label="UL1642">UL</el-checkbox>
          <el-checkbox label="UN38.3">UN38.3</el-checkbox>
          <el-checkbox label="IEC60086">IEC</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading">开始匹配</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const emit = defineEmits<{ submit: [data: any] }>()
const loading = ref(false)

const form = reactive({
  categoryId: 507,
  usageType: '',
  tempMin: '',
  tempMax: '',
  sealLevel: '',
  lifeCycleYears: null as number | null,
  certifications: [] as string[],
})

function handleSubmit() {
  loading.value = true
  const r: any = {}
  if (form.usageType) r.usageType = form.usageType
  if (form.tempMin || form.tempMax) {
    r.tempMin = parseFloat(form.tempMin) || 0
    r.tempMax = parseFloat(form.tempMax) || 85
  }
  if (form.sealLevel) r.sealLevel = form.sealLevel
  if (form.lifeCycleYears) r.lifeCycleYears = form.lifeCycleYears
  if (form.certifications.length) r.requiredCertifications = form.certifications
  emit('submit', { categoryId: form.categoryId, requirements: r })
  setTimeout(() => { loading.value = false }, 500)
}
</script>

<style scoped>
.req-form { border: 1px solid #e4e7ed; border-radius: 8px; padding: 14px; margin: 8px 0; background: #fff; }
.form-header { font-weight: 600; margin-bottom: 10px; }
</style>
