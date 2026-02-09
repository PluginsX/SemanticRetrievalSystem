<template>
  <div class="monitoring-panel">
    <!-- 服务器控制按钮和系统信息 -->
    <el-row :gutter="20" class="server-control" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-card>
          <div class="control-container">
            <!-- 左侧按钮区域 -->
            <div class="control-buttons">
              <el-button type="danger" @click="restartServer" :loading="restarting">
                <el-icon><Refresh /></el-icon>
                重启服务器
              </el-button>
              <el-button type="warning" @click="shutdownServer" :loading="shuttingDown">
                <el-icon><Close /></el-icon>
                关闭服务器
              </el-button>
            </div>
            <!-- 右侧系统信息 -->
            <div class="system-info-compact">
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item label="应用名称">
                  {{ systemInfo.app_name || '语义检索系统' }}
                </el-descriptions-item>
                <el-descriptions-item label="版本">
                  {{ systemInfo.version || '1.0.0' }}
                </el-descriptions-item>
                <el-descriptions-item label="运行环境">
                  {{ systemInfo.environment || 'development' }}
                </el-descriptions-item>
                <el-descriptions-item label="运行时间">
                  {{ formatUptime(metrics.uptime) }}
                </el-descriptions-item>
                <el-descriptions-item label="平均响应时间">
                  {{ metrics.avg_response_time ? metrics.avg_response_time.toFixed(3) + 's' : 'N/A' }}
                </el-descriptions-item>
                <el-descriptions-item label="Python版本">
                  {{ systemInfo.python_version || 'Unknown' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

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

    <!-- 访问统计 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Histogram /></el-icon>
              <span>访问统计</span>
              <div class="chart-controls">
                <el-select v-model="timeRange" size="small" @change="updateChart">
                  <el-option label="最近7天" value="7d" />
                  <el-option label="最近30天" value="30d" />
                  <el-option label="最近90天" value="90d" />
                </el-select>
                <el-button type="primary" link @click="refreshChartData">
                  <el-icon><Refresh /></el-icon>
                  更新
                </el-button>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div ref="performanceChart" style="width: 100%; height: 200px;"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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
    const systemInfo = ref({})
    const timeRange = ref('7d')
    const restarting = ref(false)
    const shuttingDown = ref(false)
    const accessStats = ref({ dates: [], counts: [] })
    const performanceChart = ref(null)
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
        
        // 获取系统信息
        const infoData = await systemApi.getInfo()
        systemInfo.value = infoData
        
        // 获取访问量统计
        const days = timeRange.value === '7d' ? 7 : timeRange.value === '30d' ? 30 : 90
        const statsData = await systemApi.getAccessStats(days)
        if (statsData.success) {
          accessStats.value = statsData.data
          // 数据更新后更新图表
          updateChart()
        }
        
        // 模拟CPU和内存使用率（实际应从系统获取）
        cpuUsage.value = Math.floor(Math.random() * 30) + 40 // 40-70%
        memoryUsage.value = Math.floor(Math.random() * 20) + 60 // 60-80%
        
      } catch (error) {
        ElMessage.error('获取监控数据失败: ' + error.message)
      }
    }

    // 重启服务器
    const restartServer = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要重启服务器吗？重启过程中服务将暂时不可用。',
          '重启服务器',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        restarting.value = true
        ElMessage.info('正在重启服务器...')
        
        // 调用重启服务器API
        await systemApi.restartServer()
        
        ElMessage.success('服务器重启请求已发送，请等待服务重新启动')
        
        // 3秒后刷新页面
        setTimeout(() => {
          window.location.reload()
        }, 3000)
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('重启服务器失败: ' + error.message)
        }
      } finally {
        restarting.value = false
      }
    }

    // 关闭服务器
    const shutdownServer = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要关闭服务器吗？关闭后需要手动启动服务。',
          '关闭服务器',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        shuttingDown.value = true
        ElMessage.info('正在关闭服务器...')
        
        // 调用关闭服务器API
        await systemApi.shutdownServer()
        
        ElMessage.success('服务器关闭请求已发送')
        
        // 显示关闭提示
        ElMessageBox.alert(
          '服务器已关闭，需要手动启动服务。',
          '服务器已关闭',
          {
            confirmButtonText: '确定',
            callback: () => {
              // 可以跳转到其他页面或执行其他操作
            }
          }
        )
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('关闭服务器失败: ' + error.message)
        }
      } finally {
        shuttingDown.value = false
      }
    }

    const refreshServices = async () => {
      await loadData()
      ElMessage.success('服务状态已刷新')
    }

    const initChart = () => {
      if (performanceChart.value) {
        chartInstance = echarts.init(performanceChart.value)
        updateChart()
      }
    }

    const updateChart = async () => {
      if (!chartInstance) return
      
      // 确定显示的天数
      let days = 7
      if (timeRange.value === '30d') days = 30
      if (timeRange.value === '90d') days = 90
      
      // 检查当前数据是否匹配所需天数，如果不匹配则重新获取数据
      if (accessStats.value.dates.length !== days) {
        try {
          const statsData = await systemApi.getAccessStats(days)
          if (statsData.success) {
            accessStats.value = statsData.data
          }
        } catch (error) {
          ElMessage.error('获取访问统计数据失败: ' + error.message)
          return
        }
      }
      
      // 处理日期格式，只显示月/日
      const formattedDates = accessStats.value.dates.map(date => {
        const parts = date.split('-')
        return `${parts[1]}/${parts[2]}`
      })
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const date = accessStats.value.dates[params[0].dataIndex]
            return `${date}<br/>访问量: ${params[0].value}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: formattedDates,
          axisLine: { lineStyle: { color: '#e0e0e0' } },
          axisLabel: { 
            fontSize: 10, 
            color: '#666', 
            rotate: days > 14 ? 45 : 0 
          }
        },
        yAxis: {
          type: 'value',
          name: '访问量',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } }
        },
        series: [
          {
            name: '访问量',
            type: 'line',
            smooth: true,
            showSymbol: false,
            data: accessStats.value.counts,
            lineStyle: {
              color: '#409eff',
              width: 2,
              shadowColor: 'rgba(64, 158, 255, 0.3)',
              shadowBlur: 10,
              shadowOffsetY: 2
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(64, 158, 255, 0.4)'
                },
                {
                  offset: 0.5,
                  color: 'rgba(64, 158, 255, 0.15)'
                },
                {
                  offset: 1,
                  color: 'rgba(64, 158, 255, 0.05)'
                }
              ])
            },
            emphasis: {
              lineStyle: {
                color: '#3a8ee6',
                width: 3
              },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: 'rgba(64, 158, 255, 0.6)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(64, 158, 255, 0.1)'
                  }
                ])
              }
            }
          }
        ]
      }
      
      chartInstance.setOption(option)
    }

    const generateRandomData = (min, max, count) => {
      return Array.from({ length: count }, () => 
        Math.floor(Math.random() * (max - min + 1)) + min
      )
    }

    const refreshChartData = async () => {
      await updateChart()
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
      systemInfo,
      accessStats,
      timeRange,
      restarting,
      shuttingDown,
      performanceChart,
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
      refreshChartData,
      restartServer,
      shutdownServer
    }
  }
}
</script>

<style scoped>
.monitoring-panel {
  padding: 20px;
}

.server-control {
  margin-bottom: 20px;
}

.control-container {
  display: flex;
  align-items: stretch;
  gap: 20px;
}

.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: auto;
  min-width: 140px;
}

.control-buttons :deep(.el-button) {
  width: 100%;
  padding: 10px 15px;
  font-size: 14px;
  justify-content: center;
  margin-left: 0;
}

.control-buttons :deep(.el-button + .el-button) {
  margin-left: 0;
}

.system-info-compact {
    flex: 1;
    width: 90%;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: nowrap;
}

.system-info-compact :deep(.el-descriptions__table) {
  font-size: 13px;
}

.system-info-compact :deep(.el-descriptions__label) {
  padding: 8px 12px;
  width: 100px;
}

.system-info-compact :deep(.el-descriptions__content) {
  padding: 8px 12px;
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