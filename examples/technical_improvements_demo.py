#!/usr/bin/env python3
"""
技术改进功能演示

展示新增的技术特性：
1. 统一日志系统
2. 自定义异常
3. 配置管理
4. 性能监控装饰器
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core import (
    ConfigurationError,
    LoggerManager,
    SimulationError,
    config,
    get_logger,
    monitor_performance,
    performance_monitor,
    timer,
)


# 1. 日志系统演示
def demo_logging():
    """演示统一日志系统"""
    print("\n" + "=" * 60)
    print("1. 日志系统演示")
    print("=" * 60)

    # 获取日志记录器
    logger = get_logger("demo")

    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")

    # 配置日志输出到文件
    LoggerManager.setup(log_level="DEBUG", log_file="logs/demo.log", log_to_console=True)

    logger.info("日志系统已配置，输出到文件和控制台")


# 2. 异常处理演示
def demo_exceptions():
    """演示自定义异常"""
    print("\n" + "=" * 60)
    print("2. 自定义异常演示")
    print("=" * 60)

    logger = get_logger("demo")

    try:
        # 模拟仿真错误
        raise SimulationError("仿真步骤执行失败")
    except SimulationError as e:
        logger.error(f"捕获到仿真错误: {e}")

    try:
        # 模拟配置错误
        raise ConfigurationError("配置参数无效")
    except ConfigurationError as e:
        logger.error(f"捕获到配置错误: {e}")

    print("异常处理演示完成")


# 3. 配置管理演示
def demo_config():
    """演示配置管理"""
    print("\n" + "=" * 60)
    print("3. 配置管理演示")
    print("=" * 60)

    logger = get_logger("demo")

    # 访问配置
    logger.info(f"网格大小: {config.simulation.grid_size}")
    logger.info(f"车辆数量: {config.simulation.num_cars}")
    logger.info(f"最大电量: {config.car.max_battery}")
    logger.info(f"DQN学习率: {config.rl.dqn_learning_rate}")
    logger.info(f"Web端口: {config.web.port}")

    # 修改配置
    config.simulation.grid_size = 20
    config.simulation.num_cars = 5
    logger.info(f"修改后网格大小: {config.simulation.grid_size}")
    logger.info(f"修改后车辆数量: {config.simulation.num_cars}")

    # 保存配置
    config.save_to_file("config.demo.json")
    logger.info("配置已保存到 config.demo.json")

    # 验证配置
    try:
        config.validate_all()
        logger.info("配置验证通过")
    except ValueError as e:
        logger.error(f"配置验证失败: {e}")


# 4. 性能监控演示
@timer
@monitor_performance("demo_calculation")
def expensive_calculation(n: int) -> int:
    """模拟耗时计算"""
    import time

    time.sleep(0.1)  # 模拟耗时操作
    return sum(range(n))


def demo_performance():
    """演示性能监控"""
    print("\n" + "=" * 60)
    print("4. 性能监控演示")
    print("=" * 60)

    logger = get_logger("demo")

    # 执行多次计算
    for i in range(5):
        result = expensive_calculation(1000)
        logger.info(f"计算 {i+1}: 结果 = {result}")

    # 获取性能统计
    stats = performance_monitor.get_stats("demo_calculation")
    logger.info(f"性能统计: {stats}")

    print(f"\n执行次数: {stats['count']}")
    print(f"总耗时: {stats['total']:.4f}秒")
    print(f"平均耗时: {stats['mean']:.4f}秒")
    print(f"最小耗时: {stats['min']:.4f}秒")
    print(f"最大耗时: {stats['max']:.4f}秒")


# 5. 综合示例
def demo_integrated():
    """综合示例：在实际场景中使用新特性"""
    print("\n" + "=" * 60)
    print("5. 综合示例")
    print("=" * 60)

    logger = get_logger("integrated_demo")

    try:
        # 加载配置
        logger.info("加载配置...")
        # config.load_from_file("config.json")  # 如果有配置文件

        # 验证配置
        logger.info("验证配置...")
        config.validate_all()

        # 模拟仿真初始化
        logger.info(f"初始化仿真: {config.simulation.grid_size}x{config.simulation.grid_size} 网格")
        logger.info(f"车辆数量: {config.simulation.num_cars}")

        # 模拟仿真运行
        @timer
        def run_simulation_step():
            import time

            time.sleep(0.05)
            return True

        logger.info("开始仿真...")
        for step in range(10):
            _ = run_simulation_step()
            if step % 3 == 0:
                logger.info(f"步骤 {step}: 运行中")

        logger.info("仿真完成")

    except ConfigurationError as e:
        logger.error(f"配置错误: {e}")
    except SimulationError as e:
        logger.error(f"仿真错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("CampusFleet AI 技术改进功能演示")
    print("=" * 60)

    # 初始化日志系统
    LoggerManager.setup(log_level="INFO", log_to_console=True)

    # 运行各个演示
    demo_logging()
    demo_exceptions()
    demo_config()
    demo_performance()
    demo_integrated()

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)

    print("\n技术改进总结:")
    print("1. 统一日志系统 - 支持多级别日志和文件输出")
    print("2. 自定义异常类 - 更精确的错误处理")
    print("3. 配置管理系统 - 集中管理和验证配置")
    print("4. 性能监控装饰器 - 自动记录函数执行时间")
    print("5. 类型提示完善 - 提高代码可维护性")

    # 清理演示文件
    import os

    if os.path.exists("config.demo.json"):
        os.remove("config.demo.json")
        print("\n已清理演示文件")


if __name__ == "__main__":
    main()
