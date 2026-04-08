<template>
  <div class="dashboard">
    <!-- 第一行：统计卡片 -->
    <el-row :gutter="12" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" @click="$router.push('/plans')">
          <div class="stat-icon blue">
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <div class="stat-value">{{ stats.total_plans }}</div>
          <div class="stat-label">测试计划</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" @click="$router.push('/tasks')">
          <div class="stat-icon green">
            <el-icon><VideoPlay /></el-icon>
          </div>
          <div class="stat-value">{{ stats.total_tasks }}</div>
          <div class="stat-label">测试任务</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" @click="$router.push('/suites')">
          <div class="stat-icon orange">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="stat-value">{{ stats.total_suites }}</div>
          <div class="stat-label">测试套件</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon purple">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-value">{{ stats.total_cases }}</div>
          <div class="stat-label">测试用例</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 第二行：今日统计 -->
    <el-card class="section-card today-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="today-stat clickable" @click="goToTasks({})">
            <div class="today-value">{{ stats.today_tasks || 0 }}</div>
            <div class="today-label">今日任务</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="today-stat clickable" @click="goToTasks({ status: 'passed' })">
            <div class="today-value success">{{ stats.today_passed || 0 }}</div>
            <div class="today-label">通过</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="today-stat clickable" @click="goToTasks({ status: 'failed' })">
            <div class="today-value danger">{{ stats.today_failed || 0 }}</div>
            <div class="today-label">失败</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 第三行：运行中任务 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon class="rotating"><Loading /></el-icon>
            <span>运行中任务</span>
            <el-tag type="primary" size="small">{{ runningTotal }}</el-tag>
          </div>
          <el-button link @click="$router.push({ path: '/tasks', query: { status: 'running' } })">查看全部</el-button>
        </div>
      </template>
      
      <el-table 
        v-if="runningTasks.length" 
        :data="runningTasksPage" 
        stripe
        class="running-table"
      >
        <el-table-column prop="name" label="任务名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="plan_name" label="所属计划" min-width="140" show-overflow-tooltip />
        <el-table-column label="触发" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.trigger_type === 'schedule'" type="warning" size="small">定时</el-tag>
            <el-tag v-else type="info" size="small">手动</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.status === 'pending' ? '待执行' : '执行中' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用例数" width="80" align="center">
          <template #default="{ row }">
            {{ row.total_cases || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="175">
          <template #default="{ row }">
            {{ formatDate(row.started_at || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewTask(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div v-if="runningTotal > runningPageSize" class="running-pagination">
        <el-pagination
          v-model:current-page="runningPage"
          :page-size="runningPageSize"
          :total="runningTotal"
          layout="prev, pager, next"
          small
        />
      </div>
      
      <el-empty v-else-if="!runningTasks.length" description="暂无运行中的任务" :image-size="80" />
    </el-card>
    
    <!-- 第四行：最近执行 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Clock /></el-icon>
            <span>最近执行</span>
          </div>
          <el-button link @click="$router.push('/tasks')">查看全部</el-button>
        </div>
      </template>
      
      <el-table v-if="recentTasks.length" :data="recentTasks" stripe>
        <el-table-column prop="name" label="任务名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="plan_name" label="所属计划" min-width="120" show-overflow-tooltip />
        <el-table-column label="触发" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.trigger_type === 'schedule'" type="warning" size="small">定时</el-tag>
            <el-tag v-else type="info" size="small">手动</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用例数" width="80" align="center">
          <template #default="{ row }">
            {{ row.total_cases || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="通过率" width="120">
          <template #default="{ row }">
            <el-progress 
              v-if="row.total_cases > 0"
              :percentage="Math.round(row.pass_rate)" 
              :color="getProgressColor(row)"
              :stroke-width="6"
              :format="(p) => Math.round(p) + '%'"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="完成时间" width="175">
          <template #default="{ row }">
            {{ formatDate(row.completed_at || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewTask(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-else description="暂无执行记录" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi } from '@/api/dashboard'
import { taskApi } from '@/api/task'

const router = useRouter()
const stats = ref({})
const runningTasks = ref([])
const runningTotal = ref(0)
const recentTasks = ref([])

// 运行中任务分页
const runningPage = ref(1)
const runningPageSize = ref(5)
const runningTasksPage = computed(() => {
  const start = (runningPage.value - 1) * runningPageSize.value
  const end = start + runningPageSize.value
  return runningTasks.value.slice(start, end)
})

const loadData = async () => {
  // 加载统计数据
  const statsRes = await dashboardApi.getStats()
  stats.value = statsRes.data
  
  // 加载运行中任务（包含pending和running）
  const runningRes = await taskApi.getList({ status: 'running', per_page: 10 })
  runningTasks.value = runningRes.data.items || []
  runningTotal.value = runningRes.data.total || 0
  
  // 同时加载pending状态的任务
  const pendingRes = await taskApi.getList({ status: 'pending', per_page: 10 })
  if (pendingRes.data.items && pendingRes.data.items.length > 0) {
    runningTasks.value = [...runningTasks.value, ...pendingRes.data.items]
    runningTotal.value += pendingRes.data.total || 0
  }
  
  // 加载最近完成的任务（显示5条）
  const recentRes = await taskApi.getList({ per_page: 5 })
  recentTasks.value = recentRes.data.items || []
}

const viewTask = (row) => {
  router.push(`/tasks/${row.id}`)
}

// 跳转到任务列表并携带筛选条件
const goToTasks = (query) => {
  // 如果是今日统计，需要计算日期范围
  if (!query.start_date && !query.end_date) {
    const today = new Date().toISOString().split('T')[0]
    query.start_date = today
    query.end_date = today
  }
  router.push({ path: '/tasks', query })
}

const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'running': 'primary',
    'passed': 'success',
    'failed': 'danger',
    'cancelled': 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'pending': '待执行',
    'running': '执行中',
    'passed': '通过',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return map[status] || status
}

// 进度条颜色：与任务列表保持一致
const getProgressColor = (row) => {
  if (row.pass_rate === 100) {
    return '#67c23a'  // 绿色 - 全部成功
  } else if (row.pass_rate >= 80) {
    return '#409eff'  // 蓝色 - 良好
  } else if (row.pass_rate >= 60) {
    return '#e6a23c'  // 橙色 - 一般
  } else {
    return '#f56c6c'  // 红色 - 较差
  }
}

import { formatBeijingTime } from '@/utils/time.js'

const formatDate = formatBeijingTime

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

/* 第一行：统计卡片 - 垂直居中布局 */
.stats-row {
  margin-bottom: 12px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  cursor: pointer;
  transition: transform 0.2s;
  text-align: center;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.stat-icon :deep(.el-icon) {
  font-size: 20px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

.stat-icon.blue {
  background: #dbeafe;
  color: #2563eb;
}

.stat-icon.green {
  background: #d1fae5;
  color: #059669;
}

.stat-icon.orange {
  background: #ffedd5;
  color: #ea580c;
}

.stat-icon.purple {
  background: #f3e8ff;
  color: #9333ea;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

/* 模块间隙 */
.section-card {
  margin-bottom: 12px;
}

.section-card :deep(.el-card__header) {
  padding: 10px 12px;
  border-bottom: 1px solid #e5e7eb;
}

.section-card :deep(.el-card__body) {
  padding: 10px 12px;
}

/* 今日统计 */
.today-card :deep(.el-card__body) {
  padding: 12px;
}

.today-stat {
  text-align: center;
  padding: 8px;
}

.today-stat.clickable {
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
}

.today-stat.clickable:hover {
  background-color: #f3f4f6;
}

.today-value {
  font-size: 26px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
}

.today-value.success {
  color: #059669;
}

.today-value.danger {
  color: #dc2626;
}

.today-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rotating {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.running-table {
  margin-bottom: 6px;
}

.running-table :deep(.el-table__cell) {
  padding: 4px 0;
}

/* 时间列不换行 */
:deep(.el-table .el-table__cell) {
  white-space: nowrap;
}

.running-pagination {
  display: flex;
  justify-content: center;
  padding-top: 6px;
  border-top: 1px solid #e5e7eb;
}

:deep(.el-empty) {
  padding: 20px;
}
</style>
