"""表配置管理模块"""
from typing import Dict, Optional
import yaml
import os


class TableConfigManager:
    """表配置管理器"""
    
    def __init__(self, config_file=None):
        """初始化表配置管理器"""
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), 
            '../../config', 
            'table_config.yaml'
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件
        
        Returns:
            Dict: 表配置信息
        """
        default_config = {
            'tables': {
                'artifacts': {
                    'sort_field': 'created_at',
                    'order': 'DESC',
                    'default_fields': ['created_at', 'updated_at', 'is_active'],
                    'business_logic': ['vector_sync']
                },
                'search_history': {
                    'sort_field': 'created_at',
                    'order': 'DESC',
                    'read_only': False
                },
                'api_access_logs': {
                    'sort_field': 'created_at',
                    'order': 'DESC',
                    'read_only': True
                },
                'chunks': {
                    'sort_field': 'id',
                    'order': 'ASC',
                    'read_only': False
                }
            }
        }
        
        if not os.path.exists(self.config_file):
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config and isinstance(config, dict):
                    return config
                return default_config
        except Exception:
            return default_config
    
    def _save_config(self, config: Dict):
        """保存配置文件
        
        Args:
            config: 配置信息
        """
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception:
            pass
    
    def get_table_config(self, table_name: str) -> Dict:
        """获取表配置
        
        Args:
            table_name: 表名
            
        Returns:
            Dict: 表配置信息
        """
        return self.config.get('tables', {}).get(table_name, {})
    
    def get_all_tables(self) -> list:
        """获取所有配置的表
        
        Returns:
            list: 表名列表
        """
        return list(self.config.get('tables', {}).keys())
    
    def update_table_config(self, table_name: str, new_config: Dict):
        """更新表配置
        
        Args:
            table_name: 表名
            new_config: 新配置
        """
        if 'tables' not in self.config:
            self.config['tables'] = {}
        
        # 合并配置
        current_config = self.config['tables'].get(table_name, {})
        current_config.update(new_config)
        self.config['tables'][table_name] = current_config
        
        self._save_config(self.config)
    
    def add_table_config(self, table_name: str, config: Dict):
        """添加表配置
        
        Args:
            table_name: 表名
            config: 表配置
        """
        if 'tables' not in self.config:
            self.config['tables'] = {}
        
        self.config['tables'][table_name] = config
        self._save_config(self.config)
    
    def remove_table_config(self, table_name: str):
        """移除表配置
        
        Args:
            table_name: 表名
        """
        if 'tables' in self.config and table_name in self.config['tables']:
            del self.config['tables'][table_name]
            self._save_config(self.config)


# 全局配置管理器实例
table_config_manager = TableConfigManager()


def get_table_config_manager() -> TableConfigManager:
    """获取表配置管理器实例
    
    Returns:
        TableConfigManager: 表配置管理器实例
    """
    return table_config_manager


def get_table_config(table_name: str) -> Dict:
    """获取表配置
    
    Args:
        table_name: 表名
        
    Returns:
        Dict: 表配置信息
    """
    return table_config_manager.get_table_config(table_name)


def get_all_table_configs() -> Dict:
    """获取所有表配置
    
    Returns:
        Dict: 所有表配置
    """
    return table_config_manager.config.get('tables', {})
