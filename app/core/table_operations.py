"""数据操作抽象层"""
from typing import Dict, List, Optional, Any
import sqlite3


class TableOperationService:
    """表操作服务类"""
    
    def __init__(self, db, table_config=None):
        """初始化表操作服务"""
        self.db = db
        self.table_config = table_config or {}
    
    def is_valid_user_table(self, table_name: str) -> bool:
        """验证表是否为有效用户表
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 是否为有效用户表
        """
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name = ?
                AND name NOT LIKE 'sqlite_%'
                AND name NOT LIKE '_internal_%'
            """, (table_name,))
            return cursor.fetchone() is not None
        except Exception:
            return False
    
    def get_table_schema(self, table_name: str) -> Optional[List[Dict]]:
        """获取表结构
        
        Args:
            table_name: 表名
            
        Returns:
            Optional[List[Dict]]: 表结构信息
        """
        if not self.is_valid_user_table(table_name):
            return None
        
        try:
            cursor = self.db.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = []
            for row in cursor.fetchall():
                schema.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'dflt_value': row[4],
                    'pk': row[5]
                })
            return schema
        except Exception:
            return None
    
    def get_primary_key(self, table_name: str) -> Optional[str]:
        """获取表的主键
        
        Args:
            table_name: 表名
            
        Returns:
            Optional[str]: 主键字段名
        """
        schema = self.get_table_schema(table_name)
        if not schema:
            return None
        
        for field in schema:
            if field['pk']:
                return field['name']
        
        return None
    
    def get_table_data(self, table_name: str, page: int = 1, size: int = 20, filters=None) -> Dict:
        """获取表数据
        
        Args:
            table_name: 表名
            page: 页码
            size: 每页大小
            filters: 过滤条件
            
        Returns:
            Dict: 包含数据和分页信息的字典
        """
        if not self.is_valid_user_table(table_name):
            return {
                'success': False,
                'message': '无效的表名',
                'data': [],
                'total': 0,
                'page': page,
                'size': size
            }
        
        try:
            cursor = self.db.cursor()
            
            # 计算偏移量
            offset = (page - 1) * size
            
            # 获取表配置
            table_config = self.table_config.get(table_name, {})
            sort_field = table_config.get('sort_field', 'id')
            sort_order = table_config.get('order', 'DESC')
            
            # 构建查询条件
            where_clause = ''
            params = []
            
            if filters:
                conditions = []
                for field, value in filters.items():
                    if value is not None:
                        conditions.append(f"{field} = ?")
                        params.append(value)
                if conditions:
                    where_clause = " WHERE " + " AND ".join(conditions)
            
            # 计算总记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}{where_clause}", params)
            total = cursor.fetchone()[0]
            
            # 获取数据
            query = f"""
                SELECT * FROM {table_name}
                {where_clause}
                ORDER BY {sort_field} {sort_order}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [size, offset])
            data = cursor.fetchall()
            
            # 转换为字典格式
            schema = self.get_table_schema(table_name)
            if not schema:
                return {
                    'success': False,
                    'message': '无法获取表结构',
                    'data': [],
                    'total': 0,
                    'page': page,
                    'size': size
                }
            
            field_names = [field['name'] for field in schema]
            formatted_data = []
            for row in data:
                row_dict = {}
                for i, field_name in enumerate(field_names):
                    row_dict[field_name] = row[i]
                formatted_data.append(row_dict)
            
            return {
                'success': True,
                'message': '获取数据成功',
                'data': formatted_data,
                'total': total,
                'page': page,
                'size': size
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取数据失败: {str(e)}',
                'data': [],
                'total': 0,
                'page': page,
                'size': size
            }
    
    def create_record(self, table_name: str, data: Dict[str, Any]) -> Dict:
        """创建记录
        
        Args:
            table_name: 表名
            data: 记录数据
            
        Returns:
            Dict: 操作结果
        """
        if not self.is_valid_user_table(table_name):
            return {
                'success': False,
                'message': '无效的表名',
                'record_id': None
            }
        
        try:
            cursor = self.db.cursor()
            
            # 构建字段名和值
            fields = list(data.keys())
            values = list(data.values())
            placeholders = ','.join(['?'] * len(values))
            
            # 执行插入
            query = f"""
                INSERT INTO {table_name} ({','.join(fields)})
                VALUES ({placeholders})
            """
            cursor.execute(query, values)
            self.db.commit()
            
            return {
                'success': True,
                'message': '创建记录成功',
                'record_id': cursor.lastrowid
            }
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f'创建记录失败: {str(e)}',
                'record_id': None
            }
    
    def update_record(self, table_name: str, record_id: int, data: Dict[str, Any]) -> Dict:
        """更新记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            data: 更新数据
            
        Returns:
            Dict: 操作结果
        """
        if not self.is_valid_user_table(table_name):
            return {
                'success': False,
                'message': '无效的表名'
            }
        
        try:
            cursor = self.db.cursor()
            primary_key = self.get_primary_key(table_name)
            
            if not primary_key:
                return {
                    'success': False,
                    'message': '无法确定表的主键'
                }
            
            # 构建更新语句
            set_clause = ','.join([f"{field} = ?" for field in data.keys()])
            values = list(data.values()) + [record_id]
            
            query = f"""
                UPDATE {table_name}
                SET {set_clause}
                WHERE {primary_key} = ?
            """
            cursor.execute(query, values)
            self.db.commit()
            
            if cursor.rowcount == 0:
                return {
                    'success': False,
                    'message': '记录不存在'
                }
            
            return {
                'success': True,
                'message': '更新记录成功'
            }
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f'更新记录失败: {str(e)}'
            }
    
    def delete_record(self, table_name: str, record_id: int) -> Dict:
        """删除记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            
        Returns:
            Dict: 操作结果
        """
        if not self.is_valid_user_table(table_name):
            return {
                'success': False,
                'message': '无效的表名'
            }
        
        try:
            cursor = self.db.cursor()
            primary_key = self.get_primary_key(table_name)
            
            if not primary_key:
                return {
                    'success': False,
                    'message': '无法确定表的主键'
                }
            
            query = f"DELETE FROM {table_name} WHERE {primary_key} = ?"
            cursor.execute(query, [record_id])
            self.db.commit()
            
            if cursor.rowcount == 0:
                return {
                    'success': False,
                    'message': '记录不存在'
                }
            
            return {
                'success': True,
                'message': '删除记录成功'
            }
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f'删除记录失败: {str(e)}'
            }
