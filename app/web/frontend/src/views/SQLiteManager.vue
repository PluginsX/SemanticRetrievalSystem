<template>
  <div class="sqlite-manager">
    <!-- 页面标题 -->
    <el-page-header
      :title="'SQLite数据库管理'"
      :sub-title="'管理SQLite数据库表结构和数据'"
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
            <el-button type="danger" @click="clearDatabase">
              <el-icon><Delete /></el-icon>
              清空数据库
            </el-button>
            <el-button @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" @click="addRecord">
              <el-icon><Plus /></el-icon>
              新增记录
            </el-button>
            <el-alert
              :title="dbStatus.message"
              :type="dbStatus.type"
              show-icon
              :closable="false"
              class="status-alert"
            />
          </div>
          
          <!-- 表选择器 -->
          <div class="toolbar-right">
            <el-select v-model="selectedTable" placeholder="选择表" @change="loadTableData" class="table-select" :loading="loadingTables">
              <el-option v-for="table in tableList" :key="table.name" :label="`${table.name} (${table.count} 条记录)`" :value="table.name" />
            </el-select>
          </div>
        </div>
      </el-card>
      
      <!-- 表数据 -->
      <el-card shadow="hover" v-if="selectedTable" class="data-card">
        <template #header>
          <div class="card-header">
            <span>{{ tableTitle }}</span>
          </div>
        </template>
        
        <div class="table-data">
          <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe border>
            <el-table-column v-for="column in tableColumns" :key="column.prop" :prop="column.prop" :label="column.label" show-overflow-tooltip />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="editRecord(scope.row)" :icon="Edit">
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click="deleteRecord(scope.row)" :icon="Delete">
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
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
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
        :title="editingRecord ? '编辑记录' : '新增记录'"
        width="700px"
        center
      >
        <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
          <el-form-item v-for="column in editableColumns" :key="column.prop" :label="column.label" :prop="column.prop">
            <el-input v-model="formData[column.prop]" :type="getInputType(column.prop)" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showEditDialog = false">取消</el-button>
            <el-button type="primary" @click="saveRecord">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { sqliteApi } from '@/api'

export default {
  name: 'SQLiteManager',
  components: {
    Refresh,
    Plus,
    Edit,
    Delete
  },
  setup() {
    const selectedTable = ref('')
    const tableList = ref([])
    const loadingTables = ref(false)
    const tableData = ref([])
    const tableColumns = ref([])
    const editableColumns = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const showEditDialog = ref(false)
    const editingRecord = ref(null)
    const formData = reactive({})
    const formRules = ref({})
    const formRef = ref(null)
    
    const dbStatus = reactive({
      message: '数据库状态：未连接',
      type: 'warning'
    })
    
    // 表标题
    const tableTitle = computed(() => {
      return selectedTable.value ? `${selectedTable.value} 表` : '数据表'
    })
    
    // 加载表列表
    const loadTables = async () => {
      loadingTables.value = true
      try {
        const response = await sqliteApi.getTables()
        
        if (response && response.data && response.data.tables) {
          tableList.value = response.data.tables
          
          // 如果有表，默认选择第一个
          if (tableList.value.length > 0 && !selectedTable.value) {
            selectedTable.value = tableList.value[0].name
            loadTableData()
          }
        }
      } catch (error) {
        console.error('加载表列表失败:', error)
        ElMessage.error(`加载表列表失败: ${error.message}`)
      } finally {
        loadingTables.value = false
      }
    }
    
    // 加载表数据
    const loadTableData = async () => {
      if (!selectedTable.value) return
      
      loading.value = true
      try {
        const response = await sqliteApi.getTableData(selectedTable.value, {
          page: currentPage.value,
          size: pageSize.value
        })
        
        console.log('SQLite API响应:', response)
        
        if (!response || !response.data) {
          throw new Error('API返回数据为空')
        }
        
        tableData.value = response.data.records || []
        total.value = response.data.total || 0
        tableColumns.value = response.data.columns || []
        
        // 过滤出可编辑的列
        editableColumns.value = tableColumns.value.filter(col => 
          col.prop !== 'id' && col.prop !== 'created_at' && col.prop !== 'updated_at'
        )
        
        dbStatus.message = `数据库状态：已连接，表 ${selectedTable.value} 加载成功`
        dbStatus.type = 'success'
      } catch (error) {
        console.error('加载表数据失败:', error)
        ElMessage.error(`加载表数据失败: ${error.message}`)
        dbStatus.message = `数据库状态：连接失败`
        dbStatus.type = 'error'
      } finally {
        loading.value = false
      }
    }
    
    // 初始化数据库
    const initDatabase = async () => {
      try {
        await ElMessageBox.confirm('确定要初始化数据库吗？这将创建所有必要的表结构。', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await sqliteApi.initDatabase()
        ElMessage.success('数据库初始化成功')
        dbStatus.message = '数据库状态：已初始化'
        dbStatus.type = 'success'
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(`初始化数据库失败: ${error.message}`)
        }
      }
    }
    
    // 清空数据库
    const clearDatabase = async () => {
      try {
        await ElMessageBox.confirm('确定要清空数据库吗？这将删除所有数据且无法恢复！', '危险操作', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await sqliteApi.clearDatabase()
        ElMessage.success('数据库清空成功')
        dbStatus.message = '数据库状态：已清空'
        dbStatus.type = 'success'
        // 重新加载表列表
        loadTables()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(`清空数据库失败: ${error.message}`)
        }
      }
    }
    
    // 新增记录
    const addRecord = () => {
      editingRecord.value = null
      // 清空表单数据
      Object.keys(formData).forEach(key => {
        delete formData[key]
      })
      showEditDialog.value = true
    }
    
    // 编辑记录
    const editRecord = (row) => {
      editingRecord.value = row
      Object.assign(formData, row)
      showEditDialog.value = true
    }
    
    // 保存记录
    const saveRecord = async () => {
      try {
        if (editingRecord.value) {
          // 更新记录
          await sqliteApi.updateRecord(selectedTable.value, editingRecord.value.id, formData)
          ElMessage.success('更新记录成功')
        } else {
          // 新增记录
          await sqliteApi.createRecord(selectedTable.value, formData)
          ElMessage.success('新增记录成功')
        }
        showEditDialog.value = false
        loadTableData()
      } catch (error) {
        ElMessage.error(`保存记录失败: ${error.message}`)
      }
    }
    
    // 删除记录
    const deleteRecord = async (row) => {
      try {
        await ElMessageBox.confirm('确定要删除这条记录吗？', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'danger'
        })
        
        await sqliteApi.deleteRecord(selectedTable.value, row.id)
        ElMessage.success('删除记录成功')
        loadTableData()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(`删除记录失败: ${error.message}`)
        }
      }
    }
    
    // 刷新数据
    const refreshData = () => {
      loadTables()
    }
    
    // 获取输入类型
    const getInputType = (prop) => {
      // 根据字段名判断输入类型
      if (prop.includes('password') || prop.includes('secret')) {
        return 'password'
      }
      return 'text'
    }
    
    // 分页处理
    const handleSizeChange = (size) => {
      pageSize.value = size
      loadTableData()
    }
    
    const handleCurrentChange = (current) => {
      currentPage.value = current
      loadTableData()
    }
    
    onMounted(() => {
      // 初始加载表列表
      loadTables()
    })
    
    return {
      selectedTable,
      tableList,
      loadingTables,
      tableData,
      tableColumns,
      editableColumns,
      loading,
      currentPage,
      pageSize,
      total,
      showEditDialog,
      editingRecord,
      formData,
      formRules,
      formRef,
      dbStatus,
      tableTitle,
      loadTableData,
      loadTables,
      initDatabase,
      clearDatabase,
      addRecord,
      editRecord,
      saveRecord,
      deleteRecord,
      refreshData,
      getInputType,
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
  gap: 10px;
  align-items: center;
}

.table-select {
  min-width: 200px;
}

.status-alert {
  margin: 0;
  min-width: 250px;
}

.status-card {
  margin-bottom: 10px;
}

.data-card {
  margin-bottom: 20px;
}

.table-data {
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
</style>