"""资料管理API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import time

from app.models.schemas import ArtifactCreate, ArtifactResponse, ArtifactListResponse
from app.api.dependencies import DatabaseDep
from app.services.vector_sync import vector_sync_service

router = APIRouter(prefix="/api/v1", tags=["资料管理"])

@router.get("/artifacts", response_model=ArtifactListResponse)
async def get_artifacts(
    db: DatabaseDep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选")
):
    """获取资料列表"""
    try:
        cursor = db["sqlite"].cursor()
        
        # 构建查询条件
        conditions = ["a.is_active = 1"]
        params = []
        
        if keyword:
            conditions.append("(a.title LIKE ? OR a.content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if category:
            conditions.append("a.category = ?")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) FROM artifacts a WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * size
        data_query = f"""
            SELECT id, title, content, source_type, source_path, category, tags, metadata, created_at, updated_at, is_active
            FROM artifacts a
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([size, offset])
        cursor.execute(data_query, params)
        
        artifacts = []
        for row in cursor.fetchall():
            # 确保行数据足够长，防止索引越界
            if len(row) < 11:
                # 如果行数据不足，跳过这条记录或使用默认值
                continue
            artifacts.append(ArtifactResponse(
                id=row[0] if row[0] is not None else int(time.time()*1000) % 1000000,
                title=row[1],
                content=row[2],
                category=row[5] or "",
                created_at=row[8],
                updated_at=row[9],
                is_active=bool(row[10]) if row[10] is not None else True
            ))
        
        return ArtifactListResponse(
            artifacts=artifacts,
            total_count=total_count,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资料列表失败: {str(e)}")

@router.post("/artifacts", response_model=ArtifactResponse)
async def create_artifact(artifact: ArtifactCreate, db: DatabaseDep):
    """创建新资料"""
    try:
        cursor = db["sqlite"].cursor()
        
        # 插入资料
        cursor.execute("""
            INSERT INTO artifacts (title, content, category, is_active, created_at, updated_at)
            VALUES (?, ?, ?, 1, datetime('now'), datetime('now'))
        """, (artifact.title, artifact.content, artifact.category))
        
        db["sqlite"].commit()
        
        # 获取插入的ID
        artifact_id = cursor.lastrowid
        if artifact_id is None:
            # 如果lastrowid为None，查询刚插入的记录获取ID
            cursor.execute("SELECT id FROM artifacts WHERE rowid = last_insert_rowid()")
            result = cursor.fetchone()
            if result:
                artifact_id = result[0]
            else:
                # 如果还是获取不到，生成临时ID
                artifact_id = int(time.time() * 1000) % 1000000
        
        # 返回创建的资料
        cursor.execute("""
            SELECT id, title, content, category, created_at, updated_at, is_active
            FROM artifacts
            WHERE rowid = ?
        """, (artifact_id,))
        
        row = cursor.fetchone()
        if row:
            # 确保ID是有效的，如果不是则使用备选ID
            artifact_id_result = row[0] if row[0] is not None else str(artifact_id)
            response = ArtifactResponse(
                id=artifact_id_result,
                title=row[1],
                content=row[2],
                category=row[3],
                created_at=row[4],
                updated_at=row[5],
                is_active=bool(row[6]) if row[6] is not None else True
            )
        else:
            # 如果获取不到，返回基本数据
            response = ArtifactResponse(
                id=str(artifact_id),
                title=artifact.title,
                content=artifact.content,
                category=artifact.category or "",
                created_at=__import__('datetime').datetime.now(),
                updated_at=__import__('datetime').datetime.now(),
                is_active=True
            )
        
        # 异步同步到向量数据库
        try:
            import asyncio
            # 确保ID是整数类型
            artifact_id_for_sync = artifact_id_result if isinstance(artifact_id_result, int) else int(artifact_id_result)
            
            # 创建一个安全的异步任务包装器
            async def safe_sync():
                try:
                    await vector_sync_service.sync_artifact_to_vector_db(
                        artifact_id_for_sync,
                        artifact.title,
                        artifact.content,
                        artifact.category or ""
                    )
                except Exception as sync_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"向量同步失败: {str(sync_error)}", exc_info=True)
            
            asyncio.create_task(safe_sync())
        except Exception as ve:
            # 向量同步失败不影响主流程，仅记录错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"创建向量同步任务失败: {str(ve)}", exc_info=True)
        
        return response
        
    except Exception as e:
        db["sqlite"].rollback()
        raise HTTPException(status_code=500, detail=f"创建资料失败: {str(e)}")

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: int, db: DatabaseDep):
    """获取指定资料"""
    try:
        cursor = db["sqlite"].cursor()
        cursor.execute("""
            SELECT id, title, content, category, created_at, updated_at, is_active
            FROM artifacts
            WHERE id = ? AND is_active = 1
        """, (artifact_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="资料不存在")
        
        # 确保行数据足够长，防止索引越界
        if len(row) < 7:
            raise HTTPException(status_code=500, detail="数据库记录格式错误")
        
        return ArtifactResponse(
            id=row[0],
            title=row[1],
            content=row[2],
            category=row[3],
            created_at=row[4],
            updated_at=row[5],
            is_active=bool(row[6])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资料失败: {str(e)}")

@router.put("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(artifact_id: int, artifact: ArtifactCreate, db: DatabaseDep):
    """更新资料"""
    try:
        cursor = db["sqlite"].cursor()
        
        # 检查资料是否存在
        cursor.execute("SELECT id, title, content, category FROM artifacts WHERE id = ? AND is_active = 1", (artifact_id,))
        existing_artifact = cursor.fetchone()
        if not existing_artifact:
            raise HTTPException(status_code=404, detail="资料不存在")
        
        # 更新资料
        cursor.execute("""
            UPDATE artifacts
            SET title = ?, content = ?, category = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (artifact.title, artifact.content, artifact.category, artifact_id))
        
        db["sqlite"].commit()
        
        # 返回更新后的资料
        updated_artifact = await get_artifact(artifact_id, db)
        
        # 异步同步到向量数据库
        try:
            import asyncio
            
            # 创建一个安全的异步任务包装器
            async def safe_sync():
                try:
                    await vector_sync_service.sync_artifact_to_vector_db(
                        artifact_id,
                        artifact.title,
                        artifact.content,
                        artifact.category or ""
                    )
                except Exception as sync_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"向量同步失败: {str(sync_error)}", exc_info=True)
            
            asyncio.create_task(safe_sync())
        except Exception as ve:
            # 向量同步失败不影响主流程，仅记录错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"创建向量同步任务失败: {str(ve)}", exc_info=True)
        
        return updated_artifact
        
    except HTTPException:
        raise
    except Exception as e:
        db["sqlite"].rollback()
        raise HTTPException(status_code=500, detail=f"更新资料失败: {str(e)}")

@router.delete("/artifacts/{artifact_id}")
async def delete_artifact(artifact_id: int, db: DatabaseDep):
    """删除资料"""
    try:
        cursor = db["sqlite"].cursor()
        
        # 检查资料是否存在
        cursor.execute("SELECT id FROM artifacts WHERE id = ? AND is_active = 1", (artifact_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="资料不存在")
        
        # 软删除资料
        cursor.execute("UPDATE artifacts SET is_active = 0, updated_at = datetime('now') WHERE id = ?", (artifact_id,))
        db["sqlite"].commit()
        
        # 异步从向量数据库中移除
        try:
            import asyncio
            
            # 创建一个安全的异步任务包装器
            async def safe_remove():
                try:
                    await vector_sync_service.remove_artifact_from_vector_db(artifact_id)
                except Exception as remove_error:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"从向量数据库移除失败: {str(remove_error)}", exc_info=True)
            
            asyncio.create_task(safe_remove())
        except Exception as ve:
            # 向量移除失败不影响主流程，仅记录错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"创建向量移除任务失败: {str(ve)}", exc_info=True)
        
        return {"success": True, "message": "资料删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db["sqlite"].rollback()
        raise HTTPException(status_code=500, detail=f"删除资料失败: {str(e)}")