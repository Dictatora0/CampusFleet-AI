"""
仿真主循环模块 - 控制整个仿真的运行
"""

import time
from typing import Optional

from .context import SimulationContext


class Simulation:
    """仿真控制类"""

    def __init__(self, context: SimulationContext, fps: int = 2):
        """
        初始化仿真控制器
        Args:
            context: 仿真上下文
            fps: 每秒帧数（控制动画速度）
        """
        self.context = context
        self.fps = fps
        self.frame_delay = 1.0 / fps if fps > 0 else 0.5
        self.auto_mode = False
        self.auto_order_interval = 10  # 自动模式下每N步添加一个订单

    def run_interactive(self):
        """
        运行交互式仿真
        用户可以手动添加订单并观察系统运行
        """
        print("启动交互式仿真模式")
        print("=" * 60)
        print("命令说明:")
        print("  add <x1> <y1> <x2> <y2> - 添加订单（从(x1,y1)到(x2,y2)）")
        print("  random - 添加随机订单")
        print("  auto - 切换自动模式（自动生成订单）")
        print("  step [n] - 执行n步仿真（默认1步）")
        print("  run - 持续运行仿真")
        print("  pause - 暂停仿真")
        print("  reset - 重置仿真")
        print("  status - 显示详细状态")
        print("  quit - 退出")
        print("=" * 60)

        self.context.display()

        while True:
            try:
                command = input("\n输入命令: ").strip().lower()

                if not command:
                    continue

                parts = command.split()
                cmd = parts[0]

                if cmd == "quit" or cmd == "exit" or cmd == "q":
                    print("退出仿真")
                    break

                elif cmd == "add":
                    if len(parts) == 5:
                        try:
                            x1, y1, x2, y2 = map(int, parts[1:5])
                            self.context.add_order((x1, y1), (x2, y2))
                        except ValueError:
                            print("错误: 坐标必须是整数")
                    else:
                        print("用法: add <x1> <y1> <x2> <y2>")

                elif cmd == "random":
                    self.context.add_random_order()

                elif cmd == "auto":
                    self.auto_mode = not self.auto_mode
                    status = "开启" if self.auto_mode else "关闭"
                    print(f"自动模式已{status}")

                elif cmd == "step":
                    steps = 1
                    if len(parts) > 1:
                        try:
                            steps = int(parts[1])
                        except ValueError:
                            print("错误: 步数必须是整数")
                            continue

                    for i in range(steps):
                        if (
                            self.auto_mode
                            and self.context.current_step % self.auto_order_interval == 0
                        ):
                            self.context.add_random_order()

                        self.context.step()
                        self.context.display()

                        if i < steps - 1:
                            time.sleep(self.frame_delay)

                elif cmd == "run":
                    print("开始运行仿真... (按 Ctrl+C 暂停)")
                    self.context.is_running = True
                    try:
                        while self.context.is_running:
                            if (
                                self.auto_mode
                                and self.context.current_step % self.auto_order_interval == 0
                            ):
                                self.context.add_random_order()

                            if not self.context.step():
                                print("仿真已达到最大步数")
                                break

                            self.context.display()
                            time.sleep(self.frame_delay)
                    except KeyboardInterrupt:
                        print("\n仿真已暂停")
                        self.context.is_running = False

                elif cmd == "pause":
                    self.context.is_running = False
                    print("仿真已暂停")

                elif cmd == "reset":
                    self.context.reset()
                    print("仿真已重置")
                    self.context.display()

                elif cmd == "status":
                    self._print_detailed_status()

                else:
                    print(f"未知命令: {cmd}")

            except KeyboardInterrupt:
                print("\n退出仿真")
                break
            except Exception as e:
                print(f"错误: {e}")

    def run_auto(self, num_steps: int = 100, num_orders: int = 10):
        """
        运行自动仿真模式
        Args:
            num_steps: 运行步数
            num_orders: 自动生成的订单数
        """
        print(f"启动自动仿真模式: {num_steps}步, {num_orders}个订单")

        # 预先生成订单
        for _ in range(num_orders):
            self.context.add_random_order()

        self.context.display()
        time.sleep(1)

        # 运行仿真
        for step in range(num_steps):
            if not self.context.step():
                break

            self.context.display()
            time.sleep(self.frame_delay)

            # 检查是否所有订单都已完成
            if self.context.order_agent.report()["pending_orders"] == 0:
                active_orders = len([car for car in self.context.cars if not car.is_idle()])
                if active_orders == 0:
                    print("\n所有订单已完成。")
                    break

        # 显示最终统计
        self._print_final_statistics()

    def _print_detailed_status(self):
        """打印详细状态信息"""
        print("\n" + "=" * 60)
        print("详细状态信息")
        print("=" * 60)

        stats = self.context.get_statistics()

        print(f"仿真步数: {stats['current_step']}")
        print(f"已完成订单: {stats['total_completed_orders']}")
        print(f"总移动距离: {stats['total_distance']}")
        print(f"平均每订单距离: {stats['avg_distance_per_order']:.2f}")

        print("\n车辆详情:")
        for car_info in stats["cars"]:
            print(f"  车辆 {car_info['car_id']}:")
            print(f"    位置: {car_info['position']}")
            print(f"    状态: {car_info['state']}")
            print(f"    当前订单: {car_info['current_order']}")
            print(f"    已完成订单: {car_info['completed_orders']}")
            print(f"    行驶距离: {car_info['total_distance']}")

        print("\n订单统计:")
        order_stats = stats["orders"]["status_counts"]
        for status, count in order_stats.items():
            print(f"  {status}: {count}")

        print("\n调度器信息:")
        print(f"  策略: {stats['scheduler']['strategy']}")
        print(f"  总分配次数: {stats['scheduler']['total_assignments']}")

        print("=" * 60)

    def _print_final_statistics(self):
        """打印最终统计信息"""
        print("\n" + "=" * 60)
        print("仿真完成 - 最终统计")
        print("=" * 60)

        stats = self.context.get_statistics()

        print(f"总完成订单数: {stats['total_completed_orders']}")
        print(f"总移动距离: {stats['total_distance']}")

        if stats["total_completed_orders"] > 0:
            print(f"平均每订单距离: {stats['avg_distance_per_order']:.2f}")
            efficiency = stats["total_completed_orders"] / stats["current_step"] * 100
            print(f"订单完成效率: {efficiency:.2f}%")

        print("\n车辆表现:")
        for car_info in stats["cars"]:
            print(
                f"  车辆{car_info['car_id']}: 完成{car_info['completed_orders']}单, "
                f"行驶{car_info['total_distance']}格"
            )

        print("=" * 60)

        # 导出数据和生成可视化
        self._export_and_visualize()

    def set_fps(self, fps: int):
        """
        设置帧率
        Args:
            fps: 每秒帧数
        """
        self.fps = fps
        self.frame_delay = 1.0 / fps if fps > 0 else 0.5

    def _export_and_visualize(self):
        """导出数据并生成可视化图表"""
        if not self.context.enable_data_logging:
            return

        print("\n" + "=" * 60)
        print("正在导出数据和生成图表...")
        print("=" * 60)

        # 导出CSV数据
        exported_files = self.context.export_data()

        if not exported_files:
            return

        # 生成可视化图表
        try:
            from analytics import DataVisualizer

            # 找到CSV文件
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
                visualizer = DataVisualizer()
                grid_size = self.context.grid_env.size
                visualizer.generate_all_plots(frames_csv, cars_csv, orders_csv, grid_size)
                print("\n所有图表已生成。")
            else:
                print("未找到必要的CSV文件，跳过可视化")

        except ImportError as e:
            print(f"缺少依赖库，跳过可视化: {e}")
            print("提示: 请安装 matplotlib 和 pandas: pip install matplotlib pandas")
        except Exception as e:
            print(f"生成图表时出错: {e}")

        print("=" * 60)


def run_simulation(grid_size: int = 15, num_cars: int = 3, mode: str = "interactive"):
    """
    快速启动仿真的辅助函数
    Args:
        grid_size: 网格大小
        num_cars: 车辆数量
        mode: 运行模式 ("interactive" 或 "auto")
    """
    context = SimulationContext(grid_size=grid_size, num_cars=num_cars)
    simulation = Simulation(context, fps=2)

    if mode == "interactive":
        simulation.run_interactive()
    elif mode == "auto":
        simulation.run_auto(num_steps=100, num_orders=10)
    else:
        print(f"❌ 未知模式: {mode}")
