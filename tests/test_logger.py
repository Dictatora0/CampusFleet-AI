"""
测试日志系统模块
"""

import logging
import os
import tempfile

import pytest

from core.logger import LoggerManager, get_logger


class TestLoggerManager:
    """测试 LoggerManager 类"""

    def test_setup_default(self):
        """测试默认设置"""
        LoggerManager.setup()
        logger = get_logger("test")
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_setup_with_file(self):
        """测试文件输出"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            # 重置 LoggerManager 以避免之前的设置干扰
            LoggerManager._initialized = False
            LoggerManager.setup(log_file=log_file, log_to_console=False)

            logger = get_logger("test_file")
            logger.info("测试消息")

            # 刷新所有处理器
            for handler in logger.handlers:
                handler.flush()

            assert os.path.exists(log_file), f"日志文件不存在: {log_file}"
            with open(log_file, "r") as f:
                content = f.read()
                assert "测试消息" in content, f"日志内容不包含测试消息: {content}"

    def test_setup_log_level(self):
        """测试日志级别"""
        LoggerManager.setup(log_level="ERROR")
        logger = get_logger("test_level")

        # ERROR 级别应该能记录
        assert logger.isEnabledFor(logging.ERROR)
        # DEBUG 级别不应该记录
        assert not logger.isEnabledFor(logging.DEBUG)

    def test_get_logger_multiple_times(self):
        """测试多次获取同一日志记录器"""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")

        # 应该返回同一个实例
        assert logger1 is logger2


class TestGetLogger:
    """测试 get_logger 函数"""

    def test_get_logger_basic(self):
        """测试基本功能"""
        logger = get_logger("test_basic")
        assert logger is not None
        assert logger.name == "campusfleet.test_basic"

    def test_logger_hierarchy(self):
        """测试日志层次结构"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "campusfleet.module1"
        assert logger2.name == "campusfleet.module2"
        assert logger1 is not logger2

    def test_logger_methods(self):
        """测试日志方法"""
        logger = get_logger("test_methods")

        # 测试所有日志方法都存在
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")

        # 测试调用不会抛出异常
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
