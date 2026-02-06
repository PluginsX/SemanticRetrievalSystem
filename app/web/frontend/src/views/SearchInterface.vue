<template>
  <div class="search-interface">
    <el-row :gutter="20">
      <!-- 检索配置面板 -->
      <el-col :span="8">
        <el-card class="config-panel">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>检索配置</span>
            </div>
          </template>
          
          <el-form :model="searchConfig" label-width="100px">
            <el-form-item label="检索关键词">
              <el-input
                v-model="searchConfig.query"
                placeholder="请输入检索关键词"
                @keyup.enter="performSearch"
              >
                <template #suffix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="返回数量">
              <el-slider
                v-model="searchConfig.top_k"
                :min="1"
                :max="20"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="相似度阈值">
              <el-slider
                v-model="searchConfig.threshold"
                :min="0"
                :max="1"
                :step="0.1"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="分类筛选">
              <el-select
                v-model="searchConfig.category_filter"
                multiple
                placeholder="选择分类"
                style="width: 100%"
              >
                <el-option label="技术文档" value="技术文档" />
                <el-option label="产品说明" value="产品说明" />
                <el-option label="用户手册" value="用户手册" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                @click="performSearch"
                :loading="searching"
                style="width: 100%"
              >
                <el-icon><Search /></el-icon>
                执行检索
              </el-button>
            </el-form-item>
          </el-form>
          
          <!-- 搜索历史 -->
          <div class="search-history">
            <h4>最近搜索</h4>
            <div class="history-list">
              <div
                v-for="history in searchHistory"
                :key="history.id"
                class="history-item"
                @click="loadHistory(history)"
              >
                {{ history.query }}
                <span class="history-time">{{ formatHistoryTime(history.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 检索结果面板 -->
      <el-col :span="16">
        <el-card class="results-panel">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>检索结果</span>
              <div class="result-summary" v-if="searchResults.length > 0">
                找到 {{ searchResults.length }} 条相关资料，耗时 {{ responseTime }}ms
              </div>
            </div>
          </template>
          
          <div v-if="searching" class="loading-results">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item variant="p" style="width: 60%" />
                <div style="margin-top: 20px">
                  <el-skeleton-item variant="p" style="width: 100%" />
                  <el-skeleton-item variant="p" style="width: 80%; margin-top: 10px" />
                </div>
              </template>
            </el-skeleton>
          </div>
          
          <div v-else-if="searchResults.length === 0 && hasSearched" class="no-results">
            <el-empty description="没有找到相关资料" />
          </div>
          
          <div v-else class="results-list">
            <div
              v-for="(result, index) in searchResults"
              :key="result.id"
              class="result-item"
            >
              <div class="result-header">
                <div class="result-title">
                  <el-tag type="primary" size="small">{{ index + 1 }}</el-tag>
                  {{ result.title }}
                </div>
                <div class="result-score">
                  <el-tag :type="getScoreType(result.similarity)">
                    相似度: {{ (result.similarity * 100).toFixed(1) }}%
                  </el-tag>
                </div>
              </div>
              
              <div class="result-meta">
                <el-tag size="small">{{ result.category || '未分类' }}</el-tag>
                <span class="result-time">{{ formatDate(result.created_at) }}</span>
              </div>
              
              <div class="result-content">
                {{ truncateText(result.content, 200) }}
              </div>
              
              <div v-if="result.chunks && result.chunks.length > 0" class="result-chunks">
                <div class="chunks-title">相关片段:</div>
                <div
                  v-for="chunk in result.chunks"
                  :key="chunk.chunk_id"
                  class="chunk-item"
                >
                  <div class="chunk-score">
                    <el-tag type="info" size="small">
                      片段相似度: {{ (chunk.similarity * 100).toFixed(1) }}%
                    </el-tag>
                  </div>
                  <div class="chunk-content">{{ chunk.content }}</div>
                </div>
              </div>
              
              <div class="result-actions">
                <el-button link type="primary" @click="viewFullContent(result)">
                  查看全文
                </el-button>
                <el-button link type="primary" @click="copyContent(result.content)">
                  复制内容
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 全文查看对话框 -->
    <el-dialog
      v-model="showFullContent"
      :title="selectedResult?.title"
      width="800px"
    >
      <div v-if="selectedResult" class="full-content">
        <div class="content-meta">
          <el-tag>{{ selectedResult.category || '未分类' }}</el-tag>
          <span class="content-time">{{ formatDate(selectedResult.created_at) }}</span>
        </div>
        <div class="content-body">
          {{ selectedResult.content }}
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showFullContent = false">关闭</el-button>
          <el-button type="primary" @click="copyFullContent">复制全文</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { searchApi } from '@/api'

export default {
  name: 'SearchInterface',
  setup() {
    const searching = ref(false)
    const hasSearched = ref(false)
    const searchResults = ref([])
    const responseTime = ref(0)
    const showFullContent = ref(false)
    const selectedResult = ref(null)
    const searchHistory = ref([
      { id: 1, query: '人工智能发展历史', created_at: new Date(Date.now() - 3600000) },
      { id: 2, query: '机器学习算法', created_at: new Date(Date.now() - 7200000) },
      { id: 3, query: '深度学习应用', created_at: new Date(Date.now() - 10800000) }
    ])
    
    const searchConfig = reactive({
      query: '',
      top_k: 5,
      threshold: 0.7,
      category_filter: []
    })
    
    const performSearch = async () => {
      if (!searchConfig.query.trim()) {
        ElMessage.warning('请输入检索关键词')
        return
      }
      
      searching.value = true
      hasSearched.value = true
      const startTime = Date.now()
      
      try {
        const requestData = {
          query: searchConfig.query,
          top_k: searchConfig.top_k,
          threshold: searchConfig.threshold
        }
        
        if (searchConfig.category_filter.length > 0) {
          requestData.category_filter = searchConfig.category_filter
        }
        
        const response = await searchApi.retrieve(requestData)
        
        responseTime.value = Date.now() - startTime
        searchResults.value = response.data?.artifacts || []
        
        // 添加到搜索历史
        addToHistory(searchConfig.query)
        
        if (searchResults.value.length === 0) {
          ElMessage.info('未找到相关资料')
        } else {
          ElMessage.success(`找到 ${searchResults.value.length} 条相关资料`)
        }
        
      } catch (error) {
        responseTime.value = Date.now() - startTime
        ElMessage.error('检索失败: ' + error.message)
        searchResults.value = []
      } finally {
        searching.value = false
      }
    }
    
    const loadHistory = (history) => {
      searchConfig.query = history.query
      performSearch()
    }
    
    const addToHistory = (query) => {
      const existingIndex = searchHistory.value.findIndex(item => item.query === query)
      if (existingIndex > -1) {
        searchHistory.value.splice(existingIndex, 1)
      }
      
      searchHistory.value.unshift({
        id: Date.now(),
        query: query,
        created_at: new Date()
      })
      
      // 保留最近10条记录
      if (searchHistory.value.length > 10) {
        searchHistory.value = searchHistory.value.slice(0, 10)
      }
    }
    
    const viewFullContent = (result) => {
      selectedResult.value = result
      showFullContent.value = true
    }
    
    const copyContent = (content) => {
      navigator.clipboard.writeText(content)
      ElMessage.success('内容已复制到剪贴板')
    }
    
    const copyFullContent = () => {
      if (selectedResult.value) {
        copyContent(selectedResult.value.content)
      }
    }
    
    const getScoreType = (score) => {
      if (score >= 0.8) return 'success'
      if (score >= 0.6) return 'warning'
      return 'danger'
    }
    
    const truncateText = (text, length) => {
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('zh-CN')
    }
    
    const formatHistoryTime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const now = new Date()
      const diff = now - date
      
      if (diff < 3600000) return '刚刚'
      if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
      return Math.floor(diff / 86400000) + '天前'
    }
    
    return {
      searching,
      hasSearched,
      searchResults,
      responseTime,
      showFullContent,
      selectedResult,
      searchHistory,
      searchConfig,
      performSearch,
      loadHistory,
      viewFullContent,
      copyContent,
      copyFullContent,
      getScoreType,
      truncateText,
      formatDate,
      formatHistoryTime
    }
  }
}
</script>

<style scoped>
.search-interface {
  padding: 20px;
}

.config-panel {
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.results-panel {
  height: calc(100vh - 40px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
}

.result-summary {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}

.loading-results {
  padding: 40px 0;
}

.no-results {
  padding: 60px 0;
}

.results-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.result-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 15px;
  background-color: white;
  transition: box-shadow 0.3s;
}

.result-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 12px;
  color: #909399;
}

.result-time {
  color: #909399;
}

.result-content {
  line-height: 1.6;
  color: #606266;
  margin-bottom: 15px;
}

.result-chunks {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.chunks-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.chunk-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
}

.chunk-score {
  margin-bottom: 5px;
}

.chunk-content {
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.search-history {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.search-history h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: background-color 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item:hover {
  background-color: #f5f7fa;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.full-content {
  max-height: 60vh;
  overflow-y: auto;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.content-time {
  color: #909399;
  font-size: 14px;
}

.content-body {
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>