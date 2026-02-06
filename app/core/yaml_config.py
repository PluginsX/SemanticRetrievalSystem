"""
增强型配置管理器
实现运行时对象与外部文件的双向同步
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from copy import deepcopy


class ConfigManager:
    """配置管理器 - 实现运行时对象与外部文件的双向同步"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or "./config")
        self.current_env = os.getenv("APP_ENV", "development")
        self._config_data = {}
        self._original_config = {}
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载初始配置
        self._load_all_configs()
        
        # 保存原始配置副本用于比较
        self._original_config = deepcopy(self._config_data)
        
        # 配置变化监听器
        self._change_listeners = []
    
    def _load_all_configs(self):
        """加载所有配置文件"""
        # 加载默认配置文件 - 包含所有配置项的默认值
        default_config = self._load_config_file("default_config.yaml")
        self._config_data = default_config or {}
        
        # 加载环境特定配置并合并
        env_config = self._load_config_file(f"{self.current_env}.yaml")
        if env_config:
            self._deep_merge(self._config_data, env_config)
        
        # 加载当前配置并合并（最高优先级）
        current_config = self._load_config_file("current_config.yaml")
        if current_config:
            self._deep_merge(self._config_data, current_config)
    
    def _load_config_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """加载单个配置文件"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            # 只有当文件名不是current_config.yaml时才记录警告
            if filename != "current_config.yaml":
                logging.warning(f"配置文件不存在: {config_path}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logging.info(f"成功加载配置文件: {config_path}")
                return config
        except Exception as e:
            logging.error(f"加载配置文件失败 {config_path}: {e}")
            return None
    
    def _deep_merge(self, target: dict, source: dict):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get_config(self, section: str = None, key: str = None, default=None):
        """获取配置值"""
        if section is None:
            return self._config_data
        
        if section in self._config_data:
            section_config = self._config_data[section]
            if key is not None:
                return section_config.get(key, default)
            return section_config
        
        return default
    
    def set_config(self, value, section: str = None, key: str = None):
        """设置配置值 - 这将触发自动同步到文件"""
        if section is None:
            # 设置整个配置数据
            old_value = deepcopy(self._config_data)
            self._config_data = value
            self._on_config_changed("root", old_value, value)
        elif key is None:
            # 设置整个section
            old_value = deepcopy(self._config_data.get(section))
            if section not in self._config_data:
                self._config_data[section] = {}
            self._config_data[section] = value
            self._on_config_changed(f"section:{section}", old_value, value)
        else:
            # 设置特定的key
            if section not in self._config_data:
                self._config_data[section] = {}
            old_value = self._config_data[section].get(key)
            self._config_data[section][key] = value
            self._on_config_changed(f"{section}.{key}", old_value, value)
    
    def update_config(self, updates: Dict[str, Any]):
        """批量更新配置"""
        old_config = deepcopy(self._config_data)
        self._deep_merge(self._config_data, updates)
        self._on_config_changed("bulk_update", old_config, self._config_data)
    
    def _on_config_changed(self, key_path: str, old_value, new_value):
        """配置变化回调"""
        # 自动保存到文件
        self._save_current_config()
        
        # 通知监听器
        for listener in self._change_listeners:
            try:
                listener(key_path, old_value, new_value)
            except Exception as e:
                logging.error(f"配置变化监听器执行失败: {e}")
    
    def _save_current_config(self):
        """保存当前配置到current_config.yaml文件"""
        try:
            # 创建备份
            config_path = self.config_dir / "current_config.yaml"
            if config_path.exists():
                backup_path = config_path.with_suffix('.yaml.bak')
                if backup_path.exists():
                    backup_path.unlink()
                config_path.rename(backup_path)
                logging.info(f"创建配置备份: {backup_path}")
            
            # 保存新配置 - 只保存与默认和环境配置不同的部分
            current_config = self._extract_current_config()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(current_config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logging.info(f"配置已保存到: {config_path}")
            self._original_config = deepcopy(self._config_data)
            
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
    
    def _extract_current_config(self) -> Dict[str, Any]:
        """提取当前配置中与默认配置不同的部分"""
        # 这里简化处理，直接返回当前配置
        # 在实际应用中，可以实现更复杂的差异检测
        return deepcopy(self._config_data)
    
    def reload_config(self):
        """重新加载配置"""
        logging.info("重新加载配置...")
        old_config = deepcopy(self._config_data)
        self._load_all_configs()
        self._original_config = deepcopy(self._config_data)
        logging.info("配置重新加载完成")
        
        # 通知监听器配置已重载
        for listener in self._change_listeners:
            try:
                listener("reload", old_config, self._config_data)
            except Exception as e:
                logging.error(f"配置重载监听器执行失败: {e}")
    
    def add_change_listener(self, callback):
        """添加配置变化监听器"""
        self._change_listeners.append(callback)
    
    def remove_change_listener(self, callback):
        """移除配置变化监听器"""
        if callback in self._change_listeners:
            self._change_listeners.remove(callback)


# 全局配置管理器实例
_config_manager_instance = None


def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance


# 便捷函数
def get_config(section: str = None, key: str = None, default=None):
    """获取配置的便捷函数"""
    return get_config_manager().get_config(section, key, default)


def set_config(value, section: str = None, key: str = None):
    """设置配置的便捷函数"""
    get_config_manager().set_config(value, section, key)


def update_config(updates: Dict[str, Any]):
    """批量更新配置的便捷函数"""
    get_config_manager().update_config(updates)