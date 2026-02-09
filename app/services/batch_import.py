"""
批量导入服务模块
负责处理JSON格式的批量资料导入功能
"""
import json
import asyncio
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.vector_sync import vector_sync_service
from app.core.database import db_manager
from app.core.logger_manager import log, LogType
from app.models.schemas import ArtifactCreate


class BatchImportService:
    """批量导入服务"""
    
    def __init__(self):
        self.import_tasks = {}  # 存储导入任务状态
        self.lock = threading.Lock()  # 线程锁保护共享状态
        
    def validate_json_data(self, json_str: str) -> tuple[bool, List[Dict[str, Any]], str]:
        """
        验证JSON数据格式
        
        Args:
            json_str: JSON字符串
            
        Returns:
            tuple: (是否有效, 解析的数据列表, 错误信息)
        """
        try:
            data = json.loads(json_str)
            
            # 检查是否为列表
            if not isinstance(data, list):
                return False, [], "JSON数据必须是一个数组"
            
            validated_data = []
            for i, item in enumerate(data):
                # 检查是否为对象
                if not isinstance(item, dict):
                    return False, [], f"第{i+1}项不是有效的对象"
                
                # 检查必需字段
                if 'title' not in item or not str(item['title']).strip():
                    return False, [], f"第{i+1}项缺少必需的'title'字段或为空"
                
                if 'content' not in item or not str(item['content']).strip():
                    return False, [], f"第{i+1}项缺少必需的'content'字段或为空"
                
                # 直接使用原始数据，不做复杂转换
                validated_item = {
                    'title': str(item['title']).strip(),
                    'content': str(item['content']).strip(),
                    'category': str(item.get('category', '')).strip(),
                    'tags': item.get('tags', []),
                    'metadata': item.get('metadata', {}),
                    'source_type': str(item.get('source_type', '')).strip(),
                    'source_path': str(item.get('source_path', '')).strip()
                }
                
                validated_data.append(validated_item)
            
            return True, validated_data, ""
            
        except json.JSONDecodeError as e:
            return False, [], f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, [], f"验证过程中发生错误: {str(e)}"
    
    async def import_artifacts_from_json(self, json_str: str, task_id: str = None) -> Dict[str, Any]:
        """
        从JSON字符串批量导入资料
        
        Args:
            json_str: JSON格式的资料数据
            task_id: 任务ID，用于跟踪进度
            
        Returns:
            导入结果
        """
        log(f"批量导入 - 开始批量导入任务，任务ID: {task_id}", LogType.DATABASE, "INFO")
        
        # 初始化任务状态
        if task_id:
            with self.lock:
                self.import_tasks[task_id] = {
                    'total': 0,
                    'processed': 0,
                    'success': 0,
                    'failed': 0,
                    'errors': [],
                    'status': 'processing',
                    'start_time': datetime.now()
                }
        
        try:
            # 验证JSON数据
            log(f"批量导入 - 开始验证JSON数据", LogType.DATABASE, "INFO")
            is_valid, data_list, error_msg = self.validate_json_data(json_str)
            if not is_valid:
                log(f"批量导入 - JSON数据验证失败: {error_msg}", LogType.DATABASE, "ERROR")
                if task_id:
                    with self.lock:
                        self.import_tasks[task_id]['status'] = 'failed'
                        self.import_tasks[task_id]['errors'].append(error_msg)
                return {
                    'success': False,
                    'message': error_msg,
                    'total': 0,
                    'success_count': 0,
                    'failed_count': 0
                }
            
            log(f"批量导入 - JSON数据验证成功，共 {len(data_list)} 条记录", LogType.DATABASE, "INFO")
            total_items = len(data_list)
            
            if task_id:
                with self.lock:
                    self.import_tasks[task_id]['total'] = total_items
                    self.import_tasks[task_id]['processed'] = 0
                    self.import_tasks[task_id]['success'] = 0
                    self.import_tasks[task_id]['failed'] = 0
                    self.import_tasks[task_id]['status'] = 'processing'
            
            success_count = 0
            failed_count = 0
            errors = []
            
            # 初始化数据库连接
            log(f"批量导入 - 初始化数据库连接", LogType.DATABASE, "INFO")
            db = {"sqlite": db_manager.init_sqlite()}
            
            for i, item in enumerate(data_list):
                # 检查任务是否被取消
                if task_id:
                    with self.lock:
                        if self.import_tasks.get(task_id, {}).get('status') == 'cancelled':
                            log(f"批量导入 - 任务被取消，停止处理", LogType.DATABASE, "INFO")
                            break
                
                try:
                    log(f"批量导入 - 开始处理第 {i+1}/{total_items} 条记录，标题: {item['title'][:50]}...", LogType.DATABASE, "INFO")
                    
                    # 创建资料对象
                    artifact_create = ArtifactCreate(
                        title=item['title'],
                        content=item['content'],
                        category=item['category'],
                        tags=item['tags'],
                        metadata=item['metadata'],
                        source_type=item['source_type'],
                        source_path=item['source_path']
                    )
                    
                    # 调用现有的资料创建逻辑
                    artifact = await self._create_single_artifact(artifact_create, db)
                    
                    if artifact:
                        log(f"批量导入 - 第 {i+1} 条记录创建成功，ID: {artifact.id}", LogType.DATABASE, "INFO")
                        
                        # 同步到向量数据库 - 等待完成
                        try:
                            # 确保ID是整数类型
                            artifact_id = int(artifact.id) if isinstance(artifact.id, str) else artifact.id
                            
                            # 直接等待向量同步完成
                            await vector_sync_service.sync_artifact_to_vector_db(
                                artifact_id,
                                artifact.title,
                                artifact.content,
                                artifact.category or ""
                            )
                            log(f"批量导入 - 第 {i+1} 条记录向量同步成功", LogType.DATABASE, "INFO")
                        except Exception as sync_error:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"向量同步失败: {str(sync_error)}", exc_info=True)
                            log(f"批量导入 - 第 {i+1} 条记录向量同步失败: {str(sync_error)}", LogType.DATABASE, "ERROR")
                        
                        success_count += 1
                    else:
                        log(f"批量导入 - 第 {i+1} 条记录创建失败", LogType.DATABASE, "ERROR")
                        failed_count += 1
                        errors.append(f"第{i+1}项创建失败")
                
                except Exception as e:
                    log(f"批量导入 - 第 {i+1} 条记录处理失败: {str(e)}", LogType.DATABASE, "ERROR")
                    failed_count += 1
                    errors.append(f"第{i+1}项处理失败: {str(e)}")
                
                # 更新进度
                if task_id:
                    with self.lock:
                        if task_id in self.import_tasks:
                            self.import_tasks[task_id]['processed'] = i + 1
                            self.import_tasks[task_id]['success'] = success_count
                            self.import_tasks[task_id]['failed'] = failed_count
                            if errors:
                                self.import_tasks[task_id]['errors'] = errors[-5:]  # 只保留最后5个错误
            
            # 更新任务状态
            if task_id:
                with self.lock:
                    self.import_tasks[task_id]['status'] = 'completed'
                    self.import_tasks[task_id]['end_time'] = datetime.now()
            
            log(f"批量导入 - 任务完成，成功: {success_count}, 失败: {failed_count}", LogType.DATABASE, "INFO")
            
            return {
                'success': True,
                'message': f"成功导入 {success_count} 条资料，{failed_count} 条失败",
                'total': total_items,
                'success_count': success_count,
                'failed_count': failed_count,
                'errors': errors
            }
            
        except Exception as e:
            log(f"批量导入 - 导入过程中发生异常: {str(e)}", LogType.DATABASE, "ERROR")
            if task_id:
                with self.lock:
                    self.import_tasks[task_id]['status'] = 'failed'
                    self.import_tasks[task_id]['errors'].append(str(e))
            
            return {
                'success': False,
                'message': f"导入过程中发生错误: {str(e)}",
                'total': 0,
                'success_count': 0,
                'failed_count': 0,
                'errors': [str(e)]
            }
    
    async def _create_single_artifact(self, artifact_create: ArtifactCreate, db: Dict):
        """
        创建单个资料（复用现有的创建逻辑）
        """
        cursor = None
        try:
            from datetime import datetime as dt
            import time
            
            cursor = db["sqlite"].cursor()
            
            # 处理tags和metadata字段 - 需要转换为字符串存储
            tags_str = ','.join(artifact_create.tags) if artifact_create.tags else None
            metadata_str = json.dumps(artifact_create.metadata, ensure_ascii=False) if artifact_create.metadata else None
            
            # 插入资料
            cursor.execute("""
                INSERT INTO artifacts (title, content, category, tags, metadata, source_type, source_path, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now', 'localtime'), datetime('now', 'localtime'))
            """, (
                artifact_create.title,
                artifact_create.content,
                artifact_create.category,
                tags_str,
                metadata_str,
                artifact_create.source_type,
                artifact_create.source_path
            ))
            
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
                SELECT id, title, content, category, tags, metadata, source_type, source_path, created_at, updated_at, is_active
                FROM artifacts
                WHERE id = ?
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
                
                from app.models.schemas import ArtifactResponse
                return ArtifactResponse(
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
                from app.models.schemas import ArtifactResponse
                return ArtifactResponse(
                    id=str(artifact_id),
                    title=artifact_create.title,
                    content=artifact_create.content,
                    category=artifact_create.category or "",
                    tags=artifact_create.tags or [],
                    metadata=artifact_create.metadata or {},
                    source_type=artifact_create.source_type or "",
                    source_path=artifact_create.source_path or "",
                    created_at=dt.now(),
                    updated_at=dt.now(),
                    is_active=True
                )
                
        except Exception as e:
            # 发生错误时回滚事务
            try:
                db["sqlite"].rollback()
            except:
                pass  # 即使回滚失败也不影响错误报告
            log(f"SQLite - 创建资料失败: {str(e)}", LogType.DATABASE, "ERROR")
            raise e
        finally:
            # 确保游标被适当地处理
            try:
                if cursor:
                    cursor.close()
            except:
                pass
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        with self.lock:
            return self.import_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        with self.lock:
            if task_id in self.import_tasks:
                self.import_tasks[task_id]['status'] = 'cancelled'
                return True
            return False
    
    def cleanup_completed_tasks(self, max_age_minutes: int = 30):
        """
        清理完成超过指定时间的任务
        
        Args:
            max_age_minutes: 最大保留时间（分钟）
        """
        import time
        from datetime import timedelta
        
        current_time = datetime.now()
        with self.lock:
            task_ids_to_remove = []
            for task_id, task_info in self.import_tasks.items():
                if task_info['status'] in ['completed', 'failed', 'cancelled']:
                    end_time = task_info.get('end_time', current_time)
                    if (current_time - end_time).total_seconds() > max_age_minutes * 60:
                        task_ids_to_remove.append(task_id)
            
            for task_id in task_ids_to_remove:
                del self.import_tasks[task_id]


# 全局批量导入服务实例
batch_import_service = BatchImportService()