<template>
  <div class="task-list">
    <div class="page-header">
      <h3>测试任务</h3>
    </div>
    
    <el-card>
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索任务名称"
          clearable
          style="width: 200px"
          @keyup.enter="handleSearch"
        />
        
        <el-select v-model="searchStatus" placeholder="任务状态" clearable style="width: 120px; margin-left: 10px">
          <el-option label="待执行" value="pending" />
          <el-option label="执行中" value="running" />
          <el-option label="已通过" value="passed" />
          <el-option label="已失败" value="failed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始"
          end-placeholder="结束"
          value-format="YYYY-MM-DD"
          style="width: 250px; flex: 0 0 auto;"
          popper-class="chinese-date-picker"
        />
        
        <el-button type="primary" style="margin-left: 10px" @click="handleSearch">筛选</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      
      <el-table 
        :data="tasks" 
        v-loading="loading" 
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="任务名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="所属计划" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.plan_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="85">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
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
        <el-table-column label="触发方式" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.trigger_type === 'schedule'" type="warning">定时</el-tag>
            <el-tag v-else type="info">手动</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行方式" width="85" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.parallel" type="warning">并行</el-tag>
            <el-tag v-else type="info">串行</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行时长" width="110" sortable="custom" prop="duration">
          <template #default="{ row }">
            {{ row.duration ? formatDuration(row.duration) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="完成时间" width="160" sortable="custom" prop="completed_at">
          <template #default="{ row }">
            {{ formatDate(row.completed_at) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160" sortable="custom" prop="created_at">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              详情
            </el-button>
            <el-button
              v-if="['pending', 'running'].includes(row.status)"
              type="danger" link
              @click="cancelTask(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadTasks"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '@/api/task'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const tasks = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索相关
const searchKeyword = ref('')
const searchStatus = ref('')
const dateRange = ref([])
const sortField = ref('created_at')
const sortOrder = ref('desc')

const loadTasks = async () => {
  loading.value = true
  try {
    const params = { 
      page: page.value, 
      per_page: pageSize.value,
      sort_by: sortField.value,
      sort_order: sortOrder.value
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (searchStatus.value) {
      params.status = searchStatus.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await taskApi.getList(params)
    tasks.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const handleSortChange = ({ prop, order }) => {
  sortField.value = prop || 'created_at'
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  loadTasks()
}

const handleSearch = () => {
  page.value = 1
  loadTasks()
}

const resetSearch = () => {
  searchKeyword.value = ''
  searchStatus.value = ''
  dateRange.value = []
  page.value = 1
  loadTasks()
}

const viewDetail = (row) => {
  router.push(`/tasks/${row.id}`)
}

const cancelTask = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要取消任务 "${row.name}" 吗？`, '提示')
    await taskApi.cancel(row.id)
    ElMessage.success('已取消')
    loadTasks()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
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

// 进度条颜色：全部成功=绿色，其他按通过率显示
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

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600 * 10) / 10}小时`
}

import { formatBeijingTime } from '@/utils/time.js'

const formatDate = formatBeijingTime

onMounted(() => {
  // 从 URL 读取状态参数
  if (route.query.status) {
    searchStatus.value = route.query.status
  }
  // 从 URL 读取日期参数
  if (route.query.start_date && route.query.end_date) {
    dateRange.value = [route.query.start_date, route.query.end_date]
  }
  loadTasks()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 12px;
}

.page-header h3 {
  margin: 0;
  font-size: 18px;
}

.search-bar {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.search-bar .el-input,
.search-bar .el-select {
  margin-left: 0 !important;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
