"""资料管理API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import time
import json

from app.models.schemas import ArtifactCreate, ArtifactResponse, ArtifactListResponse
from app.api.dependencies import DatabaseDep
from app.services.vector_sync import vector_sync_service
from app.core.logger_manager import log, LogType

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
        log(f"SQLite - 开始获取资料列表，页码: {page}, 每页大小: {size}, 关键词: {keyword}, 分类: {category}", LogType.DATABASE, "INFO")
        cursor = db["sqlite"].cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if keyword:
            conditions.append("(a.title LIKE ? OR a.content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if category:
            conditions.append("a.category = ?")
            params.append(category)
        
        # 构建WHERE子句
        where_clause = ""
        if conditions:
            where_clause = " AND ".join(conditions)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) FROM artifacts a"
        if where_clause:
            count_query += f" WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * size
        data_query = f"""
            SELECT id, title, content, source_type, source_path, category, tags, metadata, created_at, updated_at, is_active
            FROM artifacts a
        """
        if where_clause:
            data_query += f" WHERE {where_clause}"
        data_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
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
        
        log(f"SQLite - 获取资料列表成功，共 {total_count} 条，返回 {len(artifacts)} 条", LogType.DATABASE, "INFO")
        
        return ArtifactListResponse(
            artifacts=artifacts,
            total_count=total_count,
            page=page,
            size=size
        )
        
    except Exception as e:
        log(f"SQLite - 获取资料列表失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取资料列表失败: {str(e)}")

@router.post("/artifacts", response_model=ArtifactResponse)
async def create_artifact(artifact: ArtifactCreate, db: DatabaseDep):
    """创建新资料"""
    try:
        log(f"SQLite - 开始创建新资料，标题: {artifact.title[:50]}...", LogType.DATABASE, "INFO")
        cursor = db["sqlite"].cursor()
        
        # 处理tags和metadata字段 - 需要转换为字符串存储
        tags_str = ','.join(artifact.tags) if artifact.tags else None
        metadata_str = json.dumps(artifact.metadata, ensure_ascii=False) if artifact.metadata else None
        
        # 插入资料
        cursor.execute("""
            INSERT INTO artifacts (title, content, category, tags, metadata, source_type, source_path, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now', 'localtime'), datetime('now', 'localtime'))
        """, (
            artifact.title, 
            artifact.content, 
            artifact.category,
            tags_str,
            metadata_str,
            artifact.source_type,
            artifact.source_path
        ))
        
        db["sqlite"].commit()
        log(f"SQLite - 创建资料成功，获取插入ID", LogType.DATABASE, "INFO")
        
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
            SELECT id, title, content, category, tags, metadata, source_type, source_path, created_at, updated_at, is_active
            FROM artifacts
            WHERE rowid = ?
        """, (artifact_id,))
        
        row = cursor.fetchone()
        if row:
            # 确保ID是有效的，如果不是则使用备选ID
            artifact_id_result = row[0] if row[0] is not None else str(artifact_id)
            
            # 处理tags字段 - 从字符串转换为列表
            tags_list = []
            if row[4]:  # tags字段
                if isinstance(row[4], str):
                    tags_list = [tag.strip() for tag in row[4].split(',') if tag.strip()]
                elif isinstance(row[4], list):
                    tags_list = row[4]
            
            # 处理metadata字段 - 从字符串转换为字典
            metadata_dict = {}
            if row[5]:  # metadata字段
                if isinstance(row[5], str):
                    try:
                        metadata_dict = json.loads(row[5])
                    except:
                        metadata_dict = {}
                elif isinstance(row[5], dict):
                    metadata_dict = row[5]
            
            response = ArtifactResponse(
                id=artifact_id_result,
                title=row[1],
                content=row[2],
                category=row[3],
                tags=tags_list,
                metadata=metadata_dict,
                source_type=row[6],
                source_path=row[7],
                created_at=row[8],
                updated_at=row[9],
                is_active=bool(row[10]) if row[10] is not None else True
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
        
        log(f"SQLite - 创建资料完成，ID: {artifact_id}", LogType.DATABASE, "INFO")
        return response
        
    except Exception as e:
        db["sqlite"].rollback()
        log(f"SQLite - 创建资料失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"创建资料失败: {str(e)}")

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: int, db: DatabaseDep):
    """获取指定资料"""
    try:
        log(f"SQLite - 开始获取指定资料，ID: {artifact_id}", LogType.DATABASE, "INFO")
        cursor = db["sqlite"].cursor()
        cursor.execute("""
            SELECT id, title, content, category, created_at, updated_at, is_active
            FROM artifacts
            WHERE id = ?
        """, (artifact_id,))
        
        row = cursor.fetchone()
        if not row:
            log(f"SQLite - 资料不存在，ID: {artifact_id}", LogType.DATABASE, "WARNING")
            raise HTTPException(status_code=404, detail="资料不存在")
        
        # 确保行数据足够长，防止索引越界
        if len(row) < 7:
            raise HTTPException(status_code=500, detail="数据库记录格式错误")
        
        log(f"SQLite - 获取资料成功，ID: {artifact_id}, 标题: {row[1][:30]}...", LogType.DATABASE, "INFO")
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
        log(f"SQLite - 获取资料失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取资料失败: {str(e)}")

@router.put("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(artifact_id: int, artifact: ArtifactCreate, db: DatabaseDep):
    """更新资料"""
    try:
        log(f"SQLite - 开始更新资料，ID: {artifact_id}, 新标题: {artifact.title[:50]}...", LogType.DATABASE, "INFO")
        cursor = db["sqlite"].cursor()
        
        # 检查资料是否存在
        cursor.execute("SELECT id, title, content, category FROM artifacts WHERE id = ? AND is_active = 1", (artifact_id,))
        existing_artifact = cursor.fetchone()
        if not existing_artifact:
            log(f"SQLite - 资料不存在，ID: {artifact_id}", LogType.DATABASE, "WARNING")
            raise HTTPException(status_code=404, detail="资料不存在")
        
        # 更新资料
        cursor.execute("""
            UPDATE artifacts
            SET title = ?, content = ?, category = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """, (artifact.title, artifact.content, artifact.category, artifact_id))
        
        db["sqlite"].commit()
        log(f"SQLite - 更新资料成功，ID: {artifact_id}", LogType.DATABASE, "INFO")
        
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
        
        log(f"SQLite - 更新资料完成，ID: {artifact_id}", LogType.DATABASE, "INFO")
        return updated_artifact
        
    except HTTPException:
        raise
    except Exception as e:
        db["sqlite"].rollback()
        log(f"SQLite - 更新资料失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"更新资料失败: {str(e)}")

@router.delete("/artifacts/{artifact_id}")
async def delete_artifact(artifact_id: int, db: DatabaseDep):
    """删除资料"""
    try:
        log(f"SQLite - 开始删除资料，ID: {artifact_id}", LogType.DATABASE, "INFO")
        cursor = db["sqlite"].cursor()
        
        # 检查资料是否存在
        cursor.execute("SELECT id FROM artifacts WHERE id = ?", (artifact_id,))
        if not cursor.fetchone():
            log(f"SQLite - 资料不存在，ID: {artifact_id}", LogType.DATABASE, "WARNING")
            raise HTTPException(status_code=404, detail="资料不存在")
        
        # 物理删除资料
        cursor.execute("DELETE FROM artifacts WHERE id = ?", (artifact_id,))
        db["sqlite"].commit()
        log(f"SQLite - 删除资料成功，ID: {artifact_id}", LogType.DATABASE, "INFO")
        
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
        log(f"SQLite - 删除资料失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"删除资料失败: {str(e)}")


@router.post("/artifacts/batch")
async def batch_import_artifacts(json_data: dict):
    """批量导入资料"""
    try:
        import uuid
        from app.services.batch_import import batch_import_service
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 提取数据 - 兼容两种格式：直接数组或 { data: [...] } 对象
        if isinstance(json_data, list):
            # 直接是数组格式
            data_list = json_data
        else:
            # 对象格式，检查是否有 'data' 键
            data_list = json_data.get('data', json_data if isinstance(json_data, list) else [])
        
        # 将数据转换为JSON字符串
        import json
        json_str = json.dumps(data_list, ensure_ascii=False)
        
        # 启动批量导入任务（异步）
        import asyncio
        asyncio.create_task(batch_import_service.import_artifacts_from_json(json_str, task_id))
        
        return {
            "success": True,
            "message": "批量导入任务已启动",
            "task_id": task_id
        }
        
    except Exception as e:
        log(f"SQLite - 批量导入启动失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"批量导入启动失败: {str(e)}")


@router.get("/artifacts/batch/status/{task_id}")
async def get_batch_import_status(task_id: str):
    """获取批量导入任务状态"""
    try:
        from app.services.batch_import import batch_import_service
        
        status = batch_import_service.get_task_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "success": True,
            "data": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"SQLite - 获取批量导入状态失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取批量导入状态失败: {str(e)}")


@router.post("/artifacts/batch/cancel/{task_id}")
async def cancel_batch_import(task_id: str):
    """取消批量导入任务"""
    try:
        from app.services.batch_import import batch_import_service
        
        success = batch_import_service.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "success": True,
            "message": "任务已取消"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"SQLite - 取消批量导入任务失败: {str(e)}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"取消批量导入任务失败: {str(e)}")