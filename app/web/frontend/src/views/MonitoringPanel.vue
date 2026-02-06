<template>
  <div class="monitoring-panel">
    <!-- 实时监控卡片 -->
    <el-row :gutter="20" class="monitoring-cards">
      <el-col :span="8">
        <el-card class="monitoring-card cpu-card">
          <template #header>
            <div class="card-header">
              <el-icon><Cpu /></el-icon>
              <span>CPU使用率</span>
            </div>
          </template>
          <div class="metric-display">
            <div class="metric-value">{{ cpuUsage }}%</div>
            <el-progress :percentage="cpuUsage" :stroke-width="12" :color="getCpuColor(cpuUsage)" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="monitoring-card memory-card">
          <template #header>
            <div class="card-header">
              <el-icon><Box /></el-icon>
              <span>内存使用率</span>
            </div>
          </template>
          <div class="metric-display">
            <div class="metric-value">{{ memoryUsage }}%</div>
            <el-progress :percentage="memoryUsage" :stroke-width="12" :color="getMemoryColor(memoryUsage)" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="monitoring-card response-card">
          <template #header>
            <div class="card-header">
              <el-icon><Timer /></el-icon>
              <span>响应时间</span>
            </div>
          </template>
          <div class="metric-display">
            <div class="metric-value">{{ avgResponseTime }}ms</div>
            <div class="response-status" :class="getResponseClass(avgResponseTime)">
              {{ getResponseStatus(avgResponseTime) }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务状态监控 -->
    <el-row :gutter="20" class="service-monitoring">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>服务状态</span>
              <el-button type="primary" link @click="refreshServices">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="service-list">
            <div class="service-item" v-for="(status, service) in serviceStatus" :key="service">
              <div class="service-info">
                <el-icon :class="getServiceIconClass(status)">
                  <CircleCheck v-if="status === 'healthy'" />
                  <CircleClose v-else-if="status === 'unhealthy'" />
                  <Warning v-else />
                </el-icon>
                <span class="service-name">{{ getServiceName(service) }}</span>
              </div>
              <el-tag :type="getStatusType(status)" size="small">
                {{ getServiceStatusText(status) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>数据库统计</span>
            </div>
          </template>
          <div class="database-stats">
            <div class="stat-item">
              <span class="stat-label">资料总数:</span>
              <span class="stat-value">{{ metrics.artifact_count || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">切片数量:</span>
              <span class="stat-value">{{ metrics.chunk_count || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">检索记录:</span>
              <span class="stat-value">{{ metrics.search_count || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">运行时间:</span>
              <span class="stat-value">{{ formatUptime(metrics.uptime) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 性能图表区域 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Histogram /></el-icon>
              <span>性能趋势</span>
              <div class="chart-controls">
                <el-select v-model="timeRange" size="small" @change="updateChart">
                  <el-option label="最近1小时" value="1h" />
                  <el-option label="最近6小时" value="6h" />
                  <el-option label="最近24小时" value="24h" />
                </el-select>
                <el-button type="primary" link @click="refreshChartData">
                  <el-icon><Refresh /></el-icon>
                  更新
                </el-button>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div ref="performanceChart" style="width: 100%; height: 400px;"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { systemApi } from '@/api'

export default {
  name: 'MonitoringPanel',
  setup() {
    const cpuUsage = ref(0)
    const memoryUsage = ref(0)
    const avgResponseTime = ref(0)
    const serviceStatus = ref({})
    const metrics = ref({})
    const timeRange = ref('1h')
    let chartInstance = null
    let refreshInterval = null

    const getCpuColor = (usage) => {
      if (usage < 70) return '#67c23a'
      if (usage < 85) return '#e6a23c'
      return '#f56c6c'
    }

    const getMemoryColor = (usage) => {
      if (usage < 80) return '#409eff'
      if (usage < 90) return '#e6a23c'
      return '#f56c6c'
    }

    const getResponseClass = (time) => {
      if (time < 200) return 'excellent'
      if (time < 500) return 'good'
      if (time < 1000) return 'warning'
      return 'poor'
    }

    const getResponseStatus = (time) => {
      if (time < 200) return '优秀'
      if (time < 500) return '良好'
      if (time < 1000) return '一般'
      return '较差'
    }

    const getServiceName = (serviceKey) => {
      const serviceNames = {
        'database': 'SQLite数据库',
        'vector_store': 'Chroma向量库',
        'llm_service': '大语言模型',
        'embedding_service': '向量编码服务'
      }
      return serviceNames[serviceKey] || serviceKey
    }

    const getServiceIconClass = (status) => {
      return status === 'healthy' ? 'status-success' : 'status-error'
    }

    const getStatusType = (status) => {
      const statusTypes = {
        'healthy': 'success',
        'unhealthy': 'danger',
        'configured': 'warning',
        'unavailable': 'info'
      }
      return statusTypes[status] || 'info'
    }

    const getServiceStatusText = (status) => {
      const statusTexts = {
        'healthy': '正常',
        'unhealthy': '异常',
        'configured': '已配置',
        'unavailable': '不可用'
      }
      return statusTexts[status] || status
    }

    const formatUptime = (seconds) => {
      if (!seconds) return 'N/A'
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (days > 0) return `${days}天${hours}小时`
      if (hours > 0) return `${hours}小时${minutes}分钟`
      return `${minutes}分钟`
    }

    const loadData = async () => {
      try {
        // 获取健康状态
        const healthData = await systemApi.getHealth()
        serviceStatus.value = healthData.services || {}
        
        // 获取系统指标
        const metricsData = await systemApi.getMetrics()
        metrics.value = metricsData
        avgResponseTime.value = Math.round((metricsData.avg_response_time || 0) * 1000)
        
        // 模拟CPU和内存使用率（实际应从系统获取）
        cpuUsage.value = Math.floor(Math.random() * 30) + 40 // 40-70%
        memoryUsage.value = Math.floor(Math.random() * 20) + 60 // 60-80%
        
      } catch (error) {
        ElMessage.error('获取监控数据失败: ' + error.message)
      }
    }

    const refreshServices = async () => {
      await loadData()
      ElMessage.success('服务状态已刷新')
    }

    const initChart = () => {
      const chartDom = document.querySelector('[ref="performanceChart"]')
      if (chartDom) {
        chartInstance = echarts.init(chartDom)
        updateChart()
      }
    }

    const updateChart = () => {
      if (!chartInstance) return
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['CPU使用率', '内存使用率', '响应时间(ms)']
        },
        xAxis: {
          type: 'category',
          data: generateTimePoints()
        },
        yAxis: [
          {
            type: 'value',
            name: '使用率(%)',
            min: 0,
            max: 100
          },
          {
            type: 'value',
            name: '响应时间(ms)',
            min: 0,
            max: 2000
          }
        ],
        series: [
          {
            name: 'CPU使用率',
            type: 'line',
            data: generateRandomData(0, 100, 20),
            smooth: true
          },
          {
            name: '内存使用率',
            type: 'line',
            data: generateRandomData(60, 90, 20),
            smooth: true
          },
          {
            name: '响应时间(ms)',
            type: 'line',
            yAxisIndex: 1,
            data: generateRandomData(50, 800, 20),
            smooth: true
          }
        ]
      }
      
      chartInstance.setOption(option)
    }

    const generateTimePoints = () => {
      const points = []
      const now = new Date()
      for (let i = 19; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 300000) // 每5分钟一个点
        points.push(time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }))
      }
      return points
    }

    const generateRandomData = (min, max, count) => {
      return Array.from({ length: count }, () => 
        Math.floor(Math.random() * (max - min + 1)) + min
      )
    }

    const refreshChartData = () => {
      updateChart()
      ElMessage.success('图表数据已更新')
    }

    onMounted(() => {
      loadData()
      initChart()
      
      // 设置定时刷新
      refreshInterval = setInterval(loadData, 30000) // 30秒刷新一次
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
      if (chartInstance) {
        chartInstance.dispose()
      }
    })

    return {
      cpuUsage,
      memoryUsage,
      avgResponseTime,
      serviceStatus,
      metrics,
      timeRange,
      getCpuColor,
      getMemoryColor,
      getResponseClass,
      getResponseStatus,
      getServiceName,
      getServiceIconClass,
      getStatusType,
      getServiceStatusText,
      formatUptime,
      refreshServices,
      updateChart,
      refreshChartData
    }
  }
}
</script>

<style scoped>
.monitoring-panel {
  padding: 20px;
}

.monitoring-cards {
  margin-bottom: 20px;
}

.monitoring-card {
  height: 180px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
}

.metric-display {
  text-align: center;
  padding: 0;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 0px;
  color: #303133;
}

.response-status {
  font-size: 14px;
  margin-top: 0px;
  padding: 4px 12px;
  border-radius: 4px;
}

.response-status.excellent {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #67c23a;
}

.response-status.good {
  background-color: #f0f9ff;
  color: #409eff;
  border: 1px solid #409eff;
}

.response-status.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #e6a23c;
}

.response-status.poor {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #f56c6c;
}

.service-monitoring {
  margin-bottom: 20px;
}

.service-list {
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  background-color: #fafafa;
}

.service-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.service-name {
  font-size: 14px;
  color: #606266;
}

.status-success {
  color: #67c23a;
}

.status-error {
  color: #f56c6c;
}

.database-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-container {
  margin-top: 20px;
}
</style>