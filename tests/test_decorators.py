"""
测试装饰器模块
"""

import time

import pytest

from core.decorators import (
    PerformanceMonitor,
    cache_result,
    monitor_performance,
    performance_monitor,
    retry,
    timer,
    validate_args,
)


class TestTimerDecorator:
    """测试计时装饰器"""

    def test_timer_basic(self):
        """测试基本功能"""

        @timer
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()
        assert result == "done"

    def test_timer_with_args(self):
        """测试带参数的函数"""

        @timer
        def add(a, b):
            return a + b

        result = add(2, 3)
        assert result == 5


class TestRetryDecorator:
    """测试重试装饰器"""

    def test_retry_success_first_time(self):
        """测试第一次就成功"""
        call_count = [0]

        @retry(max_attempts=3, delay=0.01)
        def stable_function():
            call_count[0] += 1
            return "success"

        result = stable_function()
        assert result == "success"
        assert call_count[0] == 1

    def test_retry_success_after_failures(self):
        """测试失败后重试成功"""
        call_count = [0]

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("临时错误")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count[0] == 3

    def test_retry_all_attempts_failed(self):
        """测试所有尝试都失败"""

        @retry(max_attempts=3, delay=0.01)
        def always_fail():
            raise ValueError("永久错误")

        with pytest.raises(ValueError, match="永久错误"):
            always_fail()


class TestCacheResultDecorator:
    """测试缓存装饰器"""

    def test_cache_basic(self):
        """测试基本缓存"""
        call_count = [0]

        @cache_result(maxsize=10)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2

        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1

        # 第二次调用（应该使用缓存）
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # 没有增加

        # 不同参数（不使用缓存）
        result3 = expensive_function(6)
        assert result3 == 12
        assert call_count[0] == 2

    def test_cache_info(self):
        """测试缓存信息"""

        @cache_result(maxsize=10)
        def cached_func(x):
            return x**2

        cached_func(5)
        cached_func(5)  # 命中缓存
        cached_func(6)

        cache_info = cached_func.cache_info()
        assert cache_info.hits > 0
        assert cache_info.misses > 0


class TestValidateArgsDecorator:
    """测试参数验证装饰器"""

    def test_validate_success(self):
        """测试验证成功"""

        @validate_args(x=lambda x: x > 0, y=lambda y: isinstance(y, str))
        def my_function(x, y):
            return f"{y}: {x}"

        result = my_function(5, "value")
        assert result == "value: 5"

    def test_validate_failure(self):
        """测试验证失败"""

        @validate_args(x=lambda x: x > 0)
        def my_function(x):
            return x

        with pytest.raises(ValueError, match="Validation failed"):
            my_function(-5)


class TestMonitorPerformanceDecorator:
    """测试性能监控装饰器"""

    def test_monitor_basic(self):
        """测试基本监控"""
        _ = PerformanceMonitor()

        @monitor_performance("test_metric")
        def monitored_function():
            time.sleep(0.01)
            return "done"

        # 执行几次
        for _ in range(3):
            monitored_function()

        # 获取统计
        stats = performance_monitor.get_stats("test_metric")
        assert stats["count"] >= 3
        assert "mean" in stats
        assert "min" in stats
        assert "max" in stats

    def test_monitor_multiple_metrics(self):
        """测试多个指标"""

        @monitor_performance("metric1")
        def func1():
            time.sleep(0.01)

        @monitor_performance("metric2")
        def func2():
            time.sleep(0.02)

        func1()
        func2()

        stats1 = performance_monitor.get_stats("metric1")
        stats2 = performance_monitor.get_stats("metric2")

        assert stats1["count"] == 1
        assert stats2["count"] == 1


class TestPerformanceMonitor:
    """测试性能监控类"""

    def test_record_and_get_stats(self):
        """测试记录和获取统计"""
        monitor = PerformanceMonitor()

        monitor.record("test", 0.1)
        monitor.record("test", 0.2)
        monitor.record("test", 0.3)

        stats = monitor.get_stats("test")
        assert stats["count"] == 3
        assert stats["total"] == pytest.approx(0.6, rel=1e-5)
        assert stats["mean"] == pytest.approx(0.2, rel=1e-5)
        assert stats["min"] == 0.1
        assert stats["max"] == 0.3

    def test_clear(self):
        """测试清除"""
        monitor = PerformanceMonitor()

        monitor.record("test", 0.1)
        monitor.clear()

        stats = monitor.get_stats("test")
        assert stats == {}

    def test_nonexistent_metric(self):
        """测试不存在的指标"""
        monitor = PerformanceMonitor()
        stats = monitor.get_stats("nonexistent")
        assert stats == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
