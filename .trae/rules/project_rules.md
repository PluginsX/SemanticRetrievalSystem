0. PowerShell中， && 不是有效的语句分隔符。需要使用分号 ; 来分隔命令
   
1. 全部使用中文交流

2. 所有的python命令运行前必须先激活项目专用环境 .\venv\Scripts\Activate.ps1

3. 所有pip指令都用官方源安装依赖：-i https://pypi.org/simple --trusted-host pypi.org

4. 规范化文件命名 
 不要包含任何开发者的标记性质命名！例如 “增强版”“新版”“修正版”等等

1. 遵守覆盖原则
同一个模块，新版本要彻底替换旧版本，不能保留旧版本的文件！

1. 忽略兼容原则
任何时候都不能因为兼容问题而保留旧版本的文件！一切以新的架构实现需求为准。

1. 前后端同步修改
前后端关联内容必须同步修改，前端修改后必须重新构建

1. 前端构建命令：“cd E:\Project\Python\SemanticRetrievalSystem\app\web\frontend; npm run build;”

2. API 配置信息
## Embedding API（Qwen3-Embedding-4B）
- **Base URL**: `http://127.0.0.1:11434/v1`
- **Model ID**: `qwen3-embedding-4b`
- **API Key**: `ollama`
## LLM API（Qwen2:7b）
- **Base URL**: `http://127.0.0.1:11434/v1`
- **Model ID**: `qwen2:7b`
- **API Key**: `ollama`

1.  所有涉及模型调用的接口严格按照OpenAI API规范实现
    
2.  严格遵守模块化开发原则！单一职责原则！最小化修改原则！严谨遍地微调修改！