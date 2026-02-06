"""依赖注入模块"""
from fastapi import Depends, HTTPException, status
from typing import Annotated
import logging

from app.core.config import config
from app.core.database import db_manager

logger = logging.getLogger(__name__)


from contextlib import contextmanager

def get_db():
    """获取数据库连接依赖 - 使用同步版本避免异步问题"""
    import sqlite3
    from app.core.config import config
    
    # 为每个请求创建新的SQLite连接
    conn = sqlite3.connect(
        config.SQLITE_DB_PATH,
        check_same_thread=False,
        timeout=config.SQLITE_TIMEOUT
    )
    conn.row_factory = sqlite3.Row
    
    try:
        # 安全地获取ChromaDB相关信息
        chroma_client = getattr(db_manager, 'chroma_client', None) if getattr(db_manager, 'chroma_available', False) else None
        collection = getattr(db_manager, 'collection', None) if getattr(db_manager, 'chroma_available', False) else None
        
        yield {
            "sqlite": conn,
            "chroma": chroma_client,
            "collection": collection
        }
    finally:
        # 确保连接被正确关闭
        conn.close()


# 数据库依赖类型
DatabaseDep = Annotated[dict, Depends(get_db)]


async def verify_api_key(api_key: str):
    """API密钥验证依赖"""
    if not api_key or api_key != config.API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key


APIKeyDep = Annotated[str, Depends(verify_api_key)]