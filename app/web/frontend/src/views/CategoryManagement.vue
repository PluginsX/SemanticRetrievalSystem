<template>
  <el-dialog
    v-model="visible"
    title="分类管理"
    width="600px"
    :before-close="handleClose"
  >
    <div class="category-management">
      <div class="category-actions">
        <el-input
          v-model="newCategory"
          placeholder="输入新分类名称"
          style="width: 300px; margin-right: 10px;"
          @keyup.enter="addCategory"
        >
          <template #append>
            <el-button @click="addCategory">添加</el-button>
          </template>
        </el-input>
      </div>
      
      <div class="category-list">
        <el-table
          :data="categories"
          style="width: 100%; margin-top: 20px;"
          empty-text="暂无分类"
        >
          <el-table-column prop="name" label="分类名称" width="300" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button link type="primary" @click="editCategory(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteCategory(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="saveCategories">保存</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'CategoryManagement',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'saved'],
  setup(props, { emit }) {
    const visible = ref(props.modelValue)
    const newCategory = ref('')
    const categories = ref([])
    
    // 监听props变化
    const updateVisible = (val) => {
      visible.value = val
      if (val) {
        loadCategories()
      }
    }
    
    // 加载分类列表
    const loadCategories = async () => {
      try {
        // 模拟加载分类数据 - 在实际实现中，这里应该调用API
        // 目前我们使用模拟数据，后续需要与后端API集成
        categories.value = [
          { id: 1, name: '技术文档' },
          { id: 2, name: '产品说明' },
          { id: 3, name: '用户手册' },
          { id: 4, name: '青铜器' }
        ]
      } catch (error) {
        console.error('加载分类失败:', error)
        ElMessage.error('加载分类失败: ' + error.message)
      }
    }
    
    // 添加分类
    const addCategory = () => {
      if (!newCategory.value.trim()) {
        ElMessage.warning('请输入分类名称')
        return
      }
      
      const exists = categories.value.some(cat => cat.name === newCategory.value.trim())
      if (exists) {
        ElMessage.warning('分类名称已存在')
        return
      }
      
      categories.value.push({
        id: Date.now(), // 临时ID，实际使用时应由后端生成
        name: newCategory.value.trim()
      })
      
      newCategory.value = ''
      ElMessage.success('分类添加成功')
    }
    
    // 编辑分类
    const editCategory = (row) => {
      ElMessageBox.prompt('请输入新的分类名称', '编辑分类', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: row.name
      }).then(({ value }) => {
        if (!value.trim()) {
          ElMessage.warning('分类名称不能为空')
          return
        }
        
        const exists = categories.value.some(cat => 
          cat.id !== row.id && cat.name === value.trim()
        )
        
        if (exists) {
          ElMessage.warning('分类名称已存在')
          return
        }
        
        row.name = value.trim()
        ElMessage.success('分类更新成功')
      }).catch(() => {
        // 用户取消操作
      })
    }
    
    // 删除分类
    const deleteCategory = (row) => {
      ElMessageBox.confirm(
        `确定要删除分类 "${row.name}" 吗？此操作不会删除相关资料。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        categories.value = categories.value.filter(cat => cat.id !== row.id)
        ElMessage.success('分类删除成功')
      }).catch(() => {
        // 用户取消操作
      })
    }
    
    // 保存分类
    const saveCategories = async () => {
      try {
        // 在实际实现中，这里应该调用API保存分类
        console.log('保存分类:', categories.value)
        ElMessage.success('分类保存成功')
        emit('saved', categories.value)
        handleClose()
      } catch (error) {
        console.error('保存分类失败:', error)
        ElMessage.error('保存分类失败: ' + error.message)
      }
    }
    
    // 关闭对话框
    const handleClose = () => {
      emit('update:modelValue', false)
    }
    
    onMounted(() => {
      if (props.modelValue) {
        loadCategories()
      }
    })
    
    return {
      visible,
      newCategory,
      categories,
      updateVisible,
      loadCategories,
      addCategory,
      editCategory,
      deleteCategory,
      saveCategories,
      handleClose
    }
  },
  watch: {
    modelValue(val) {
      this.updateVisible(val)
    },
    visible(val) {
      this.$emit('update:modelValue', val)
    }
  }
}
</script>

<style scoped>
.category-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-list {
  max-height: 400px;
  overflow-y: auto;
}
</style>