"""
轻量级数据库管理模块（不包含ChromaDB）
用于快速测试和开发
"""
import logging
import sqlite3
import os
from typing import Optional
import uuid
from .config import config
from .logger_manager import log, LogType


class LightweightDatabaseManager:
    """轻量级数据库管理器（仅SQLite）"""
    
    def __init__(self):
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.chroma_available = False
        
    def init_sqlite(self) -> sqlite3.Connection:
        """初始化SQLite数据库连接"""
        if self.sqlite_conn is None:
            # 创建数据库连接
            self.sqlite_conn = sqlite3.connect(
                config.SQLITE_DB_PATH,
                check_same_thread=False,  # 固定值，避免配置访问问题
                timeout=config.SQLITE_TIMEOUT
            )
            self.sqlite_conn.row_factory = sqlite3.Row
            
            # 创建表结构
            self._create_tables()
            
        return self.sqlite_conn
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.sqlite_conn.cursor()
        
        # 资料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type VARCHAR(32),
                source_path TEXT,
                category VARCHAR(64),
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # 切片表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                token_count INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE
            )
        """)
        
        # 检索历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                artifact_count INTEGER,
                response_time FLOAT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_category ON artifacts(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_created_at ON artifacts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_artifact_id ON chunks(artifact_id)")
        
        self.sqlite_conn.commit()
    
    def init_chroma(self):
        """初始化Chroma向量数据库（总是返回None）"""
        log("使用轻量级模式，ChromaDB功能不可用", LogType.SERVER, "WARNING")
        return None
    
    def close_connections(self):
        """关闭所有数据库连接"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            self.sqlite_conn = None


# 全局轻量级数据库管理器实例
lightweight_db_manager = LightweightDatabaseManager()