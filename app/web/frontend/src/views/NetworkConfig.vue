<template>
  <div class="network-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>网络配置</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <!-- API服务配置 -->
        <el-tab-pane label="API服务配置" name="api">
          <el-form :model="apiConfig" label-width="150px" style="max-width: 600px;">
            <el-form-item label="服务器主机地址">
              <el-input v-model="apiConfig.host" placeholder="例如: 0.0.0.0" />
            </el-form-item>
            
            <el-form-item label="服务器端口">
              <el-input v-model.number="apiConfig.port" type="number" placeholder="例如: 8000" />
            </el-form-item>
            
            <el-form-item label="允许的跨域来源">
              <el-input 
                v-model="apiConfig.allowed_origins" 
                type="textarea"
                :rows="3"
                placeholder="多个地址用逗号分隔，例如: http://localhost:3000,http://127.0.0.1:3000" 
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveApiConfig">保存配置</el-button>
              <el-button @click="resetApiConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- LLM API配置 -->
        <el-tab-pane label="LLM API配置" name="llm">
          <el-form :model="llmConfig" label-width="150px" style="max-width: 600px;">
            <el-form-item label="服务类型">
              <el-select v-model="llmConfig.service_type" placeholder="请选择服务类型">
                <el-option label="OpenAI Compatible" value="openai-compatible" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="API基础URL">
              <el-input v-model="llmConfig.base_url" placeholder="例如: http://localhost:11434/v1" />
            </el-form-item>
            
            <el-form-item label="API密钥">
              <el-input 
                v-model="llmConfig.api_key" 
                type="text"
                placeholder="输入API密钥" 
              />
            </el-form-item>
            
            <el-form-item label="模型名称">
              <el-input v-model="llmConfig.model" placeholder="例如: qwen2:7b" />
            </el-form-item>
            
            <el-form-item label="API超时时间（秒）">
              <el-input-number v-model.number="llmConfig.max_tokens" :min="1" :max="3600" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveLlmConfig">保存配置</el-button>
              <el-button @click="testLlmConfig" :loading="testingLlm">测试连接</el-button>
              <el-button @click="resetLlmConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- Embedding API配置 -->
        <el-tab-pane label="Embedding API配置" name="embedding">
          <el-form :model="embeddingConfig" label-width="150px" style="max-width: 600px;">
            <el-form-item label="服务类型">
              <el-select v-model="embeddingConfig.service_type" placeholder="请选择服务类型">
                <el-option label="OpenAI Compatible" value="openai-compatible" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="API基础URL">
              <el-input v-model="embeddingConfig.base_url" placeholder="例如: http://localhost:8080/v1" />
            </el-form-item>
            
            <el-form-item label="API密钥">
              <el-input 
                v-model="embeddingConfig.api_key" 
                type="text"
                placeholder="输入API密钥" 
              />
            </el-form-item>
            
            <el-form-item label="模型名称">
              <el-input v-model="embeddingConfig.model" placeholder="例如: Qwen3-Embedding-4B" />
            </el-form-item>
            
            <el-form-item label="向量维度">
              <el-input-number v-model.number="embeddingConfig.dimensions" :min="1" :max="10000" />
            </el-form-item>
            
            <el-form-item label="API超时时间（秒）">
              <el-input-number v-model.number="embeddingConfig.timeout" :min="1" :max="3600" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveEmbeddingConfig">保存配置</el-button>
              <el-button @click="testEmbeddingConfig" :loading="testingEmbedding">测试连接</el-button>
              <el-button @click="resetEmbeddingConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { configApi, systemApi } from '@/api'

export default {
  name: 'NetworkConfig',
  setup() {
    const activeTab = ref('api')
    
    // API服务配置
    const apiConfig = reactive({
      host: '',
      port: 8000,
      allowed_origins: ''
    })
    
    // LLM配置
    const llmConfig = reactive({
        service_type: 'openai-compatible',
        base_url: 'http://localhost:8080/v1',
        api_key: '',
        model: 'qwen2:7b',
        max_tokens: 300 // API超时时间（秒）
    })
    
    // Embedding配置
    const embeddingConfig = reactive({
      service_type: 'openai-compatible',
      base_url: 'http://localhost:8080/v1',
      api_key: '',
      model: 'Qwen3-Embedding-4B',
      dimensions: 1024,
      timeout: 300 // API超时时间（秒）
    })
    
    const testingLlm = ref(false)
    const testingEmbedding = ref(false)
    
    // 加载现有配置
    const loadConfig = async () => {
      try {
        const config = await configApi.getConfig()
        
        // 加载API配置
        apiConfig.host = config.data?.server?.host || '127.0.0.1'
        apiConfig.port = config.data?.server?.port || 8000
        apiConfig.allowed_origins = Array.isArray(config.data?.cors?.origins)
          ? config.data.cors.origins.join(',')
          : (config.data?.cors?.origins || '')
        
        // 加载LLM配置
        if (config.data?.llm) {
          Object.assign(llmConfig, {
            service_type: config.data.llm.service_type || '',
            base_url: config.data.llm.base_url || '',
            api_key: config.data.llm.api_key || '',
            model: config.data.llm.model || '',
            max_tokens: config.data.llm.max_tokens || 4096
          })
        }
        
        // 加载Embedding配置
        if (config.data?.embedding) {
          Object.assign(embeddingConfig, {
            service_type: config.data.embedding.service_type || '',
            base_url: config.data.embedding.base_url || '',
            api_key: config.data.embedding.api_key || '',
            model: config.data.embedding.model || '',
            dimensions: config.data.embedding.dimensions || 1024,
            timeout: config.data.embedding.timeout || 300
          })
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        ElMessage.error('加载配置失败: ' + error.message)
      }
    }
    
    // 保存API配置
    const saveApiConfig = async () => {
      try {
        const configData = {
          server: {
            host: apiConfig.host,
            port: apiConfig.port
          },
          cors: {
            origins: apiConfig.allowed_origins.split(',').map(s => s.trim()).filter(s => s)
          }
        }
        
        const response = await configApi.updateConfig(configData)
        if (response.needs_restart) {
          // 显示重启提示对话框
          try {
            await ElMessageBox.confirm(
              '配置更新成功，但需要重启服务器才能生效。\n\n请选择以下操作：',
              '需要重启服务器',
              {
                confirmButtonText: '立即重启',
                cancelButtonText: '放弃修改',
                type: 'warning',
                customClass: 'restart-dialog'
              }
            )
            
            // 用户选择立即重启
            ElMessage.info('正在重启服务器...')
            try {
              // 调用后端重启服务器API
              await systemApi.restartServer()
              ElMessage.success('服务器重启请求已发送，请等待服务重新启动')
              
              // 3秒后刷新页面
              setTimeout(() => {
                window.location.reload()
              }, 3000)
            } catch (restartError) {
              console.error('重启服务器失败:', restartError)
              ElMessage.error('重启服务器失败: ' + restartError.message)
              // 重新加载配置以确保前端显示最新值
              await loadConfig()
            }
          } catch (error) {
            // 用户选择放弃修改
            if (error !== 'cancel') {
              console.error('对话框操作失败:', error)
              ElMessage.error('操作失败: ' + error.message)
            } else {
              // 放弃修改，重新加载原始配置
              ElMessage.info('已放弃修改，恢复原始配置')
              await loadConfig()
            }
          }
        } else {
          ElMessage.success(response.message)
          // 重新加载配置以确保前端显示最新值
          await loadConfig()
        }
      } catch (error) {
        console.error('保存API配置失败:', error)
        ElMessage.error('保存API配置失败: ' + error.message)
      }
    }
    
    // 保存LLM配置
    const saveLlmConfig = async () => {
      try {
        const configData = {
          llm: {
            service_type: llmConfig.service_type,
            base_url: llmConfig.base_url,
            api_key: llmConfig.api_key,
            model: llmConfig.model,
            max_tokens: llmConfig.max_tokens
          }
        }
        
        const response = await configApi.updateConfig(configData)
        if (response.needs_restart) {
          ElMessage.warning(response.message)
        } else {
          ElMessage.success(response.message)
        }
        
        // 重新加载配置以确保前端显示最新值
        await loadConfig()
      } catch (error) {
        console.error('保存LLM配置失败:', error)
        ElMessage.error('保存LLM配置失败: ' + error.message)
      }
    }
    
    // 测试LLM配置
    const testLlmConfig = async () => {
      testingLlm.value = true
      try {
        await configApi.testLlmConfig({
          service_type: llmConfig.service_type,
          base_url: llmConfig.base_url,
          api_key: llmConfig.api_key,
          model: llmConfig.model
        })
        ElMessage.success('LLM连接测试成功')
      } catch (error) {
        console.error('LLM连接测试失败:', error)
        ElMessage.error('LLM连接测试失败: ' + error.message)
      } finally {
        testingLlm.value = false
      }
    }
    
    // 保存Embedding配置
    const saveEmbeddingConfig = async () => {
      try {
        const configData = {
          embedding: {
            service_type: embeddingConfig.service_type,
            base_url: embeddingConfig.base_url,
            api_key: embeddingConfig.api_key,
            model: embeddingConfig.model,
            dimensions: embeddingConfig.dimensions,
            timeout: embeddingConfig.timeout
          }
        }
        
        const response = await configApi.updateConfig(configData)
        if (response.needs_restart) {
          ElMessage.warning(response.message)
        } else {
          ElMessage.success(response.message)
        }
        
        // 重新加载配置以确保前端显示最新值
        await loadConfig()
      } catch (error) {
        console.error('保存Embedding配置失败:', error)
        ElMessage.error('保存Embedding配置失败: ' + error.message)
      }
    }
    
    // 测试Embedding配置
    const testEmbeddingConfig = async () => {
      testingEmbedding.value = true
      try {
        await configApi.testEmbeddingConfig({
          service_type: embeddingConfig.service_type,
          base_url: embeddingConfig.base_url,
          api_key: embeddingConfig.api_key,
          model: embeddingConfig.model,
          timeout: embeddingConfig.timeout
        })
        ElMessage.success('Embedding连接测试成功')
      } catch (error) {
        console.error('Embedding连接测试失败:', error)
        ElMessage.error('Embedding连接测试失败: ' + error.message)
      } finally {
        testingEmbedding.value = false
      }
    }
    
    // 重置配置
    const resetApiConfig = () => {
      loadConfig()
    }
    
    const resetLlmConfig = () => {
        // 重置为默认值
        Object.assign(llmConfig, {
            service_type: 'openai-compatible',
            base_url: 'http://localhost:8080/v1',
            api_key: '',
            model: 'qwen2:7b',
            max_tokens: 300 // API超时时间（秒）
        })
    }
    
    const resetEmbeddingConfig = () => {
      // 重置为默认值
      Object.assign(embeddingConfig, {
        service_type: 'openai-compatible',
        base_url: 'http://localhost:8080/v1',
        api_key: '',
        model: 'Qwen3-Embedding-4B',
        dimensions: 1024,
        timeout: 300 // API超时时间（秒）
      })
    }
    
    onMounted(() => {
      loadConfig()
    })
    
    return {
      activeTab,
      apiConfig,
      llmConfig,
      embeddingConfig,
      testingLlm,
      testingEmbedding,
      saveApiConfig,
      saveLlmConfig,
      testLlmConfig,
      saveEmbeddingConfig,
      testEmbeddingConfig,
      resetApiConfig,
      resetLlmConfig,
      resetEmbeddingConfig
    }
  }
}
</script>

<style scoped>
.network-config {
  padding: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}
</style>