<template>
  <el-container class="layout">
    <!-- PC端侧边栏 -->
    <el-aside width="220px" class="sidebar desktop-sidebar">
      <div class="logo">
        <el-icon size="24"><Monitor /></el-icon>
        <span>测试平台</span>
      </div>
      
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
        background-color="#1e3a8a"
        text-color="#fff"
        active-text-color="#60a5fa"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-menu-item index="/plans">
          <el-icon><DocumentChecked /></el-icon>
          <span>测试计划</span>
        </el-menu-item>
        
        <el-menu-item index="/tasks">
          <el-icon><VideoPlay /></el-icon>
          <span>测试任务</span>
        </el-menu-item>
        
        <el-menu-item index="/suites">
          <el-icon><FolderOpened /></el-icon>
          <span>测试套件</span>
        </el-menu-item>
        
        <el-menu-item index="/about">
          <el-icon><InfoFilled /></el-icon>
          <span>关于</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 移动端抽屉侧边栏 -->
    <el-drawer
      v-model="mobileMenuVisible"
      :with-header="false"
      size="280px"
      direction="ltr"
      class="mobile-drawer"
    >
      <div class="mobile-menu-wrapper">
        <div class="logo">
          <el-icon size="24"><Monitor /></el-icon>
          <span>测试平台</span>
        </div>
        
        <el-menu
          :default-active="$route.path"
          router
          class="mobile-menu"
          background-color="#1e3a8a"
          text-color="#fff"
          active-text-color="#60a5fa"
          @select="mobileMenuVisible = false"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <el-menu-item index="/plans">
            <el-icon><DocumentChecked /></el-icon>
            <span>测试计划</span>
          </el-menu-item>
          
          <el-menu-item index="/tasks">
            <el-icon><VideoPlay /></el-icon>
            <span>测试任务</span>
          </el-menu-item>
          
          <el-menu-item index="/suites">
            <el-icon><FolderOpened /></el-icon>
            <span>测试套件</span>
          </el-menu-item>
          
          <el-menu-item index="/about">
            <el-icon><InfoFilled /></el-icon>
            <span>关于</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-drawer>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-button 
            class="mobile-menu-btn"
            text
            @click="mobileMenuVisible = true"
          >
            <el-icon size="22"><Fold /></el-icon>
          </el-button>
          <h2>{{ $route.meta.title || '固件自动化测试平台' }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const mobileMenuVisible = ref(false)

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
      // 取消
    }
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

/* PC端侧边栏 */
.desktop-sidebar {
  background: #1e3a8a;
  color: white;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}

.sidebar::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: #1e3a8a;
  color: white;
}

.menu {
  border-right: none;
}

.menu :deep(.el-menu-item) {
  font-size: 17px;
  height: 54px;
  line-height: 54px;
}

.menu :deep(.el-menu-item .el-icon) {
  font-size: 20px;
  margin-right: 12px;
}

.header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 50px;
  padding: 0 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.mobile-menu-btn {
  display: none;
  padding: 8px;
  color: #4b5563;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #4b5563;
}

.main {
  background: #f3f4f6;
  padding: 16px;
  margin-left: 220px;
  min-height: calc(100vh - 50px);
}

/* 移动端抽屉样式 */
.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: #1e3a8a;
}

.mobile-menu-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e3a8a;
}

.mobile-menu {
  flex: 1;
  border-right: none;
}

.mobile-menu :deep(.el-menu-item) {
  font-size: 17px;
  height: 56px;
  line-height: 56px;
  padding-left: 24px;
}

.mobile-menu :deep(.el-menu-item .el-icon) {
  font-size: 20px;
  margin-right: 12px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .desktop-sidebar {
    display: none;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .main {
    margin-left: 0;
    padding: 12px;
  }
  
  .header-left h2 {
    font-size: 16px;
  }
}
</style>
