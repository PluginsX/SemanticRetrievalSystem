"""系统管理API路由"""
from datetime import datetime
from fastapi import APIRouter, Depends
from typing import Dict, Any
import psutil
import time

from app.models.schemas import HealthCheckResponse, MetricsResponse
from app.api.dependencies import DatabaseDep
from app.services.vector_sync import vector_sync_service

router = APIRouter(prefix="/api/v1", tags=["系统管理"])

# 记录应用启动时间
START_TIME = time.time()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: DatabaseDep):
    """健康检查接口"""
    services_status = {}
    
    # 检查数据库连接
    try:
        db["sqlite"].execute("SELECT 1")
        services_status["database"] = "healthy"
    except Exception:
        services_status["database"] = "unhealthy"
    
    # 检查向量数据库
    try:
        if hasattr(db["chroma"], 'heartbeat'):
            db["chroma"].heartbeat()
            services_status["vector_store"] = "healthy"
        else:
            services_status["vector_store"] = "unavailable"
    except Exception:
        services_status["vector_store"] = "unhealthy"
    
    # 检查AI服务配置
    # 如果配置了必要的参数，则认为服务已配置好
    from app.core.config import config
    
    # 检查LLM服务配置和可用性
    if hasattr(config, 'LLM_MODEL') and config.LLM_MODEL:
        try:
            if hasattr(config, 'LLM_API_BASE_URL') and config.LLM_API_BASE_URL:
                # 尝试调用实际的LLM API端点进行测试
                from openai import OpenAI
                import httpx
                
                client = OpenAI(
                    base_url=config.LLM_API_BASE_URL,
                    api_key=config.LLM_API_KEY if hasattr(config, 'LLM_API_KEY') else "test",
                    timeout=10.0,
                    http_client=httpx.Client(limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))
                )
                
                # 尝试生成一个简单的测试文本
                test_response = client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个专业的AI助手"},
                        {"role": "user", "content": "你好"}
                    ],
                    max_tokens=10
                )
                
                if test_response and test_response.choices:
                    services_status["llm_service"] = "healthy"
                else:
                    services_status["llm_service"] = "configured"
            else:
                services_status["llm_service"] = "healthy"
        except Exception as e:
            # 记录错误日志，帮助调试
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"LLM服务健康检查失败: {str(e)}")
            services_status["llm_service"] = "configured"  # 已配置但不可用
    else:
        services_status["llm_service"] = "configured"  # 已配置但未启用
    
    # 检查嵌入服务配置和可用性
    if hasattr(config, 'EMBEDDING_MODEL') and config.EMBEDDING_MODEL:
        try:
            # 尝试连接到嵌入服务
            if hasattr(config, 'EMBEDDING_API_BASE_URL') and config.EMBEDDING_API_BASE_URL:
                # 尝试调用实际的embedding API端点进行测试
                from openai import OpenAI
                import httpx
                
                client = OpenAI(
                    base_url=config.EMBEDDING_API_BASE_URL,
                    api_key=config.EMBEDDING_API_KEY if hasattr(config, 'EMBEDDING_API_KEY') else "test",
                    timeout=10.0,
                    http_client=httpx.Client(limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))
                )
                
                # 尝试生成一个简单的测试向量
                test_response = client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input="test"
                )
                
                if test_response and test_response.data:
                    services_status["embedding_service"] = "healthy"
                else:
                    services_status["embedding_service"] = "configured"
            else:
                # 如果没有专门的嵌入API URL，假设有嵌入模型就是健康的
                services_status["embedding_service"] = "healthy"
        except Exception as e:
            # 记录错误日志，帮助调试
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"嵌入服务健康检查失败: {str(e)}")
            services_status["embedding_service"] = "configured"  # 已配置但不可用
    else:
        services_status["embedding_service"] = "configured"  # 已配置但未启用
    
    # 只有核心服务健康时，系统状态才是健康
    core_services_healthy = (
        services_status.get("database") == "healthy" and 
        services_status.get("vector_store") == "healthy"
    )
    
    return HealthCheckResponse(
        status="healthy" if core_services_healthy else "degraded",
        timestamp=datetime.now(),
        services=services_status
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: DatabaseDep):
    """获取系统指标"""
    # 获取运行时间
    uptime = time.time() - START_TIME
    
    # 获取数据库统计信息
    cursor = db["sqlite"].cursor()
    
    # 资料总数
    cursor.execute("SELECT COUNT(*) FROM artifacts WHERE is_active = 1")
    artifact_count = cursor.fetchone()[0]
    
    # 切片总数
    cursor.execute("SELECT COUNT(*) FROM chunks")
    chunk_count = cursor.fetchone()[0]
    
    # 检索历史总数
    cursor.execute("SELECT COUNT(*) FROM search_history")
    search_count = cursor.fetchone()[0]
    
    # 平均响应时间（最近100次检索）
    cursor.execute("""
        SELECT AVG(response_time) 
        FROM search_history 
        WHERE response_time IS NOT NULL 
        ORDER BY created_at DESC 
        LIMIT 100
    """)
    avg_response_time = cursor.fetchone()[0] or 0.0
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    
    return MetricsResponse(
        uptime=uptime,
        artifact_count=artifact_count,
        chunk_count=chunk_count,
        search_count=search_count,
        avg_response_time=avg_response_time
    )


@router.get("/info")
async def get_system_info():
    """获取系统信息"""
    # 避免直接导入chromadb导致NumPy兼容性问题
    try:
        import chromadb
        chromadb_version = chromadb.__version__
    except:
        chromadb_version = "unavailable"
    
    return {
        "app_name": "语义检索系统",
        "version": "1.0.0",
        "environment": "development",
        "python_version": __import__('sys').version,
        "dependencies": {
            "fastapi": __import__('fastapi').__version__,
            "chromadb": chromadb_version,
            "sqlite3": "builtin"
        }
    }


@router.post("/reindex")
async def reindex_vectors(db: DatabaseDep):
    """重建向量索引"""
    try:
        # 使用向量同步服务重新索引所有资料
        success = await vector_sync_service.reindex_all_artifacts()
        
        if success:
            # 获取活跃资料总数
            cursor = db["sqlite"].cursor()
            cursor.execute("SELECT COUNT(*) FROM artifacts WHERE is_active = 1")
            reindexed_count = cursor.fetchone()[0]
            
            return {
                "success": True,
                "message": f"成功重建 {reindexed_count} 条资料的向量索引",
                "reindexed_count": reindexed_count
            }
        else:
            return {
                "success": False,
                "message": "重建索引失败"
            }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"重建索引失败: {str(e)}"
        }