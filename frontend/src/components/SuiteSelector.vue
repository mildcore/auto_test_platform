<template>
  <div class="suite-selector">
    <div class="selector-header">
      <span>
        已选 <strong>{{ selectedSuites.length }}</strong> 个套件，
        <strong>{{ selectedCases.length }}</strong> 个用例
      </span>
      <el-button v-if="selectedSuites.length > 0" link @click="clearAll">
        清空选择
      </el-button>
    </div>
    
    <div class="selector-body">
      <!-- 第一列：套件列表 (30%) -->
      <div class="column suite-column">
        <div class="column-title">测试套件</div>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else class="list-content">
          <div
            v-for="suite in suites"
            :key="suite.id"
            :class="['suite-item', { active: activeSuiteId === suite.id }]"
            @click="selectSuite(suite)"
          >
            <el-checkbox
              :model-value="isSuiteSelected(suite.id)"
              @change="(val) => toggleSuite(suite, val)"
              @click.stop
            />
            <span class="suite-name">{{ suite.name }}</span>
            <el-tag size="small" type="info">{{ suite.case_count || 0 }}</el-tag>
          </div>
        </div>
      </div>
      
      <!-- 第二列：当前套件用例 (35%) -->
      <div class="column case-column">
        <div class="column-title">
          {{ activeSuite ? activeSuite.name : '请选择套件' }}
        </div>
        <div v-if="!activeSuite" class="empty-tip">
          点击左侧套件查看用例
        </div>
        <div v-else-if="suiteCases.length === 0" class="empty-tip">
          该套件下暂无测试用例
        </div>
        <div v-else class="list-content">
          <div
            v-for="caseItem in suiteCases"
            :key="caseItem.id"
            :class="['case-item', { selected: isCaseSelected(caseItem.id) }]"
          >
            <el-checkbox
              :model-value="isCaseSelected(caseItem.id)"
              @change="(val) => toggleCase(caseItem, val)"
            />
            <span class="case-name">{{ caseItem.name }}</span>
            <el-tag size="small" :type="getTypeTag(caseItem.test_type)">
              {{ caseItem.test_type }}
            </el-tag>
          </div>
        </div>
      </div>
      
      <!-- 第三列：已选用例 (35%) -->
      <div class="column selected-column">
        <div class="column-title">
          已选用例
          <span class="subtitle">（共 {{ orderedSelectedCases.length }} 个）</span>
        </div>
        <div v-if="orderedSelectedCases.length === 0" class="empty-tip">
          请在左侧选择用例
        </div>
        <div v-else class="list-content">
          <div
            v-for="(caseItem, index) in orderedSelectedCases"
            :key="caseItem.id"
            class="case-item selected"
          >
            <span class="case-index">{{ index + 1 }}</span>
            <div class="case-info">
              <div class="case-name">{{ caseItem.name }}</div>
              <div class="case-suite">{{ caseItem.suite_name }}</div>
            </div>
            <div class="sort-buttons">
              <el-button 
                link 
                size="small" 
                :disabled="index === 0"
                @click="moveCaseToTop(caseItem.id)"
                title="移到顶部"
              >
                <el-icon><Upload /></el-icon>
              </el-button>
              <el-button 
                link 
                size="small" 
                :disabled="index === 0"
                @click="moveCase(caseItem.id, -1)"
                title="上移"
              >
                <el-icon><SortUp /></el-icon>
              </el-button>
              <el-button 
                link 
                size="small" 
                :disabled="index === orderedSelectedCases.length - 1"
                @click="moveCase(caseItem.id, 1)"
                title="下移"
              >
                <el-icon><SortDown /></el-icon>
              </el-button>
              <el-button 
                link 
                size="small" 
                :disabled="index === orderedSelectedCases.length - 1"
                @click="moveCaseToBottom(caseItem.id)"
                title="移到底部"
              >
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button 
                link 
                size="small" 
                type="danger"
                @click="removeCase(caseItem.id)"
                title="移除"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { suiteApi } from '@/api/suite'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ suite_ids: [], case_ids: [] })
  }
})

const emit = defineEmits(['update:modelValue'])

// 本地状态
const suites = ref([])
const activeSuiteId = ref(null)
const allCases = ref({})  // { suiteId: [cases] }
const caseMap = ref({}) // { caseId: caseItem }
const loading = ref(false)

// 选中的数据
const selectedSuites = computed(() => props.modelValue.suite_ids || [])
const selectedCases = computed(() => props.modelValue.case_ids || [])

// 当前选中的套件
const activeSuite = computed(() => {
  return suites.value.find(s => s.id === activeSuiteId.value) || null
})

// 当前套件的用例
const suiteCases = computed(() => {
  if (!activeSuiteId.value) return []
  return allCases.value[activeSuiteId.value] || []
})

// 所有已选的用例（按 case_ids 的顺序）
const orderedSelectedCases = computed(() => {
  return selectedCases.value
    .map(id => caseMap.value[id])
    .filter(Boolean)  // 过滤掉未加载的
})

// 加载套件
const loadSuites = async () => {
  loading.value = true
  try {
    const res = await suiteApi.getList({ per_page: 100 })
    suites.value = res.data.items || res.data
    
    // 预加载所有用例
    for (const suite of suites.value) {
      const casesRes = await suiteApi.getCases(suite.id)
      allCases.value[suite.id] = casesRes.data || []
      casesRes.data.forEach(c => {
        caseMap.value[c.id] = { ...c, suite_name: suite.name, suite_id: suite.id }
      })
    }
  } finally {
    loading.value = false
  }
}

// 选中套件（点击行）
const selectSuite = (suite) => {
  activeSuiteId.value = suite.id
}

// 判断是否选中套件
const isSuiteSelected = (suiteId) => {
  return selectedSuites.value.includes(suiteId)
}

// 判断是否选中用例
const isCaseSelected = (caseId) => {
  return selectedCases.value.includes(caseId)
}

// 切换套件选择
const toggleSuite = (suite, checked) => {
  const suiteIds = [...selectedSuites.value]
  const caseIds = [...selectedCases.value]
  const suiteCaseIds = (allCases.value[suite.id] || []).map(c => c.id)
  
  if (checked) {
    // 勾选套件：添加套件，并将其所有用例按顺序添加到 case_ids
    if (!suiteIds.includes(suite.id)) {
      suiteIds.push(suite.id)
    }
    // 添加该套件的所有用例（保持原有顺序）
    suiteCaseIds.forEach(id => {
      if (!caseIds.includes(id)) {
        caseIds.push(id)
      }
    })
  } else {
    // 取消勾选套件：移除套件，并取消其所有用例
    const index = suiteIds.indexOf(suite.id)
    if (index > -1) suiteIds.splice(index, 1)
    
    // 从 case_ids 中移除该套件的所有用例
    const newCaseIds = caseIds.filter(id => !suiteCaseIds.includes(id))
    
    emit('update:modelValue', {
      suite_ids: suiteIds,
      case_ids: newCaseIds
    })
    return
  }
  
  activeSuiteId.value = suite.id
  emit('update:modelValue', {
    suite_ids: suiteIds,
    case_ids: caseIds
  })
}

// 切换用例选择
const toggleCase = (caseItem, checked) => {
  const suiteIds = [...selectedSuites.value]
  let caseIds = [...selectedCases.value]
  
  if (checked) {
    // 勾选用例：添加到 case_ids 末尾
    if (!caseIds.includes(caseItem.id)) {
      caseIds.push(caseItem.id)
    }
    // 确保套件被选中
    if (!suiteIds.includes(caseItem.suite_id)) {
      suiteIds.push(caseItem.suite_id)
    }
  } else {
    // 取消勾选用例：从 case_ids 中移除
    return removeCase(caseItem.id)
  }
  
  emit('update:modelValue', {
    suite_ids: suiteIds,
    case_ids: caseIds
  })
}

// 移动用例顺序（上移/下移一格）
const moveCase = (caseId, direction) => {
  const caseIds = [...selectedCases.value]
  const index = caseIds.indexOf(caseId)
  if (index === -1) return
  
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= caseIds.length) return
  
  // 交换位置
  [caseIds[index], caseIds[newIndex]] = [caseIds[newIndex], caseIds[index]]
  
  emit('update:modelValue', {
    suite_ids: [...selectedSuites.value],
    case_ids: caseIds
  })
}

// 移动用例到顶部
const moveCaseToTop = (caseId) => {
  const caseIds = [...selectedCases.value]
  const index = caseIds.indexOf(caseId)
  if (index <= 0) return
  
  // 移除当前位置并插入到顶部
  caseIds.splice(index, 1)
  caseIds.unshift(caseId)
  
  emit('update:modelValue', {
    suite_ids: [...selectedSuites.value],
    case_ids: caseIds
  })
}

// 移动用例到底部
const moveCaseToBottom = (caseId) => {
  const caseIds = [...selectedCases.value]
  const index = caseIds.indexOf(caseId)
  if (index === -1 || index === caseIds.length - 1) return
  
  // 移除当前位置并插入到底部
  caseIds.splice(index, 1)
  caseIds.push(caseId)
  
  emit('update:modelValue', {
    suite_ids: [...selectedSuites.value],
    case_ids: caseIds
  })
}

// 移除用例
const removeCase = (caseId) => {
  const caseIds = selectedCases.value.filter(id => id !== caseId)
  let suiteIds = [...selectedSuites.value]

  const suiteID = caseMap.value[caseId]?.suite_id
  const suiteCaseIds = (allCases.value[suiteID] || []).map(c => c.id)
  const selectedCaseIdsInSuite = caseIds.filter(id => suiteCaseIds.includes(id))

  if (selectedCaseIdsInSuite.length <= 0) {
    suiteIds = suiteIds.filter(id => id !== suiteID)
  }
  
  emit('update:modelValue', {
    suite_ids: suiteIds,
    case_ids: caseIds
  })
}

// 清空选择
const clearAll = () => {
  activeSuiteId.value = null
  emit('update:modelValue', { suite_ids: [], case_ids: [] })
}

// 获取测试类型标签样式
const getTypeTag = (type) => {
  const map = {
    'unit': '',
    'integration': 'success',
    'system': 'warning',
    'performance': 'danger'
  }
  return map[type] || ''
}

// 初始化
loadSuites()
</script>

<style scoped>
.suite-selector {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.selector-body {
  display: flex;
  height: 450px;
}

/* 三列布局比例 3:3.5:3.5 */
.suite-column {
  width: 30%;
  flex: 0 0 30%;
  border-right: 1px solid #e5e7eb;
}

.case-column {
  width: 35%;
  flex: 0 0 35%;
  border-right: 1px solid #e5e7eb;
}

.selected-column {
  width: 35%;
  flex: 0 0 35%;
}

.column-title {
  padding: 12px 16px;
  font-weight: 600;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.column-title .subtitle {
  font-weight: normal;
  color: #6b7280;
  font-size: 12px;
}

.list-content {
  padding: 8px;
  overflow-y: auto;
  height: calc(100% - 45px);
}

.suite-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 4px;
  cursor: pointer;
  gap: 8px;
}

.suite-item:hover {
  background: #f3f4f6;
}

.suite-item.active {
  background: #eff6ff;
}

.suite-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.case-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 4px;
  gap: 8px;
}

.case-item:hover {
  background: #f3f4f6;
}

.case-item.selected {
  background: #eff6ff;
}

.case-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.case-info {
  flex: 1;
  min-width: 0;
}

.case-name {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.case-suite {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.sort-buttons {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.loading, .empty-tip {
  padding: 40px;
  text-align: center;
  color: #9ca3af;
}
</style>
