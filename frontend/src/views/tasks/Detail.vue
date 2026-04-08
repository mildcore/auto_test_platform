<template>
  <div class="task-detail">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h3>任务详情</h3>
    </div>

    <el-card v-loading="loading">
      <!-- 基本信息 -->
      <div class="info-section">
        <h4>基本信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称" :span="2">{{ task.name }}</el-descriptions-item>
          <el-descriptions-item label="所属计划">{{ task.plan_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(task.status)">
              {{ getStatusText(task.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行方式">
            <el-tag v-if="task.parallel" type="warning">并行（{{ task.max_concurrent }}并发）</el-tag>
            <el-tag v-else type="info">串行</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="通过率">{{ task.pass_rate }}%</el-descriptions-item>
          <el-descriptions-item label="总用例">{{ task.total_cases }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(task.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(task.completed_at) }}</el-descriptions-item>
          <el-descriptions-item label="执行时长">{{ formatDuration(task.duration) }}</el-descriptions-item>
          <el-descriptions-item label="触发方式">{{ task.trigger_type === 'schedule' ? '定时触发' : '手动触发' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 执行统计 -->
      <div class="stats-section" v-if="task.total_cases > 0">
        <h4>执行统计</h4>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-box success">
              <div class="stat-value">{{ task.passed_cases || 0 }}</div>
              <div class="stat-label">通过</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box danger">
              <div class="stat-value">{{ task.failed_cases || 0 }}</div>
              <div class="stat-label">失败</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box warning">
              <div class="stat-value">{{ task.error_cases || 0 }}</div>
              <div class="stat-label">错误</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box info">
              <div class="stat-value">{{ task.total_cases || 0 }}</div>
              <div class="stat-label">总计</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 执行详情 -->
      <div class="executions-section" v-if="report?.executions?.length">
        <h4>执行详情</h4>
        <el-table :data="report?.executions || []" stripe>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="case_name" label="用例名称" min-width="200" />
          <el-table-column prop="suite_name" label="所属套件" width="150" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'passed' ? 'success' : 'danger'">
                {{ row.status === 'passed' ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="execution_time" label="耗时" width="100">
            <template #default="{ row }">
              {{ row.execution_time?.toFixed(2) }}s
            </template>
          </el-table-column>
          <el-table-column label="输出" min-width="300">
            <template #default="{ row }">
              <pre class="output-pre">{{ row.output }}</pre>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 错误信息 -->
      <div class="error-section" v-if="report?.summary?.error_message">
        <h4>错误信息</h4>
        <el-alert
          :title="report?.summary?.error_message || ''"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { taskApi } from '@/api/task'

const route = useRoute()
const loading = ref(false)
const task = ref({})
const report = ref(null)

const loadTask = async () => {
  loading.value = true
  try {
    const res = await taskApi.getById(route.params.id)
    task.value = res.data
    report.value = res.data.report
  } finally {
    loading.value = false
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

import { formatBeijingTime } from '@/utils/time.js'

const formatDate = formatBeijingTime

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600 * 10) / 10}小时`
}

onMounted(loadTask)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.page-header h3 {
  margin: 0;
  font-size: 18px;
}

.info-section,
.stats-section,
.executions-section,
.error-section {
  margin-bottom: 16px;
}

h4 {
  margin-bottom: 16px;
  color: #1f2937;
}

.stat-box {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f9fafb;
}

.stat-box.success {
  background: #d1fae5;
  color: #059669;
}

.stat-box.danger {
  background: #fee2e2;
  color: #dc2626;
}

.stat-box.warning {
  background: #fef3c7;
  color: #d97706;
}

.stat-box.info {
  background: #dbeafe;
  color: #2563eb;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
}

.output-pre {
  margin: 0;
  padding: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  font-size: 12px;
  max-height: 150px;
  overflow: auto;
  white-space: pre-wrap;
}
</style>
