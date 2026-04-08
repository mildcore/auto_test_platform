<template>
  <div class="plan-list">
    <div class="page-header">
      <h3>测试计划</h3>
      <el-button type="primary" @click="$router.push('/plans/create')">
        <el-icon><Plus /></el-icon>
        创建计划
      </el-button>
    </div>
    
    <el-card>
      <el-table :data="plans" v-loading="loading" stripe>
        <el-table-column prop="name" label="计划名称" min-width="200" />
        <el-table-column label="测试范围" width="200">
          <template #default="{ row }">
            {{ row.suite_count }} 个套件
            <el-tag v-if="!row.case_ids || row.case_ids.length === 0" type="success">全选</el-tag>
            <el-tag v-else>{{ row.case_ids.length }} 个用例</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行方式" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.parallel" type="warning">并行</el-tag>
            <el-tag v-else type="info">串行</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="触发方式" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.trigger_type === 'manual'" type="info">手动</el-tag>
            <el-tag v-else-if="row.trigger_type === 'schedule'" type="warning">定时</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="定时规则" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.trigger_type === 'schedule' ? (row.schedule_cron || '-') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="下次执行" width="160">
          <template #default="{ row }">
            <span v-if="row.trigger_type === 'schedule' && row.is_active">
              {{ row.next_run_at ? formatDate(row.next_run_at) : '-' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="togglePlan(row)"
              :loading="row.toggling"
            />
          </template>
        </el-table-column>
        <el-table-column label="执行次数" width="90" prop="total_runs" />
        <el-table-column label="上次执行" width="160">
          <template #default="{ row }">
            {{ row.last_run_at ? formatDate(row.last_run_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-tooltip content="执行计划" placement="top">
              <el-button 
                circle
                type="primary" 
                plain
                @click="executePlan(row)"
              >
                <el-icon><VideoPlay /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="编辑计划" placement="top">
              <el-button 
                circle
                @click="$router.push(`/plans/${row.id}/edit`)"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadPlans"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { planApi } from '@/api/plan'

const $router = useRouter()

const loading = ref(false)
const plans = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadPlans = async () => {
  loading.value = true
  try {
    const res = await planApi.getList({ page: page.value, per_page: pageSize.value })
    plans.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const executePlan = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要执行计划 "${row.name}" 吗？`, '提示')
    const res = await planApi.execute(row.id)
    ElMessage.success('任务已启动')
    // 跳转到任务列表查看
    setTimeout(() => {
      $router.push('/tasks')
    }, 500)
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error(e.response?.data?.message || '执行失败，请检查后端服务')
    }
  }
}

const togglePlan = async (row) => {
  row.toggling = true
  try {
    await planApi.toggle(row.id)
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
  } catch (e) {
    row.is_active = !row.is_active
    console.error(e)
  } finally {
    row.toggling = false
  }
}

import { formatBeijingTime } from '@/utils/time.js'

const formatDate = formatBeijingTime

onMounted(loadPlans)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.page-header h3 {
  margin: 0;
  font-size: 18px;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
