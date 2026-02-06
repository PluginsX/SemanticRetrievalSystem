import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import DataManager from './views/DataManager.vue'
import MonitoringPanel from './views/MonitoringPanel.vue'
import SearchInterface from './views/SearchInterface.vue'
import NetworkConfig from './views/NetworkConfig.vue'
import LogSystem from './views/LogSystem.vue'

// 路由配置
const routes = [
  { path: '/', component: Dashboard },
  { path: '/dashboard', component: Dashboard },
  { path: '/monitoring', component: MonitoringPanel },
  { path: '/search', component: SearchInterface },
  { path: '/data', component: DataManager },
  { path: '/config', component: NetworkConfig },
  { path: '/logs', component: LogSystem }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 创建应用实例
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')