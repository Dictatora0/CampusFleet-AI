#!/usr/bin/env python3
"""
从已有的 CSV 数据重新生成图表
"""
from pathlib import Path

from analytics import DataVisualizer


def regenerate_plots_for_strategy(strategy_name: str):
    """为指定策略重新生成图表"""
    log_dir = Path(f"gui_logs_{strategy_name}")

    if not log_dir.exists():
        print(f"⚠️  目录不存在: {log_dir}/")
        return

    # 查找 CSV 文件
    csv_files = list(log_dir.glob("*.csv"))
    if not csv_files:
        print(f"⚠️  目录 {log_dir}/ 中没有找到 CSV 文件")
        return

    frames_csv = None
    cars_csv = None
    orders_csv = None

    for csv_file in csv_files:
        if "frames" in csv_file.name:
            frames_csv = str(csv_file)
        elif "cars" in csv_file.name:
            cars_csv = str(csv_file)
        elif "orders" in csv_file.name:
            orders_csv = str(csv_file)

    if not frames_csv or not cars_csv:
        print(f"⚠️  缺少必要的 CSV 文件（frames 或 cars）")
        return

    print(f"\n📊 为策略 {strategy_name} 重新生成图表...")
    print(f"   frames: {frames_csv}")
    print(f"   cars: {cars_csv}")
    if orders_csv:
        print(f"   orders: {orders_csv}")

    # 创建可视化器（使用策略特定目录）
    visualizer = DataVisualizer(output_dir=str(log_dir))

    # 生成所有图表
    try:
        visualizer.generate_all_plots(frames_csv, cars_csv, orders_csv, grid_size=15)
        print(f"✅ 图表已保存到: {log_dir}/")
    except Exception as e:
        print(f"❌ 生成图表时出错: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("从 CSV 数据重新生成图表")
    print("=" * 60)

    strategies = ["GREEDY_NEAREST", "AUCTION_CNP", "RL_SCHEDULER"]

    for strategy in strategies:
        regenerate_plots_for_strategy(strategy)

    print("\n" + "=" * 60)
    print("✅ 完成！检查以下目录查看图表：")
    print("   - gui_logs_GREEDY_NEAREST/")
    print("   - gui_logs_AUCTION_CNP/")
    print("   - gui_logs_RL_SCHEDULER/")
    print("=" * 60)
