import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 系统相关API
export const systemApi = {
  // 健康检查
  getHealth() {
    return api.get('/health')
  },
  
  // 获取系统指标
  getMetrics() {
    return api.get('/metrics')
  },
  
  // 获取系统信息
  getInfo() {
    return api.get('/info')
  },
  
  // 重建向量索引
  reindexVectors() {
    return api.post('/reindex')
  },
  
  // 获取日志数据
  getLogData(type, lines = 100) {
    if (type === 'database') {
      return api.get('/logs/database', { params: { lines } })
    } else if (type === 'server') {
      return api.get('/logs/server', { params: { lines } })
    } else {
      return api.get('/logs', { params: { lines } })
    }
  },
  
  // 清空日志
  clearLog(type) {
    if (type === 'database') {
      return api.delete('/logs/database')
    } else if (type === 'server') {
      return api.delete('/logs/server')
    }
  },
  
  // 重启服务器
  restartServer() {
    return api.post('/server/restart')
  },
  
  // 关闭服务器
  shutdownServer() {
    return api.post('/server/shutdown')
  }
}

// 资料管理API
export const artifactApi = {
  // 获取所有资料
  getAllArtifacts(params = {}) {
    return api.get('/artifacts', { params })
  },
  
  // 获取指定资料
  getArtifact(id) {
    return api.get(`/artifacts/${id}`)
  },
  
  // 创建新资料
  createArtifact(data) {
    return api.post('/artifacts', data)
  },
  
  // 更新资料
  updateArtifact(id, data) {
    return api.put(`/artifacts/${id}`, data)
  },
  
  // 删除资料
  deleteArtifact(id) {
    return api.delete(`/artifacts/${id}`)
  },
  
  // 批量导入
  batchImport(data) {
    return api.post('/artifacts/batch', data)
  }
}

// 检索API
export const searchApi = {
  // 执行检索
  retrieve(data) {
    return api.post('/search/retrieve', data)
  },
  
  // 获取搜索历史
  getSearchHistory(limit = 10) {
    return api.get('/search/history', { params: { limit } })
  }
}

// 配置API
export const configApi = {
  // 获取配置
  getConfig() {
    return api.get('/config')
  },
  
  // 更新配置
  updateConfig(data) {
    return api.post('/config', data)
  },
  
  // 测试LLM配置
  testLlmConfig(data) {
    return api.post('/config/test-llm', data)
  },
  
  // 测试Embedding配置
  testEmbeddingConfig(data) {
    return api.post('/config/test-embedding', data)
  }
}

// SQLite数据库API
export const sqliteApi = {
  // 获取所有表
  getTables() {
    return api.get('/sqlite/tables')
  },
  
  // 获取表数据
  getTableData(tableName, params = {}) {
    return api.get(`/sqlite/tables/${tableName}`, { params })
  },
  
  // 创建记录
  createRecord(tableName, data) {
    return api.post(`/sqlite/tables/${tableName}`, data)
  },
  
  // 更新记录
  updateRecord(tableName, recordId, data) {
    return api.put(`/sqlite/tables/${tableName}/${recordId}`, data)
  },
  
  // 删除记录
  deleteRecord(tableName, recordId) {
    return api.delete(`/sqlite/tables/${tableName}/${recordId}`)
  },
  
  // 初始化数据库
  initDatabase() {
    return api.post('/sqlite/init')
  }
}

// ChromaDB数据库API
export const chromadbApi = {
  // 获取文档列表
  getDocuments(params = {}) {
    return api.get('/chromadb/documents', { params })
  },
  
  // 搜索文档
  searchDocuments(data) {
    return api.post('/chromadb/documents/search', data)
  },
  
  // 创建文档
  createDocument(data) {
    return api.post('/chromadb/documents', data)
  },
  
  // 更新文档
  updateDocument(documentId, data) {
    return api.put(`/chromadb/documents/${documentId}`, data)
  },
  
  // 删除文档
  deleteDocument(documentId) {
    return api.delete(`/chromadb/documents/${documentId}`)
  },
  
  // 检查文档ID是否存在
  checkDocumentIdExists(documentId) {
    return api.get(`/chromadb/documents/${documentId}/exists`)
  },
  
  // 获取单个文档的完整信息，包括向量数据
  getDocument(documentId) {
    return api.get(`/chromadb/documents/${documentId}`)
  },
  
  // 初始化数据库
  initDatabase() {
    return api.post('/chromadb/init')
  },
  
  // 获取集合信息
  getCollectionInfo() {
    return api.get('/chromadb/info')
  },
  
  // 获取所有集合
  getCollections() {
    return api.get('/chromadb/collections')
  }
}

// 默认导出
export default api