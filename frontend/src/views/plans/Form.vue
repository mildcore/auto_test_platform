<template>
  <div class="plan-form">
    <div class="page-header">
      <h3>{{ isEdit ? '编辑测试计划' : '创建测试计划' }}</h3>
    </div>
    
    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <!-- 基本信息 -->
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入计划名称" />
        </el-form-item>
        
        <el-form-item label="计划描述">
          <el-input
            v-model="form.description"
            type="textarea"
            rows="3"
            placeholder="请输入计划描述"
          />
        </el-form-item>
        
        <!-- 测试范围选择 -->
        <el-form-item label="测试内容" prop="suite_ids">
          <suite-selector v-model="selection" />
        </el-form-item>
        
        <!-- 触发方式 -->
        <el-form-item label="触发方式">
          <el-radio-group v-model="form.trigger_type">
            <el-radio label="manual">手动触发</el-radio>
            <el-radio label="schedule">定时触发</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 定时配置 -->
        <el-form-item v-if="form.trigger_type === 'schedule'" label="Cron表达式">
          <el-input v-model="form.schedule_cron" placeholder="如: 0 2 * * * (每天2点)" />
          <div class="form-tip">Cron格式：分 时 日 月 周</div>
        </el-form-item>
        
        <!-- 执行配置 -->
        <el-form-item label="执行方式">
          <el-checkbox v-model="form.parallel">并行执行用例</el-checkbox>
        </el-form-item>
        
        <el-form-item v-if="form.parallel" label="并发数">
          <el-slider v-model="form.max_concurrent" :min="1" :max="10" show-stops />
        </el-form-item>
        
        <!-- 操作按钮 -->
        <el-form-item>
          <div class="form-actions">
            <div class="left-actions">
              <el-button type="primary" @click="handleSubmit" :loading="submitting">
                {{ isEdit ? '保存' : '创建' }}
              </el-button>
              <el-button @click="$router.push('/plans')">取消</el-button>
            </div>
            <div class="right-actions" v-if="isEdit">
              <el-button link type="primary" @click="copyPlan">
                <el-icon><CopyDocument /></el-icon>复制计划
              </el-button>
              <el-button link type="danger" @click="deletePlan">
                <el-icon><Delete /></el-icon>删除计划
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { planApi } from '@/api/plan'
import SuiteSelector from '@/components/SuiteSelector.vue'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)
const planId = computed(() => route.params.id)

// 表单数据
const form = reactive({
  name: '',
  description: '',
  trigger_type: 'manual',
  schedule_cron: '',
  parallel: true,  // 默认勾选并行
  max_concurrent: 3
})

// 套件选择数据（case_ids 的顺序即执行顺序）
const selection = ref({
  suite_ids: [],
  case_ids: []
})

const rules = {
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }]
}

// 加载计划详情（编辑模式）
const loadPlan = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await planApi.getById(planId.value)
    const data = res.data
    
    form.name = data.name
    form.description = data.description
    form.trigger_type = data.trigger_type
    form.schedule_cron = data.schedule_cron
    form.parallel = data.parallel
    form.max_concurrent = data.max_concurrent
    
    selection.value = {
      suite_ids: data.suite_ids || [],
      case_ids: data.case_ids || []
    }
  } catch (e) {
    console.error(e)
  }
}

// 提交表单
const handleSubmit = async () => {
  // 检查是否有选择内容
  if (selection.value.suite_ids.length === 0 && selection.value.case_ids.length === 0) {
    ElMessage.warning('请至少选择一个测试内容')
    return
  }
  
  // 表单验证
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const data = {
      ...form,
      suite_ids: selection.value.suite_ids,
      case_ids: selection.value.case_ids,
      case_order: {}  // 保持兼容，后端不再依赖此字段
    }
    
    console.log('提交数据:', data)
    
    if (isEdit.value) {
      await planApi.update(planId.value, data)
      ElMessage.success('保存成功')
    } else {
      await planApi.create(data)
      ElMessage.success('创建成功')
    }
    
    router.push('/plans')
  } catch (e) {
    console.error('保存失败:', e)
    ElMessage.error(e.response?.data?.message || '保存失败，请检查网络')
  } finally {
    submitting.value = false
  }
}

// 删除计划
const deletePlan = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除计划 "${form.name}" 吗？\n删除后无法恢复，相关任务记录也会被删除。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await planApi.delete(planId.value)
    ElMessage.success('删除成功')
    router.push('/plans')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error(e.response?.data?.message || '删除失败')
    }
  }
}

// 复制计划
const copyPlan = async () => {
  try {
    await ElMessageBox.confirm(`确定要复制计划 "${form.name}" 吗？`, '复制计划')
    const res = await planApi.copy(planId.value)
    ElMessage.success('复制成功')
    router.push('/plans')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error(e.response?.data?.message || '复制失败')
    }
  }
}

// 初始化
loadPlan()
</script>

<style scoped>
.page-header {
  margin-bottom: 12px;
}

.page-header h3 {
  margin: 0;
  font-size: 18px;
}

:deep(.el-card__body) {
  padding: 16px;
}

/* 让表单项内容区域占满可用宽度 */
:deep(.el-form-item__content) {
  flex: 1;
  min-width: 0;
}

/* 测试内容选择器占满宽度 */
:deep(.el-form-item:has(.suite-selector)) .el-form-item__content {
  width: 100%;
  max-width: 100%;
}

.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

/* 确保 slider 不会溢出 */
:deep(.el-slider) {
  width: 100%;
  max-width: 600px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.right-actions {
  display: flex;
  gap: 8px;
}
</style>
