"""
日志管理系统
统一管理应用日志输出，支持控制台输出和文件记录

本模块提供了一个完整的日志管理系统，具有以下功能：
- 支持两种日志类型：数据库操作日志和服务器事件日志
- 支持多种日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 支持同时输出到控制台和文件
- 支持自定义日志格式和额外信息
- 提供便捷的日志记录函数

使用示例：
    from app.core.logger_manager import log, LogType
    
    # 记录服务器信息日志
    log("服务器启动成功", LogType.SERVER, "INFO")
    
    # 记录数据库操作日志
    log("SQLite - 查询用户表", LogType.DATABASE, "INFO")
    
    # 记录错误日志
    log("连接数据库失败", LogType.DATABASE, "ERROR")
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Optional


class LogType(Enum):
    """日志类型枚举
    
    用于区分不同类型的日志，对应不同的日志文件：
    - DATABASE: 数据库操作日志，输出到 Database.log 文件
    - SERVER: 服务器事件日志，输出到 Server.log 文件
    """
    DATABASE = "database"  # 数据库操作日志
    SERVER = "server"      # 服务器日志


class LoggerManager:
    """日志管理器 - 统一日志处理系统
    
    提供统一的日志管理功能，支持：
    - 多类型日志（数据库和服务器）
    - 多级别日志（DEBUG、INFO、WARNING、ERROR、CRITICAL）
    - 多输出目标（控制台和文件）
    - 自定义日志格式
    - 额外信息记录
    """
    
    def __init__(self, log_dir: str = "./logs", enable_console: bool = True):
        """初始化日志管理器
        
        Args:
            log_dir: 日志文件存储目录
            enable_console: 是否启用控制台输出
        """
        # 确保日志目录存在
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 是否启用控制台输出
        self.enable_console = enable_console
        
        # 初始化日志处理器
        self._setup_handlers()
        
        # 创建数据库日志和服务器日志的logger实例
        self._db_logger = self._create_logger(
            LogType.DATABASE.value, 
            self.log_dir / "Database.log"
        )
        self._server_logger = self._create_logger(
            LogType.SERVER.value, 
            self.log_dir / "Server.log"
        )
    
    def _setup_handlers(self):
        """设置基础日志配置
        
        配置logging模块的基础设置，确保日志系统正常工作
        """
        # 设置基础配置
        logging.basicConfig(
            level=logging.INFO,  # 基础日志级别
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
            handlers=[]  # 不添加默认处理器，由后续代码自定义
        )
    
    def _create_logger(self, name: str, log_file: Path):
        """创建日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
            
        Returns:
            logging.Logger: 配置好的日志记录器实例
        """
        # 创建logger实例
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)  # 设置日志级别
        
        # 避免重复添加处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建文件处理器 - 在Windows上使用utf-8-sig编码处理BOM
        file_handler = logging.FileHandler(log_file, encoding='utf-8-sig', mode='a')
        # 文件日志格式，包含更多详细信息
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 如果启用控制台输出，添加控制台处理器
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            # 控制台日志格式，简洁明了
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
        
        # 如果有额外信息，添加到日志消息中
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
        """记录调试级别日志
        
        Args:
            content: 日志内容
            log_type: 日志类型
            **kwargs: 额外参数
        """
        self.log(content, log_type, "DEBUG", **kwargs)
    
    def info(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """记录信息级别日志
        
        Args:
            content: 日志内容
            log_type: 日志类型
            **kwargs: 额外参数
        """
        self.log(content, log_type, "INFO", **kwargs)
    
    def warning(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """记录警告级别日志
        
        Args:
            content: 日志内容
            log_type: 日志类型
            **kwargs: 额外参数
        """
        self.log(content, log_type, "WARNING", **kwargs)
    
    def error(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """记录错误级别日志
        
        Args:
            content: 日志内容
            log_type: 日志类型
            **kwargs: 额外参数
        """
        self.log(content, log_type, "ERROR", **kwargs)
    
    def critical(self, content: str, log_type: LogType = LogType.SERVER, **kwargs):
        """记录严重错误级别日志
        
        Args:
            content: 日志内容
            log_type: 日志类型
            **kwargs: 额外参数
        """
        self.log(content, log_type, "CRITICAL", **kwargs)
    
    def log_database_operation(self, operation: str, table: str, details: str = ""):
        """记录数据库操作日志
        
        Args:
            operation: 操作类型（如SELECT、INSERT、UPDATE、DELETE）
            table: 操作的表名
            details: 操作详情
        """
        content = f"[DATABASE] Operation: {operation}, Table: {table}"
        if details:
            content += f", Details: {details}"
        self.log(content, LogType.DATABASE, "INFO")
    
    def log_server_event(self, event: str, details: str = ""):
        """记录服务器事件日志
        
        Args:
            event: 事件类型（如启动、关闭、请求）
            details: 事件详情
        """
        content = f"[SERVER] Event: {event}"
        if details:
            content += f", Details: {details}"
        self.log(content, LogType.SERVER, "INFO")


# 全局日志管理器实例
_logger_manager = None


def get_logger_manager() -> LoggerManager:
    """获取全局日志管理器实例
    
    使用单例模式，确保整个应用中只有一个日志管理器实例
    
    Returns:
        LoggerManager: 全局日志管理器实例
    """
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
    """便捷的日志记录函数
    
    提供全局访问日志系统的便捷方法
    
    Args:
        content: 日志内容
        log_type: 日志类型
        level: 日志级别
        module: 模块名
        function: 函数名
        line_number: 行号
        extra_info: 额外信息字典
    """
    manager = get_logger_manager()
    manager.log(content, log_type, level, module, function, line_number, extra_info)


def debug(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的调试日志函数
    
    Args:
        content: 日志内容
        log_type: 日志类型
        **kwargs: 额外参数
    """
    manager = get_logger_manager()
    manager.debug(content, log_type, **kwargs)


def info(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的信息日志函数
    
    Args:
        content: 日志内容
        log_type: 日志类型
        **kwargs: 额外参数
    """
    manager = get_logger_manager()
    manager.info(content, log_type, **kwargs)


def warning(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的警告日志函数
    
    Args:
        content: 日志内容
        log_type: 日志类型
        **kwargs: 额外参数
    """
    manager = get_logger_manager()
    manager.warning(content, log_type, **kwargs)


def error(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的错误日志函数
    
    Args:
        content: 日志内容
        log_type: 日志类型
        **kwargs: 额外参数
    """
    manager = get_logger_manager()
    manager.error(content, log_type, **kwargs)


def critical(content: str, log_type: LogType = LogType.SERVER, **kwargs):
    """便捷的严重错误日志函数
    
    Args:
        content: 日志内容
        log_type: 日志类型
        **kwargs: 额外参数
    """
    manager = get_logger_manager()
    manager.critical(content, log_type, **kwargs)


def log_database_operation(operation: str, table: str, details: str = ""):
    """便捷的数据库操作日志函数
    
    Args:
        operation: 操作类型
        table: 表名
        details: 详情
    """
    manager = get_logger_manager()
    manager.log_database_operation(operation, table, details)


def log_server_event(event: str, details: str = ""):
    """便捷的服务器事件日志函数
    
    Args:
        event: 事件类型
        details: 详情
    """
    manager = get_logger_manager()
    manager.log_server_event(event, details)