#!/usr/bin/env python3
"""
MAPF CBS算法测试
测试冲突感知搜索的协调能力
"""
import time

from agents import SchedulingStrategy
from core import SimulationContext
from visualization import PygameViewer


def test_mapf_cbs():
    """测试MAPF CBS算法"""
    print("🧠 MAPF CBS算法测试")
    print("=" * 60)

    # 创建仿真上下文，使用MAPF CBS策略
    context = SimulationContext(
        grid_size=12,  # 较小的网格便于观察协调效果
        num_cars=3,  # 3辆车容易产生冲突
        scheduling_strategy=SchedulingStrategy.MAPF_CBS,
        enable_data_logging=False,
    )

    print("📋 创建测试场景...")

    # 创建容易产生冲突的订单布局
    test_orders = [
        ((1, 1), (10, 10)),  # 对角线
        ((10, 1), (1, 10)),  # 交叉对角线
        ((5, 1), (5, 10)),  # 中央纵向
        ((1, 5), (10, 5)),  # 中央横向
    ]

    orders_created = 0
    for pickup, delivery in test_orders:
        try:
            # 直接创建订单而不是随机生成
            context.order_agent.create_order(pickup, delivery)
            orders_created += 1
            print(f" 订单 #{orders_created}: {pickup} → {delivery}")
        except Exception:
            # 如果不支持直接创建，使用随机方法
            context.add_random_order()
            orders_created += 1

    print(f" 创建了 {orders_created} 个测试订单")

    # 创建GUI
    viewer = PygameViewer(grid_size=12, cell_size=40, fps=6)  # 慢速便于观察

    print("\n" + "=" * 60)
    print("🧠 MAPF CBS协调演示")
    print("=" * 60)
    print("观察要点：")
    print("- CBS预先规划无冲突路径")
    print("- 车辆严格按照时空路径移动")
    print("- 不会出现死锁或碰撞")
    print("- 路径可能不是最短，但保证无冲突")
    print("- 按 ESC 退出")
    print("=" * 60)
    print()

    step = 0
    max_steps = 200
    cbs_calls = 0
    successful_assignments = 0

    try:
        while viewer.running and step < max_steps:
            if not viewer.handle_events():
                break

            # 记录CBS调用前的状态
            old_assignments = successful_assignments

            # 执行仿真
            context.step()
            viewer.render(context)

            step += 1

            # 检测是否有新的CBS分配
            current_assignments = context.scheduler.total_assignments
            if current_assignments > old_assignments:
                successful_assignments = current_assignments
                cbs_calls += 1

            # 每15步报告一次
            if step % 15 == 0:
                stats = context.get_statistics()
                completed = stats["total_completed_orders"]

                print(f" 步骤 {step:3d}: 完成 {completed:2d} 单, " f"CBS调用 {cbs_calls} 次")

                # 显示车辆协调状态
                for car in context.cars:
                    coord_info = ""
                    if hasattr(car, "use_coordinated_path") and car.use_coordinated_path:
                        path_len = (
                            len(car.coordinated_path) if car.coordinated_path else 0
                        )
                        coord_info = f"CBS路径[{car.path_time_step}/{path_len}]"
                    else:
                        coord_info = "传统规划"

                    print(f"车辆{car.car_id}: {car.state.value[:8]} | {coord_info}")

                # 检查完成条件
                pending = context.order_agent.report()["pending_orders"]
                all_idle = all(car.is_idle() for car in context.cars)

                if pending == 0 and all_idle:
                    print(f"\n MAPF测试完成！（步骤 {step}）")
                    break

        # 最终统计
        print("\n" + "=" * 60)
        print("🧠 MAPF CBS测试结果")
        print("=" * 60)

        final_stats = context.get_statistics()
        print(f" 总完成订单: {final_stats['total_completed_orders']}")
        print(f" 总移动距离: {final_stats['total_distance']}")
        print(f"🧠 CBS协调调用: {cbs_calls} 次")
        print(f"⚡ 协调成功率: {successful_assignments}/{cbs_calls * 3:.1f}" if cbs_calls > 0 else "N/A")

        # MAPF算法分析
        efficiency = final_stats["total_completed_orders"] / step * 100 if step > 0 else 0
        print(f" 完成效率: {efficiency:.1f}%")

        print("\nMAPF CBS优势：")
        print("完备性：保证找到解（如果存在）")
        print("最优性：找到成本最优的无冲突路径")
        print("无死锁：预先消除所有时空冲突")
        print("可扩展：支持任意数量的智能体")

        print("\n算法复杂度：")
        print("- 时间复杂度: 指数级（最坏情况）")
        print("- 空间复杂度: 多项式级")
        print("- 实际性能: 在稀疏冲突场景下表现良好")

        # 保持窗口显示
        print("\n 窗口保持打开，观察最终状态...")
        for _ in range(30):  # 显示3秒
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
        print("\n👋 MAPF测试结束")


def demo_algorithm_comparison():
    """对比传统避障vs MAPF协调"""
    print("\n🔄 避障算法对比")
    print("=" * 60)

    algorithms = [
        (SchedulingStrategy.GREEDY_NEAREST, "传统贪心+避障"),
        (SchedulingStrategy.MAPF_CBS, "MAPF CBS协调"),
    ]

    results = []

    for strategy, name in algorithms:
        print(f"\n🧪 测试 {name}...")

        context = SimulationContext(
            grid_size=10, num_cars=3, scheduling_strategy=strategy, enable_data_logging=False
        )

        # 创建相同的测试场景
        for _ in range(6):
            context.add_random_order()

        # 运行仿真
        steps = 0
        max_steps = 80
        deadlocks = 0

        while steps < max_steps:
            context.step()
            steps += 1

            # 检测死锁（车辆长时间不动）
            stuck_cars = sum(
                1 for car in context.cars if hasattr(car, "stuck_counter") and car.stuck_counter > 5
            )
            if stuck_cars > 0:
                deadlocks += 1

            # 检查完成条件
            pending = context.order_agent.report()["pending_orders"]
            all_idle = all(car.is_idle() for car in context.cars)

            if pending == 0 and all_idle:
                break

        stats = context.get_statistics()
        results.append(
            {
                "algorithm": name,
                "steps": steps,
                "completed": stats["total_completed_orders"],
                "distance": stats["total_distance"],
                "deadlocks": deadlocks,
                "efficiency": stats["total_completed_orders"] / steps * 100,
            }
        )

        print(
            f"{steps}步完成 {stats['total_completed_orders']}单，"
            f"距离{stats['total_distance']}，死锁{deadlocks}次"
        )

    # 显示对比结果
    print("\n 算法对比结果：")
    print("-" * 70)
    print(f"{'算法':<20} {'步数':<6} {'订单':<6} {'距离':<8} {'死锁':<6} {'效率%'}")
    print("-" * 70)

    for result in results:
        print(
            f"{result['algorithm']:<20} {result['steps']:<6} {result['completed']:<6} "
            f"{result['distance']:<8} {result['deadlocks']:<6} {result['efficiency']:.1f}"
        )

    # 分析优势
    print("\n 算法特点分析：")
    print("传统避障：")
    print("计算简单，响应快速")
    print("容易死锁，效率不稳定")
    print("局部最优，缺乏全局视野")

    print("\nMAPF CBS：")
    print("理论完备，保证无死锁")
    print("全局最优，协调一致")
    print("计算复杂，适合小规模")
    print("需要完整信息，实时性挑战")


if __name__ == "__main__":
    test_mapf_cbs()
    demo_algorithm_comparison()
