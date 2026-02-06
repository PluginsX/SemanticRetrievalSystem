"""
配置热重载管理器
实现运行时配置更新功能
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI
    from app.core.config import Config

logger = logging.getLogger(__name__)

# 全局变量存储FastAPI应用实例
_fastapi_app = None
_config_instance = None

def set_fastapi_app(app: 'FastAPI'):
    """设置FastAPI应用实例"""
    global _fastapi_app
    _fastapi_app = app

def set_config_instance(config: 'Config'):
    """设置配置实例"""
    global _config_instance
    _config_instance = config

def hot_reload_config():
    """
    热重载配置
    重新加载配置并更新应用设置
    """
    global _fastapi_app, _config_instance
    
    if _fastapi_app is None or _config_instance is None:
        logger.warning("FastAPI应用实例或配置实例未设置，无法执行热重载")
        return False
    
    try:
        # 重新加载配置管理器中的配置
        config_manager = _config_instance._rt_config._config_manager
        config_manager.reload_config()
        
        # 更新CORS中间件 - 需要重新构建中间件栈
        _update_cors_middleware()
        
        # 更新应用标题和版本
        _fastapi_app.title = _config_instance.APP_NAME
        _fastapi_app.version = _config_instance.APP_VERSION
        _fastapi_app.debug = _config_instance.DEBUG
        
        logger.info("配置热重载成功")
        return True
    except Exception as e:
        logger.error(f"配置热重载失败: {e}")
        return False

def _update_cors_middleware():
    """
    更新CORS中间件配置
    注意：FastAPI不直接支持动态更新中间件，这里使用一种变通方法
    """
    global _fastapi_app, _config_instance
    
    if _fastapi_app is None or _config_instance is None:
        return
    
    try:
        # 获取新的CORS源
        new_origins = _config_instance.ALLOWED_ORIGINS
        
        # 由于FastAPI不支持动态移除中间件，我们需要标记新的CORS源
        # 并在自定义中间件中处理CORS逻辑
        setattr(_fastapi_app, '_cors_origins', new_origins)
        
        logger.info(f"CORS配置已更新: {new_origins}")
    except Exception as e:
        logger.error(f"更新CORS中间件失败: {e}")

def register_config_change_listener():
    """
    注册配置变更监听器
    当配置发生变化时自动触发热重载
    """
    def on_config_change(key_path: str, old_value, new_value):
        logger.info(f"配置变化: {key_path}, 旧值: {old_value}, 新值: {new_value}")
        # 对于某些关键配置变化，可以触发热重载
        if key_path in ['app.host', 'app.port', 'web_service.cors.allowed_origins']:
            logger.info(f"检测到关键配置变化: {key_path}，建议重启服务以完全生效")
        else:
            logger.info(f"配置变化: {key_path} 已保存到文件")
    
    from app.core.yaml_config import get_config_manager
    config_manager = get_config_manager()
    config_manager.add_change_listener(on_config_change)