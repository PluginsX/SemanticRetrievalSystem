<template>
    <div class="data-manager">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>资料管理</span>
                    <div class="status-message" v-if="asyncTaskStatus.show">
                        <el-icon class="status-icon"><Loading /></el-icon>
                        <span class="status-text" :title="asyncTaskStatus.message">{{ asyncTaskStatus.message }}</span>
                    </div>
                    <div class="header-actions">
                        <el-button type="info" @click="reindexVectors">
                            <el-icon><Refresh /></el-icon>
                            重建索引
                        </el-button>
                        <el-button type="primary" @click="showCreateDialog = true">
                            <el-icon><Plus /></el-icon>
                            新建资料
                        </el-button>
                        <el-button type="success" @click="showBatchImportDialog = true">
                            <el-icon><Upload /></el-icon>
                            批量新增
                        </el-button>
                        <el-button @click="refreshData">
                            <el-icon><Refresh /></el-icon>
                            刷新
                        </el-button>
                    </div>
                </div>
            </template>
            
            <!-- 搜索和筛选 -->
            <div class="filter-section">
                <el-row :gutter="20">
                    <el-col :span="8">
                        <el-input
                        v-model="searchKeyword"
                        placeholder="搜索资料标题或内容"
                        clearable
                        @keyup.enter="searchArtifacts"
                        >
                        <template #prefix>
                            <el-icon><Search /></el-icon>
                        </template>
                    </el-input>
                </el-col>
                <el-col :span="6">
                    <el-select v-model="selectedCategory" placeholder="选择分类" clearable>
                        <el-option label="全部分类" value="" />
                        <el-option label="技术文档" value="技术文档" />
                        <el-option label="产品说明" value="产品说明" />
                        <el-option label="用户手册" value="用户手册" />
                    </el-select>
                </el-col>
                <el-col :span="4">
                    <el-button-group>
                        <el-button type="primary" @click="searchArtifacts">搜索</el-button>
                        <el-button type="info" @click="showCategoryManagement = true">管理</el-button>
                    </el-button-group>
                </el-col>
            </el-row>
        </div>
        
        <!-- 资料表格 -->
        <el-table
        :data="artifacts"
        style="width: 100%"
        v-loading="loading"
        stripe
        >
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
                {{ formatDate(row.created_at) }}
            </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
            <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
                <el-button link type="primary" @click="viewArtifact(row)">查看</el-button>
                <el-button link type="primary" @click="editArtifact(row)">编辑</el-button>
                <el-button link type="danger" @click="deleteArtifact(row)">删除</el-button>
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
        />
    </div>
</el-card>

<!-- 创建/编辑对话框 -->
<el-dialog
v-model="showCreateDialog"
:title="editingArtifact ? '编辑资料' : '新建资料'"
width="600px"
>
<el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px">
    <el-form-item label="标题" prop="title">
        <el-input v-model="formData.title" placeholder="请输入资料标题" />
    </el-form-item>
    <el-form-item label="分类" prop="category">
        <el-select v-model="formData.category" placeholder="请选择分类">
            <el-option label="技术文档" value="技术文档" />
            <el-option label="产品说明" value="产品说明" />
            <el-option label="用户手册" value="用户手册" />
        </el-select>
    </el-form-item>
    <el-form-item label="内容" prop="content">
        <el-input
        v-model="formData.content"
        type="textarea"
        :rows="10"
        placeholder="请输入资料内容"
        />
    </el-form-item>
    <el-form-item label="来源类型" prop="source_type">
        <el-select v-model="formData.source_type" placeholder="请选择来源类型">
            <el-option label="手动录入" value="manual" />
            <el-option label="文件导入" value="file" />
            <el-option label="API导入" value="api" />
        </el-select>
    </el-form-item>
    <el-form-item label="来源路径" prop="source_path">
        <el-input v-model="formData.source_path" placeholder="请输入来源路径（文件路径或URL）" />
    </el-form-item>
    <el-form-item label="标签" prop="tags">
        <el-select v-model="formData.tags" multiple placeholder="请选择标签">
            <el-option label="重要" value="重要" />
            <el-option label="待审核" value="待审核" />
            <el-option label="已归档" value="已归档" />
            <el-option label="技术" value="技术" />
            <el-option label="产品" value="产品" />
        </el-select>
    </el-form-item>
    <el-form-item label="元数据" prop="metadata">
        <el-input
        v-model="formData.metadata_json"
        type="textarea"
        :rows="4"
        placeholder='请输入元数据（JSON格式），例如：{"author": "张三", "version": "1.0"}'
        />
    </el-form-item>
</el-form>
<template #footer>
    <span class="dialog-footer">
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveArtifact">保存</el-button>
    </span>
</template>
</el-dialog>

<!-- 分类管理对话框 -->
<CategoryManagement 
  v-model="showCategoryManagement"
  @saved="onCategoriesSaved"
/>

<!-- 批量导入对话框 -->
<el-dialog
  v-model="showBatchImportDialog"
  title="批量新增资料"
  width="800px"
  @close="closeBatchImportDialog"
>
  <div class="batch-import-content">
    <p>请将批量收集的资料按照以下JSON格式输入：</p>
    <el-input
      v-model="batchJsonData"
      type="textarea"
      :rows="15"
      placeholder='示例格式：
[
  {
    "title": "资料标题1",
    "content": "资料内容1",
    "category": "可选分类",
    "tags": "可选标签",
    "metadata": "可选元数据"
  },
  {
    "title": "资料标题2",
    "content": "资料内容2",
    "category": "可选分类",
    "tags": "可选标签",
    "metadata": "可选元数据"
  }
]'
    />
    <div style="margin-top: 15px; color: #909399; font-size: 14px;">
      <p>注意：<br>
      1. 标题(title)和内容(content)字段为必填项<br>
      2. 其他字段(category, tags, metadata等)为可选项<br>
      3. 每条资料都将按照正常流程导入，包括生成Embedding数据</p>
    </div>
  </div>
  <template #footer>
    <span class="dialog-footer">
      <el-button @click="closeBatchImportDialog">取消</el-button>
      <el-button type="primary" @click="startBatchImport">开始导入</el-button>
    </span>
  </template>
</el-dialog>

<!-- 进度对话框 -->
<el-dialog
  v-model="showProgress"
  title="批量导入进度"
  width="500px"
  :show-close="false"
  :close-on-click-modal="false"
  :close-on-press-escape="false"
>
  <div class="progress-content">
    <p>{{ progressStatus }}</p>
    <el-progress 
      :percentage="progressPercentage" 
      :status="progressPercentage === 100 ? 'success' : null"
      :indeterminate="progressStatus.includes('processing')"
      :duration="1"
    />
  </div>
  <template #footer>
    <span class="dialog-footer">
      <el-button @click="cancelImport" :disabled="progressPercentage === 100">取消导入</el-button>
      <el-button type="primary" @click="closeProgressDialog" v-if="progressPercentage === 100">确定</el-button>
    </span>
  </template>
</el-dialog>

</div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Upload, Search, Loading } from '@element-plus/icons-vue'
import CategoryManagement from './CategoryManagement.vue'
import { artifactApi, systemApi } from '@/api'

export default {
    name: 'DataManager',
    setup() {
        const loading = ref(false)
        const artifacts = ref([])
        const searchKeyword = ref('')
        const selectedCategory = ref('')
        const currentPage = ref(1)
        const pageSize = ref(10)
        const total = ref(0)
        const showCreateDialog = ref(false)
        const editingArtifact = ref(null)
        
        const asyncTaskStatus = reactive({
            show: false,
            message: ''
        })
        
        const formData = reactive({
            title: '',
            category: '',
            content: '',
            source_type: '',
            source_path: '',
            tags: [],
            metadata: {}
        })
        
        const formRules = {
            title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
            content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
        }
        
        const formRef = ref(null)
        
        const loadData = async () => {
            loading.value = true
            try {
                const params = {
                    page: currentPage.value,
                    size: pageSize.value
                }
                if (searchKeyword.value) params.keyword = searchKeyword.value
                if (selectedCategory.value) params.category = selectedCategory.value
                
                const response = await artifactApi.getAllArtifacts(params)
                // 直接使用response，因为响应拦截器已经处理了response.data
                artifacts.value = response.artifacts || []
                total.value = response.total_count || 0
            } catch (error) {
                ElMessage.error('加载资料失败: ' + error.message)
                artifacts.value = [] // 显示空列表而不是错误
            } finally {
                loading.value = false
            }
        }
        
        const searchArtifacts = () => {
            currentPage.value = 1
            loadData()
        }
        
        const refreshData = () => {
            loadData()
            ElMessage.success('数据已刷新')
        }
        
        const reindexVectors = async () => {
            try {
                asyncTaskStatus.show = true
                asyncTaskStatus.message = '正在重建向量索引...'
                await systemApi.reindexVectors()
                ElMessage.success('向量索引重建请求已发送')
                asyncTaskStatus.show = true
                asyncTaskStatus.message = '向量索引重建请求已发送'
                // 5秒后隐藏状态信息
                setTimeout(() => {
                    asyncTaskStatus.show = false
                }, 5000)
            } catch (error) {
                ElMessage.error('重建索引失败: ' + error.message)
                asyncTaskStatus.show = true
                asyncTaskStatus.message = '重建索引失败: ' + error.message
                // 5秒后隐藏状态信息
                setTimeout(() => {
                    asyncTaskStatus.show = false
                }, 5000)
            }
        }
        
        const handleSizeChange = (val) => {
            pageSize.value = val
            loadData()
        }
        
        const handleCurrentChange = (val) => {
            currentPage.value = val
            loadData()
        }
        
        const viewArtifact = (artifact) => {
            ElMessageBox.alert(artifact.content, artifact.title, {
                confirmButtonText: '确定'
            })
        }
        
        const editArtifact = (artifact) => {
            editingArtifact.value = artifact
            formData.title = artifact.title
            formData.category = artifact.category
            formData.content = artifact.content
            formData.source_type = artifact.source_type || ''
            formData.source_path = artifact.source_path || ''
            formData.tags = artifact.tags ? artifact.tags.split(',').map(tag => tag.trim()) : []
            formData.metadata = artifact.metadata ? JSON.parse(artifact.metadata) : {}
            formData.metadata_json = artifact.metadata || ''
            showCreateDialog.value = true
        }
        
        const deleteArtifact = async (artifact) => {
            try {
                await ElMessageBox.confirm(
                `确定要删除资料 "${artifact.title}" 吗？`,
                '删除确认',
                {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }
                )
                
                await artifactApi.deleteArtifact(artifact.id)
                ElMessage.success('删除成功')
                loadData()
            } catch (error) {
                if (error !== 'cancel') {
                    ElMessage.error('删除失败: ' + error.message)
                }
            }
        }
        
        const saveArtifact = async () => {
            try {
                await formRef.value.validate()
                
                // 显示加载状态
                const loadingMessage = ElMessage({
                    message: '正在处理资料...',
                    type: 'info',
                    duration: 2000 // 2秒后自动消失
                })
                
                // 处理表单数据
                const submitData = { ...formData }
                
                // 处理metadata
                if (submitData.metadata_json) {
                    try {
                        submitData.metadata = JSON.parse(submitData.metadata_json)
                    } catch (e) {
                        ElMessage.error('元数据格式错误，请输入有效的JSON格式')
                        return
                    }
                } else {
                    submitData.metadata = null
                }
                delete submitData.metadata_json
                
                // 处理可选字段
                if (!submitData.category) submitData.category = null
                if (!submitData.source_type) submitData.source_type = null
                if (!submitData.source_path) submitData.source_path = null
                
                // 处理tags
                if (!submitData.tags || submitData.tags.length === 0) {
                    submitData.tags = null
                }
                
                if (editingArtifact.value) {
                    await artifactApi.updateArtifact(editingArtifact.value.id, submitData)
                    ElMessage.success('更新成功，正在生成向量...')
                } else {
                    await artifactApi.createArtifact(submitData)
                    ElMessage.success('创建成功，正在生成向量...')
                }
                
                showCreateDialog.value = false
                resetForm()
                loadData()
            } catch (error) {
                ElMessage.error('保存失败: ' + error.message)
            }
        }
        
        const resetForm = () => {
            formRef.value?.resetFields()
            editingArtifact.value = null
            formData.title = ''
            formData.category = ''
            formData.content = ''
            formData.source_type = ''
            formData.source_path = ''
            formData.tags = []
            formData.metadata = {}
            formData.metadata_json = ''
        }
        
        const formatDate = (dateString) => {
            if (!dateString) return ''
            return new Date(dateString).toLocaleString('zh-CN')
        }
        
        // 分类管理回调
        const onCategoriesSaved = (categories) => {
            ElMessage.success('分类管理完成')
            // 这里可以更新分类下拉选项
            console.log('分类已更新:', categories)
        }
        
        // 分类管理对话框相关
        // 批量导入相关
        const showBatchImportDialog = ref(false)
        const batchJsonData = ref('')
        const showProgress = ref(false)
        const progressPercentage = ref(0)
        const progressStatus = ref('')
        const taskId = ref('')
        const importInterval = ref(null)
        
        // 显示批量导入对话框
        const showBatchImport = () => {
            showBatchImportDialog.value = true
            batchJsonData.value = ''
        }
        
        // 开始批量导入
        const startBatchImport = async () => {
            if (!batchJsonData.value.trim()) {
                ElMessage.error('请输入JSON数据')
                return
            }
            
            try {
                // 解析JSON数据以验证格式
                JSON.parse(batchJsonData.value)
            } catch (error) {
                ElMessage.error('JSON格式错误: ' + error.message)
                return
            }
            
            try {
                const response = await artifactApi.batchImport({ data: JSON.parse(batchJsonData.value) })
                
                if (response.success) {
                    taskId.value = response.task_id
                    showProgress.value = true
                    progressPercentage.value = 0
                    progressStatus.value = '开始导入...'
                    
                    // 开始轮询进度
                    startProgressPolling()
                } else {
                    ElMessage.error(response.message || '批量导入启动失败')
                }
            } catch (error) {
                ElMessage.error('批量导入启动失败: ' + error.message)
            }
        }
        
        // 开始轮询进度
        const startProgressPolling = () => {
            // 清除之前的轮询
            if (importInterval.value) {
                clearInterval(importInterval.value)
            }
            
            // 显示异步任务状态
            asyncTaskStatus.show = true
            asyncTaskStatus.message = '正在批量导入资料...'
            
            // 每1秒查询一次进度
            importInterval.value = setInterval(async () => {
                try {
                    const response = await artifactApi.getBatchImportStatus(taskId.value)
                    
                    if (response.success) {
                        const status = response.data
                        const processed = status.processed || 0
                        const total = status.total || 0
                        
                        // 更新状态信息
                        if (status.status === 'processing') {
                            asyncTaskStatus.show = true
                            asyncTaskStatus.message = `正在批量导入资料... (${processed}/${total})`
                        } else if (status.status === 'completed') {
                            asyncTaskStatus.show = true
                            asyncTaskStatus.message = `批量导入完成！成功: ${status.success}, 失败: ${status.failed}`
                        } else if (status.status === 'failed') {
                            asyncTaskStatus.show = true
                            asyncTaskStatus.message = `批量导入失败！失败: ${status.failed}`
                        } else if (status.status === 'cancelled') {
                            asyncTaskStatus.show = true
                            asyncTaskStatus.message = '批量导入已取消'
                        }
                        
                        if (total > 0) {
                            progressPercentage.value = Math.round((processed / total) * 100)
                        } else {
                            progressPercentage.value = 0
                        }
                        
                        progressStatus.value = `${status.status} - 已处理: ${processed}/${total}`
                        
                        // 如果任务完成，停止轮询
                        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
                            clearInterval(importInterval.value)
                            importInterval.value = null
                            
                            if (status.status === 'completed') {
                                ElMessage.success(`批量导入完成！成功: ${status.success}, 失败: ${status.failed}`)
                                asyncTaskStatus.show = true
                                asyncTaskStatus.message = `批量导入完成！成功: ${status.success}, 失败: ${status.failed}`
                                // 5秒后隐藏状态信息
                                setTimeout(() => {
                                    asyncTaskStatus.show = false
                                }, 5000)
                            } else if (status.status === 'failed') {
                                ElMessage.error('批量导入失败')
                                asyncTaskStatus.show = true
                                asyncTaskStatus.message = `批量导入失败！失败: ${status.failed}`
                                // 5秒后隐藏状态信息
                                setTimeout(() => {
                                    asyncTaskStatus.show = false
                                }, 5000)
                            } else if (status.status === 'cancelled') {
                                ElMessage.info('批量导入已取消')
                                asyncTaskStatus.show = true
                                asyncTaskStatus.message = '批量导入已取消'
                                // 5秒后隐藏状态信息
                                setTimeout(() => {
                                    asyncTaskStatus.show = false
                                }, 5000)
                            }
                            
                            // 刷新数据
                            loadData()
                        }
                    }
                } catch (error) {
                    console.error('获取进度失败:', error)
                    clearInterval(importInterval.value)
                    importInterval.value = null
                    ElMessage.error('获取导入进度失败')
                }
            }, 1000) // 每秒轮询一次
        }
        
        // 取消导入
        const cancelImport = async () => {
            try {
                const response = await artifactApi.cancelBatchImport(taskId.value)
                
                if (response.success) {
                    ElMessage.info('正在取消导入...')
                    // 停止轮询
                    if (importInterval.value) {
                        clearInterval(importInterval.value)
                        importInterval.value = null
                    }
                } else {
                    ElMessage.error(response.message || '取消导入失败')
                }
            } catch (error) {
                ElMessage.error('取消导入失败: ' + error.message)
            }
        }
        
        // 关闭批量导入对话框
        const closeBatchImportDialog = () => {
            showBatchImportDialog.value = false
            // 停止轮询
            if (importInterval.value) {
                clearInterval(importInterval.value)
                importInterval.value = null
            }
        }
        
        // 关闭进度对话框
        const closeProgressDialog = () => {
            showProgress.value = false
            // 停止轮询
            if (importInterval.value) {
                clearInterval(importInterval.value)
                importInterval.value = null
            }
        }
        
        const showCategoryManagement = ref(false)
        
        onMounted(() => {
            loadData()
        })
        
        return {
            loading,
            artifacts,
            searchKeyword,
            selectedCategory,
            currentPage,
            pageSize,
            total,
            showCreateDialog,
            editingArtifact,
            formData,
            formRules,
            formRef,
            showCategoryManagement,
            // 批量导入相关
            showBatchImportDialog,
            batchJsonData,
            showProgress,
            progressPercentage,
            progressStatus,
            taskId,
            importInterval,
            // 异步任务状态
            asyncTaskStatus,
            searchArtifacts,
            refreshData,
            reindexVectors,
            handleSizeChange,
            handleCurrentChange,
            viewArtifact,
            editArtifact,
            deleteArtifact,
            saveArtifact,
            formatDate,
            // 批量导入方法
            showBatchImport,
            startBatchImport,
            cancelImport,
            closeBatchImportDialog,
            closeProgressDialog,
            onCategoriesSaved
        }
    }
}
</script>

<style scoped>
.data-manager {
    padding: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.status-message {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 20px;
    padding: 8px 16px;
    background-color: #f0f9ff;
    border: 1px solid #409eff;
    border-radius: 4px;
    color: #409eff;
    font-size: 14px;
}

.status-icon {
    margin-right: 8px;
    animation: rotate 1s linear infinite;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.status-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 400px;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.filter-section {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
}

.pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style>