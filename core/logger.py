"""
统一日志系统模块
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class LoggerManager:
    """日志管理器"""

    _loggers = {}
    _initialized = False

    @classmethod
    def setup(
        cls, log_level: str = "INFO", log_file: Optional[str] = None, log_to_console: bool = True
    ):
        """
        设置全局日志配置

        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径，None 则不写入文件
            log_to_console: 是否输出到控制台
        """
        if cls._initialized:
            return

        # 创建根日志记录器
        root_logger = logging.getLogger("campusfleet")
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # 清除已有的处理器
        root_logger.handlers.clear()

        # 日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台处理器
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # 文件处理器
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            日志记录器实例
        """
        if not cls._initialized:
            cls.setup()

        if name not in cls._loggers:
            logger = logging.getLogger(f"campusfleet.{name}")
            cls._loggers[name] = logger

        return cls._loggers[name]


# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数"""
    return LoggerManager.get_logger(name)


# 默认初始化
LoggerManager.setup(log_level="INFO", log_to_console=True, log_file=None)  # 默认不写入文件
