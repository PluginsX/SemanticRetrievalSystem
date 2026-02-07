from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import yaml
import os

from app.api.dependencies import DatabaseDep
from app.core.config import config
from app.core.yaml_config import get_config_manager

router = APIRouter(prefix="/api/v1", tags=["configuration"])


logger = logging.getLogger(__name__)

def load_config_from_core():
    """从核心配置系统加载配置"""
    try:
        # 从核心配置系统获取配置
        config_manager = get_config_manager()
        core_config = config_manager.get_config()
        
        # 获取各个配置值，添加错误处理
        try:
            server_host = config.HOST
        except Exception as e:
            logger.warning(f"获取HOST配置失败: {e}")
            server_host = "127.0.0.1"
        
        try:
            server_port = config.PORT
        except Exception as e:
            logger.warning(f"获取PORT配置失败: {e}")
            server_port = 8000
            
        try:
            allowed_origins = config.ALLOWED_ORIGINS
        except Exception as e:
            logger.warning(f"获取ALLOWED_ORIGINS配置失败: {e}")
            allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
            
        try:
            llm_provider = config.LLM_PROVIDER
        except Exception as e:
            logger.warning(f"获取LLM_PROVIDER配置失败: {e}")
            llm_provider = "ollama"
            
        try:
            llm_base_url = config.LLM_API_BASE_URL
        except Exception as e:
            logger.warning(f"获取LLM_API_BASE_URL配置失败: {e}")
            llm_base_url = "http://localhost:11434/v1"
            
        try:
            llm_api_key = config.LLM_API_KEY
        except Exception as e:
            logger.warning(f"获取LLM_API_KEY配置失败: {e}")
            llm_api_key = ""
            
        try:
            llm_model = config.LLM_MODEL
        except Exception as e:
            logger.warning(f"获取LLM_MODEL配置失败: {e}")
            llm_model = "qwen2:7b"
            
        try:
            llm_timeout = config.LLM_TIMEOUT
        except Exception as e:
            logger.warning(f"获取LLM_TIMEOUT配置失败: {e}")
            llm_timeout = 30
            
        try:
            embedding_provider = config.EMBEDDING_PROVIDER
        except Exception as e:
            logger.warning(f"获取EMBEDDING_PROVIDER配置失败: {e}")
            embedding_provider = "local"
            
        try:
            embedding_base_url = config.EMBEDDING_API_BASE_URL
        except Exception as e:
            logger.warning(f"获取EMBEDDING_API_BASE_URL配置失败: {e}")
            embedding_base_url = "http://localhost:8080/v1"
            
        try:
            embedding_api_key = config.EMBEDDING_API_KEY
        except Exception as e:
            logger.warning(f"获取EMBEDDING_API_KEY配置失败: {e}")
            embedding_api_key = ""
            
        try:
            embedding_model = config.EMBEDDING_MODEL
        except Exception as e:
            logger.warning(f"获取EMBEDDING_MODEL配置失败: {e}")
            embedding_model = "BAAI/bge-large-zh-v1.5"
            
        try:
            embedding_dimensions = config.EMBEDDING_DIMENSIONS
        except Exception as e:
            logger.warning(f"获取EMBEDDING_DIMENSIONS配置失败: {e}")
            embedding_dimensions = 1024
        
        try:
            embedding_timeout = config.EMBEDDING_TIMEOUT
        except Exception as e:
            logger.warning(f"获取EMBEDDING_TIMEOUT配置失败: {e}")
            embedding_timeout = 300
        
        # 转换为前端期望的格式
        frontend_config = {
            "server": {
                "host": server_host,
                "port": server_port
            },
            "cors": {
                "origins": allowed_origins
            },
            "llm": {
                "service_type": llm_provider.replace("_", "-"),
                "base_url": llm_base_url,
                "api_key": llm_api_key,
                "model": llm_model,
                "max_tokens": llm_timeout
            },
            "embedding": {
                "service_type": embedding_provider.replace("_", "-"),
                "base_url": embedding_base_url,
                "api_key": embedding_api_key,
                "model": embedding_model,
                "dimensions": embedding_dimensions,
                "timeout": embedding_timeout
            }
        }
        
        return frontend_config
    except Exception as e:
        logger.error(f"加载配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载配置失败: {str(e)}")


@router.get("/config")
async def get_config():
    """获取系统配置"""
    try:
        config_data = load_config_from_core()
        # 为了与前端期望的格式匹配，返回包含data字段的对象
        return {"data": config_data}
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/config")
async def update_config(config_data: Dict[str, Any]):
    """更新系统配置"""
    try:
        # 从现有的配置管理器获取当前配置
        config_manager = get_config_manager()
        current_config = config_manager.get_config() or {}
        
        # 记录哪些配置发生了变化，用于决定是否需要重启
        changed_keys = []
        
        # 根据传入的数据更新配置
        if "server" in config_data:
            if "app" not in current_config:
                current_config["app"] = {}
            old_host = current_config["app"].get("host", "0.0.0.0")
            old_port = current_config["app"].get("port", 8001)
            new_host = config_data["server"].get("host", old_host)
            new_port = config_data["server"].get("port", old_port)
            
            if old_host != new_host or old_port != new_port:
                changed_keys.append("server")
                
            current_config["app"].update({
                "host": new_host,
                "port": new_port
            })
        
        if "cors" in config_data:
            if "web_service" not in current_config:
                current_config["web_service"] = {}
            if "cors" not in current_config["web_service"]:
                current_config["web_service"]["cors"] = {}
            
            old_origins = current_config["web_service"]["cors"].get("allowed_origins", ["*"])
            new_origins = config_data["cors"].get("origins", old_origins)
            
            if old_origins != new_origins:
                changed_keys.append("cors")
                
            current_config["web_service"]["cors"]["allowed_origins"] = new_origins
        
        if "llm" in config_data:
            # 更新LLM服务配置
            if "services" not in current_config:
                current_config["services"] = {}
            if "llm_services" not in current_config["services"]:
                current_config["services"]["llm_services"] = {}
            if "openai-compatible" not in current_config["services"]["llm_services"]:
                current_config["services"]["llm_services"]["openai-compatible"] = {}
            
            old_base_url = current_config["services"]["llm_services"]["openai-compatible"].get("api_base", "http://localhost:8080/v1")
            old_api_key = current_config["services"]["llm_services"]["openai-compatible"].get("api_key", "")
            old_model = current_config["services"]["llm_services"]["openai-compatible"].get("default_model", "qwen2:7b")
            old_timeout = current_config["services"]["llm_services"]["openai-compatible"].get("timeout", 300)
            
            new_base_url = config_data["llm"].get("base_url", old_base_url)
            new_api_key = config_data["llm"].get("api_key", old_api_key)
            new_model = config_data["llm"].get("model", old_model)
            new_timeout = config_data["llm"].get("max_tokens", old_timeout)
            
            if old_base_url != new_base_url or old_api_key != new_api_key or old_model != new_model or old_timeout != new_timeout:
                changed_keys.append("llm")
            
            current_config["services"]["llm_services"]["openai-compatible"].update({
                "api_base": new_base_url,
                "api_key": new_api_key,
                "default_model": new_model,
                "timeout": new_timeout
            })
        
        if "embedding" in config_data:
            # 更新Embedding服务配置
            if "services" not in current_config:
                current_config["services"] = {}
            if "embedding_services" not in current_config["services"]:
                current_config["services"]["embedding_services"] = {}
            if "openai-compatible" not in current_config["services"]["embedding_services"]:
                current_config["services"]["embedding_services"]["openai-compatible"] = {}
            
            old_base_url = current_config["services"]["embedding_services"]["openai-compatible"].get("api_base", "http://localhost:8080/v1")
            old_api_key = current_config["services"]["embedding_services"]["openai-compatible"].get("api_key", "")
            old_model = current_config["services"]["embedding_services"]["openai-compatible"].get("default_model", "Qwen3-Embedding-4B")
            old_dimensions = current_config["services"]["embedding_services"]["openai-compatible"].get("dimensions", 1024)
            old_timeout = current_config["services"]["embedding_services"]["openai-compatible"].get("timeout", 300)
            
            new_base_url = config_data["embedding"].get("base_url", old_base_url)
            new_api_key = config_data["embedding"].get("api_key", old_api_key)
            new_model = config_data["embedding"].get("model", old_model)
            new_dimensions = config_data["embedding"].get("dimensions", old_dimensions)
            new_timeout = config_data["embedding"].get("timeout", old_timeout)
            
            if old_base_url != new_base_url or old_api_key != new_api_key or old_model != new_model or old_dimensions != new_dimensions or old_timeout != new_timeout:
                changed_keys.append("embedding")
            
            current_config["services"]["embedding_services"]["openai-compatible"].update({
                "api_base": new_base_url,
                "api_key": new_api_key,
                "default_model": new_model,
                "dimensions": new_dimensions,
                "timeout": new_timeout
            })
        
        # 更新配置
        config_manager.update_config(current_config)
        
        # 检查是否需要重启服务
        needs_restart = any(key in changed_keys for key in ["server", "cors"])
        
        response_data = {
            "message": "配置更新成功",
            "changed_keys": changed_keys,
            "needs_restart": needs_restart
        }
        
        if needs_restart:
            response_data["message"] += "，部分配置需要重启服务才能完全生效"
        else:
            response_data["message"] += "，配置已实时生效"
        
        logger.info(f"配置已成功更新并保存: {config_data}")
        
        return response_data
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post("/config/test-llm")
async def test_llm_config(config_data: Dict[str, Any]):
    """测试LLM配置连接"""
    try:
        from openai import OpenAI
        import httpx
        
        # 使用传入的配置参数测试连接
        service_type = config_data.get("service_type", "openai-compatible")
        api_base = config_data.get("base_url", "http://localhost:11434/v1")
        api_key = config_data.get("api_key", "")
        model = config_data.get("model", "qwen2:7b")
        
        # 创建临时的OpenAI客户端进行测试
        try:
            client = OpenAI(
                base_url=api_base,
                api_key=api_key,
                timeout=10.0,
                http_client=httpx.Client(limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))
            )
            
            # 尝试发送一个简单的测试请求
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user", 
                    "content": "你好，请回复'测试成功'，仅回复这四个字。"
                }],
                max_tokens=20,
                temperature=0.1
            )
            
            test_response = response.choices[0].message.content.strip()
            
            # 如果能收到响应，说明连接成功
            if test_response and len(test_response) > 0:
                return {
                    "message": "LLM配置测试成功",
                    "data": {
                        "connected": True,
                        "model": model,
                        "service_type": service_type,
                        "response_preview": test_response[:50] + "..." if len(test_response) > 50 else test_response
                    }
                }
            else:
                raise Exception("LLM服务无响应或返回空结果")
                
        except Exception as e:
            logger.error(f"LLM连接测试失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"LLM连接测试失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"LLM配置测试异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM配置测试异常: {str(e)}")


@router.post("/config/test-embedding")
async def test_embedding_config(config_data: Dict[str, Any]):
    """测试Embedding配置连接"""
    try:
        from openai import OpenAI
        import httpx
        
        # 使用传入的配置参数测试连接
        service_type = config_data.get("service_type", "openai-compatible")
        api_base = config_data.get("base_url", "http://localhost:8080/v1")
        api_key = config_data.get("api_key", "")
        model = config_data.get("model", "Qwen3-Embedding-4B")
        dimensions = config_data.get("dimensions", 1024)
        timeout = config_data.get("timeout", 300)
        
        # 创建临时的OpenAI客户端进行测试
        try:
            client = OpenAI(
                base_url=api_base,
                api_key=api_key,
                timeout=min(timeout, 30.0),  # 测试连接时最多等待30秒
                http_client=httpx.Client(limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))
            )
            
            # 尝试发送一个简单的测试请求
            test_text = "这是测试文本"
            response = client.embeddings.create(
                model=model,
                input=test_text
            )
            
            test_embedding = response.data[0].embedding
            
            # 检查嵌入向量是否成功生成
            if test_embedding is not None and len(test_embedding) > 0:
                return {
                    "message": "Embedding配置测试成功",
                    "data": {
                        "connected": True,
                        "model": model,
                        "service_type": service_type,
                        "dimensions": len(test_embedding)
                    }
                }
            else:
                raise Exception("Embedding服务无响应或返回空结果")
                
        except Exception as e:
            logger.error(f"Embedding连接测试失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Embedding连接测试失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"Embedding配置测试异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding配置测试异常: {str(e)}")
    except Exception as e:
        logger.error(f"Embedding配置测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding配置测试失败: {str(e)}")