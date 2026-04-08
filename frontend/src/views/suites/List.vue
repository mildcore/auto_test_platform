<template>
  <div class="suite-list">
    <div class="page-header">
      <h3>测试套件</h3>
      <el-button type="primary" @click="showAddSuite">
        <el-icon><Plus /></el-icon>
        创建套件
      </el-button>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="8" v-for="suite in suites" :key="suite.id">
        <el-card class="suite-card" shadow="hover">
          <div class="suite-header">
            <h4>{{ suite.name }}</h4>
            <el-tag :type="getCategoryType(suite.category)">
              {{ getCategoryText(suite.category) }}
            </el-tag>
          </div>
          <p class="suite-desc">{{ suite.description || '暂无描述' }}</p>
          <div class="suite-footer">
            <span class="case-count">
              <el-icon><Document /></el-icon>
              {{ suite.case_count }} 个用例
            </span>
            <div class="actions">
              <el-button type="primary" link @click="viewDetail(suite)">
                详情
              </el-button>
              <el-button type="danger" link @click="deleteSuite(suite)">
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建套件弹窗 -->
    <el-dialog
      v-model="addSuiteVisible"
      title="创建测试套件"
      width="500px"
    >
      <el-form :model="suiteForm" label-width="100px">
        <el-form-item label="套件名称" required>
          <el-input v-model="suiteForm.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="suiteForm.category" style="width: 100%">
            <el-option label="固件测试" value="firmware" />
            <el-option label="协议测试" value="protocol" />
            <el-option label="性能测试" value="performance" />
            <el-option label="电源测试" value="power" />
            <el-option label="其他" value="general" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="suiteForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入套件描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addSuiteVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddSuite" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 套件详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentSuite?.name"
      width="800px"
    >
      <div v-if="currentSuite">
        <p><strong>分类：</strong>{{ getCategoryText(currentSuite.category) }}</p>
        <p><strong>描述：</strong>{{ currentSuite.description || '暂无描述' }}</p>
        
        <el-divider />
        
        <div class="cases-header">
          <h4>测试用例列表</h4>
          <el-button type="primary" @click="showAddCase">
            <el-icon><Plus /></el-icon> 添加用例
          </el-button>
        </div>
        
        <el-table :data="suiteCases" v-loading="casesLoading">
          <el-table-column prop="name" label="用例名称" min-width="200" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.test_type)">
                {{ row.test_type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="danger" link @click="deleteCase(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加用例弹窗 -->
    <el-dialog
      v-model="addCaseVisible"
      title="添加测试用例"
      width="600px"
    >
      <el-form :model="caseForm" label-width="100px">
        <el-form-item label="用例名称" required>
          <el-input v-model="caseForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="用例描述">
          <el-input
            v-model="caseForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入用例描述"
          />
        </el-form-item>
        <el-form-item label="测试类型">
          <el-select v-model="caseForm.test_type" style="width: 100%">
            <el-option label="单元测试" value="unit" />
            <el-option label="集成测试" value="integration" />
            <el-option label="系统测试" value="system" />
            <el-option label="性能测试" value="performance" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCaseVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddCase" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { suiteApi } from '@/api/suite'
import { caseApi } from '@/api/case'

const suites = ref([])
const addSuiteVisible = ref(false)
const detailVisible = ref(false)
const addCaseVisible = ref(false)
const currentSuite = ref(null)
const suiteCases = ref([])
const casesLoading = ref(false)
const submitting = ref(false)

const suiteForm = ref({
  name: '',
  category: 'general',
  description: ''
})

const caseForm = ref({
  name: '',
  description: '',
  test_type: 'unit'
})

const loadSuites = async () => {
  const res = await suiteApi.getList({ per_page: 100 })
  suites.value = res.data.items || res.data
}

const showAddSuite = () => {
  suiteForm.value = {
    name: '',
    category: 'general',
    description: ''
  }
  addSuiteVisible.value = true
}

const submitAddSuite = async () => {
  if (!suiteForm.value.name) {
    ElMessage.warning('请输入套件名称')
    return
  }
  
  submitting.value = true
  try {
    await suiteApi.create(suiteForm.value)
    ElMessage.success('创建成功')
    addSuiteVisible.value = false
    loadSuites()
  } catch (e) {
    console.error(e)
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

const viewDetail = async (suite) => {
  currentSuite.value = suite
  detailVisible.value = true
  await loadSuiteCases(suite.id)
}

const loadSuiteCases = async (suiteId) => {
  casesLoading.value = true
  try {
    const res = await suiteApi.getCases(suiteId)
    suiteCases.value = res.data
  } finally {
    casesLoading.value = false
  }
}

const deleteSuite = async (suite) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除套件 "${suite.name}" 吗？此操作将删除该套件下的所有用例。`,
      '警告',
      { type: 'warning' }
    )
    await suiteApi.delete(suite.id)
    ElMessage.success('删除成功')
    loadSuites()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('删除失败')
    }
  }
}

const showAddCase = () => {
  caseForm.value = {
    name: '',
    description: '',
    test_type: 'unit'
  }
  addCaseVisible.value = true
}

const submitAddCase = async () => {
  if (!caseForm.value.name) {
    ElMessage.warning('请输入用例名称')
    return
  }
  
  submitting.value = true
  try {
    await suiteApi.createCase(currentSuite.value.id, caseForm.value)
    ElMessage.success('添加成功')
    addCaseVisible.value = false
    loadSuiteCases(currentSuite.value.id)
    loadSuites()
  } catch (e) {
    console.error(e)
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}

const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用例 "${row.name}" 吗？`, '提示')
    await caseApi.delete(row.id)
    ElMessage.success('删除成功')
    loadSuiteCases(currentSuite.value.id)
    loadSuites()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('删除失败')
    }
  }
}

const getCategoryType = (category) => {
  const map = {
    'firmware': 'primary',
    'protocol': 'success',
    'performance': 'warning',
    'power': 'info'
  }
  return map[category] || ''
}

const getCategoryText = (category) => {
  const map = {
    'firmware': '固件测试',
    'protocol': '协议测试',
    'performance': '性能测试',
    'power': '电源测试'
  }
  return map[category] || category
}

const getTypeTag = (type) => {
  const map = {
    'unit': '',
    'integration': 'success',
    'system': 'warning',
    'performance': 'danger'
  }
  return map[type] || ''
}

onMounted(loadSuites)
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

.suite-card {
  margin-bottom: 12px;
}

.suite-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.suite-header h4 {
  margin: 0;
}

.suite-desc {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 16px;
  min-height: 40px;
}

.suite-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.case-count {
  color: #9ca3af;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.actions {
  display: flex;
  gap: 8px;
}

.cases-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.cases-header h4 {
  margin: 0;
}
</style>
