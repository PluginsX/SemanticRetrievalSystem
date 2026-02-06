<template>
  <div class="log-system">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志系统</span>
          <div class="header-actions">
            <el-button @click="clearDatabaseLogs" type="danger" size="small">清空数据库日志</el-button>
            <el-button @click="clearServerLogs" type="danger" size="small">清空服务器日志</el-button>
            <el-button @click="refreshLogs" type="primary" size="small">刷新</el-button>
          </div>
        </div>
      </template>
      
      <div class="logs-container">
        <el-row :gutter="20">
          <!-- 数据库日志 -->
          <el-col :span="12">
            <div class="log-panel database-log">
              <div class="panel-header">
                <h3>数据库日志</h3>
                <el-tag type="info" size="small">{{ dbLogLines.length }} 行</el-tag>
              </div>
              <div class="log-content" ref="dbLogRef">
                <div 
                  v-for="(log, index) in dbLogLines" 
                  :key="'db-' + index" 
                  class="log-line"
                  @dblclick="selectLogLine(log)"
                >
                  {{ log }}
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- 服务器日志 -->
          <el-col :span="12">
            <div class="log-panel server-log">
              <div class="panel-header">
                <h3>服务器日志</h3>
                <el-tag type="info" size="small">{{ serverLogLines.length }} 行</el-tag>
              </div>
              <div class="log-content" ref="serverLogRef">
                <div 
                  v-for="(log, index) in serverLogLines" 
                  :key="'server-' + index" 
                  class="log-line"
                  @dblclick="selectLogLine(log)"
                >
                  {{ log }}
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { systemApi } from '@/api'

export default {
  name: 'LogSystem',
  setup() {
    const dbLogLines = ref([])
    const serverLogLines = ref([])
    const dbLogRef = ref(null)
    const serverLogRef = ref(null)
    
    // 加载日志数据
    const loadLogs = async () => {
      try {
        // 加载数据库日志
        const dbResponse = await systemApi.getLogData('database')
        dbLogLines.value = dbResponse.logs || []
        
        // 加载服务器日志
        const serverResponse = await systemApi.getLogData('server')
        serverLogLines.value = serverResponse.logs || []
        
        // 自动滚动到底部
        await nextTick()
        scrollToBottom()
      } catch (error) {
        console.error('加载日志失败:', error)
        ElMessage.error('加载日志失败: ' + error.message)
      }
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (dbLogRef.value) {
        dbLogRef.value.scrollTop = dbLogRef.value.scrollHeight
      }
      if (serverLogRef.value) {
        serverLogRef.value.scrollTop = serverLogRef.value.scrollHeight
      }
    }
    
    // 选择日志行
    const selectLogLine = (logLine) => {
      const textArea = document.createElement('textarea')
      textArea.value = logLine
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      ElMessage.success('已复制到剪贴板')
    }
    
    // 清空数据库日志
    const clearDatabaseLogs = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要清空所有数据库日志吗？此操作不可恢复。',
          '确认清空',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 调用API清空数据库日志
        await systemApi.clearLog('database')
        dbLogLines.value = []
        ElMessage.success('数据库日志已清空')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('清空数据库日志失败:', error)
          ElMessage.error('清空数据库日志失败: ' + error.message)
        }
        // 用户取消操作时不显示错误
      }
    }
    
    // 清空服务器日志
    const clearServerLogs = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要清空所有服务器日志吗？此操作不可恢复。',
          '确认清空',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 调用API清空服务器日志
        await systemApi.clearLog('server')
        serverLogLines.value = []
        ElMessage.success('服务器日志已清空')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('清空服务器日志失败:', error)
          ElMessage.error('清空服务器日志失败: ' + error.message)
        }
        // 用户取消操作时不显示错误
      }
    }
    
    // 刷新日志
    const refreshLogs = () => {
      loadLogs()
    }
    
    onMounted(() => {
      loadLogs()
    })
    
    return {
      dbLogLines,
      serverLogLines,
      dbLogRef,
      serverLogRef,
      loadLogs,
      scrollToBottom,
      selectLogLine,
      clearDatabaseLogs,
      clearServerLogs,
      refreshLogs
    }
  }
}
</script>

<style scoped>
.log-system {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.logs-container {
  height: calc(100vh - 200px);
}

.log-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.log-line {
  margin-bottom: 2px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.log-line:hover {
  background-color: #333;
  border-radius: 2px;
}

/* 为不同类型的日志添加颜色 */
.log-line:contains('ERROR') {
  color: #f56c6c;
}

.log-line:contains('WARN') {
  color: #e6a23c;
}

.log-line:contains('INFO') {
  color: #909399;
}
</style>

<style>
/* 添加全局样式以支持日志行的颜色标记 */
.log-content .log-line {
  /* 默认文本颜色 */
}

.log-content .log-line:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
</style>