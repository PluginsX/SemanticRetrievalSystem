"""数据库管理API路由"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.api.dependencies import DatabaseDep
from app.core.database import db_manager
from app.core.logger_manager import log, LogType

router = APIRouter(prefix="/api/v1", tags=["数据库管理"])


# SQLite数据库管理接口
@router.get("/sqlite/tables")
async def get_sqlite_tables(
    db: DatabaseDep
):
    """获取SQLite所有用户表"""
    try:
        cursor = db["sqlite"].cursor()
        
        # 获取所有表，过滤掉SQLite默认自带的表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%' 
            ORDER BY name
        """)
        
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            # 获取表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            tables.append({
                "name": table_name,
                "count": count
            })
        
        return {
            "data": {
                "tables": tables
            }
        }
        
    except Exception as e:
        log(f"SQLite - 获取表列表失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取表列表失败: {str(e)}")


@router.get("/sqlite/tables/{table_name}")
async def get_sqlite_table_data(
    table_name: str,
    db: DatabaseDep,
    page: int = 1,
    size: int = 20
):
    """获取SQLite表数据"""
    try:
        # 验证表名 - 只允许访问真实存在的用户表
        cursor = db["sqlite"].cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name = ?
            AND name NOT LIKE 'sqlite_%'
        """, (table_name,))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="无效的表名")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        columns = []
        for col in columns_info:
            columns.append({
                "prop": col[1],
                "label": col[1],
                "type": col[2]
            })
        
        # 计算偏移量
        offset = (page - 1) * size
        
        # 获取数据
        if table_name == "artifacts":
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT ? OFFSET ?", (size, offset))
        else:
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT ? OFFSET ?", (size, offset))
        
        rows = cursor.fetchall()
        
        # 转换为字典列表
        records = []
        for row in rows:
            record = {}
            for i, col in enumerate(columns):
                record[col["prop"]] = row[i]
            records.append(record)
        
        # 获取总数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        
        return {
            "data": {
                "records": records,
                "columns": columns,
                "total": total,
                "page": page,
                "size": size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"SQLite - 获取表数据失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取表数据失败: {str(e)}")


@router.post("/sqlite/tables/{table_name}")
async def create_sqlite_record(
    table_name: str,
    data: Dict[str, Any],
    db: DatabaseDep
):
    """创建SQLite记录"""
    try:
        # 验证表名
        valid_tables = ["artifacts", "chunks", "search_history", "api_access_logs"]
        if table_name not in valid_tables:
            raise HTTPException(status_code=400, detail="无效的表名")
        
        cursor = db["sqlite"].cursor()
        
        # 为资料表添加默认值
        if table_name == "artifacts":
            # 为资料表添加默认值
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in data:
                data["updated_at"] = datetime.now().isoformat()
            if "is_active" not in data:
                data["is_active"] = 1
        
        # 构建插入语句
        columns = list(data.keys())
        placeholders = ["?"] * len(columns)
        columns_str = ", ".join(columns)
        placeholders_str = ", ".join(placeholders)
        values = list(data.values())
        
        cursor.execute(
            f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders_str})",
            values
        )
        
        db["sqlite"].commit()
        
        # 获取插入的ID
        record_id = cursor.lastrowid
        
        log(f"SQLite - 创建记录成功，表: {table_name}, ID: {record_id}", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "创建记录成功",
            "record_id": record_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"SQLite - 创建记录失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"创建记录失败: {str(e)}")


@router.put("/sqlite/tables/{table_name}/{record_id}")
async def update_sqlite_record(
    table_name: str,
    record_id: int,
    data: Dict[str, Any],
    db: DatabaseDep
):
    """更新SQLite记录"""
    try:
        # 验证表名
        valid_tables = ["artifacts", "chunks", "search_history", "api_access_logs"]
        if table_name not in valid_tables:
            raise HTTPException(status_code=400, detail="无效的表名")
        
        cursor = db["sqlite"].cursor()
        
        # 构建更新语句
        set_clauses = []
        values = []
        
        for key, value in data.items():
            if key != "id":  # 不允许更新ID
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            raise HTTPException(status_code=400, detail="没有要更新的字段")
        
        # 为资料表更新updated_at
        if table_name == "artifacts":
            set_clauses.append("updated_at = ?")
            values.append(datetime.now().isoformat())
        
        values.append(record_id)
        set_clauses_str = ", ".join(set_clauses)
        
        cursor.execute(
            f"UPDATE {table_name} SET {set_clauses_str} WHERE id = ?",
            values
        )
        
        db["sqlite"].commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        log(f"SQLite - 更新记录成功，表: {table_name}, ID: {record_id}", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "更新记录成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"SQLite - 更新记录失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"更新记录失败: {str(e)}")


@router.delete("/sqlite/tables/{table_name}/{record_id}")
async def delete_sqlite_record(
    table_name: str,
    record_id: int,
    db: DatabaseDep
):
    """删除SQLite记录"""
    try:
        # 验证表名
        valid_tables = ["artifacts", "chunks", "search_history", "api_access_logs"]
        if table_name not in valid_tables:
            raise HTTPException(status_code=400, detail="无效的表名")
        
        cursor = db["sqlite"].cursor()
        
        # 执行删除
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
        
        db["sqlite"].commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        log(f"SQLite - 删除记录成功，表: {table_name}, ID: {record_id}", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "删除记录成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"SQLite - 删除记录失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"删除记录失败: {str(e)}")


@router.post("/sqlite/init")
async def init_sqlite_database():
    """初始化SQLite数据库"""
    try:
        # 重新初始化SQLite数据库
        db_manager.init_sqlite()
        
        log("SQLite - 数据库初始化成功", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "数据库初始化成功"
        }
        
    except Exception as e:
        log(f"SQLite - 数据库初始化失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")


# ChromaDB数据库管理接口
@router.get("/chromadb/documents")
async def get_chromadb_documents(
    db: DatabaseDep,
    page: int = 1,
    size: int = 20
):
    """获取ChromaDB文档列表"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        # 获取所有文档，包括documents字段
        result = db["collection"].get(include=["embeddings", "documents", "metadatas"])
        
        if not result or "ids" not in result:
            log(f"ChromaDB - 结果为空或缺少ids字段", LogType.DATABASE, "INFO")
            return {
                "data": {
                    "records": [],
                    "total": 0,
                    "page": page,
                    "size": size
                }
            }
        
        # 确保所有字段都是列表，避免NoneType错误
        ids_list = result.get("ids", []) or []
        documents_list = result.get("documents", []) or []
        metadatas_list = result.get("metadatas", []) or []
        embeddings_list = result.get("embeddings", []) or []
        
        log(f"ChromaDB - ids数量: {len(ids_list)}, documents数量: {len(documents_list)}, metadatas数量: {len(metadatas_list)}, embeddings数量: {len(embeddings_list)}", LogType.DATABASE, "INFO")
        
        # 构建文档列表（只使用ChromaDB中的数据，不依赖SQLite）
        documents = []
        
        for i, (doc_id, document, metadata) in enumerate(zip(ids_list, documents_list, metadatas_list)):
            # 只返回是否有向量的布尔值，不返回完整的向量数据
            has_embedding = i < len(embeddings_list) and embeddings_list[i] is not None
            
            # 直接使用ChromaDB中的数据，包括documents字段
            documents.append({
                "id": doc_id,
                "document": document or "",
                "metadata": metadata or {},
                "has_embedding": has_embedding
            })
        
        # 分页
        total = len(documents)
        start = (page - 1) * size
        end = start + size
        paginated_docs = documents[start:end]
        
        return {
            "data": {
                "records": paginated_docs,
                "total": total,
                "page": page,
                "size": size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 获取文档列表失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.get("/chromadb/documents/{document_id}")
async def get_chromadb_document(
    document_id: str,
    db: DatabaseDep
):
    """获取单个ChromaDB文档的完整信息，包括向量数据"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        # 获取单个文档，包括完整的向量数据
        result = db["collection"].get(
            ids=[document_id],
            include=["embeddings", "documents", "metadatas"]
        )
        
        if not result or not result.get("ids"):
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 构建返回数据
        doc = {
            "id": result["ids"][0],
            "document": result.get("documents", [""])[0] or "",
            "embedding": result.get("embeddings", [None])[0],
            "metadata": result.get("metadatas", [{}])[0] or {}
        }
        
        log(f"ChromaDB - 获取文档成功，ID: {document_id}", LogType.DATABASE, "INFO")
        
        return {
            "data": doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 获取文档失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")


@router.post("/chromadb/documents/search")
async def search_chromadb_documents(
    data: Dict[str, Any],
    db: DatabaseDep
):
    """搜索ChromaDB文档"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        query = data.get("query")
        top_k = data.get("top_k", 10)
        threshold = data.get("threshold", 0.0)
        
        if not query:
            raise HTTPException(status_code=400, detail="搜索查询不能为空")
        
        # 使用外部Embedding API生成查询向量
        from app.services.ai_clients import embedding_client
        
        log("开始执行ChromaDB向量搜索", LogType.DATABASE, "INFO")
        
        # 生成查询向量
        query_embedding = await embedding_client.embed(query)
        log(f"生成查询向量成功，维度: {len(query_embedding)}", LogType.DATABASE, "INFO")
        
        # 执行向量搜索（不获取documents，从SQLite查询）
        result = db["collection"].query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["distances", "metadatas"]
        )
        
        # 获取匹配的artifact_id列表
        artifact_ids = []
        for metadata in result.get("metadatas", [[]])[0]:
            artifact_id = metadata.get('artifact_id') if metadata else None
            if artifact_id:
                artifact_ids.append(int(artifact_id))
        
        # 批量查询SQLite获取完整的资料信息
        cursor = db["sqlite"].cursor()
        sqlite_results = {}
        if artifact_ids:
            placeholders = ','.join(['?' for _ in artifact_ids])
            cursor.execute(f"""
                SELECT id, title, content, category, created_at, updated_at, is_active
                FROM artifacts
                WHERE id IN ({placeholders}) AND is_active = 1
            """, artifact_ids)
            sqlite_results = {row[0]: row for row in cursor.fetchall()}
        
        # 构建搜索结果
        documents = []
        for i, (doc_id, metadata, distance) in enumerate(zip(
            result.get("ids", [[]])[0],
            result.get("metadatas", [[]])[0],
            result.get("distances", [[]])[0]
        )):
            # 计算相似度（距离越小，相似度越高）
            similarity = 1.0 / (1.0 + distance)
            
            # 只添加相似度大于等于阈值的结果
            if similarity >= threshold:
                # 从SQLite获取完整的资料信息
                sqlite_row = sqlite_results.get(int(doc_id)) if doc_id.isdigit() else None
                
                if sqlite_row:
                    documents.append({
                        "id": doc_id,
                        "document": f"{sqlite_row[1]}\n\n{sqlite_row[2]}",  # 从SQLite组合title和content
                        "metadata": metadata or {},
                        "similarity": similarity,
                        "distance": distance
                    })
                else:
                    # 如果SQLite中没有对应记录，只返回基本信息
                    documents.append({
                        "id": doc_id,
                        "document": "",
                        "metadata": metadata or {},
                        "similarity": similarity,
                        "distance": distance
                    })
        
        return {
            "data": {
                "records": documents,
                "total": len(documents)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 搜索文档失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"搜索文档失败: {str(e)}")


@router.get("/chromadb/documents/{document_id}/exists")
async def check_document_id_exists(
    document_id: str,
    db: DatabaseDep
):
    """检查ChromaDB文档ID是否存在"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        # 获取所有文档ID
        result = db["collection"].get(include=["documents"])
        if not result or "ids" not in result:
            return {
                "exists": False
            }
        
        # 检查ID是否存在
        exists = document_id in result["ids"]
        
        return {
            "exists": exists
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 检查文档ID失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"检查文档ID失败: {str(e)}")


@router.post("/chromadb/documents")
async def create_chromadb_document(
    data: Dict[str, Any],
    db: DatabaseDep
):
    """创建ChromaDB文档"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        document = data.get("document")
        
        # 使用前端传递的ID或生成新ID
        doc_id = data.get("id", f"doc_{int(datetime.now().timestamp() * 1000)}")
        
        # 检查ID是否已存在
        result = db["collection"].get()
        if result and "ids" in result and doc_id in result["ids"]:
            raise HTTPException(status_code=400, detail="文档ID已存在")
        
        # 检查是否提供了embedding
        embedding = data.get("embedding")
        
        # 如果没有提供embedding但提供了document，使用外部Embedding API生成
        if embedding is None and document:
            from app.services.ai_clients import embedding_client
            log(f"ChromaDB - 开始为文档生成向量，ID: {doc_id}", LogType.DATABASE, "INFO")
            embedding = await embedding_client.embed(document)
            log(f"ChromaDB - 生成向量成功，维度: {len(embedding)}", LogType.DATABASE, "INFO")
        
        # 如果既没有提供embedding也没有提供document，抛出错误
        if embedding is None and not document:
            raise HTTPException(status_code=400, detail="Embeddings和Documents至少填写一个")
        
        # 添加文档
        # ChromaDB的metadatas参数是可选的，如果metadata为空则不传递
        metadata = data.get("metadata")
        
        add_params = {
            "ids": [doc_id],
            "embeddings": [embedding]
        }
        
        # 只有在document非空时才添加documents参数
        if document:
            add_params["documents"] = [document]
        
        # 只有在metadata非空时才添加metadatas参数
        if metadata:
            add_params["metadatas"] = [metadata]
        
        log(f"ChromaDB - 添加文档参数: ids={add_params['ids']}, embeddings维度={len(add_params['embeddings'][0]) if add_params['embeddings'] else 0}, metadatas={'metadatas' in add_params}", LogType.DATABASE, "INFO")
        
        db["collection"].add(**add_params)
        
        log(f"ChromaDB - 创建文档成功，ID: {doc_id}", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "创建文档成功",
            "document_id": doc_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 创建文档失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"创建文档失败: {str(e)}")


@router.put("/chromadb/documents/{document_id}")
async def update_chromadb_document(
    document_id: str,
    data: Dict[str, Any],
    db: DatabaseDep
):
    """更新ChromaDB文档"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        document = data.get("document")
        
        # 检查是否提供了embedding
        embedding = data.get("embedding")
        
        # 如果既没有提供embedding也没有提供document，抛出错误
        if embedding is None and document is None:
            raise HTTPException(status_code=400, detail="Embeddings和Documents至少填写一个")
        
        # 准备更新参数
        update_params = {
            "ids": [document_id]
        }
        
        # 如果提供了embedding，更新embedding
        if embedding is not None:
            update_params["embeddings"] = [embedding]
        
        # 如果提供了document，更新document
        if document is not None:
            update_params["documents"] = [document]
        
        # 处理metadata
        metadata = data.get("metadata")
        if metadata is not None:
            update_params["metadatas"] = [metadata]
        
        # 执行更新
        db["collection"].update(**update_params)
        
        log(f"ChromaDB - 更新文档成功，ID: {document_id}", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "更新文档成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 更新文档失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"更新文档失败: {str(e)}")


@router.delete("/chromadb/documents/{document_id}")
async def delete_chromadb_document(
    document_id: str,
    db: DatabaseDep
):
    """删除ChromaDB文档"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        # 删除文档
        db["collection"].delete(
            ids=[document_id]
        )
        
        log(f"ChromaDB - 删除文档成功，ID: {document_id}", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "删除文档成功"
        }
        
    except Exception as e:
        log(f"ChromaDB - 删除文档失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.post("/chromadb/init")
async def init_chromadb_database():
    """初始化ChromaDB数据库"""
    try:
        # 重新初始化ChromaDB
        result = db_manager.init_chroma()
        
        if result is None:
            raise HTTPException(status_code=400, detail="ChromaDB初始化失败")
        
        log("ChromaDB - 数据库初始化成功", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "数据库初始化成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 数据库初始化失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")


@router.get("/chromadb/info")
async def get_chromadb_info(
    db: DatabaseDep
):
    """获取ChromaDB集合信息"""
    try:
        if not db["collection"]:
            raise HTTPException(status_code=400, detail="ChromaDB集合未初始化")
        
        # 获取集合信息
        collection_info = {
            "name": "artifact_embeddings",
            "count": 0,
            "dimension": 1024  # 默认向量维度
        }
        
        # 获取文档数量（不获取embeddings，避免输出大量向量数据）
        result = db["collection"].get(include=["documents"])
        if result and "documents" in result:
            collection_info["count"] = len(result["documents"])
        
        return {
            "data": collection_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 获取集合信息失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取集合信息失败: {str(e)}")


@router.get("/chromadb/collections")
async def get_chromadb_collections(
    db: DatabaseDep
):
    """获取ChromaDB所有集合"""
    try:
        if not db["chroma"]:
            raise HTTPException(status_code=400, detail="ChromaDB客户端未初始化")
        
        # 获取所有集合
        collections = db["chroma"].list_collections()
        
        # 构建集合列表
        collection_list = []
        for collection in collections:
            # 获取集合文档数量（不获取embeddings，避免输出大量向量数据）
            try:
                result = collection.get(include=["documents"])
                count = len(result["documents"]) if result and "documents" in result else 0
            except:
                count = 0
            
            collection_list.append({
                "name": collection.name,
                "count": count
            })
        
        return {
            "data": {
                "collections": collection_list
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 获取集合列表失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")


@router.post("/chromadb/collections/recreate")
async def recreate_chromadb_collection(
    db: DatabaseDep
):
    """删除并重新创建ChromaDB集合"""
    try:
        if not db["chroma"]:
            raise HTTPException(status_code=400, detail="ChromaDB客户端未初始化")
        
        # 删除现有集合
        log("ChromaDB - 开始删除现有集合", LogType.DATABASE, "INFO")
        try:
            db["chroma"].delete_collection(name="artifact_embeddings")
            log("ChromaDB - 删除集合成功", LogType.DATABASE, "INFO")
        except Exception as e:
            log(f"ChromaDB - 删除集合失败（可能不存在）: {e}", LogType.DATABASE, "WARNING")
        
        # 重新创建集合，使用预计算的向量
        log("ChromaDB - 开始创建新集合", LogType.DATABASE, "INFO")
        new_collection = db["chroma"].create_collection(
            name="artifact_embeddings",
            metadata={
                "description": "语义检索系统资料向量存储",
                "use_precomputed_embeddings": "true"
            },
            embedding_function=None
        )
        
        # 更新数据库管理器中的集合引用
        db["collection"] = new_collection
        db_manager.collection = new_collection
        
        log("ChromaDB - 创建集合成功", LogType.DATABASE, "INFO")
        
        return {
            "success": True,
            "message": "集合重新创建成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log(f"ChromaDB - 重新创建集合失败: {e}", LogType.DATABASE, "ERROR")
        raise HTTPException(status_code=500, detail=f"重新创建集合失败: {str(e)}")
