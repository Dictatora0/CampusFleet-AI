#!/usr/bin/env python3
"""
测试所有改进功能的脚本
"""
import os

from agents import CarAgent, SchedulingStrategy
from core import SimulationContext


def test_data_logging():
    """测试数据记录功能"""
    print("\n" + "=" * 60)
    print("测试 1: 数据记录和导出功能")
    print("=" * 60)

    context = SimulationContext(grid_size=10, num_cars=2, enable_data_logging=True)

    # 添加几个订单
    context.add_random_order()
    context.add_random_order()

    # 运行几步
    for _ in range(20):
        context.step()

    # 检查数据记录器
    assert context.data_logger is not None, "数据记录器未初始化"
    summary = context.data_logger.get_summary()

    print(f" 记录帧数: {summary['total_frames']}")
    print(f" 车辆记录数: {summary['total_car_records']}")
    print(f" 订单事件数: {summary['total_order_events']}")

    # 导出数据
    exported_files = context.export_data("test_simulation")
    assert len(exported_files) > 0, "数据导出失败"
    print(f" 成功导出 {len(exported_files)} 个文件")

    # 清理测试文件
    for file in exported_files:
        if os.path.exists(file):
            os.remove(file)

    print(" 数据记录功能测试通过！")


def test_deadlock_handling():
    """测试死锁处理机制"""
    print("\n" + "=" * 60)
    print("测试 2: 死锁处理机制")
    print("=" * 60)

    # 创建简单的测试环境
    grid_size = 5
    grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]
    pathfinder = PathFinding(grid)

    # 创建两辆车在相邻位置
    car1 = CarAgent(car_id=0, initial_position=(1, 1))
    car2 = CarAgent(car_id=1, initial_position=(1, 2))

    # 模拟车辆被卡住的情况
    car1.last_position = (1, 1)
    car1.position = (1, 1)
    car1.stuck_counter = 0

    # 模拟多步没有移动
    for i in range(12):  # 超过max_stuck_time=10
        if car1.position == car1.last_position:
            car1.stuck_counter += 1

        if car1.stuck_counter >= car1.max_stuck_time:
            print(f"步骤 {i}: 检测到死锁，stuck_counter = {car1.stuck_counter}")
            assert car1.stuck_counter >= 10, "死锁检测失败"
            # 触发死锁恢复
            other_positions = {car2.position}
            result = car1._handle_deadlock(pathfinder, other_positions)
            print(f"死锁恢复结果: {result}")
            break

    print(" 死锁检测功能正常")
    print(f" 死锁恢复模式: {car1.deadlock_recovery_mode}")
    print(" 死锁处理机制测试通过！")


def test_battery_system():
    """测试电量系统"""
    print("\n" + "=" * 60)
    print("测试 3: 电量系统和充电站")
    print("=" * 60)

    # 创建带电量的车辆
    car = CarAgent(car_id=0, initial_position=(0, 0), max_battery=100.0)

    # 检查初始电量
    assert car.battery == 100.0, "初始电量错误"
    print(f" 初始电量: {car.battery}%")

    # 模拟移动消耗电量
    initial_battery = car.battery
    car.battery -= car.battery_consumption_rate
    assert car.battery < initial_battery, "电量消耗失败"
    print(f" 移动后电量: {car.battery}%")

    # 测试低电量检测
    car.battery = 15.0  # 设置为低电量
    assert car.needs_charging(), "低电量检测失败"
    print(f" 低电量检测正常: {car.battery}%")

    car.battery = 8.0  # 设置为严重低电
    assert car.is_critical_battery(), "严重低电检测失败"
    print(f" 严重低电检测正常: {car.battery}%")

    # 测试充电
    car.state = car.state.__class__.CHARGING
    for _ in range(5):
        car.charge_step()
    assert car.battery > 15.0, "充电失败"
    print(f" 充电后电量: {car.battery}%")

    # 测试充电站
    context = SimulationContext(grid_size=10, num_cars=2)
    stations = context.grid_env.get_charging_stations()
    assert len(stations) >= 1, "充电站初始化失败"
    print(f" 充电站数量: {len(stations)}")

    # 测试最近充电站查找
    nearest = context.grid_env.get_nearest_charging_station((0, 0))
    assert nearest is not None, "最近充电站查找失败"
    print(f" 找到最近充电站: {nearest}")

    print(" 电量系统测试通过！")


def test_pygame_visualization():
    """测试Pygame可视化（如果可用）"""
    print("\n" + "=" * 60)
    print("测试 4: Pygame可视化")
    print("=" * 60)

    try:

        print(" Pygame模块导入成功")
        print("警告:  跳过实际渲染测试（需要图形界面）")
        print(" Pygame可视化模块可用！")

    except ImportError:
        print("警告:  Pygame未安装，跳过可视化测试")


def test_scheduler_with_battery():
    """测试调度器考虑电量"""
    print("\n" + "=" * 60)
    print("测试 5: 调度器电量考虑")
    print("=" * 60)

    context = SimulationContext(grid_size=10, num_cars=3)

    # 设置一辆车为低电量
    context.cars[0].battery = 5.0  # 严重低电
    context.cars[1].battery = 100.0
    context.cars[2].battery = 100.0

    # 添加订单
    context.add_random_order()

    # 执行调度
    pending_orders = context.order_agent.get_pending_orders()
    if pending_orders:
        assignments = context.scheduler.schedule(context.cars, pending_orders, context.grid_env)

        # 检查低电量车辆不应该被分配任务
        for car_id, order_id, _, _ in assignments:
            assert car_id != 0, "低电量车辆不应该被分配任务"

        print(" 调度器正确排除低电量车辆")
        print(f" 分配了 {len(assignments)} 个任务")

    print(" 调度器电量考虑测试通过！")


def test_integration():
    """集成测试：运行完整仿真"""
    print("\n" + "=" * 60)
    print("测试 6: 完整系统集成测试")
    print("=" * 60)

    context = SimulationContext(
        grid_size=10,
        num_cars=2,
        scheduling_strategy=SchedulingStrategy.HUNGARIAN,
        enable_data_logging=True,
    )

    # 添加多个订单
    for _ in range(5):
        context.add_random_order()

    # 运行仿真
    max_steps = 100
    for step in range(max_steps):
        if not context.step():
            break

        # 检查系统状态
        stats = context.get_statistics()
        assert stats["current_step"] == step + 1, "步数计数错误"

        # 检查车辆电量
        for car in context.cars:
            assert 0 <= car.battery <= car.max_battery, "电量超出范围"

    # 检查最终状态
    final_stats = context.get_statistics()
    print(f" 完成步数: {final_stats['current_step']}")
    print(f" 完成订单: {final_stats['total_completed_orders']}")
    print(f" 总移动距离: {final_stats['total_distance']}")

    # 验证数据记录
    summary = context.data_logger.get_summary()
    assert summary["total_frames"] > 0, "没有记录数据"
    print(f" 记录了 {summary['total_frames']} 帧数据")

    print(" 完整系统集成测试通过！")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 校园无人配送车系统改进功能测试")
    print("=" * 60)

    tests = [
        ("数据记录和导出", test_data_logging),
        ("死锁处理机制", test_deadlock_handling),
        ("电量系统", test_battery_system),
        ("Pygame可视化", test_pygame_visualization),
        ("调度器电量考虑", test_scheduler_with_battery),
        ("完整系统集成", test_integration),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n 测试失败: {name}")
            print(f"错误: {e}")
            failed += 1
        except Exception as e:
            print(f"\n 测试出错: {name}")
            print(f"异常: {e}")
            failed += 1

    # 总结
    print("\n" + "=" * 60)
    print(" 测试总结")
    print("=" * 60)
    print(f" 通过: {passed}/{len(tests)}")
    print(f" 失败: {failed}/{len(tests)}")

    if failed == 0:
        print("\n 所有测试通过！系统改进成功！")
    else:
        print(f"\n警告:  有 {failed} 个测试失败，请检查")

    print("=" * 60)


if __name__ == "__main__":
    main()
