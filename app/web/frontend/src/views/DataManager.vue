<template>
    <div class="data-manager">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>资料管理</span>
                    <div class="header-actions">
                        <el-button type="primary" @click="showCreateDialog = true">
                            <el-icon><Plus /></el-icon>
                            新建资料
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
</div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CategoryManagement from './CategoryManagement.vue'
import { artifactApi } from '@/api'

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
            searchArtifacts,
            refreshData,
            handleSizeChange,
            handleCurrentChange,
            viewArtifact,
            editArtifact,
            deleteArtifact,
            saveArtifact,
            formatDate,
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