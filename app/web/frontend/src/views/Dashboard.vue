<template>
  <div class="dashboard">
    <!-- 服务器控制按钮 -->
    <el-row :gutter="20" class="server-control" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-card>
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
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 系统状态概览 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon status-success">
              <el-icon size="32"><Monitor /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">系统状态</div>
              <div class="card-value">{{ systemStatus }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon status-info">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">资料总数</div>
              <div class="card-value">{{ metrics.artifact_count || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon status-warning">
              <el-icon size="32"><Coin /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">切片数量</div>
              <div class="card-value">{{ metrics.chunk_count || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon status-primary">
              <el-icon size="32"><Search /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">检索次数</div>
              <div class="card-value">{{ metrics.search_count || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作和服务状态 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="actions-grid">
            <el-button type="primary" @click="$router.push('/monitoring')">
              <el-icon><Monitor /></el-icon>
              系统监控
            </el-button>
            <el-button type="success" @click="$router.push('/search')">
              <el-icon><Search /></el-icon>
              检索测试
            </el-button>
            <el-button type="warning" @click="$router.push('/data')">
              <el-icon><Document /></el-icon>
              资料管理
            </el-button>
            <el-button type="info" @click="reindexVectors">
              <el-icon><Refresh /></el-icon>
              重建索引
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>服务状态</span>
            </div>
          </template>
          <div class="service-status">
            <div class="status-item" v-for="(status, service) in serviceStatus" :key="service">
              <span class="service-name">{{ getServiceName(service) }}</span>
              <el-tag :type="getStatusType(status)">
                {{ status }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统信息 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          <el-descriptions :column="3" border>
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
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { systemApi } from '@/api'

export default {
  name: 'Dashboard',
  setup() {
    const metrics = ref({})
    const systemInfo = ref({})
    const serviceStatus = ref({})
    const systemStatus = ref('未知')
    const restarting = ref(false)
    const shuttingDown = ref(false)

    const getServiceName = (serviceKey) => {
      const serviceNames = {
        'database': '数据库',
        'vector_store': '向量存储',
        'llm_service': '大语言模型',
        'embedding_service': '向量编码服务'
      }
      return serviceNames[serviceKey] || serviceKey
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

    const formatUptime = (seconds) => {
      if (!seconds) return 'N/A'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}小时${minutes}分钟`
    }

    const loadData = async () => {
      try {
        // 获取健康状态
        const healthData = await systemApi.getHealth()
        serviceStatus.value = healthData.services || {}
        systemStatus.value = healthData.status === 'healthy' ? '正常运行' : '存在问题'
        
        // 获取系统指标
        const metricsData = await systemApi.getMetrics()
        metrics.value = metricsData
        
        // 获取系统信息
        const infoData = await systemApi.getInfo()
        systemInfo.value = infoData
        
      } catch (error) {
        ElMessage.error('获取系统数据失败: ' + error.message)
      }
    }

    const reindexVectors = async () => {
      try {
        await systemApi.reindexVectors()
        ElMessage.success('向量索引重建请求已发送')
      } catch (error) {
        ElMessage.error('重建索引失败: ' + error.message)
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

    onMounted(() => {
      loadData()
    })

    return {
      metrics,
      systemInfo,
      serviceStatus,
      systemStatus,
      restarting,
      shuttingDown,
      getServiceName,
      getStatusType,
      formatUptime,
      reindexVectors,
      restartServer,
      shutdownServer
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.overview-card {
  height: 120px;
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  color: white;
}

.status-success {
  background-color: #67c23a;
}

.status-info {
  background-color: #409eff;
}

.status-warning {
  background-color: #e6a23c;
}

.status-primary {
  background-color: #909399;
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.quick-actions {
  margin-bottom: 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.actions-grid .el-button {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin-left: 0 !important;
  width: 100%;
}

.service-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-name {
  font-size: 14px;
  color: #606266;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.control-buttons {
  display: flex;
  gap: 15px;
}

.control-buttons .el-button {
  padding: 10px 20px;
  font-size: 14px;
}

.server-control {
  margin-bottom: 20px;
}
</style>