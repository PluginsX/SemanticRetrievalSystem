<template>
  <div class="chromadb-manager">
    <!-- 页面标题 -->
    <el-page-header
      :title="'ChromaDB向量数据库管理'"
      :sub-title="'管理ChromaDB向量数据库的文档和向量'"
      class="page-header"
    />
    
    <div class="manager-content">
      <!-- 操作工具栏 -->
      <el-card shadow="hover" class="toolbar-card">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-button type="primary" @click="initDatabase">
              <el-icon><Refresh /></el-icon>
              初始化数据库
            </el-button>
            <el-button @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" @click="addDocument">
              <el-icon><Plus /></el-icon>
              新增文档
            </el-button>
            <el-alert
              :title="dbStatus.message"
              :type="dbStatus.type"
              show-icon
              :closable="false"
              class="status-alert"
            />
          </div>
          <div class="toolbar-right">
            <div class="collection-info">
              <span class="info-item">记录数量: {{ collectionInfo.count }}</span>
              <span class="info-item">向量维度: {{ collectionInfo.dimension }}</span>
            </div>
            <el-select v-model="selectedCollection" @change="handleCollectionChange" placeholder="选择集合" class="table-select" popper-append-to-body placement="bottom">
              <el-option
                v-for="collection in collections"
                :key="collection.name"
                :label="`${collection.name} (${collection.count} 文档)`"
                :value="collection.name"
              />
            </el-select>
          </div>
        </div>
      </el-card>
      
      <!-- 搜索功能 -->
      <el-card shadow="hover" class="search-card">
        <template #header>
          <div class="card-header">
            <span>搜索功能</span>
          </div>
        </template>
        <div class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文档内容"
            clearable
            @keyup.enter="searchDocuments"
            class="search-input"
          >
            <template #append>
              <el-button type="primary" @click="searchDocuments">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>
          <div class="search-config">
            <el-form label-width="100px">
              <el-form-item label="相似度阈值">
                <el-slider
                  v-model="searchThreshold"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  show-input
                />
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-card>
      
      <!-- 文档列表 -->
      <el-card shadow="hover" class="document-card">
        <template #header>
          <div class="card-header">
            <span>文档列表</span>
            <span class="document-count">共 {{ collectionInfo.count }} 个文档</span>
          </div>
        </template>
        <div class="document-list">
          <el-table :data="documents" style="width: 100%" v-loading="loading" stripe border>
            <el-table-column prop="id" label="ids" width="150" show-overflow-tooltip />
            <el-table-column label="embeddings" width="120" show-overflow-tooltip>
              <template #default="scope">
                <el-tag v-if="scope.row.has_embedding" type="success" size="small">已定义</el-tag>
                <el-tag v-else type="info" size="small">未定义</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="documents" min-width="300" show-overflow-tooltip>
              <template #default="scope">
                <span class="ellipsis">{{ scope.row.document ? (scope.row.document.length > 100 ? scope.row.document.substring(0, 100) + '...' : scope.row.document) : '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="metadatas" width="200" show-overflow-tooltip>
              <template #default="scope">
                <span class="ellipsis">{{ scope.row.metadata ? JSON.stringify(scope.row.metadata).substring(0, 50) + '...' : '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="similarity" label="Similarity" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.similarity" :type="getSimilarityType(scope.row.similarity)">
                  {{ (scope.row.similarity * 100).toFixed(1) }}%
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="Operation" width="180" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="editDocument(scope.row)" :icon="Edit">
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click="deleteDocument(scope.row.id)" :icon="Delete">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              background
            />
          </div>
        </div>
      </el-card>
      
      <!-- 编辑对话框 -->
      <el-dialog
        v-model="showEditDialog"
        :title="editingDocument ? '编辑文档' : '新增文档'"
        width="1000px"
        center
      >
        <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
          <el-form-item label="IDs" prop="id">
            <el-input
              v-model="formData.id"
              placeholder="请输入文档ID"
            />
          </el-form-item>
          <el-form-item label="Embeddings" prop="embedding">
            <el-input
              v-model="formData.embedding_json"
              type="textarea"
              :rows="4"
              placeholder="请输入向量数据（JSON格式数组），例如：[0.1, 0.2, 0.3, ...]"
              resize="vertical"
            />
          </el-form-item>
          <el-form-item label="Documents" prop="document">
            <el-input
              v-model="formData.document"
              type="textarea"
              :rows="8"
              placeholder="请输入文档内容"
              resize="vertical"
            />
          </el-form-item>
          <el-form-item label="Metadatas" prop="metadata">
            <el-input
              v-model="formData.metadata_json"
              type="textarea"
              :rows="4"
              placeholder='请输入元数据（JSON格式），例如：{"author": "张三", "version": "1.0"}'
              resize="vertical"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showEditDialog = false">取消</el-button>
            <el-button type="primary" @click="saveDocument">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
    
    <!-- 加载等待对话框 -->
    <el-dialog
      v-model="showLoadingDialog"
      title="处理中"
      width="30%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div style="text-align: center; padding: 20px 0;">
        <el-icon class="is-loading" style="font-size: 32px; margin-bottom: 16px;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path fill="currentColor" d="M512 0a512 512 0 110 1024 512 512 0 010-1024zm0 128a384 384 0 100 768 384 384 0 000-768zM512 224a288 288 0 11-288 288 288 288 0 01288-288zm0 64a224 224 0 100 448 224 224 0 000-448z"></path></svg></el-icon>
        <p>{{ loadingMessage }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { chromadbApi } from '@/api'

export default {
  name: 'ChromaDBManager',
  components: {
    Refresh,
    Plus,
    Edit,
    Delete,
    Search
  },
  setup() {
    const documents = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const searchQuery = ref('')
    const searchThreshold = ref(0.0)
    const showEditDialog = ref(false)
    const editingDocument = ref(null)
    const formData = reactive({ 
      id: '',
      document: '',
      embedding_json: '',
      metadata_json: ''
    })
    const formRules = ref({ 
      // 移除强制要求填写documents字段的限制
      // 改为Embeddings和Documents至少填写一个
    })
    const formRef = ref(null)
    const showLoadingDialog = ref(false)
    const loadingMessage = ref('')
    
    const dbStatus = reactive({
      message: '数据库状态：未连接',
      type: 'warning'
    })
    
    const collectionInfo = reactive({
      name: 'artifact_embeddings',
      count: 0,
      dimension: 1024
    })
    
    const collections = ref([])
    const selectedCollection = ref('artifact_embeddings')
    
    // 集合状态
    const collectionStatus = computed(() => {
      if (collectionInfo.count === 0) {
        return { type: 'warning', text: '空集合' }
      } else if (collectionInfo.count < 10) {
        return { type: 'info', text: '文档较少' }
      } else {
        return { type: 'success', text: '正常' }
      }
    })
    
    // 加载集合列表
    const loadCollections = async () => {
      try {
        const response = await chromadbApi.getCollections()
        if (response && response.data) {
          collections.value = response.data.collections || []
          // 如果有集合，确保选中的集合在列表中
          if (collections.value.length > 0 && !collections.value.some(c => c.name === selectedCollection.value)) {
            selectedCollection.value = collections.value[0].name
            collectionInfo.name = selectedCollection.value
          }
        }
      } catch (error) {
        console.error('加载集合列表失败:', error)
      }
    }
    
    // 加载文档数据
    const loadDocuments = async () => {
      loading.value = true
      try {
        const response = await chromadbApi.getDocuments({
          page: currentPage.value,
          size: pageSize.value
        })
        
        console.log('ChromaDB API响应:', response)
        
        if (!response || !response.data) {
          throw new Error('API返回数据为空')
        }
        
        documents.value = response.data.records || []
        total.value = response.data.total || 0
        collectionInfo.count = total.value
        
        dbStatus.message = `数据库状态：已连接，共 ${total.value} 条文档`
        dbStatus.type = 'success'
      } catch (error) {
        console.error('加载文档失败:', error)
        ElMessage.error(`加载文档失败: ${error.message}`)
        dbStatus.message = '数据库状态：连接失败'
        dbStatus.type = 'error'
      } finally {
        loading.value = false
      }
    }
    
    // 处理集合切换
    const handleCollectionChange = (collectionName) => {
      // 这里可以添加切换集合的逻辑
      // 目前我们的API只支持默认集合，所以这里只是更新显示
      collectionInfo.name = collectionName
      // 重新加载文档数据
      loadDocuments()
    }
    
    // 初始化数据库
    const initDatabase = async () => {
      try {
        await ElMessageBox.confirm('确定要初始化ChromaDB吗？这将创建必要的集合结构。', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await chromadbApi.initDatabase()
        ElMessage.success('数据库初始化成功')
        await loadDocuments()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(`初始化数据库失败: ${error.message}`)
        }
      }
    }
    
    // 搜索文档
    const searchDocuments = async () => {
      if (!searchQuery.value) {
        await loadDocuments()
        return
      }
      
      loading.value = true
      try {
        const response = await chromadbApi.searchDocuments({
          query: searchQuery.value,
          top_k: pageSize.value,
          threshold: searchThreshold.value
        })
        
        documents.value = response.data.records || []
        total.value = response.data.total || 0
      } catch (error) {
        ElMessage.error(`搜索失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }
    
    // 新增文档
    const addDocument = () => {
      editingDocument.value = null
      formData.id = ''
      formData.document = ''
      formData.embedding_json = ''
      formData.metadata_json = ''
      showEditDialog.value = true
    }
    
    // 编辑文档
    const editDocument = async (doc) => {
      try {
        // 显示加载对话框
        loadingMessage.value = '正在获取文档详细信息...'
        showLoadingDialog.value = true
        
        // 获取单个文档的完整信息，包括向量数据
        const response = await chromadbApi.getDocument(doc.id)
        const fullDoc = response.data
        
        editingDocument.value = fullDoc
        formData.id = fullDoc.id || ''
        formData.document = fullDoc.document || ''
        // 显示完整的向量数据
        formData.embedding_json = fullDoc.embedding ? JSON.stringify(fullDoc.embedding) : ''
        formData.metadata_json = fullDoc.metadata ? JSON.stringify(fullDoc.metadata) : ''
        showEditDialog.value = true
      } catch (error) {
        console.error('获取文档详细信息失败:', error)
        ElMessage.error(`获取文档详细信息失败: ${error.message}`)
        // 即使获取失败，也打开编辑对话框，使用基本信息
        editingDocument.value = doc
        formData.id = doc.id || ''
        formData.document = doc.document || ''
        formData.embedding_json = ''
        formData.metadata_json = doc.metadata ? JSON.stringify(doc.metadata) : ''
        showEditDialog.value = true
      } finally {
        showLoadingDialog.value = false
      }
    }
    
    // 保存文档
    const saveDocument = async () => {
      try {
        // 验证表单
        if (!formRef.value) return
        
        // 自定义验证：Embeddings和Documents至少填写一个
        if (!formData.document && !formData.embedding_json) {
          ElMessage.error('Embeddings和Documents至少填写一个')
          return
        }
        
        // 准备保存的数据
        const saveData = {}
        
        // 只有在提供了ID时才添加到保存数据中
        if (formData.id) {
          saveData.id = formData.id
        }
        
        // 处理document（可选）
        if (formData.document) {
          saveData.document = formData.document
        }
        
        // 处理embedding（可选）
        if (formData.embedding_json) {
          try {
            saveData.embedding = JSON.parse(formData.embedding_json)
          } catch (e) {
            ElMessage.error('Embedding数据格式错误，请输入有效的JSON数组')
            return
          }
        }
        
        // 处理metadata（可选）
        if (formData.metadata_json) {
          try {
            saveData.metadata = JSON.parse(formData.metadata_json)
          } catch (e) {
            ElMessage.error('Metadata数据格式错误，请输入有效的JSON对象')
            return
          }
        }
        
        if (editingDocument.value) {
          // 如果ID发生变化，需要检测唯一性
          if (formData.id && formData.id !== editingDocument.value.id) {
            // 检查新ID是否已存在
            const response = await chromadbApi.checkDocumentIdExists(formData.id)
            if (response.exists) {
              ElMessage.error('文档ID已存在，请使用其他ID')
              return
            }
            
            // 先删除旧文档
            await chromadbApi.deleteDocument(editingDocument.value.id)
            // 再创建新文档
            loadingMessage.value = '正在处理文档...'
            showLoadingDialog.value = true
            try {
              await chromadbApi.createDocument(saveData)
            } finally {
              showLoadingDialog.value = false
            }
          } else {
            // 更新文档（使用原有ID）
            loadingMessage.value = '正在处理文档...'
            showLoadingDialog.value = true
            try {
              await chromadbApi.updateDocument(editingDocument.value.id, saveData)
            } finally {
              showLoadingDialog.value = false
            }
          }
          ElMessage.success('更新文档成功')
        } else {
          // 新增文档
          // 如果提供了ID，检查是否已存在
          if (formData.id) {
            const response = await chromadbApi.checkDocumentIdExists(formData.id)
            if (response.exists) {
              ElMessage.error('文档ID已存在，请使用其他ID')
              return
            }
          }
          
          loadingMessage.value = '正在处理文档...'
          showLoadingDialog.value = true
          try {
            await chromadbApi.createDocument(saveData)
          } finally {
            showLoadingDialog.value = false
          }
          ElMessage.success('新增文档成功')
        }
        showEditDialog.value = false
        await loadDocuments()
      } catch (error) {
        showLoadingDialog.value = false
        ElMessage.error(`保存文档失败: ${error.message}`)
      }
    }
    
    // 删除文档
    const deleteDocument = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个文档吗？', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'danger'
        })
        
        await chromadbApi.deleteDocument(id)
        ElMessage.success('删除文档成功')
        await loadDocuments()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(`删除文档失败: ${error.message}`)
        }
      }
    }
    
    // 刷新数据
    const refreshData = async () => {
      await loadCollections()
      await loadDocuments()
    }
    
    // 获取相似度标签类型
    const getSimilarityType = (similarity) => {
      if (similarity >= 0.8) return 'success'
      if (similarity >= 0.6) return 'warning'
      return 'danger'
    }
    
    // 分页处理
    const handleSizeChange = (size) => {
      pageSize.value = size
      loadDocuments()
    }
    
    const handleCurrentChange = (current) => {
      currentPage.value = current
      loadDocuments()
    }
    
    onMounted(async () => {
      await loadCollections()
      await loadDocuments()
    })
    
    return {
      documents,
      loading,
      currentPage,
      pageSize,
      total,
      searchQuery,
      searchThreshold,
      showEditDialog,
      editingDocument,
      formData,
      formRules,
      formRef,
      showLoadingDialog,
      loadingMessage,
      dbStatus,
      collectionInfo,
      collectionStatus,
      collections,
      selectedCollection,
      loadDocuments,
      loadCollections,
      initDatabase,
      searchDocuments,
      addDocument,
      editDocument,
      saveDocument,
      deleteDocument,
      refreshData,
      handleCollectionChange,
      getSimilarityType,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.manager-content {
  gap: 20px;
  display: flex;
  flex-direction: column;
}

.toolbar-card {
  margin-bottom: 10px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.toolbar-left {
  display: flex;
  gap: 10px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.collection-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  flex-shrink: 0;
  white-space: nowrap;
}

.collection-info .info-item {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.collection-info .info-item strong {
  color: #303133;
  font-weight: 600;
}

.status-alert {
  margin: 0;
  min-width: 250px;
}

.table-select {
  min-width: 150px;
  max-width: 400px;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  width: 100%;
}

.status-card {
  margin-bottom: 10px;
}

.search-card {
  margin-bottom: 10px;
}

.document-card {
  margin-bottom: 20px;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-input {
  width: 100%;
}

.search-config {
  margin-top: 10px;
}

.document-list {
  margin-top: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 表格样式优化 */
:deep(.el-table__header-wrapper th) {
  background-color: #f5f7fa;
  font-weight: bold;
}

:deep(.el-table__row:hover) {
  background-color: #ecf5ff;
}

:deep(.el-table__fixed-right) {
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

/* 卡片标题样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.document-count {
  font-size: 14px;
  color: #909399;
}
</style>