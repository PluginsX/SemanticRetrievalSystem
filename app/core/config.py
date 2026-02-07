"""
统一配置管理器 - 基于运行时配置对象
实现运行时对象与外部文件的双向同步
"""
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from .config_runtime import runtime_config as rt_config

class Config:
    """应用配置类 - 基于运行时配置对象"""
    
    def __init__(self):
        """初始化配置管理器"""
        self._rt_config = rt_config
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 确保数据库目录存在
        sqlite_path = Path(self.SQLITE_DB_PATH).parent
        sqlite_path.mkdir(parents=True, exist_ok=True)
        
        # 确保Chroma目录存在
        chroma_path = Path(self.CHROMA_PERSIST_DIR)
        chroma_path.mkdir(parents=True, exist_ok=True)
        
        # 确保临时目录存在
        temp_path = Path(self.TEMP_DIRECTORY)
        temp_path.mkdir(parents=True, exist_ok=True)
    
    # 应用配置
    @property
    def APP_NAME(self) -> str:
        return getattr(self._rt_config, 'APP_NAME', '语义检索系统')
    
    @APP_NAME.setter
    def APP_NAME(self, value: str):
        setattr(self._rt_config, 'APP_NAME', value)
    
    @property
    def APP_VERSION(self) -> str:
        return getattr(self._rt_config, 'APP_VERSION', '1.0.0')
    
    @APP_VERSION.setter
    def APP_VERSION(self, value: str):
        setattr(self._rt_config, 'APP_VERSION', value)
    
    @property
    def APP_ENV(self) -> str:
        return getattr(self._rt_config, 'APP_ENV', 'development')
    
    @APP_ENV.setter
    def APP_ENV(self, value: str):
        setattr(self._rt_config, 'APP_ENV', value)
    
    @property
    def HOST(self) -> str:
        return getattr(self._rt_config, 'HOST', '0.0.0.0')
    
    @HOST.setter
    def HOST(self, value: str):
        setattr(self._rt_config, 'HOST', value)
    
    @property
    def PORT(self) -> int:
        return getattr(self._rt_config, 'PORT', 8001)
    
    @PORT.setter
    def PORT(self, value: int):
        setattr(self._rt_config, 'PORT', value)
    
    @property
    def LOG_LEVEL(self) -> str:
        return getattr(self._rt_config, 'LOG_LEVEL', 'INFO')
    
    @LOG_LEVEL.setter
    def LOG_LEVEL(self, value: str):
        setattr(self._rt_config, 'LOG_LEVEL', value)
    
    @property
    def DEBUG(self) -> bool:
        return getattr(self._rt_config, 'DEBUG', True)
    
    @DEBUG.setter
    def DEBUG(self, value: bool):
        setattr(self._rt_config, 'DEBUG', value)
    
    # 数据库配置
    @property
    def SQLITE_DB_PATH(self) -> str:
        return getattr(self._rt_config, 'SQLITE_DB_PATH', './data/sqlite/semantic_retrieval.db')
    
    @SQLITE_DB_PATH.setter
    def SQLITE_DB_PATH(self, value: str):
        setattr(self._rt_config, 'SQLITE_DB_PATH', value)
    
    @property
    def SQLITE_TIMEOUT(self) -> float:
        return getattr(self._rt_config, 'SQLITE_TIMEOUT', 30.0)
    
    @SQLITE_TIMEOUT.setter
    def SQLITE_TIMEOUT(self, value: float):
        setattr(self._rt_config, 'SQLITE_TIMEOUT', value)
    
    @property
    def CHROMA_PERSIST_DIR(self) -> str:
        return getattr(self._rt_config, 'CHROMA_PERSIST_DIR', './data/chroma')
    
    @CHROMA_PERSIST_DIR.setter
    def CHROMA_PERSIST_DIR(self, value: str):
        setattr(self._rt_config, 'CHROMA_PERSIST_DIR', value)
    
    @property
    def CHROMA_COLLECTION_NAME(self) -> str:
        return getattr(self._rt_config, 'CHROMA_COLLECTION_NAME', 'artifact_embeddings')
    
    @CHROMA_COLLECTION_NAME.setter
    def CHROMA_COLLECTION_NAME(self, value: str):
        setattr(self._rt_config, 'CHROMA_COLLECTION_NAME', value)
    
    # AI服务配置
    @property
    def LLM_PROVIDER(self) -> str:
        return getattr(self._rt_config, 'LLM_PROVIDER', 'openai_compatible')
    
    @LLM_PROVIDER.setter
    def LLM_PROVIDER(self, value: str):
        setattr(self._rt_config, 'LLM_PROVIDER', value)
    
    @property
    def LLM_API_BASE_URL(self) -> str:
        return getattr(self._rt_config, 'LLM_API_BASE_URL', 'http://localhost:8080/v1')
    
    @LLM_API_BASE_URL.setter
    def LLM_API_BASE_URL(self, value: str):
        setattr(self._rt_config, 'LLM_API_BASE_URL', value)
    
    @property
    def LLM_API_KEY(self) -> str:
        return getattr(self._rt_config, 'LLM_API_KEY', '')
    
    @LLM_API_KEY.setter
    def LLM_API_KEY(self, value: str):
        setattr(self._rt_config, 'LLM_API_KEY', value)
    
    @property
    def LLM_MODEL(self) -> str:
        return getattr(self._rt_config, 'LLM_MODEL', 'qwen2:7b')
    
    @LLM_MODEL.setter
    def LLM_MODEL(self, value: str):
        setattr(self._rt_config, 'LLM_MODEL', value)
    
    @property
    def LLM_TIMEOUT(self) -> int:
        return getattr(self._rt_config, 'LLM_TIMEOUT', 300)
    
    @LLM_TIMEOUT.setter
    def LLM_TIMEOUT(self, value: int):
        setattr(self._rt_config, 'LLM_TIMEOUT', value)
    
    @property
    def LLM_MAX_RETRIES(self) -> int:
        return getattr(self._rt_config, 'LLM_MAX_RETRIES', 3)
    
    @LLM_MAX_RETRIES.setter
    def LLM_MAX_RETRIES(self, value: int):
        setattr(self._rt_config, 'LLM_MAX_RETRIES', value)
    
    @property
    def EMBEDDING_PROVIDER(self) -> str:
        return getattr(self._rt_config, 'EMBEDDING_PROVIDER', 'openai_compatible')
    
    @EMBEDDING_PROVIDER.setter
    def EMBEDDING_PROVIDER(self, value: str):
        setattr(self._rt_config, 'EMBEDDING_PROVIDER', value)
    
    @property
    def EMBEDDING_API_BASE_URL(self) -> str:
        return getattr(self._rt_config, 'EMBEDDING_API_BASE_URL', 'http://localhost:8080/v1')
    
    @EMBEDDING_API_BASE_URL.setter
    def EMBEDDING_API_BASE_URL(self, value: str):
        setattr(self._rt_config, 'EMBEDDING_API_BASE_URL', value)
    
    @property
    def EMBEDDING_API_KEY(self) -> str:
        return getattr(self._rt_config, 'EMBEDDING_API_KEY', '')
    
    @EMBEDDING_API_KEY.setter
    def EMBEDDING_API_KEY(self, value: str):
        setattr(self._rt_config, 'EMBEDDING_API_KEY', value)
    
    @property
    def EMBEDDING_MODEL(self) -> str:
        return getattr(self._rt_config, 'EMBEDDING_MODEL', 'Qwen3-Embedding-4B')
    
    @EMBEDDING_MODEL.setter
    def EMBEDDING_MODEL(self, value: str):
        setattr(self._rt_config, 'EMBEDDING_MODEL', value)
    
    @property
    def EMBEDDING_DIMENSIONS(self) -> int:
        return getattr(self._rt_config, 'EMBEDDING_DIMENSIONS', 1024)
    
    @EMBEDDING_DIMENSIONS.setter
    def EMBEDDING_DIMENSIONS(self, value: int):
        setattr(self._rt_config, 'EMBEDDING_DIMENSIONS', value)
    
    @property
    def EMBEDDING_TIMEOUT(self) -> int:
        return getattr(self._rt_config, 'EMBEDDING_TIMEOUT', 30)
    
    @EMBEDDING_TIMEOUT.setter
    def EMBEDDING_TIMEOUT(self, value: int):
        setattr(self._rt_config, 'EMBEDDING_TIMEOUT', value)
    
    @property
    def EMBEDDING_MAX_RETRIES(self) -> int:
        return getattr(self._rt_config, 'EMBEDDING_MAX_RETRIES', 3)
    
    @EMBEDDING_MAX_RETRIES.setter
    def EMBEDDING_MAX_RETRIES(self, value: int):
        setattr(self._rt_config, 'EMBEDDING_MAX_RETRIES', value)
    
    # 检索参数
    @property
    def DEFAULT_TOP_K(self) -> int:
        return getattr(self._rt_config, 'DEFAULT_TOP_K', 5)
    
    @DEFAULT_TOP_K.setter
    def DEFAULT_TOP_K(self, value: int):
        setattr(self._rt_config, 'DEFAULT_TOP_K', value)
    
    @property
    def SIMILARITY_THRESHOLD(self) -> float:
        return getattr(self._rt_config, 'SIMILARITY_THRESHOLD', 0.7)
    
    @SIMILARITY_THRESHOLD.setter
    def SIMILARITY_THRESHOLD(self, value: float):
        setattr(self._rt_config, 'SIMILARITY_THRESHOLD', value)
    
    @property
    def MAX_CHUNK_SIZE(self) -> int:
        return getattr(self._rt_config, 'MAX_CHUNK_SIZE', 1000)
    
    @MAX_CHUNK_SIZE.setter
    def MAX_CHUNK_SIZE(self, value: int):
        setattr(self._rt_config, 'MAX_CHUNK_SIZE', value)
    
    @property
    def OVERLAP_SIZE(self) -> int:
        return getattr(self._rt_config, 'OVERLAP_SIZE', 100)
    
    @OVERLAP_SIZE.setter
    def OVERLAP_SIZE(self, value: int):
        setattr(self._rt_config, 'OVERLAP_SIZE', value)
    
    @property
    def BATCH_SIZE(self) -> int:
        return getattr(self._rt_config, 'BATCH_SIZE', 10)
    
    @BATCH_SIZE.setter
    def BATCH_SIZE(self, value: int):
        setattr(self._rt_config, 'BATCH_SIZE', value)
    
    # Web服务配置
    @property
    def WEB_SERVICE_ENABLED(self) -> bool:
        return getattr(self._rt_config, 'WEB_SERVICE_ENABLED', True)
    
    @WEB_SERVICE_ENABLED.setter
    def WEB_SERVICE_ENABLED(self, value: bool):
        setattr(self._rt_config, 'WEB_SERVICE_ENABLED', value)
    
    @property
    def STATIC_FILES_DIR(self) -> str:
        return getattr(self._rt_config, 'STATIC_FILES_DIR', './app/web/static')
    
    @STATIC_FILES_DIR.setter
    def STATIC_FILES_DIR(self, value: str):
        setattr(self._rt_config, 'STATIC_FILES_DIR', value)
    
    @property
    def STATIC_MOUNT_PATH(self) -> str:
        return getattr(self._rt_config, 'STATIC_MOUNT_PATH', '/static')
    
    @STATIC_MOUNT_PATH.setter
    def STATIC_MOUNT_PATH(self, value: str):
        setattr(self._rt_config, 'STATIC_MOUNT_PATH', value)
    
    @property
    def TEMPLATES_DIR(self) -> str:
        return getattr(self._rt_config, 'TEMPLATES_DIR', './app/web/templates')
    
    @TEMPLATES_DIR.setter
    def TEMPLATES_DIR(self, value: str):
        setattr(self._rt_config, 'TEMPLATES_DIR', value)
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        # 从web_service.cors.allowed_origins获取，如果不存在则返回默认值
        web_service = getattr(self._rt_config, 'WEB_SERVICE', {})
        cors = web_service.get('cors', {}) if isinstance(web_service, dict) else {}
        origins = cors.get('allowed_origins', []) if isinstance(cors, dict) else []
        if not origins:
            origins = getattr(self._rt_config, 'ALLOWED_ORIGINS', ["*"])
        return origins
    
    @ALLOWED_ORIGINS.setter
    def ALLOWED_ORIGINS(self, value: List[str]):
        setattr(self._rt_config, 'ALLOWED_ORIGINS', value)
    
    # 安全配置
    @property
    def API_KEY_SECRET(self) -> str:
        return getattr(self._rt_config, 'API_KEY_SECRET', 'your-secret-key-here')
    
    @API_KEY_SECRET.setter
    def API_KEY_SECRET(self, value: str):
        setattr(self._rt_config, 'API_KEY_SECRET', value)
    
    @property
    def JWT_SECRET(self) -> str:
        return getattr(self._rt_config, 'JWT_SECRET', 'your-jwt-secret-here')
    
    @JWT_SECRET.setter
    def JWT_SECRET(self, value: str):
        setattr(self._rt_config, 'JWT_SECRET', value)
    
    # 缓存配置
    @property
    def CACHE_ENABLED(self) -> bool:
        return getattr(self._rt_config, 'CACHE_ENABLED', False)
    
    @CACHE_ENABLED.setter
    def CACHE_ENABLED(self, value: bool):
        setattr(self._rt_config, 'CACHE_ENABLED', value)
    
    @property
    def REDIS_HOST(self) -> str:
        return getattr(self._rt_config, 'REDIS_HOST', 'localhost')
    
    @REDIS_HOST.setter
    def REDIS_HOST(self, value: str):
        setattr(self._rt_config, 'REDIS_HOST', value)
    
    @property
    def REDIS_PORT(self) -> int:
        return getattr(self._rt_config, 'REDIS_PORT', 6379)
    
    @REDIS_PORT.setter
    def REDIS_PORT(self, value: int):
        setattr(self._rt_config, 'REDIS_PORT', value)
    
    @property
    def CACHE_TTL_SECONDS(self) -> int:
        return getattr(self._rt_config, 'CACHE_TTL_SECONDS', 3600)
    
    @CACHE_TTL_SECONDS.setter
    def CACHE_TTL_SECONDS(self, value: int):
        setattr(self._rt_config, 'CACHE_TTL_SECONDS', value)
    
    # 文件处理配置
    @property
    def SUPPORTED_FORMATS(self) -> List[str]:
        return getattr(self._rt_config, 'SUPPORTED_FORMATS', ['.txt', '.pdf', '.docx', '.html'])
    
    @SUPPORTED_FORMATS.setter
    def SUPPORTED_FORMATS(self, value: List[str]):
        setattr(self._rt_config, 'SUPPORTED_FORMATS', value)
    
    @property
    def MAX_FILE_SIZE_MB(self) -> int:
        return getattr(self._rt_config, 'MAX_FILE_SIZE_MB', 50)
    
    @MAX_FILE_SIZE_MB.setter
    def MAX_FILE_SIZE_MB(self, value: int):
        setattr(self._rt_config, 'MAX_FILE_SIZE_MB', value)
    
    @property
    def TEMP_DIRECTORY(self) -> str:
        return getattr(self._rt_config, 'TEMP_DIRECTORY', './temp')
    
    @TEMP_DIRECTORY.setter
    def TEMP_DIRECTORY(self, value: str):
        setattr(self._rt_config, 'TEMP_DIRECTORY', value)
    
    def reload(self):
        """重新加载配置"""
        self._rt_config.reload()
        self._ensure_directories()


# 创建全局配置实例
config = Config()