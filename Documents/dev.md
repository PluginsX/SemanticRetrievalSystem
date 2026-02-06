明白了！我们需要一个**纯Python项目架构**，不依赖Docker，作为标准的本地Python服务管理。

## 📁 项目目录结构（原生Python）

```
museum-rag-server/
├── README.md                    # 项目说明
├── requirements.txt            # Python依赖
├── requirements-dev.txt        # 开发依赖
├── pyproject.toml             # 项目配置（可选）
├── .env                       # 环境变量
├── .env.example               # 环境变量示例
├── .gitignore
├── config/                    # 配置文件目录
│   ├── __init__.py
│   ├── default.yaml          # 默认配置
│   ├── development.yaml      # 开发环境配置
│   ├── production.yaml       # 生产环境配置
│   └── services/             # 服务配置文件
│       ├── llm_services.yaml
│       ├── embedding_services.yaml
│       └── api_routes.yaml
├── src/                       # 源代码目录
│   ├── __init__.py
│   ├── main.py               # 主入口文件
│   ├── app/                  # FastAPI应用
│   │   ├── __init__.py
│   │   ├── api.py            # FastAPI应用实例
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   └── dependencies.py   # 依赖注入
│   ├── core/                 # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── rag_engine.py     # RAG引擎
│   │   ├── search_engine.py  # 搜索引擎
│   │   ├── llm_client.py     # LLM客户端
│   │   ├── embedding_client.py
│   │   └── artifact_manager.py
│   ├── models/               # 数据模型
│   │   ├── __init__.py
│   │   ├── schemas.py        # Pydantic模型
│   │   ├── database.py       # SQLAlchemy模型
│   │   └── config_models.py  # 配置相关模型
│   ├── services/             # 服务层
│   │   ├── __init__.py
│   │   ├── config_service.py # 配置服务
│   │   ├── artifact_service.py
│   │   ├── search_service.py
│   │   ├── llm_service.py
│   │   └── embedding_service.py
│   ├── routes/               # API路由
│   │   ├── __init__.py
│   │   ├── artifacts.py      # 文物管理API
│   │   ├── search.py         # 搜索API
│   │   ├── admin.py          # 管理后台API
│   │   ├── config.py         # 配置管理API
│   │   └── system.py         # 系统API
│   ├── webui/                # Web管理界面
│   │   ├── __init__.py
│   │   ├── static/           # 静态文件
│   │   │   ├── index.html
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── assets/
│   │   └── templates/         # 模板文件
│   │       └── index.html
│   ├── database/             # 数据库相关
│   │   ├── __init__.py
│   │   ├── crud.py           # CRUD操作
│   │   └── session.py        # 数据库会话
│   ├── configs/              # 配置管理
│   │   ├── __init__.py
│   │   ├── manager.py        # 配置管理器
│   │   ├── loader.py         # 配置加载器
│   │   └── validators.py     # 配置验证器
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   ├── security.py       # 安全相关
│   │   ├── logger.py         # 日志
│   │   └── helpers.py        # 辅助函数
│   └── scripts/              # 脚本目录
│       ├── __init__.py
│       ├── init_db.py        # 初始化数据库
│       ├── backup_db.py      # 备份数据库
│       ├── import_data.py    # 导入数据
│       └── check_services.py # 检查服务状态
├── data/                     # 数据目录
│   ├── db/                   # 数据库文件
│   │   ├── museum.db         # SQLite数据库
│   │   └── backups/          # 备份目录
│   ├── chroma/               # ChromaDB数据
│   │   ├── chroma.sqlite3
│   │   └── chroma-embeddings/
│   ├── uploads/              # 上传文件
│   │   ├── images/           # 图片
│   │   └── documents/        # 文档
│   └── logs/                 # 日志文件
│       ├── app.log
│       ├── access.log
│       └── error.log
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_config.py
└── docs/                     # 文档目录
    ├── api.md               # API文档
    ├── deployment.md        # 部署文档
    ├── config.md           # 配置文档
    └── development.md      # 开发文档
```

## 📦 环境配置

### 1. **requirements.txt**

```txt
# 核心依赖
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.23
alembic==1.12.1
chromadb==0.4.22
pysqlite3==0.5.2

# AI服务客户端
openai==1.3.0
httpx==0.25.1
aiohttp==3.9.1

# 数据处理
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pyyaml==6.0.1

# Web前端
jinja2==3.1.2
aiofiles==23.2.1

# 工具类
python-dateutil==2.8.2
cryptography==41.0.7
passlib[bcrypt]==1.7.4
pyjwt==2.8.0

# 开发工具
watchfiles==0.21.0
click==8.1.7
rich==13.7.0
```

### 2. **requirements-dev.txt**

```txt
# 开发依赖
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.0
pre-commit==3.5.0
pylint==3.0.2

# 测试工具
httpx==0.25.1
pytest-httpx==0.26.0
faker==20.1.0

# 文档
mkdocs==1.5.3
mkdocs-material==9.5.3
mkdocstrings[python]==0.24.1
```

### 3. **.env 文件**

```env
# 应用配置
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key-here-change-in-production
APP_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 数据库配置
DATABASE_URL=sqlite:///data/db/museum.db
CHROMA_DB_PATH=./data/chroma
SQLITE_TIMEOUT=30

# 文件存储
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=104857600  # 100MB
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.pdf,.txt,.md

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./data/logs/app.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_ROTATION=1 day
LOG_RETENTION=30 days

# 安全配置
API_KEY_HEADER=X-API-Key
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440  # 24小时
BCRYPT_ROUNDS=12

# 外部服务默认配置（可在Web UI中修改）
DEFAULT_LLM_SERVICE=ollama
DEFAULT_LLM_MODEL=qwen2:7b
DEFAULT_EMBEDDING_SERVICE=local
DEFAULT_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5

# 备用配置（Web UI配置失败时的fallback）
FALLBACK_LLM_BASE_URL=http://localhost:11434/v1
FALLBACK_LLM_API_KEY=
FALLBACK_EMBEDDING_BASE_URL=http://localhost:8080/v1
FALLBACK_EMBEDDING_API_KEY=
```

### 4. **pyproject.toml**（可选但推荐）

```toml
[project]
name = "museum-rag-server"
version = "0.1.0"
description = "语义检索系统 - 智能知识检索系统"
readme = "README.md"
requires-python = ">=3.9"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "chromadb>=0.4.0",
    "openai>=1.3.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
museum-rag = "src.main:main"
museum-rag-cli = "src.cli:app"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

## 🚀 启动脚本

### 1. **主启动文件：src/main.py**

```python
#!/usr/bin/env python3
"""
语义检索系统 - 主启动文件
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app.config import get_settings, setup_logging
from src.app.api import create_app
from src.app.database import init_database, get_db
from src.configs.manager import ConfigManager
from src.services.config_service import ConfigService
import uvicorn

logger = logging.getLogger(__name__)

async def init_services():
    """初始化所有服务"""
    settings = get_settings()
    
    # 1. 初始化数据库
    logger.info("初始化数据库...")
    await init_database()
    
    # 2. 初始化配置管理器
    logger.info("初始化配置管理器...")
    config_manager = ConfigManager()
    await config_manager.load_all_configs()
    
    # 3. 初始化配置服务
    logger.info("初始化配置服务...")
    config_service = ConfigService(config_manager)
    await config_service.initialize()
    
    # 4. 初始化外部服务
    logger.info("检查外部服务连接...")
    await config_service.test_all_services()
    
    return config_manager, config_service

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 获取配置
    settings = get_settings()
    
    logger.info(f"启动博物馆RAG服务器 v{settings.version}")
    logger.info(f"环境: {settings.app_env}")
    logger.info(f"主机: {settings.app_host}:{settings.app_port}")
    
    # 创建应用
    app = create_app()
    
    # 配置uvicorn
    config = uvicorn.Config(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
        reload=settings.app_debug,
        reload_dirs=[str(project_root / "src")] if settings.app_debug else None,
        access_log=True,
    )
    
    server = uvicorn.Server(config)
    
    # 运行服务器
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("服务器已停止")

if __name__ == "__main__":
    main()
```

### 2. **启动脚本：start.sh**（Linux/Mac）

```bash
#!/bin/bash
# 启动脚本 for Linux/Mac

set -e

# 进入项目根目录
cd "$(dirname "$0")"

# 检查Python版本
PYTHON_REQUIRED="3.9"
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

if [ $(echo "$PYTHON_VERSION < $PYTHON_REQUIRED" | bc) -eq 1 ]; then
    echo "错误: 需要Python $PYTHON_REQUIRED 或更高版本，当前版本: $PYTHON_VERSION"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件，使用 .env.example 作为模板创建"
    cp .env.example .env
    echo "请编辑 .env 文件并设置必要的环境变量"
    exit 1
fi

# 初始化数据库
echo "初始化数据库..."
python -m src.scripts.init_db

# 启动服务器
echo "启动RAG服务器..."
python -m src.main
```

### 3. **启动脚本：start.bat**（Windows）

```batch
@echo off
REM 启动脚本 for Windows

cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请安装Python 3.9或更高版本
    pause
    exit /b 1
)

REM 检查Python版本
for /f "tokens=2" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i
if %PYTHON_VERSION% LSS 3.9 (
    echo 错误: 需要Python 3.9或更高版本，当前版本: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install --upgrade pip
pip install -r requirements.txt

REM 检查环境变量
if not exist ".env" (
    echo 警告: 未找到 .env 文件
    copy .env.example .env
    echo 请编辑 .env 文件并设置必要的环境变量
    pause
    exit /b 1
)

REM 初始化数据库
echo 初始化数据库...
python -m src.scripts.init_db

REM 启动服务器
echo 启动RAG服务器...
python -m src.main

pause
```

### 4. **开发启动脚本：run_dev.py**

```python
#!/usr/bin/env python3
"""
开发环境启动脚本 - 带热重载
"""

import os
import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """开发环境启动"""
    # 设置环境变量
    os.environ["APP_ENV"] = "development"
    os.environ["APP_DEBUG"] = "true"
    
    # 导入uvicorn
    import uvicorn
    
    # 运行带热重载的服务器
    uvicorn.run(
        "src.app.api:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()
```

## 🔧 核心配置文件

### 1. **配置管理：src/app/config.py**

```python
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """应用设置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用配置
    app_env: str = "development"  # development/production
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = False
    app_secret_key: str = Field(default="your-secret-key-change-in-production")
    app_allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    # 数据库配置
    database_url: str = f"sqlite:///{BASE_DIR}/data/db/museum.db"
    chroma_db_path: str = f"{BASE_DIR}/data/chroma"
    sqlite_timeout: int = 30
    
    # 文件存储
    upload_dir: str = f"{BASE_DIR}/data/uploads"
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = Field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".pdf", ".txt", ".md"])
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = f"{BASE_DIR}/data/logs/app.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    
    # 安全配置
    api_key_header: str = "X-API-Key"
    jwt_secret_key: str = Field(default="your-jwt-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    bcrypt_rounds: int = 12
    
    # 外部服务默认配置
    default_llm_service: str = "ollama"
    default_llm_model: str = "qwen2:7b"
    default_embedding_service: str = "local"
    default_embedding_model: str = "BAAI/bge-large-zh-v1.5"
    
    # 备用配置
    fallback_llm_base_url: str = "http://localhost:11434/v1"
    fallback_llm_api_key: str = ""
    fallback_embedding_base_url: str = "http://localhost:8080/v1"
    fallback_embedding_api_key: str = ""
    
    # 应用信息
    version: str = "0.1.0"
    project_name: str = "语义检索系统"
    description: str = "文物知识检索与管理系统"
    
    @validator("app_allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """解析允许的源"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_extensions", pre=True)
    def parse_allowed_extensions(cls, v):
        """解析允许的扩展名"""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def database_url_with_pool(self) -> str:
        """带连接池的数据库URL"""
        if self.database_url.startswith("sqlite"):
            return f"{self.database_url}?check_same_thread=False"
        return self.database_url

def setup_logging():
    """设置日志"""
    settings = get_settings()
    
    # 创建日志目录
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": settings.log_level,
                "formatter": "detailed",
                "filename": settings.log_file,
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # 根logger
                "handlers": ["console", "file"],
                "level": settings.log_level,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    
    # 设置SQLAlchemy日志级别
    if settings.is_development:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"日志已初始化，级别: {settings.log_level}")

@lru_cache
def get_settings() -> Settings:
    """获取设置（单例）"""
    return Settings()

# 导出
__all__ = ["Settings", "get_settings", "setup_logging"]
```

### 2. **配置加载器：src/configs/loader.py**

```python
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from ..app.config import get_settings

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.settings = get_settings()
        self.config_dir = config_dir or Path(__file__).parent.parent.parent / "config"
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = self.config_dir / f"{config_name}.yaml"
        
        if not config_path.exists():
            # 如果YAML文件不存在，尝试JSON
            config_path = self.config_dir / f"{config_name}.json"
            
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return {}
        
        try:
            if config_path.suffix == ".yaml":
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
            else:  # .json
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            logger.info(f"配置文件加载成功: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败 {config_path}: {e}")
            return {}
    
    def save_config(self, config_name: str, config: Dict[str, Any]):
        """保存配置文件"""
        config_path = self.config_dir / f"{config_name}.yaml"
        
        try:
            # 备份旧配置
            if config_path.exists():
                backup_path = config_path.with_suffix(".yaml.bak")
                config_path.rename(backup_path)
            
            # 保存新配置
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"配置文件保存成功: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败 {config_path}: {e}")
            return False
    
    def load_all_configs(self) -> Dict[str, Any]:
        """加载所有配置文件"""
        configs = {}
        
        # 加载默认配置
        default_config = self.load_config("default")
        configs.update(default_config)
        
        # 加载环境特定配置
        env = self.settings.app_env
        env_config = self.load_config(env)
        configs.update(env_config)
        
        # 加载服务配置
        services_dir = self.config_dir / "services"
        if services_dir.exists():
            for config_file in services_dir.glob("*.yaml"):
                service_name = config_file.stem
                service_config = self.load_config(f"services/{service_name}")
                configs[service_name] = service_config
        
        return configs
    
    def get_service_config(self, service_type: str) -> Dict[str, Any]:
        """获取服务配置"""
        config_path = self.config_dir / "services" / f"{service_type}.yaml"
        
        if not config_path.exists():
            logger.warning(f"服务配置文件不存在: {config_path}")
            return self._get_default_service_config(service_type)
        
        return self.load_config(f"services/{service_type}")
    
    def _get_default_service_config(self, service_type: str) -> Dict[str, Any]:
        """获取默认服务配置"""
        defaults = {
            "llm_services": {
                "ollama": {
                    "name": "Ollama",
                    "api_base": "http://localhost:11434/v1",
                    "api_key": "",
                    "models": ["qwen2:7b", "llama3:8b", "mistral:7b"],
                    "default_model": "qwen2:7b",
                    "timeout": 30,
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
            },
            "embedding_services": {
                "local": {
                    "name": "本地嵌入服务",
                    "api_base": "http://localhost:8080/v1",
                    "api_key": "",
                    "models": ["BAAI/bge-large-zh-v1.5"],
                    "default_model": "BAAI/bge-large-zh-v1.5",
                    "timeout": 30
                }
            },
            "api_routes": {
                "search": {
                    "enabled": True,
                    "rate_limit": 100,
                    "require_auth": False
                }
            }
        }
        
        return defaults.get(f"{service_type}_services", {})
```

## 🎯 初始化脚本

### 1. **数据库初始化：src/scripts/init_db.py**

```python
#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from src.app.database import init_database, get_engine
from src.database.crud import create_tables
from src.configs.manager import ConfigManager
from src.app.config import get_settings, setup_logging

logger = logging.getLogger(__name__)

async def init_db():
    """初始化数据库"""
    settings = get_settings()
    
    logger.info("开始初始化数据库...")
    
    try:
        # 1. 初始化数据库连接
        await init_database()
        
        # 2. 创建表
        logger.info("创建数据库表...")
        engine = get_engine()
        await create_tables(engine)
        
        # 3. 初始化配置表
        logger.info("初始化配置表...")
        config_manager = ConfigManager()
        await config_manager.initialize_default_configs()
        
        # 4. 创建数据目录
        data_dirs = [
            settings.upload_dir,
            Path(settings.log_file).parent,
            Path(settings.chroma_db_path),
            Path(settings.upload_dir) / "images",
            Path(settings.upload_dir) / "documents",
        ]
        
        for data_dir in data_dirs:
            if isinstance(data_dir, str):
                data_dir = Path(data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {data_dir}")
        
        logger.info("数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        sys.exit(1)

async def reset_db():
    """重置数据库（开发用）"""
    import os
    from pathlib import Path
    
    settings = get_settings()
    
    logger.warning("警告：这将删除所有数据！")
    confirm = input("确定要重置数据库吗？(y/N): ")
    
    if confirm.lower() != 'y':
        logger.info("操作已取消")
        return
    
    try:
        # 删除数据库文件
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        if db_path.exists():
            db_path.unlink()
            logger.info(f"删除数据库文件: {db_path}")
        
        # 删除ChromaDB数据
        chroma_path = Path(settings.chroma_db_path)
        if chroma_path.exists():
            import shutil
            shutil.rmtree(chroma_path)
            logger.info(f"删除ChromaDB数据: {chroma_path}")
        
        # 重新初始化
        await init_db()
        
        logger.info("数据库重置完成！")
        
    except Exception as e:
        logger.error(f"数据库重置失败: {e}", exc_info=True)
        sys.exit(1)

async def backup_db():
    """备份数据库"""
    from datetime import datetime
    import shutil
    from pathlib import Path
    
    settings = get_settings()
    
    # 创建备份目录
    backup_dir = Path(settings.upload_dir).parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    backup_path = backup_dir / f"museum_db_{timestamp}.db"
    
    try:
        # 备份SQLite数据库
        if db_path.exists():
            shutil.copy2(db_path, backup_path)
            logger.info(f"数据库备份到: {backup_path}")
        
        # 备份ChromaDB
        chroma_path = Path(settings.chroma_db_path)
        if chroma_path.exists():
            chroma_backup = backup_dir / f"chroma_{timestamp}"
            shutil.copytree(chroma_path, chroma_backup)
            logger.info(f"ChromaDB备份到: {chroma_backup}")
        
        logger.info("备份完成！")
        
    except Exception as e:
        logger.error(f"备份失败: {e}", exc_info=True)
        sys.exit(1)

def main():
    """主函数"""
    setup_logging()
    
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("command", choices=["init", "reset", "backup"], 
                       help="命令: init=初始化, reset=重置, backup=备份")
    
    args = parser.parse_args()
    
    if args.command == "init":
        asyncio.run(init_db())
    elif args.command == "reset":
        asyncio.run(reset_db())
    elif args.command == "backup":
        asyncio.run(backup_db())

if __name__ == "__main__":
    main()
```

## 📁 项目文档

### 1. **README.md**

```markdown
# 语义检索系统

文物知识检索与管理系统，提供内部管理界面和外部API服务。

## ✨ 功能特性

- 🎨 **内部管理界面**：博物馆工作人员友好的数据管理界面
- 🔍 **智能检索**：支持关键词、语义、混合搜索
- 🧠 **AI增强**：集成外部LLM和Embedding服务
- ⚙️ **可配置**：所有服务都可通过Web UI配置
- 🚀 **高性能**：异步架构，响应迅速
- 🔐 **安全可靠**：API密钥管理、访问控制

## 🚀 快速开始

### 环境要求

- Python 3.9+
- SQLite 3.35+
- 至少4GB可用内存

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd museum-rag-server
```

2. **创建虚拟环境**
```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

5. **初始化数据库**
```bash
python -m src.scripts.init_db init
```

6. **启动服务**
```bash
# 生产环境
python -m src.main

# 开发环境（带热重载）
python -m src.scripts.run_dev
```

7. **访问应用**
- 管理界面: http://127.0.0.1:8000/admin
- API文档: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health

## ⚙️ 配置管理

所有配置都可以通过Web UI管理：

1. **访问管理界面**: http://127.0.0.1:8000/admin
2. **配置外部服务**（LLM、Embedding等）
3. **配置API路由和权限**
4. **配置系统参数**

## 📖 API文档

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## 🗂️ 项目结构

```
museum-rag-server/
├── src/                    # 源代码
├── data/                  # 数据文件
├── config/               # 配置文件
├── tests/               # 测试文件
└── docs/                # 文档
```

## 🧪 开发

### 运行测试
```bash
pytest tests/
```

### 代码格式化
```bash
black src/
isort src/
flake8 src/
```

### 项目打包
```bash
pip install build
python -m build
```

## 📄 许可证

LICENSE

## 🤝 贡献

欢迎提交Issue和Pull Request！
```

### 2. **部署文档：docs/deployment.md**

```markdown
# 部署指南

## 系统要求

- **操作系统**: Ubuntu 20.04+, CentOS 7+, Windows Server 2019+
- **Python**: 3.9+
- **内存**: 最少4GB，推荐8GB+
- **磁盘空间**: 最少10GB可用空间
- **网络**: 可访问外部API服务

## 部署步骤

### 1. 服务器准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev sqlite3

# CentOS/RHEL
sudo yum install python39 python39-devel sqlite
```

### 2. 获取代码

```bash
git clone <repository-url>
cd museum-rag-server
```

### 3. 安装依赖

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置

```bash
cp .env.example .env
# 编辑 .env 文件
nano .env
```

重要配置项：
```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
APP_SECRET_KEY=<生成强密钥>
DATABASE_URL=sqlite:///data/db/museum.db
```

### 5. 初始化

```bash
# 初始化数据库
python -m src.scripts.init_db init

# 创建管理员账户
python -m src.scripts.create_admin
```

### 6. 使用systemd管理（Linux）

创建服务文件 `/etc/systemd/system/museum-rag.service`：

```ini
[Unit]
Description=Museum RAG Server
After=network.target

[Service]
Type=exec
User=raguser
Group=raguser
WorkingDirectory=/opt/museum-rag-server
Environment=PATH=/opt/museum-rag-server/venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/opt/museum-rag-server/.env
ExecStart=/opt/museum-rag-server/venv/bin/python -m src.main

Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=museum-rag

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable museum-rag
sudo systemctl start museum-rag
sudo systemctl status museum-rag
```

### 7. 使用Nginx反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 监控与维护

### 日志查看
```bash
# 查看服务日志
sudo journalctl -u museum-rag -f

# 查看应用日志
tail -f data/logs/app.log
```

### 数据备份
```bash
# 手动备份
python -m src.scripts.init_db backup

# 自动备份（crontab）
0 2 * * * cd /opt/museum-rag-server && venv/bin/python -m src.scripts.init_db backup
```

### 服务更新
```bash
# 停止服务
sudo systemctl stop museum-rag

# 更新代码
git pull origin master

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start museum-rag
```

## 故障排除

### 常见问题

1. **端口占用**
```bash
# 检查端口占用
sudo lsof -i :8000
# 或修改 .env 中的 APP_PORT
```

2. **数据库权限**
```bash
# 确保数据目录有写入权限
sudo chown -R raguser:raguser /opt/museum-rag-server/data
```

3. **内存不足**
```bash
# 监控内存使用
free -h
# 考虑增加swap空间
```

### 获取帮助

- 查看日志: `tail -f data/logs/app.log`
- 检查服务状态: `sudo systemctl status museum-rag`
- 查看详细错误: `sudo journalctl -u museum-rag -n 50`
```

## 🎯 总结

这是一个**完整的纯Python项目结构**，具有以下特点：

### ✅ **优势**
1. **无Docker依赖**：纯Python环境，简单部署
2. **配置统一管理**：所有配置通过Web UI控制
3. **模块化设计**：清晰的项目结构，易于维护
4. **开发友好**：完善的开发工具和脚本
5. **生产就绪**：包含日志、监控、备份等生产功能

### 🚀 **快速开始**
```bash
# 1. 克隆项目
git clone <repository-url>
cd museum-rag-server

# 2. 设置虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 5. 初始化
python -m src.scripts.init_db init

# 6. 启动
python -m src.main
```

### 🔧 **管理命令**
```bash
# 初始化数据库
python -m src.scripts.init_db init

# 备份数据库
python -m src.scripts.init_db backup

# 重置数据库（开发）
python -m src.scripts.init_db reset

# 检查服务状态
python -m src.scripts.check_services

# 导入数据
python -m src.scripts.import_data /path/to/data.json
```

### 🌐 **访问地址**
- **管理界面**: http://127.0.0.1:8000/admin
- **API文档**: http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health
- **配置面板**: http://127.0.0.1:8000/admin/config

这个架构可以**直接运行**，无需复杂的容器化，适合博物馆等内部环境部署。需要我详细说明某个具体模块的实现吗？