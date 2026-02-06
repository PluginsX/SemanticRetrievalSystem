"""
数据库连接管理模块
负责SQLite和Chroma数据库的连接和初始化
"""
import sqlite3
import os
from typing import Optional
from .logger_manager import log, LogType

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    log("ChromaDB未安装或不可用，向量搜索功能将被禁用", LogType.SERVER, "WARNING")

from .config import config


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.chroma_client = None
        self.collection = None
        self.chroma_available = CHROMA_AVAILABLE
        
    def init_sqlite(self) -> sqlite3.Connection:
        """初始化SQLite数据库连接"""
        if self.sqlite_conn is None:
            # 创建数据库连接
            # 从配置中获取SQLite配置
            import yaml
            from pathlib import Path
            
            # 读取current_config.yaml获取完整的SQLite配置
            config_path = Path("./config/current_config.yaml")
            sqlite_config = {"check_same_thread": False}  # 默认值
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        full_config = yaml.safe_load(f)
                        if full_config and 'database' in full_config and 'sqlite' in full_config['database']:
                            sqlite_config.update(full_config['database']['sqlite'])
                except Exception as e:
                    log(f"读取配置文件失败: {e}", LogType.SERVER, "ERROR")
            
            self.sqlite_conn = sqlite3.connect(
                config.SQLITE_DB_PATH,
                check_same_thread=sqlite_config.get('check_same_thread', False),
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
            CREATE TABLE IF NOT EXISTS artifacts_new (
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
        
        # 检查是否需要迁移数据
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='artifacts_new'")
        new_table_exists = cursor.fetchone()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='artifacts'")
        old_table_exists = cursor.fetchone()
        
        if old_table_exists and new_table_exists:
            # 将旧表数据迁移到新表（忽略id列，让SQLite自动生成）
            try:
                cursor.execute("""
                    INSERT INTO artifacts_new (title, content, source_type, source_path, 
                                             category, tags, metadata, created_at, updated_at, is_active)
                    SELECT title, content, source_type, source_path, 
                           category, tags, metadata, created_at, updated_at, is_active
                    FROM artifacts
                    WHERE id IS NOT NULL
                """)
                
                # 删除旧表
                cursor.execute("DROP TABLE artifacts")
                
                # 重命名新表
                cursor.execute("ALTER TABLE artifacts_new RENAME TO artifacts")
                
            except sqlite3.Error:
                # 如果迁移失败，删除新表
                cursor.execute("DROP TABLE IF EXISTS artifacts_new")
        
        elif new_table_exists and not old_table_exists:
            # 如果只有新表存在，重命名它
            cursor.execute("ALTER TABLE artifacts_new RENAME TO artifacts")
        
        # 切片表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks_new (
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
        
        # 检查是否需要迁移数据
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_new'")
        new_chunks_table_exists = cursor.fetchone()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks'")
        old_chunks_table_exists = cursor.fetchone()
        
        if old_chunks_table_exists and new_chunks_table_exists:
            # 将旧表数据迁移到新表
            try:
                cursor.execute("""
                    INSERT INTO chunks_new (artifact_id, chunk_index, content, token_count, metadata, created_at)
                    SELECT CAST(artifact_id AS INTEGER), chunk_index, content, token_count, metadata, created_at
                    FROM chunks
                """)
                
                # 删除旧表
                cursor.execute("DROP TABLE chunks")
                
                # 重命名新表
                cursor.execute("ALTER TABLE chunks_new RENAME TO chunks")
                
            except sqlite3.Error:
                # 如果迁移失败，删除新表
                cursor.execute("DROP TABLE IF EXISTS chunks_new")
        
        elif new_chunks_table_exists and not old_chunks_table_exists:
            # 如果只有新表存在，重命名它
            cursor.execute("ALTER TABLE chunks_new RENAME TO chunks")
        
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
        
        # 系统配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_category ON artifacts(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_created_at ON artifacts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_artifact_id ON chunks(artifact_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(key)")
        
        self.sqlite_conn.commit()
    
    def init_chroma(self):
        """初始化Chroma向量数据库"""
        if not self.chroma_available:
            log("ChromaDB不可用，跳过初始化", LogType.SERVER, "WARNING")
            return None
            
        if self.chroma_client is None:
            try:
                # 创建Chroma客户端
                # 读取current_config.yaml获取完整的Chroma配置
                import yaml
                from pathlib import Path
                
                config_path = Path("./config/current_config.yaml")
                chroma_config = {
                    "anonymized_telemetry": False,
                    "allow_reset": True
                }  # 默认值
                
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            full_config = yaml.safe_load(f)
                            if full_config and 'database' in full_config and 'chroma' in full_config['database']:
                                chroma_config.update(full_config['database']['chroma'])
                    except Exception as e:
                        log(f"读取配置文件失败: {e}", LogType.SERVER, "ERROR")
                
                self.chroma_client = chromadb.PersistentClient(
                    path=config.CHROMA_PERSIST_DIR,
                    settings=Settings(
                        anonymized_telemetry=chroma_config['anonymized_telemetry'],
                        allow_reset=chroma_config['allow_reset']
                    )
                )
                
                # 检查集合是否存在
                try:
                    existing_collection = self.chroma_client.get_collection(
                        name="artifact_embeddings"
                    )
                    # 检查集合是否使用了预计算的向量
                    collection_metadata = existing_collection.metadata
                    if collection_metadata and collection_metadata.get("use_precomputed_embeddings") == "true":
                        log("使用现有的ChromaDB集合，已配置为使用预计算的向量", LogType.SERVER, "INFO")
                        self.collection = existing_collection
                    else:
                        # 集合存在但配置不正确，删除并重新创建
                        log("现有ChromaDB集合配置不正确，重新创建", LogType.SERVER, "WARNING")
                        self.chroma_client.delete_collection(name="artifact_embeddings")
                        # 重新创建集合，使用预计算的向量
                        self.collection = self.chroma_client.create_collection(
                            name="artifact_embeddings",
                            metadata={
                                "description": "语义检索系统资料向量存储",
                                "use_precomputed_embeddings": "true"
                            }
                        )
                        log("重新创建ChromaDB集合成功，使用预计算的向量", LogType.SERVER, "INFO")
                except:
                    # 集合不存在，创建新的
                    # 有些版本的ChromaDB使用不同的异常类型
                    # 重要：不指定embedding_function，使用预计算的向量
                    self.collection = self.chroma_client.create_collection(
                        name="artifact_embeddings",
                        metadata={
                            "description": "语义检索系统资料向量存储",
                            "use_precomputed_embeddings": "true"
                        }
                    )
                    log("创建ChromaDB集合成功，使用预计算的向量", LogType.SERVER, "INFO")
                    
            except Exception as e:
                log(f"ChromaDB初始化失败: {e}", LogType.SERVER, "ERROR")
                self.chroma_available = False
                return None
                
        return self.chroma_client
        
    def get_all_vectors(self):
        """获取所有向量数据（用于内存搜索）"""
        try:
            if not self.chroma_available or not self.collection:
                log("ChromaDB不可用，无法获取向量数据", LogType.SERVER, "WARNING")
                return []
            
            # 获取所有向量数据
            results = self.collection.get()
            ids = results.get('ids', [])
            embeddings = results.get('embeddings', [])
            metadatas = results.get('metadatas', [])
            
            # 构建向量数据列表
            vector_data = []
            for i, vec_id in enumerate(ids):
                if i < len(embeddings) and i < len(metadatas):
                    vector_data.append({
                        'id': vec_id,
                        'embedding': embeddings[i],
                        'metadata': metadatas[i]
                    })
            
            log(f"成功获取 {len(vector_data)} 个向量数据", LogType.SERVER, "INFO")
            return vector_data
        except Exception as e:
            log(f"获取向量数据失败: {str(e)}", LogType.SERVER, "ERROR")
            return []
    
    def close_connections(self):
        """关闭所有数据库连接"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            self.sqlite_conn = None
            
        if self.chroma_client:
            # Chroma客户端会自动管理连接
            self.chroma_client = None


# 全局数据库管理器实例
db_manager = DatabaseManager()