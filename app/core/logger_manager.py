"""
日志管理系统
统一管理应用日志输出，支持控制台输出和文件记录
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Optional


class LogType(Enum):
    """日志类型枚举"""
    DATABASE = "database"  # 数据库操作日志
    SERVER = "server"      # 服务器日志


class LoggerManager:
    """日志管理器 - 统一日志处理系统"""
    
    def __init__(self, log_dir: str = "./logs", enable_console: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_console = enable_console
        
        # 初始化日志处理器
        self._setup_handlers()
        
        # 创建日志文件
        self._db_logger = self._create_logger(LogType.DATABASE.value, 
                                              self.log_dir / "Database.log")
        self._server_logger = self._create_logger(LogType.SERVER.value, 
                                                 self.log_dir / "Server.log")
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 设置基础配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[]
        )
    
    def _create_logger(self, name: str, log_file: Path):
        """创建日志记录器"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建文件处理器 - 在Windows上使用utf-8-sig编码处理BOM
        file_handler = logging.FileHandler(log_file, encoding='utf-8-sig', mode='a')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 如果启用控制台输出，添加控制台处理器
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log(self, 
            content: str, 
            log_type: LogType = LogType.SERVER,
            level: str = "INFO",
            module: Optional[str] = None,
            function: Optional[str] = None,
            line_number: Optional[int] = None,
            extra_info: Optional[dict] = None):
        """
        统一日志记录方法
        
        Args:
            content: 日志内容
            log_type: 日志类型 (DATABASE 或 SERVER)
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            module: 模块名
            function: 函数名
            line_number: 行号
            extra_info: 额外信息字典
        """
        # 根据日志类型选择对应的logger
        logger = self._db_logger if log_type == LogType.DATABASE else self._server_logger
        
        # 准备日志消息
        log_msg = content
        if extra_info:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra_info.items()])
            log_msg = f"{content} [{extra_str}]"
        
        # 根据日志级别记录
        level_upper = level.upper()
        if level_upper == "DEBUG":
            logger.debug(log_msg)
        elif level_upper == "WARNING":
            logger.warning(log_msg)
        elif level_upper == "ERROR":
            logger.error(log_msg)
        elif level_upper == "CRITICAL":
            logger.critical(log_msg)
        else:  # 默认INFO
            logger.info(log_msg)
    
    def debug(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """调试日志"""
        self.log(content, log_type, "DEBUG", **kwargs)
    
    def info(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """信息日志"""
        self.log(content, log_type, "INFO", **kwargs)
    
    def warning(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """警告日志"""
        self.log(content, log_type, "WARNING", **kwargs)
    
    def error(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """错误日志"""
        self.log(content, log_type, "ERROR", **kwargs)
    
    def critical(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """严重错误日志"""
        self.log(content, log_type, "CRITICAL", **kwargs)
    
    def log_database_operation(self, operation: str, table: str, details: str = ""):
        """记录数据库操作日志"""
        content = f"[DATABASE] Operation: {operation}, Table: {table}"
        if details:
            content += f", Details: {details}"
        self.log(content, LogType.DATABASE, "INFO")
    
    def log_server_event(self, event: str, details: str = ""):
        """记录服务器事件日志"""
        content = f"[SERVER] Event: {event}"
        if details:
            content += f", Details: {details}"
        self.log(content, LogType.SERVER, "INFO")


# 全局日志管理器实例
_logger_manager = None


def get_logger_manager() -> LoggerManager:
    """获取全局日志管理器实例"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def log(content: str, 
        log_type: LogType = LogType.SERVER,
        level: str = "INFO",
        module: Optional[str] = None,
        function: Optional[str] = None,
        line_number: Optional[int] = None,
        extra_info: Optional[dict] = None):
    """便捷的日志记录函数"""
    manager = get_logger_manager()
    manager.log(content, log_type, level, module, function, line_number, extra_info)


def debug(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的调试日志函数"""
    manager = get_logger_manager()
    manager.debug(content, log_type, **kwargs)


def info(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的信息日志函数"""
    manager = get_logger_manager()
    manager.info(content, log_type, **kwargs)


def warning(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的警告日志函数"""
    manager = get_logger_manager()
    manager.warning(content, log_type, **kwargs)


def error(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的错误日志函数"""
    manager = get_logger_manager()
    manager.error(content, log_type, **kwargs)


def critical(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的严重错误日志函数"""
    manager = get_logger_manager()
    manager.critical(content, log_type, **kwargs)


def log_database_operation(operation: str, table: str, details: str = ""):
    """便捷的数据库操作日志函数"""
    manager = get_logger_manager()
    manager.log_database_operation(operation, table, details)


def log_server_event(event: str, details: str = ""):
    """便捷的服务器事件日志函数"""
    manager = get_logger_manager()
    manager.log_server_event(event, details)