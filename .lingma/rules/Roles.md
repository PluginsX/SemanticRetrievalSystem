---
trigger: always_on
---
# 全部使用中文交流

# 所有的python命令运行前必须先激活项目专用环境 .\venv\Scripts\Activate.ps1

# 所有pip指令都用官方源安装依赖：-i https://pypi.org/simple --trusted-host pypi.org

# LLM API
base_url: http://localhost:11434/v1
api_key: ollama
model_id: qwen2:7b

# Embedding API
base_url: http://localhost:5000/v1
api_key: sk-ccahwXzZsrbLaXIidBQsnv8FVIbk8Y1BjgUdnFiHjFiuGSW3
model_id: Qwen3-Embedding-4B

# 规范化文件命名 
 不要包含任何开发者的标记性质命名！例如 “增强版”“新版”“修正版”等等

# 遵守覆盖原则
同一个模块，新版本要彻底替换旧版本，不能保留旧版本的文件！

# 忽略兼容原则
任何时候都不能因为兼容问题而保留旧版本的文件！一切以新的架构实现需求为准。

# 前后端同步修改
前后端关联内容必须同步修改，前端修改后必须重新构建

# 前端构建命令：“cd E:\Project\Python\SemanticRetrievalSystem\app\web\frontend; npm run build;”