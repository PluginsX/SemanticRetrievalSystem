"""检索API路由"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import time
from datetime import datetime

from app.models.schemas import SearchRequest, SearchResult, SearchResponse
from app.api.dependencies import DatabaseDep
from app.core.logger_manager import log, LogType
import logging

router = APIRouter(prefix="/api/v1", tags=["检索服务"])

@router.post("/search/retrieve")
async def retrieve_documents(search_request: SearchRequest, db: DatabaseDep):
    """检索相关文档"""
    start_time = time.time()
    
    try:
        # 记录检索历史
        cursor = db["sqlite"].cursor()
        cursor.execute("""
            INSERT INTO search_history (query, created_at)
            VALUES (?, datetime('now'))
        """, (search_request.query,))
        db["sqlite"].commit()
        search_id = cursor.lastrowid
        
        # 检查是否可以使用向量数据库
        chroma_client = db.get("chroma")
        collection = db.get("collection")
        
        final_results = []
        
        # 启用向量搜索功能
        if chroma_client and collection:
            try:
                from app.services.ai_clients import embedding_client
                import asyncio
                
                log("开始执行向量搜索", LogType.SERVER, "INFO")
                
                from app.core.config import config
                
                # 生成查询向量
                query_embedding = await embedding_client.embed(search_request.query)
                log(f"生成查询向量成功，维度: {len(query_embedding)}", LogType.SERVER, "INFO")
                log(f"配置文件中设置的向量维度: {config.EMBEDDING_DIMENSIONS}", LogType.SERVER, "INFO")
                
                # 执行向量搜索
                vector_results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=search_request.top_k,
                    include=["documents", "distances", "metadatas"]
                )
                
                log(f"向量搜索执行成功，返回 {len(vector_results['documents'][0])} 个结果", LogType.SERVER, "INFO")
                
                # 处理向量搜索结果
                for i, (document, distance, metadata) in enumerate(zip(
                    vector_results['documents'][0], 
                    vector_results['distances'][0], 
                    vector_results['metadatas'][0]
                )):
                    # 计算相似度（距离越小，相似度越高）
                    similarity = 1.0 / (1.0 + distance)
                    
                    if similarity >= search_request.threshold:
                        # 从metadata中获取artifact_id
                        artifact_id = metadata.get('artifact_id') if metadata else None
                        
                        if artifact_id:
                            # 查询完整的artifact信息
                            cursor.execute("""
                                SELECT id, title, content, category, created_at, updated_at, is_active
                                FROM artifacts
                                WHERE id = ? AND is_active = 1
                            """, (artifact_id,))
                            artifact = cursor.fetchone()
                            
                            if artifact:
                                final_results.append(SearchResult(
                                    id=artifact[0],
                                    title=artifact[1],
                                    content=artifact[2],
                                    category=artifact[3],
                                    created_at=artifact[4],
                                    updated_at=artifact[5],
                                    is_active=bool(artifact[6]),
                                    similarity=similarity
                                ))
                
                log(f"向量搜索结果处理完成，添加了 {len(final_results)} 个结果", LogType.SERVER, "INFO")
                
            except Exception as e:
                log(f"向量搜索失败: {str(e)}", LogType.SERVER, "ERROR")
                # 向量搜索失败，继续使用关键词搜索
        else:
            log("ChromaDB客户端或集合不可用，使用关键词搜索", LogType.SERVER, "WARNING")
                
        # 如果向量搜索没有返回足够的结果或失败，则使用关键词搜索作为补充
        if len(final_results) < search_request.top_k:
            remaining_slots = search_request.top_k - len(final_results)
            
            # 构建查询条件
            conditions = ["a.is_active = 1"]
            params = []
            
            # 添加关键词搜索条件
            if search_request.query:
                conditions.append("(a.title LIKE ? OR a.content LIKE ?)")
                params.extend([f"%{search_request.query}%", f"%{search_request.query}%"])
            
            # 添加分类过滤条件
            if search_request.category_filter:
                category_placeholders = ','.join(['?' for _ in search_request.category_filter])
                conditions.append(f"a.category IN ({category_placeholders})")
                params.extend(search_request.category_filter)
            
            where_clause = " AND ".join(conditions)
            
            # 执行关键词搜索
            keyword_query = f"""
                SELECT id, title, content, category, created_at, updated_at, is_active
                FROM artifacts a
                WHERE {where_clause}
                ORDER BY CASE 
                    WHEN a.title LIKE ? THEN 1
                    WHEN a.content LIKE ? THEN 2
                    ELSE 3
                END, a.created_at DESC
                LIMIT ?
            """
            keyword_params = params + [f"%{search_request.query}%", f"%{search_request.query}%", remaining_slots]
            
            cursor.execute(keyword_query, keyword_params)
            keyword_results = cursor.fetchall()
            
            # 添加关键词搜索结果，但不重复添加已有的结果
            existing_ids = {result.id for result in final_results}
            for row in keyword_results:
                artifact_id = row[0]
                if artifact_id not in existing_ids:
                    # 对于关键词匹配的结果，给予一个较低的相似度分数
                    similarity = 0.5  # 默认相似度
                    
                    # 如果标题匹配，提高相似度
                    if search_request.query.lower() in (row[1] or "").lower():
                        similarity = 0.7
                    elif search_request.query.lower() in (row[2] or "").lower():
                        similarity = 0.5
                        
                    if similarity >= search_request.threshold:
                        final_results.append(SearchResult(
                            id=row[0],
                            title=row[1],
                            content=row[2],
                            category=row[3],
                            created_at=row[4],
                            updated_at=row[5],
                            is_active=bool(row[6]),
                            similarity=similarity
                        ))
                        
                        if len(final_results) >= search_request.top_k:
                            break
        
        # 按相似度排序
        final_results.sort(key=lambda x: x.similarity or 0, reverse=True)
        
        # 限制结果数量
        final_results = final_results[:search_request.top_k]
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        # 更新检索历史记录响应时间
        cursor.execute("""
            UPDATE search_history 
            SET artifact_count = ?, response_time = ?
            WHERE id = ?
        """, (len(final_results), response_time, search_id))
        db["sqlite"].commit()
        
        # 返回包装在data字段中的格式以匹配前端的响应拦截器期望
        return {
            "data": {
                "query": search_request.query,
                "artifacts": [artifact.dict() for artifact in final_results],
                "total_count": len(final_results),
                "response_time": response_time
            }
        }
        
    except Exception as e:
        # 记录错误的检索历史
        try:
            cursor.execute("""
                INSERT INTO search_history (query, response_time, created_at)
                VALUES (?, -1, datetime('now'))
            """, (search_request.query,))
            db["sqlite"].commit()
        except:
            pass
            
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@router.get("/search/history")
async def get_search_history(
    db: DatabaseDep,
    limit: int = 10
):
    """获取检索历史"""
    try:
        cursor = db["sqlite"].cursor()
        cursor.execute("""
            SELECT query, artifact_count, response_time, created_at
            FROM search_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "query": row[0],
                "artifact_count": row[1] or 0,
                "response_time": row[2] or 0,
                "created_at": row[3]
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检索历史失败: {str(e)}")

@router.delete("/search/history/{history_id}")
async def delete_search_history(history_id: int, db: DatabaseDep):
    """删除检索历史记录"""
    try:
        cursor = db["sqlite"].cursor()
        cursor.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
        db["sqlite"].commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        
        return {"success": True, "message": "历史记录删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除历史记录失败: {str(e)}")
