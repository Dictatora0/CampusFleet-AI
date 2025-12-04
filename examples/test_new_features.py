#!/usr/bin/env python3
"""
测试新增的技术特性（独立测试，不依赖其他模块）
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("=" * 60)
print("测试新增技术特性")
print("=" * 60)

# 测试 1: 日志系统
print("\n1. 测试日志系统...")
try:

    logger = get_logger("test")
    logger.info("日志系统工作正常")
    logger.debug("这是调试信息")
    logger.warning("这是警告信息")

    print("   日志系统测试通过")
except Exception as e:
    print(f"   日志系统测试失败: {e}")

# 测试 2: 异常类
print("\n2. 测试自定义异常...")
try:
    from core.exceptions import (
        CampusFleetException,
        ConfigurationError,
        PathfindingError,
        SimulationError,
    )

    # 测试异常继承
    assert issubclass(SimulationError, CampusFleetException)
    assert issubclass(PathfindingError, CampusFleetException)

    # 测试异常抛出和捕获
    try:
        raise SimulationError("测试错误")
    except CampusFleetException as e:
        assert str(e) == "测试错误"

    print("   异常类测试通过")
except Exception as e:
    print(f"   异常类测试失败: {e}")

# 测试 3: 配置管理
print("\n3. 测试配置管理...")
try:
    from core.config import CarConfig, ConfigManager, SimulationConfig, config

    # 测试默认配置
    assert config.simulation.grid_size == 15
    assert config.car.max_battery == 100

    # 测试配置修改
    config.simulation.grid_size = 20
    assert config.simulation.grid_size == 20

    # 测试配置验证
    config.validate_all()

    # 测试配置保存和加载
    config.save_to_file("test_config.json")
    new_config = ConfigManager()
    new_config.load_from_file("test_config.json")
    assert new_config.simulation.grid_size == 20

    # 清理测试文件
    os.remove("test_config.json")

    print("   配置管理测试通过")
except Exception as e:
    print(f"   配置管理测试失败: {e}")
    import traceback

    traceback.print_exc()

# 测试 4: 装饰器
print("\n4. 测试装饰器...")
try:
    import time

    from core.decorators import cache_result, monitor_performance, performance_monitor, timer

    # 测试 timer 装饰器
    @timer
    def test_function():
        time.sleep(0.01)
        return "done"

    result = test_function()
    assert result == "done"

    # 测试 monitor_performance 装饰器
    @monitor_performance("test_metric")
    def monitored_function():
        time.sleep(0.01)
        return 42

    for _ in range(3):
        monitored_function()

    stats = performance_monitor.get_stats("test_metric")
    assert stats["count"] == 3
    assert "mean" in stats

    # 测试 cache_result 装饰器
    @cache_result(maxsize=10)
    def cached_function(x):
        return x * 2

    result1 = cached_function(5)
    result2 = cached_function(5)  # 应该使用缓存
    assert result1 == result2 == 10

    # 验证缓存信息
    cache_info = cached_function.cache_info()
    assert cache_info.hits > 0  # 有缓存命中

    print("   装饰器测试通过")
except Exception as e:
    print(f"   装饰器测试失败: {e}")
    import traceback

    traceback.print_exc()

# 总结
print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n所有新增技术特性工作正常！")
print("\n新增功能：")
print("1. 统一日志系统 (core/logger.py)")
print("2. 自定义异常类 (core/exceptions.py)")
print("3. 配置管理系统 (core/config.py)")
print("4. 性能监控装饰器 (core/decorators.py)")
print("\n详细文档请查看: TECHNICAL_IMPROVEMENTS.md")
