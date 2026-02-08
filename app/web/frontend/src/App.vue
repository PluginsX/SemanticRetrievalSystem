<template>
  <div id="app">
    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>语义检索系统</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/monitoring">
            <el-icon><Monitor /></el-icon>
            <span>系统监控</span>
          </el-menu-item>
          <el-menu-item index="/search">
            <el-icon><Search /></el-icon>
            <span>检索测试</span>
          </el-menu-item>
          <el-menu-item index="/data">
            <el-icon><Document /></el-icon>
            <span>资料管理</span>
          </el-menu-item>
          <el-menu-item index="/config">
            <el-icon><Tools /></el-icon>
            <span>网络配置</span>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Tickets /></el-icon>
            <span>日志系统</span>
          </el-menu-item>
          <el-menu-item index="/sqlite">
            <el-icon><Postcard /></el-icon>
            <span>SQLite管理</span>
          </el-menu-item>
          <el-menu-item index="/chromadb">
            <el-icon><TrendCharts /></el-icon>
            <span>ChromaDB管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 头部 -->
        <el-header class="header">
          <div class="header-content">
            <h1>{{ currentPageTitle }}</h1>
            <div class="header-actions">
              <el-button type="primary" @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-tag type="success">运行中</el-tag>
            </div>
          </div>
        </el-header>

        <!-- 页面内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    
    const pageTitleMap = {
      '/': '系统仪表板',
      '/dashboard': '系统仪表板',
      '/monitoring': '系统监控面板',
      '/search': '检索测试界面',
      '/data': '资料管理界面',
      '/config': '网络配置',
      '/logs': '日志系统',
      '/sqlite': 'SQLite数据库管理',
      '/chromadb': 'ChromaDB向量数据库管理'
    }
    
    const currentPageTitle = computed(() => {
      return pageTitleMap[route.path] || '语义检索系统'
    })
    
    const refreshData = () => {
      // 刷新当前页面数据
      window.location.reload()
    }
    
    return {
      currentPageTitle,
      refreshData
    }
  }
}
</script>

<style scoped>
.main-container {
  height: 100vh;
}

.sidebar {
  background-color: #2c3e50;
  color: white;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #34495e;
}

.logo h2 {
  color: white;
  margin: 0;
  font-size: 18px;
}

.sidebar-menu {
  border-right: none;
  background-color: #2c3e50;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #ecf0f1;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #34495e !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #3498db !important;
  color: white !important;
}

.header {
  background-color: white;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.main-content {
  background-color: #f5f5f5;
  padding: 20px;
}
</style>