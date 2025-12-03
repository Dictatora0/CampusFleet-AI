#!/usr/bin/env python3
"""
无人配送车多智能体系统 - 主程序入口
Campus Fleet AI - Multi-Agent Delivery System

使用说明:
    python main.py                    # 默认交互模式
    python main.py --mode auto        # 自动演示模式
    python main.py --cars 5           # 指定车辆数量
    python main.py --size 20          # 指定地图大小
"""

import argparse
import os
import sys

from agents import SchedulingStrategy
from core import Simulation, SimulationContext
from core.config import config
from core.logger import get_logger

# 初始化日志
logger = get_logger("main")

# 加载配置文件
if os.path.exists("config.json"):
    try:
        config.load_from_file("config.json")
        logger.info("已加载配置文件: config.json")
    except Exception as e:
        logger.warning(f"加载配置失败: {e}")
elif os.path.exists("config.default.json"):
    try:
        config.load_from_file("config.default.json")
        logger.info("已加载默认配置: config.default.json")
    except Exception as e:
        logger.warning(f"加载默认配置失败: {e}")


def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          🚗 校园无人配送车多智能体系统 🚗                  ║
    ║         Campus Fleet AI - Multi-Agent System              ║
    ║                                                           ║
    ║              智能调度 · 路径规划 · 避障协同                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="校园无人配送车多智能体系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                           # 交互模式（默认）
  python main.py --mode auto               # 自动演示模式
  python main.py --cars 5 --size 20        # 5辆车，20x20地图
  python main.py --strategy balanced       # 使用负载均衡调度策略
  python main.py --demo                    # 快速演示模式
        """,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["interactive", "auto"],
        default="interactive",
        help="运行模式：interactive（交互）或 auto（自动）",
    )

    parser.add_argument(
        "--size",
        type=int,
        default=None,
        help=f"地图大小（默认{config.simulation.grid_size}x{config.simulation.grid_size}）",
    )

    parser.add_argument(
        "--cars", type=int, default=None, help=f"车辆数量（默认{config.simulation.num_cars}辆）"
    )

    parser.add_argument(
        "--strategy",
        type=str,
        choices=["greedy", "balanced", "hungarian"],
        default="greedy",
        help="调度策略：greedy（贪心）, balanced（负载均衡）, hungarian（匈牙利算法）",
    )

    parser.add_argument("--fps", type=int, default=2, help="动画帧率（每秒帧数，默认：2）")

    parser.add_argument("--steps", type=int, default=100, help="自动模式下的仿真步数（默认：100）")

    parser.add_argument("--orders", type=int, default=10, help="自动模式下的订单数量（默认：10）")

    parser.add_argument("--demo", action="store_true", help="运行快速演示（3辆车，10个订单，50步）")

    return parser.parse_args()


def get_scheduling_strategy(strategy_name: str) -> SchedulingStrategy:
    """
    根据策略名称获取策略枚举
    Args:
        strategy_name: 策略名称
    Returns:
        调度策略枚举
    """
    strategy_map = {
        "greedy": SchedulingStrategy.GREEDY_NEAREST,
        "balanced": SchedulingStrategy.BALANCED_LOAD,
        "hungarian": SchedulingStrategy.HUNGARIAN,
    }
    return strategy_map.get(strategy_name, SchedulingStrategy.GREEDY_NEAREST)


def run_demo():
    """运行快速演示"""
    print_banner()
    print("🎬 快速演示模式")
    print("=" * 60)
    print("配置：3辆车，10个订单，贪心调度策略")
    print("=" * 60)
    print()

    # 创建仿真上下文
    context = SimulationContext(
        grid_size=config.simulation.grid_size,
        num_cars=config.simulation.num_cars,
        scheduling_strategy=SchedulingStrategy.GREEDY_NEAREST,
    )

    # 创建仿真控制器
    simulation = Simulation(context, fps=config.simulation.fps)

    # 运行自动仿真
    simulation.run_auto(num_steps=50, num_orders=10)


def run_interactive_mode(args):
    """运行交互模式"""
    print_banner()

    # 获取调度策略
    strategy = get_scheduling_strategy(args.strategy)

    print(f"配置：{args.cars}辆车，{args.size}x{args.size}地图，{args.strategy}调度策略")
    print()

    # 创建仿真上下文
    context = SimulationContext(
        grid_size=args.size, num_cars=args.cars, scheduling_strategy=strategy
    )

    # 创建仿真控制器
    simulation = Simulation(context, fps=args.fps)

    # 运行交互式仿真
    simulation.run_interactive()


def run_auto_mode(args):
    """运行自动模式"""
    print_banner()

    # 获取调度策略
    strategy = get_scheduling_strategy(args.strategy)

    print(f"配置：{args.cars}辆车，{args.size}x{args.size}地图，{args.strategy}调度策略")
    print(f"运行：{args.steps}步，{args.orders}个订单")
    print()

    # 创建仿真上下文
    context = SimulationContext(
        grid_size=args.size, num_cars=args.cars, scheduling_strategy=strategy
    )

    # 创建仿真控制器
    simulation = Simulation(context, fps=args.fps)

    # 运行自动仿真
    simulation.run_auto(num_steps=args.steps, num_orders=args.orders)


def main():
    """主函数"""
    try:
        args = parse_arguments()

        # 演示模式
        if args.demo:
            run_demo()
            return

        # 根据模式运行
        if args.mode == "interactive":
            run_interactive_mode(args)
        elif args.mode == "auto":
            run_auto_mode(args)

    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
