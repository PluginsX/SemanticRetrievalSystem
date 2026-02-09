"""
向量同步服务模块
负责将资料数据同步到向量数据库
"""
import logging
from typing import List, Optional
from app.services.ai_clients import embedding_client
from app.core.database import db_manager
from app.core.config import config
from app.core.logger_manager import log, LogType

logger = logging.getLogger(__name__)


class VectorSyncService:
    """向量同步服务"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.embedding_client = embedding_client
    
    async def sync_artifact_to_vector_db(self, artifact_id: int, title: str, content: str, category: str = ""):
        """
        将单个资料同步到向量数据库
        
        Args:
            artifact_id: 资料ID
            title: 资料标题
            content: 资料内容
            category: 资料分类
        """
        try:
            # 初始化向量数据库
            self.db_manager.init_chroma()
            
            if not self.db_manager.chroma_available:
                log("ChromaDB - ChromaDB不可用，跳过向量同步", LogType.DATABASE, "WARNING")
                return False
            
            if not self.db_manager.collection:
                log("ChromaDB - ChromaDB集合不可用，无法同步向量数据", LogType.DATABASE, "ERROR")
                return False
            
            # 生成向量 - 结合标题和内容
            text_to_embed = f"{title}\n\n{content}" if title and content else (title or content or "")
            
            if not text_to_embed.strip():
                log(f"ChromaDB - 资料 {artifact_id} 内容为空，跳过向量化", LogType.DATABASE, "WARNING")
                return True
            
            try:
                # 调用外部Embedding API生成向量
                embedding_vector = await self.embedding_client.embed(text_to_embed)
            except Exception as embed_error:
                log(f"ChromaDB - 生成向量失败，跳过向量同步: {str(embed_error)}", LogType.DATABASE, "ERROR")
                return False
            
            # 将向量数据添加到Chroma数据库（不存储documents，只存储向量数据和必要的metadata）
            try:
                self.db_manager.collection.upsert(
                    ids=[str(artifact_id)],
                    embeddings=[embedding_vector],
                    metadatas=[{
                        "artifact_id": str(artifact_id),
                        "category": category or "",
                        "source_type": "artifact"
                    }]
                )
            except Exception as upsert_error:
                log(f"ChromaDB - 添加向量到数据库失败: {str(upsert_error)}", LogType.DATABASE, "ERROR")
                return False
            
            log(f"ChromaDB - 成功同步资料 {artifact_id} 到向量数据库", LogType.DATABASE, "INFO")
            return True
            
        except Exception as e:
            log(f"ChromaDB - 同步资料 {artifact_id} 到向量数据库失败: {str(e)}", LogType.DATABASE, "ERROR")
            return False
    
    async def remove_artifact_from_vector_db(self, artifact_id: int):
        """
        从向量数据库中移除资料
        
        Args:
            artifact_id: 资料ID
        """
        try:
            # 初始化向量数据库
            self.db_manager.init_chroma()
            
            if not self.db_manager.chroma_available:
                log("ChromaDB - ChromaDB不可用，跳过向量删除", LogType.DATABASE, "WARNING")
                return False
            
            if not self.db_manager.collection:
                log("ChromaDB - ChromaDB集合不可用，无法删除向量数据", LogType.DATABASE, "ERROR")
                return False
            
            # 从向量数据库中删除对应ID的数据
            self.db_manager.collection.delete(ids=[str(artifact_id)])
            
            log(f"ChromaDB - 成功从向量数据库中移除资料 {artifact_id}", LogType.DATABASE, "INFO")
            return True
            
        except Exception as e:
            log(f"ChromaDB - 从向量数据库中移除资料 {artifact_id} 失败: {str(e)}", LogType.DATABASE, "ERROR")
            return False
    
    async def batch_sync_artifacts_to_vector_db(self, artifacts: List[dict]):
        """
        批量同步资料到向量数据库
        
        Args:
            artifacts: 资料列表，每个元素包含id, title, content, category
        """
        try:
            # 初始化向量数据库
            self.db_manager.init_chroma()
            
            if not self.db_manager.chroma_available:
                logger.warning("ChromaDB不可用，跳过批量向量同步")
                return False
            
            if not self.db_manager.collection:
                logger.error("ChromaDB集合不可用，无法批量同步向量数据")
                return False
            
            # 准备数据
            ids = []
            metadatas = []
            embeddings = []
            
            for artifact in artifacts:
                artifact_id = artifact['id']
                title = artifact['title']
                content = artifact['content']
                category = artifact.get('category', '')
                
                # 生成向量 - 结合标题和内容
                text_to_embed = f"{title}\n\n{content}" if title and content else (title or content or "")
                
                if not text_to_embed.strip():
                    logger.warning(f"资料 {artifact_id} 内容为空，跳过向量化")
                    continue
                
                ids.append(str(artifact_id))
                metadatas.append({
                    "artifact_id": str(artifact_id),
                    "category": category or "",
                    "source_type": "artifact"
                })
            
            if not ids:
                logger.info("没有需要同步的资料")
                return True
            
            # 批量生成向量
            embeddings = await self.embedding_client.embed_batch([f"{artifact['title']}\n\n{artifact['content']}" for artifact in artifacts if artifact.get('title') and artifact.get('content')])
            
            # 批量添加到向量数据库（不存储documents）
            self.db_manager.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"成功批量同步 {len(ids)} 条资料到向量数据库")
            return True
            
        except Exception as e:
            logger.error(f"批量同步资料到向量数据库失败: {str(e)}")
            return False
    
    async def reindex_all_artifacts(self):
        """重新索引所有资料"""
        try:
            # 清空现有向量数据
            self.db_manager.init_chroma()
            
            if not self.db_manager.chroma_available:
                logger.warning("ChromaDB不可用，跳过重新索引")
                return False
            
            if not self.db_manager.collection:
                logger.error("ChromaDB集合不可用，无法重新索引")
                return False
            
            self.db_manager.collection.delete(where={})
            
            # 从SQLite获取所有活跃资料
            cursor = self.db_manager.sqlite_conn.cursor()
            cursor.execute("""
                SELECT id, title, content, category
                FROM artifacts
                WHERE is_active = 1
            """)
            
            artifacts = []
            for row in cursor.fetchall():
                artifacts.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'category': row[3] or ''
                })
            
            logger.info(f"开始重新索引 {len(artifacts)} 条资料")
            
            # 批量同步
            success = await self.batch_sync_artifacts_to_vector_db(artifacts)
            
            if success:
                logger.info(f"成功重新索引 {len(artifacts)} 条资料")
            else:
                logger.error("重新索引失败")
            
            return success
            
        except Exception as e:
            logger.error(f"重新索引所有资料失败: {str(e)}")
            return False


# 全局向量同步服务实例
vector_sync_service = VectorSyncService()