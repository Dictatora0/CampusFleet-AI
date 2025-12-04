#!/usr/bin/env python3
"""
简单的GUI演示 - 确保窗口可见
"""
import time

from agents import SchedulingStrategy
from core import SimulationContext
from visualization import PygameViewer


def main():
    print("启动图形界面...")
    print("=" * 60)

    # 创建仿真上下文
    context = SimulationContext(
        grid_size=15,
        num_cars=3,
        scheduling_strategy=SchedulingStrategy.HUNGARIAN,
        enable_data_logging=False,  # 演示时不记录数据
    )

    # 添加订单
    print("生成订单...")
    for _ in range(5):
        context.add_random_order()

    # 创建Pygame窗口
    print("打开窗口...")
    viewer = PygameViewer(grid_size=15, cell_size=40, fps=10)

    print("\n" + "=" * 60)
    print("窗口已打开")
    print("=" * 60)
    print("\n控制说明:")
    print("  - 窗口会自动运行仿真")
    print("  - 观察车辆移动（带颜色的圆圈）")
    print("  - 充电站标记为黄色圆圈")
    print("  - 右侧面板显示系统状态")
    print("  - 按 ESC 键退出")
    print("  - 或直接关闭窗口")
    print("=" * 60)
    print("\n仿真开始...\n")

    step = 0
    max_steps = 200
    idle_count = 0  # 记录所有车辆空闲的连续步数

    try:
        while viewer.running and step < max_steps:
            # 处理事件（必须调用，否则窗口无响应）
            if not viewer.handle_events():
                print("\n用户关闭窗口")
                break

            # 执行仿真
            context.step()

            # 渲染界面
            viewer.render(context)

            step += 1

            # 每20步输出一次进度
            if step % 20 == 0:
                stats = context.get_statistics()
                print(
                    f"步骤 {step}: 完成 {stats['total_completed_orders']} 单, "
                    f"距离 {stats['total_distance']}"
                )

            # 检查是否所有订单完成且所有车辆空闲
            pending = context.order_agent.report()["pending_orders"]
            all_idle = all(car.is_idle() for car in context.cars)

            if pending == 0 and all_idle:
                idle_count += 1
                if idle_count >= 10:  # 连续10步都空闲，认为仿真完成
                    print(f"\n所有任务完成（步骤 {step}）")
                    break
            else:
                idle_count = 0

        # 仿真结束
        print("\n" + "=" * 60)
        print("仿真完成")
        print("=" * 60)

        stats = context.get_statistics()
        print(f"\n完成订单: {stats['total_completed_orders']}")
        print(f"总距离: {stats['total_distance']}")

        # 保持窗口显示
        print("\n窗口将保持打开，按 ESC 或关闭窗口退出...")

        while viewer.running:
            if not viewer.handle_events():
                break
            viewer.render(context)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n👋 关闭窗口...")
        try:
            viewer.close()
        except Exception:
            pass
        print("✅ 程序结束")


if __name__ == "__main__":
    main()
