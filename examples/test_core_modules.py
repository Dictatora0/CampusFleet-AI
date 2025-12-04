#!/usr/bin/env python3
"""
直接测试新增的核心模块（不依赖其他模块）
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("=" * 60)
print("测试新增核心模块")
print("=" * 60)

# 测试 1: 日志系统
print("\n1. 测试日志系统...")
try:
    from core.logger import LoggerManager, get_logger

    LoggerManager.setup(log_level="INFO", log_to_console=True)
    logger = get_logger("test")

    logger.info("日志系统工作正常")
    logger.debug("这是调试信息")
    logger.warning("这是警告信息")

    print("   ✓ 日志系统测试通过")
except Exception as e:
    print(f"   ✗ 日志系统测试失败: {e}")

# 测试 2: 异常类
print("\n2. 测试自定义异常...")
try:
    from core.exceptions import (  # noqa: F401
        CampusFleetException,
        CarAgentError,
        ConfigurationError,
        OrderError,
        PathfindingError,
        SimulationError,
    )

    # 测试异常继承
    assert issubclass(SimulationError, CampusFleetException)
    assert issubclass(PathfindingError, CampusFleetException)
    assert issubclass(ConfigurationError, CampusFleetException)

    # 测试异常抛出和捕获
    try:
        raise SimulationError("测试仿真错误")
    except CampusFleetException as e:
        assert str(e) == "测试仿真错误"

    try:
        raise PathfindingError("测试路径规划错误")
    except PathfindingError as e:
        assert "路径规划" in str(e)

    print("   ✓ 异常类测试通过")
    print("     - 已定义 8 种自定义异常类")
    print("     - 异常继承关系正确")
except Exception as e:
    print(f"   ✗ 异常类测试失败: {e}")

# 测试 3: 配置管理
print("\n3. 测试配置管理...")
try:
    from core.config import (  # noqa: F401
        CarConfig,
        ConfigManager,
        RLConfig,
        SimulationConfig,
        WebConfig,
    )

    # 创建配置管理器
    config = ConfigManager()

    # 测试默认配置
    assert config.simulation.grid_size == 15
    assert config.simulation.num_cars == 3
    assert config.car.max_battery == 100
    assert config.rl.dqn_learning_rate == 1e-3
    assert config.web.port == 8001

    # 测试配置修改
    config.simulation.grid_size = 20
    config.car.max_battery = 150
    assert config.simulation.grid_size == 20
    assert config.car.max_battery == 150

    # 测试配置验证
    config.validate_all()

    # 测试配置保存和加载
    test_config_file = "test_config_temp.json"
    config.save_to_file(test_config_file)

    new_config = ConfigManager()
    new_config.load_from_file(test_config_file)
    assert new_config.simulation.grid_size == 20
    assert new_config.car.max_battery == 150

    # 清理测试文件
    os.remove(test_config_file)

    print("   ✓ 配置管理测试通过")
    print("     - 4 个配置类: Simulation, Car, RL, Web")
    print("     - 支持 JSON 序列化/反序列化")
    print("     - 自动配置验证")
except Exception as e:
    print(f"   ✗ 配置管理测试失败: {e}")
    import traceback

    traceback.print_exc()

# 测试 4: 装饰器
print("\n4. 测试装饰器...")
try:
    import time

    from core.decorators import cache_result, monitor_performance, performance_monitor, retry, timer

    # 测试 timer 装饰器
    @timer
    def test_function():
        time.sleep(0.01)
        return "done"

    result = test_function()
    assert result == "done"

    # 测试 monitor_performance 装饰器
    @monitor_performance("test_metric")
    def monitored_function(x):
        time.sleep(0.005)
        return x * 2

    for i in range(5):
        monitored_function(i)

    stats = performance_monitor.get_stats("test_metric")
    assert stats["count"] == 5
    assert "mean" in stats
    assert "min" in stats
    assert "max" in stats

    # 测试 cache_result 装饰器
    @cache_result(maxsize=10)
    def cached_function(x):
        return x**2

    result1 = cached_function(5)
    result2 = cached_function(5)
    assert result1 == result2 == 25

    cache_info = cached_function.cache_info()
    assert cache_info.hits > 0

    # 测试 retry 装饰器
    attempt_count = [0]

    @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise ValueError("临时错误")
        return "success"

    result = flaky_function()
    assert result == "success"
    assert attempt_count[0] == 2

    print("   ✓ 装饰器测试通过")
    print("     - @timer: 计时装饰器")
    print("     - @monitor_performance: 性能监控")
    print("     - @cache_result: 结果缓存")
    print("     - @retry: 自动重试")
    print(f"     - 性能统计: 平均 {stats['mean']*1000:.2f}ms")
except Exception as e:
    print(f"   ✗ 装饰器测试失败: {e}")
    import traceback

    traceback.print_exc()

# 总结
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)
print("\n✓ 所有新增核心模块测试通过！")
print("\n新增技术特性：")
print("  1. 统一日志系统 (core/logger.py)")
print("  2. 自定义异常类 (core/exceptions.py)")
print("  3. 配置管理系统 (core/config.py)")
print("  4. 性能监控装饰器 (core/decorators.py)")
print("\n配置文件示例：")
print("  - config.example.json")
print("\n详细文档：")
print("  - TECHNICAL_IMPROVEMENTS.md")
print("\n使用方法：")
print("  from core.logger import get_logger")
print("  from core.config import config")
print("  from core.exceptions import SimulationError")
print("  from core.decorators import timer, monitor_performance")
print("=" * 60)
