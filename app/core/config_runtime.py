"""
运行时配置对象
允许通过属性方式访问和修改配置，并自动同步到文件
"""
from typing import Any, Dict
from .yaml_config import get_config_manager, set_config, get_config
import logging


class RuntimeConfig:
    """运行时配置对象 - 提供属性式的配置访问和修改"""
    
    def __init__(self):
        self._config_manager = get_config_manager()
    
    def __getattr__(self, name: str) -> Any:
        """获取配置属性"""
        # 将驼峰命名转换为下划线命名以匹配配置键
        snake_case_name = self._camel_to_snake(name)
        
        # 尝试从配置中获取值
        # 首先尝试获取整个section
        section_config = get_config(snake_case_name)
        if section_config is not None and isinstance(section_config, dict):
            # 如果是section，返回一个RuntimeSection对象来处理子属性
            return RuntimeSection(snake_case_name, section_config)
        
        # 根据属性名映射到配置路径
        config_map = {
            'SQLITE_DB_PATH': ('database', 'sqlite', 'path'),
            'SQLITE_TIMEOUT': ('database', 'sqlite', 'timeout'),
            'CHROMA_PERSIST_DIR': ('database', 'chroma', 'persist_directory'),
            'CHROMA_COLLECTION_NAME': ('database', 'chroma', 'collection_name'),
            'HOST': ('app', 'host'),
            'PORT': ('app', 'port'),
            'LOG_LEVEL': ('app', 'log_level'),
            'DEBUG': ('app', 'debug'),
            'APP_NAME': ('app', 'name'),
            'APP_VERSION': ('app', 'version'),
            'APP_ENV': ('app', 'environment'),
            'LLM_PROVIDER': ('ai_services', 'llm', 'provider'),
            'LLM_API_BASE_URL': ('services', 'llm_services', 'openai-compatible', 'api_base'),
            'LLM_API_KEY': ('services', 'llm_services', 'openai-compatible', 'api_key'),
            'LLM_MODEL': ('services', 'llm_services', 'openai-compatible', 'default_model'),
            'LLM_TIMEOUT': ('services', 'llm_services', 'openai-compatible', 'timeout'),
            'LLM_MAX_RETRIES': ('ai_services', 'llm', 'max_retries'),
            'EMBEDDING_PROVIDER': ('ai_services', 'embedding', 'provider'),
            'EMBEDDING_API_BASE_URL': ('services', 'embedding_services', 'openai-compatible', 'api_base'),
            'EMBEDDING_API_KEY': ('services', 'embedding_services', 'openai-compatible', 'api_key'),
            'EMBEDDING_MODEL': ('services', 'embedding_services', 'openai-compatible', 'default_model'),
            'EMBEDDING_DIMENSIONS': ('services', 'embedding_services', 'openai-compatible', 'dimensions'),
            'EMBEDDING_TIMEOUT': ('ai_services', 'embedding', 'timeout'),
            'EMBEDDING_MAX_RETRIES': ('ai_services', 'embedding', 'max_retries'),
            'DEFAULT_TOP_K': ('retrieval', 'default_top_k'),
            'SIMILARITY_THRESHOLD': ('retrieval', 'similarity_threshold'),
            'MAX_CHUNK_SIZE': ('retrieval', 'max_chunk_size'),
            'OVERLAP_SIZE': ('retrieval', 'overlap_size'),
            'BATCH_SIZE': ('retrieval', 'batch_size'),
            'WEB_SERVICE_ENABLED': ('web_service', 'enabled'),
            'STATIC_FILES_DIR': ('web_service', 'static_files', 'directory'),
            'STATIC_MOUNT_PATH': ('web_service', 'static_files', 'mount_path'),
            'TEMPLATES_DIR': ('web_service', 'templates', 'directory'),
            'API_KEY_SECRET': ('security', 'api_key_secret'),
            'JWT_SECRET': ('security', 'jwt_secret'),
            'CACHE_ENABLED': ('cache', 'enabled'),
            'REDIS_HOST': ('cache', 'redis', 'host'),
            'REDIS_PORT': ('cache', 'redis', 'port'),
            'CACHE_TTL_SECONDS': ('cache', 'ttl_seconds'),
            'SUPPORTED_FORMATS': ('file_processing', 'supported_formats'),
            'MAX_FILE_SIZE_MB': ('file_processing', 'max_file_size_mb'),
            'TEMP_DIRECTORY': ('file_processing', 'temp_directory'),
        }
        
        if name in config_map:
            path = config_map[name]
            value = self._get_nested_config(path)
            # 为常见配置提供默认值
            defaults = {
                'SQLITE_DB_PATH': './data/sqlite/semantic_retrieval.db',
                'SQLITE_TIMEOUT': 30.0,
                'CHROMA_PERSIST_DIR': './data/chroma',
                'CHROMA_COLLECTION_NAME': 'artifact_embeddings',
                'HOST': '0.0.0.0',
                'PORT': 8001,
                'LOG_LEVEL': 'INFO',
                'DEBUG': True,
                'APP_NAME': '语义检索系统',
                'APP_VERSION': '1.0.0',
                'APP_ENV': 'development',
                'LLM_PROVIDER': 'openai_compatible',
                'LLM_API_BASE_URL': 'http://localhost:8080/v1',
                'LLM_API_KEY': '',
                'LLM_MODEL': 'qwen2:7b',
                'LLM_TIMEOUT': 300,
                'LLM_MAX_RETRIES': 3,
                'EMBEDDING_PROVIDER': 'openai_compatible',
                'EMBEDDING_API_BASE_URL': 'http://localhost:8080/v1',
                'EMBEDDING_API_KEY': '',
                'EMBEDDING_MODEL': 'Qwen3-Embedding-4B',
                'EMBEDDING_DIMENSIONS': 1024,
                'EMBEDDING_TIMEOUT': 30,
                'EMBEDDING_MAX_RETRIES': 3,
                'DEFAULT_TOP_K': 5,
                'SIMILARITY_THRESHOLD': 0.7,
                'MAX_CHUNK_SIZE': 1000,
                'OVERLAP_SIZE': 100,
                'BATCH_SIZE': 10,
                'WEB_SERVICE_ENABLED': True,
                'STATIC_FILES_DIR': './app/web/static',
                'STATIC_MOUNT_PATH': '/static',
                'TEMPLATES_DIR': './app/web/templates',
                'API_KEY_SECRET': 'your-secret-key-here',
                'JWT_SECRET': 'your-jwt-secret-here',
                'CACHE_ENABLED': False,
                'REDIS_HOST': 'localhost',
                'REDIS_PORT': 6379,
                'CACHE_TTL_SECONDS': 3600,
                'SUPPORTED_FORMATS': ['.txt', '.pdf', '.docx', '.html'],
                'MAX_FILE_SIZE_MB': 50,
                'TEMP_DIRECTORY': './temp',
            }
            return value if value is not None else defaults.get(name)
        else:
            # 通用方式：尝试从app部分获取
            value = get_config('app', snake_case_name)
            if value is None:
                # 如果没找到，返回默认值或抛出AttributeError
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
            return value

    def __setattr__(self, name: str, value: Any):
        """设置配置属性"""
        if name.startswith('_'):
            # 私有属性直接设置
            super().__setattr__(name, value)
            return
        
        # 将属性名转换为配置路径
        snake_case_name = self._camel_to_snake(name)
        
        # 根据属性名确定配置路径
        if name == 'SQLITE_DB_PATH':
            current_db_config = get_config('database') or {}
            if 'sqlite' not in current_db_config:
                current_db_config['sqlite'] = {}
            current_db_config['sqlite']['path'] = value
            set_config(current_db_config, 'database')
        elif name == 'CHROMA_PERSIST_DIR':
            current_db_config = get_config('database') or {}
            if 'chroma' not in current_db_config:
                current_db_config['chroma'] = {}
            current_db_config['chroma']['persist_directory'] = value
            set_config(current_db_config, 'database')
        elif name == 'HOST':
            current_app_config = get_config('app') or {}
            current_app_config['host'] = value
            set_config(current_app_config, 'app')
        elif name == 'PORT':
            current_app_config = get_config('app') or {}
            current_app_config['port'] = value
            set_config(current_app_config, 'app')
        elif name == 'LOG_LEVEL':
            current_app_config = get_config('app') or {}
            current_app_config['log_level'] = value
            set_config(current_app_config, 'app')
        elif name == 'DEBUG':
            current_app_config = get_config('app') or {}
            current_app_config['debug'] = value
            set_config(current_app_config, 'app')
        elif name == 'LLM_API_BASE_URL':
            current_services = get_config('services') or {}
            if 'llm_services' not in current_services:
                current_services['llm_services'] = {}
            if 'openai-compatible' not in current_services['llm_services']:
                current_services['llm_services']['openai-compatible'] = {}
            current_services['llm_services']['openai-compatible']['api_base'] = value
            set_config(current_services, 'services')
        elif name == 'LLM_API_KEY':
            current_services = get_config('services') or {}
            if 'llm_services' not in current_services:
                current_services['llm_services'] = {}
            if 'openai-compatible' not in current_services['llm_services']:
                current_services['llm_services']['openai-compatible'] = {}
            current_services['llm_services']['openai-compatible']['api_key'] = value
            set_config(current_services, 'services')
        elif name == 'LLM_MODEL':
            current_services = get_config('services') or {}
            if 'llm_services' not in current_services:
                current_services['llm_services'] = {}
            if 'openai-compatible' not in current_services['llm_services']:
                current_services['llm_services']['openai-compatible'] = {}
            current_services['llm_services']['openai-compatible']['default_model'] = value
            set_config(current_services, 'services')
        elif name == 'EMBEDDING_MODEL':
            current_services = get_config('services') or {}
            if 'embedding_services' not in current_services:
                current_services['embedding_services'] = {}
            if 'openai-compatible' not in current_services['embedding_services']:
                current_services['embedding_services']['openai-compatible'] = {}
            current_services['embedding_services']['openai-compatible']['default_model'] = value
            set_config(current_services, 'services')
        else:
            # 通用方式：设置到app部分
            current_app_config = get_config('app') or {}
            current_app_config[snake_case_name] = value
            set_config(current_app_config, 'app')
    
    def _camel_to_snake(self, name: str) -> str:
        """将驼峰命名转换为下划线命名"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _get_nested_config(self, path):
        """获取嵌套配置值"""
        try:
            value = get_config()
            for key in path:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    
    def reload(self):
        """重新加载配置"""
        self._config_manager.reload_config()


class RuntimeSection:
    """配置节包装器，用于处理嵌套配置"""
    
    def __init__(self, section_name: str, section_data: Dict[str, Any]):
        self._section_name = section_name
        self._section_data = section_data
        self._config_manager = get_config_manager()
    
    def __getattr__(self, name: str) -> Any:
        """获取节内配置项"""
        snake_case_name = self._camel_to_snake(name)
        return self._section_data.get(snake_case_name)
    
    def __setattr__(self, name: str, value: Any):
        """设置节内配置项"""
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        snake_case_name = self._camel_to_snake(name)
        # 更新配置管理器中的值
        current_section = get_config(self._section_name) or {}
        current_section[snake_case_name] = value
        set_config(current_section, self._section_name)
    
    def _camel_to_snake(self, name: str) -> str:
        """将驼峰命名转换为下划线命名"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# 全局运行时配置实例
runtime_config = RuntimeConfig()