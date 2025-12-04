"""
装饰器模块 - 提供性能监控、缓存等功能
"""

import functools
import time
from typing import Callable

from .logger import get_logger

logger = get_logger("decorators")


def timer(func: Callable) -> Callable:
    """
    计时装饰器 - 记录函数执行时间

    Usage:
        @timer
        def my_function():
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        logger.debug(f"{func.__name__} executed in {elapsed:.4f} seconds")
        return result

    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    重试装饰器 - 失败时自动重试

    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要捕获的异常类型

    Usage:
        @retry(max_attempts=3, delay=1.0)
        def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            raise last_exception

        return wrapper

    return decorator


def cache_result(maxsize: int = 128):
    """
    结果缓存装饰器 - 缓存函数返回值

    Args:
        maxsize: 缓存大小

    Usage:
        @cache_result(maxsize=256)
        def expensive_function(x):
            return x ** 2
    """

    def decorator(func: Callable) -> Callable:
        return functools.lru_cache(maxsize=maxsize)(func)

    return decorator


def validate_args(**validators):
    """
    参数验证装饰器

    Args:
        validators: 参数名到验证函数的映射

    Usage:
        @validate_args(x=lambda x: x > 0, y=lambda y: isinstance(y, str))
        def my_function(x, y):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数签名
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 验证参数
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for parameter '{param_name}' " f"with value {value}"
                        )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_calls(level: str = "DEBUG"):
    """
    日志记录装饰器 - 记录函数调用

    Args:
        level: 日志级别

    Usage:
        @log_calls(level="INFO")
        def my_function(x, y):
            return x + y
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_func = getattr(logger, level.lower())
            log_func(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            log_func(f"{func.__name__} returned {result}")
            return result

        return wrapper

    return decorator


class PerformanceMonitor:
    """性能监控类"""

    def __init__(self):
        self.metrics = {}

    def record(self, name: str, value: float):
        """记录性能指标"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_stats(self, name: str) -> dict:
        """获取统计信息"""
        if name not in self.metrics:
            return {}

        values = self.metrics[name]
        return {
            "count": len(values),
            "total": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def clear(self):
        """清除所有记录"""
        self.metrics.clear()


# 全局性能监控实例
performance_monitor = PerformanceMonitor()


def monitor_performance(metric_name: str):
    """
    性能监控装饰器

    Args:
        metric_name: 指标名称

    Usage:
        @monitor_performance("pathfinding_time")
        def find_path(start, goal):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            performance_monitor.record(metric_name, elapsed)
            return result

        return wrapper

    return decorator
