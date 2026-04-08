<template>
  <div class="about-page">
    <el-card class="about-card">
      <div class="header">
        <el-icon size="64" color="#2563eb"><Monitor /></el-icon>
        <h1>固件自动化测试平台</h1>
        <p class="subtitle">Firmware Automated Testing Platform</p>
        <el-tag type="primary" size="large">v1.0.0</el-tag>
      </div>

      <el-divider />

      <div class="section">
        <h3>项目介绍</h3>
        <p>
          这是一个针对 SSD 存储固件测试场景设计的自动化测试管理系统。
          系统支持测试用例管理、测试计划配置、异步任务执行和报告生成，
          模拟固件测试场景（SATA/NVMe/PCIe 协议测试）。
        </p>
      </div>

      <div class="section">
        <h3>技术架构</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="前端框架">Vue 3.5 + Vite 8</el-descriptions-item>
          <el-descriptions-item label="UI 组件库">Element Plus</el-descriptions-item>
          <el-descriptions-item label="后端框架">Flask 3.x</el-descriptions-item>
          <el-descriptions-item label="数据库">MySQL 8.0 / SQLite</el-descriptions-item>
          <el-descriptions-item label="异步任务">Celery 5.x + Redis</el-descriptions-item>
          <el-descriptions-item label="部署方式">Docker Compose</el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="section">
        <h3>核心功能</h3>
        <el-row :gutter="20">
          <el-col :span="12" v-for="feature in features" :key="feature.title">
            <div class="feature-item">
              <el-icon size="24" :color="feature.color"><component :is="feature.icon" /></el-icon>
              <div>
                <h4>{{ feature.title }}</h4>
                <p>{{ feature.desc }}</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <el-divider />

      <div class="footer">
        <p>© 2026 固件自动化测试平台</p>
        <a href="https://github.com/mildcore/firmware-test-framework" target="_blank" class="github-link" title="GitHub">
          <svg height="24" width="24" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
        </a>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const features = ref([
  {
    icon: 'DocumentChecked',
    color: '#2563eb',
    title: '测试计划管理',
    desc: '支持手动/定时触发，分层选择测试套件'
  },
  {
    icon: 'VideoPlay',
    color: '#059669',
    title: '异步任务执行',
    desc: 'Celery 异步执行，支持串行/并行模式'
  },
  {
    icon: 'FolderOpened',
    color: '#d97706',
    title: '测试套件管理',
    desc: '按分类组织用例，支持预留测试脚本'
  },
  {
    icon: 'DataLine',
    color: '#9333ea',
    title: '报告生成',
    desc: '自动生成测试报告，含执行摘要和详情'
  }
])
</script>

<style scoped>
.about-page {
  max-width: 800px;
  margin: 0 auto;
}

.about-card {
  padding: 20px;
}

.header {
  text-align: center;
  padding: 12px 0 8px;
}

.header h1 {
  margin: 8px 0 6px;
  font-size: 28px;
  color: #1f2937;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 8px;
}

.section {
  margin: 16px 0;
}

.section h3 {
  margin-bottom: 20px;
  color: #1f2937;
  border-left: 4px solid #2563eb;
  padding-left: 12px;
}

.section p {
  color: #4b5563;
  line-height: 1.8;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 16px;
}

.feature-item h4 {
  margin: 0 0 8px;
  color: #1f2937;
}

.feature-item p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.footer {
  text-align: center;
  padding: 20px 0;
  color: #6b7280;
}

.footer .hint {
  font-size: 12px;
  margin-top: 8px;
}

.github-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
  color: #6b7280;
  transition: color 0.2s;
}

.github-link:hover {
  color: #1f2937;
}
</style>
