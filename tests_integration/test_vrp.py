#!/usr/bin/env python3
"""
VRP拼单功能测试
"""
import time

from agents import SchedulingStrategy
from core import SimulationContext
from visualization import PygameViewer


def test_vrp_functionality():
    """测试VRP拼单功能"""
    print("🧪 VRP拼单功能测试")
    print("=" * 60)

    # 创建仿真上下文，使用VRP策略
    context = SimulationContext(
        grid_size=15,
        num_cars=2,  # 减少车辆数量以测试拼单效果
        scheduling_strategy=SchedulingStrategy.VRP_BATCHING,
        enable_data_logging=False,
    )

    # 添加多个订单，让车辆有机会拼单
    print("📋 创建多个订单...")
    orders_created = 0
    for _ in range(8):  # 8个订单，2辆车
        context.add_random_order()
        orders_created += 1

    print(f" 创建了 {orders_created} 个订单")

    # 创建GUI
    viewer = PygameViewer(grid_size=15, cell_size=35, fps=8)

    print("\n" + "=" * 60)
    print(" VRP拼单演示")
    print("=" * 60)
    print("观察要点：")
    print("- 每辆车可能同时处理多个订单")
    print("- 车辆会优化取货和送货顺序")
    print("- 相比传统1对1分配，应该更高效")
    print("- 按 ESC 退出")
    print("=" * 60)
    print()

    step = 0
    max_steps = 150

    # 统计数据
    last_completed = 0
    vrp_assignments = 0

    try:
        while viewer.running and step < max_steps:
            if not viewer.handle_events():
                break

            # 执行仿真
            context.step()
            viewer.render(context)

            step += 1

            # 每20步报告一次
            if step % 20 == 0:
                stats = context.get_statistics()
                completed_now = stats["total_completed_orders"]

                print(
                    f" 步骤 {step:3d}: 完成 {completed_now:2d} 单 "
                    f"(+{completed_now - last_completed}), 距离 {stats['total_distance']}"
                )

                # 显示车辆状态
                for car in context.cars:
                    capacity_info = f"载货:{car.current_capacity}/{car.max_capacity}"
                    queue_info = f"队列:{len(car.task_queue)}任务" if car.task_queue else "无队列"
                    print(f"车辆{car.car_id}: {car.state.value[:8]} | {capacity_info} | {queue_info}")

                last_completed = completed_now

                # 检查是否所有订单完成
                pending = context.order_agent.report()["pending_orders"]
                all_idle = all(car.is_idle() and car.current_capacity == 0 for car in context.cars)

                if pending == 0 and all_idle:
                    print(f"\n 所有VRP任务完成！（步骤 {step}）")
                    break

        # 最终统计
        print("\n" + "=" * 60)
        print(" VRP测试完成")
        print("=" * 60)

        final_stats = context.get_statistics()
        print(f" 总完成订单: {final_stats['total_completed_orders']}")
        print(f" 总移动距离: {final_stats['total_distance']}")
        print(f"⚡ 平均距离/订单: {final_stats['avg_distance_per_order']:.2f}")

        # VRP效率分析
        efficiency = final_stats["total_completed_orders"] / step * 100
        print(f" 订单完成效率: {efficiency:.1f}%")

        print("\nVRP优势分析：")
        print("- 允许车辆同时处理多个订单")
        print("- 优化取货送货顺序")
        print("- 减少空驶距离")
        print("- 提高车辆利用率")

        # 保持窗口显示
        print("\n 窗口保持打开，按ESC或关闭窗口退出...")
        while viewer.running:
            if not viewer.handle_events():
                break
            viewer.render(context)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n  用户中断测试")

    except Exception as e:
        print(f"\n 测试出错: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n👋 VRP测试结束")


def compare_strategies():
    """对比不同调度策略的性能"""
    print("\n🔄 策略对比测试")
    print("=" * 60)

    strategies = [
        (SchedulingStrategy.GREEDY_NEAREST, "贪心最近"),
        (SchedulingStrategy.HUNGARIAN, "匈牙利算法"),
        (SchedulingStrategy.VRP_BATCHING, "VRP拼单"),
    ]

    results = []

    for strategy, name in strategies:
        print(f"\n测试 {name} 策略...")

        context = SimulationContext(
            grid_size=12, num_cars=3, scheduling_strategy=strategy, enable_data_logging=False
        )

        # 添加相同的订单
        for _ in range(10):
            context.add_random_order()

        # 运行仿真
        steps = 0
        max_steps = 100

        while steps < max_steps:
            context.step()
            steps += 1

            # 检查完成条件
            pending = context.order_agent.report()["pending_orders"]
            all_idle = all(car.is_idle() for car in context.cars)

            if pending == 0 and all_idle:
                break

        stats = context.get_statistics()
        results.append(
            {
                "strategy": name,
                "steps": steps,
                "completed": stats["total_completed_orders"],
                "distance": stats["total_distance"],
                "efficiency": stats["total_completed_orders"] / steps * 100,
            }
        )

        print(f"{steps}步完成 {stats['total_completed_orders']}单，距离{stats['total_distance']}")

    # 显示对比结果
    print("\n 策略对比结果：")
    print("-" * 60)
    print(f"{'策略':<15} {'步数':<6} {'订单':<6} {'距离':<8} {'效率%'}")
    print("-" * 60)

    for result in results:
        print(
            f"{result['strategy']:<15} {result['steps']:<6} {result['completed']:<6} "
            f"{result['distance']:<8} {result['efficiency']:.1f}"
        )

    # 找出最佳策略
    best_by_efficiency = max(results, key=lambda x: x["efficiency"])
    best_by_distance = min(results, key=lambda x: x["distance"])

    print("\n 最佳表现：")
    print(f"效率最高: {best_by_efficiency['strategy']} ({best_by_efficiency['efficiency']:.1f}%)")
    print(f"距离最短: {best_by_distance['strategy']} ({best_by_distance['distance']} 格)")


if __name__ == "__main__":
    test_vrp_functionality()
    compare_strategies()
