#!/usr/bin/env python3
"""
使用Pygame图形界面运行仿真
"""
import os
import sys

from agents import SchedulingStrategy
from core import SimulationContext
from core.config import config
from core.logger import get_logger
from visualization import PygameViewer

# 初始化日志
logger = get_logger("run_with_gui")

# 加载配置文件（如果存在）
if os.path.exists("config.json"):
    try:
        config.load_from_file("config.json")
        logger.info("已加载配置文件: config.json")
    except Exception as e:
        logger.warning(f"加载配置文件失败: {e}，使用默认配置")
elif os.path.exists("config.default.json"):
    try:
        config.load_from_file("config.default.json")
        logger.info("已加载默认配置: config.default.json")
    except Exception as e:
        logger.warning(f"加载默认配置失败: {e}")


def main():
    """主函数"""
    logger.info("正在启动图形界面仿真...")

    # 从配置系统获取参数
    grid_size = config.simulation.grid_size
    num_cars = config.simulation.num_cars
    num_orders = config.demo.test_num_orders
    max_steps = config.simulation.max_steps

    # 选择调度策略（三大核心策略）
    print("\n请选择调度策略:")
    print("1. 贪心最近策略 (GREEDY_NEAREST) - 启发式基线")
    print("2. 拍卖机制 (AUCTION_CNP) - 多智能体协商")
    print("3. 强化学习调度 (RL_SCHEDULER) - AI 智能调度")

    choice = input("输入选择 (1/2/3, 默认1): ").strip() or "1"

    if choice == "2":
        strategy = SchedulingStrategy.AUCTION_CNP
        strategy_name = "AUCTION_CNP"
    elif choice == "3":
        strategy = SchedulingStrategy.RL_SCHEDULER
        strategy_name = "RL_SCHEDULER"
    else:
        strategy = SchedulingStrategy.GREEDY_NEAREST
        strategy_name = "GREEDY_NEAREST"

    # 为每个策略创建独立的输出目录
    output_dir = f"gui_logs_{strategy_name}"

    # 清理旧数据：删除该策略的旧结果
    import shutil

    if os.path.exists(output_dir):
        print(f"\n🗑️  删除旧数据: {output_dir}/")
        shutil.rmtree(output_dir)

    # 创建新的输出目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 数据将保存到目录: {output_dir}/")

    # 初始化仿真上下文
    context = SimulationContext(
        grid_size=grid_size,
        num_cars=num_cars,
        scheduling_strategy=strategy,
        enable_data_logging=True,
        log_dir=output_dir,  # 使用策略特定的目录
    )

    # 预先生成订单
    print(f"\n生成 {num_orders} 个随机订单...")
    for _ in range(num_orders):
        context.add_random_order()

    # 初始化Pygame查看器
    try:
        viewer = PygameViewer(
            grid_size=grid_size,
            cell_size=config.visualization.cell_size,
            fps=config.visualization.fps,
        )
    except ImportError as e:
        logger.error(f"错误: {e}")
        logger.error("请安装pygame: pip install pygame")
        sys.exit(1)

    print("\n图形界面已启动")
    print("提示: 按 ESC 键退出仿真\n")

    # 仿真主循环
    step = 0
    running = True
    idle_count = 0

    while running and step < max_steps:
        # 处理事件
        if not viewer.handle_events():
            break

        # 执行仿真步骤
        if not context.step():
            break

        # 渲染界面
        viewer.render(context)

        step += 1

        # 检查是否所有订单都已完成
        pending = context.order_agent.report()["pending_orders"]
        all_idle = all(car.is_idle() for car in context.cars)

        if pending == 0 and all_idle:
            idle_count += 1
            if idle_count >= 10:
                print(f"\n所有订单已完成（步骤 {step}）")
                # 继续显示5秒
                import time

                for _ in range(50):
                    if not viewer.handle_events():
                        break
                    viewer.render(context)
                    time.sleep(0.1)
                break
        else:
            idle_count = 0

    # 显示最终统计
    print("\n" + "=" * 60)
    print("仿真完成 - 最终统计")
    print("=" * 60)
    stats = context.get_statistics()
    print(f"总完成订单数: {stats['total_completed_orders']}")
    print(f"总移动距离: {stats['total_distance']}")
    if stats["total_completed_orders"] > 0:
        print(f"平均每订单距离: {stats['avg_distance_per_order']:.2f}")

    print("\n车辆表现:")
    for car_info in stats["cars"]:
        print(
            f"  车辆{car_info['car_id']}: "
            f"完成{car_info['completed_orders']}单, "
            f"行驶{car_info['total_distance']}格, "
            f"充电{car_info['total_charging_time']}步"
        )
    print("=" * 60)

    # 导出数据（使用策略名称作为文件前缀）
    print(f"\n正在导出数据和生成图表（策略: {strategy_name}）...")
    exported_files = context.export_data(filename_prefix=f"gui_{strategy_name}")

    if exported_files:
        try:
            from analytics import DataVisualizer

            frames_csv = None
            cars_csv = None
            orders_csv = None

            for file_path in exported_files:
                if "frames" in file_path and file_path.endswith(".csv"):
                    frames_csv = file_path
                elif "cars" in file_path and file_path.endswith(".csv"):
                    cars_csv = file_path
                elif "orders" in file_path and file_path.endswith(".csv"):
                    orders_csv = file_path

            if frames_csv and cars_csv:
                visualizer = DataVisualizer(output_dir=output_dir)  # 使用策略特定目录
                visualizer.generate_all_plots(frames_csv, cars_csv, orders_csv, grid_size)
                print(f"图表已保存到: {output_dir}/")
        except Exception as e:
            print(f"警告: 生成图表时出错: {e}")

    # 关闭Pygame
    viewer.close()

    # 最终提示
    print(f"\n实验完成！数据已保存到: {output_dir}/")
    print("\n💡 提示: 运行不同策略的实验，数据会自动保存到不同目录:")
    print("   - gui_logs_GREEDY_NEAREST/")
    print("   - gui_logs_AUCTION_CNP/")
    print("   - gui_logs_RL_SCHEDULER/")


if __name__ == "__main__":
    main()
