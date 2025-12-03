"""
数据可视化模块 - 生成各类统计图表
"""

from pathlib import Path
from typing import List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")  # 使用非交互式后端


class DataVisualizer:
    """数据可视化器 - 根据CSV数据生成图表"""

    def __init__(self, output_dir: str = "simulation_logs"):
        """
        初始化可视化器
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 设置中文字体支持
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

    def load_data(self, frames_csv: str, cars_csv: str, orders_csv: str = None) -> tuple:
        """
        加载CSV数据
        Args:
            frames_csv: 帧数据CSV路径
            cars_csv: 车辆数据CSV路径
            orders_csv: 订单数据CSV路径
        Returns:
            (frames_df, cars_df, orders_df) 数据框元组
        """
        frames_df = pd.read_csv(frames_csv)
        cars_df = pd.read_csv(cars_csv)
        orders_df = pd.read_csv(orders_csv) if orders_csv else None
        return frames_df, cars_df, orders_df

    def plot_order_completion_over_time(
        self, frames_df: pd.DataFrame, save_path: Optional[str] = None
    ):
        """
        绘制订单完成率随时间变化图
        Args:
            frames_df: 帧数据DataFrame
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            frames_df["step"],
            frames_df["completed_orders"],
            label="Completed Orders",
            linewidth=2,
            color="green",
        )
        ax.plot(
            frames_df["step"],
            frames_df["pending_orders"],
            label="Pending Orders",
            linewidth=2,
            color="orange",
        )
        ax.plot(
            frames_df["step"],
            frames_df["assigned_orders"],
            label="Assigned Orders",
            linewidth=2,
            color="blue",
        )

        ax.set_xlabel("Simulation Step", fontsize=12)
        ax.set_ylabel("Number of Orders", fontsize=12)
        ax.set_title("Order Status Over Time", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")
        else:
            save_path = self.output_dir / "order_completion_over_time.png"
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")

        plt.close()

    def plot_efficiency_metrics(self, frames_df: pd.DataFrame, save_path: Optional[str] = None):
        """
        绘制效率指标图（订单完成效率、车辆利用率）
        Args:
            frames_df: 帧数据DataFrame
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 计算效率指标
        frames_df["completion_rate"] = frames_df["completed_orders"] / (frames_df["step"] + 1) * 100
        frames_df["utilization_rate"] = frames_df["active_cars"] / frames_df["total_cars"] * 100

        # 订单完成效率
        ax1.plot(frames_df["step"], frames_df["completion_rate"], linewidth=2, color="green")
        ax1.set_xlabel("Simulation Step", fontsize=12)
        ax1.set_ylabel("Completion Rate (%)", fontsize=12)
        ax1.set_title("Order Completion Efficiency", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # 车辆利用率
        ax2.plot(frames_df["step"], frames_df["utilization_rate"], linewidth=2, color="blue")
        ax2.fill_between(
            frames_df["step"], 0, frames_df["utilization_rate"], alpha=0.3, color="blue"
        )
        ax2.set_xlabel("Simulation Step", fontsize=12)
        ax2.set_ylabel("Utilization Rate (%)", fontsize=12)
        ax2.set_title("Vehicle Utilization Rate", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 105)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")
        else:
            save_path = self.output_dir / "efficiency_metrics.png"
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")

        plt.close()

    def plot_distance_statistics(self, cars_df: pd.DataFrame, save_path: Optional[str] = None):
        """
        绘制距离统计图（每辆车的总距离、距离分布）
        Args:
            cars_df: 车辆数据DataFrame
            save_path: 保存路径
        """
        # 获取每辆车的最终距离
        final_step = cars_df["step"].max()
        final_data = cars_df[cars_df["step"] == final_step]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 每辆车的总距离柱状图
        colors = plt.cm.viridis(np.linspace(0, 1, len(final_data)))
        ax1.bar(
            final_data["car_id"].astype(str),
            final_data["total_distance"],
            color=colors,
            edgecolor="black",
            linewidth=1.5,
        )
        ax1.set_xlabel("Car ID", fontsize=12)
        ax1.set_ylabel("Total Distance", fontsize=12)
        ax1.set_title("Total Distance by Vehicle", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3, axis="y")

        # 添加数值标签
        for i, (idx, row) in enumerate(final_data.iterrows()):
            ax1.text(
                i,
                row["total_distance"] + 0.5,
                str(int(row["total_distance"])),
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        # 距离随时间变化
        for car_id in cars_df["car_id"].unique():
            car_data = cars_df[cars_df["car_id"] == car_id]
            ax2.plot(
                car_data["step"], car_data["total_distance"], label=f"Car {car_id}", linewidth=2
            )

        ax2.set_xlabel("Simulation Step", fontsize=12)
        ax2.set_ylabel("Cumulative Distance", fontsize=12)
        ax2.set_title("Distance Accumulation Over Time", fontsize=14, fontweight="bold")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")
        else:
            save_path = self.output_dir / "distance_statistics.png"
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")

        plt.close()

    def plot_heatmap(
        self, cars_df: pd.DataFrame, grid_size: int = 15, save_path: Optional[str] = None
    ):
        """
        绘制车辆访问热力图
        Args:
            cars_df: 车辆数据DataFrame
            grid_size: 网格大小
            save_path: 保存路径
        """
        # 统计每个位置被访问的次数
        heatmap = np.zeros((grid_size, grid_size))

        for _, row in cars_df.iterrows():
            x, y = int(row["x"]), int(row["y"])
            if 0 <= x < grid_size and 0 <= y < grid_size:
                heatmap[x, y] += 1

        fig, ax = plt.subplots(figsize=(10, 8))

        im = ax.imshow(heatmap, cmap="hot", interpolation="nearest")
        ax.set_xlabel("Y Coordinate", fontsize=12)
        ax.set_ylabel("X Coordinate", fontsize=12)
        ax.set_title("Traffic Heatmap (Visit Frequency)", fontsize=14, fontweight="bold")

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Visit Count", fontsize=12)

        # 设置网格
        ax.set_xticks(np.arange(grid_size))
        ax.set_yticks(np.arange(grid_size))
        ax.grid(which="both", color="gray", linestyle="-", linewidth=0.5, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")
        else:
            save_path = self.output_dir / "traffic_heatmap.png"
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 图表已保存: {save_path}")

        plt.close()

    def plot_order_waiting_time(self, orders_df: pd.DataFrame, save_path: Optional[str] = None):
        """
        绘制订单等待时间分布图
        Args:
            orders_df: 订单数据DataFrame
            save_path: 保存路径
        """
        if orders_df is None or orders_df.empty:
            print("⚠️ 没有订单数据，跳过等待时间图表")
            return

        # 计算等待时间（从创建到分配）
        created = orders_df[orders_df["event_type"] == "created"].set_index("order_id")
        assigned = orders_df[orders_df["event_type"] == "assigned"].set_index("order_id")

        waiting_times = []
        for order_id in created.index:
            if order_id in assigned.index:
                wait_time = assigned.loc[order_id, "step"] - created.loc[order_id, "step"]
                waiting_times.append(wait_time)

        if not waiting_times:
            print("⚠️ 没有足够的订单数据计算等待时间")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 直方图
        ax1.hist(waiting_times, bins=20, color="skyblue", edgecolor="black", alpha=0.7)
        ax1.set_xlabel("Waiting Time (steps)", fontsize=12)
        ax1.set_ylabel("Frequency", fontsize=12)
        ax1.set_title("Order Waiting Time Distribution", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3, axis="y")

        # 统计信息
        avg_wait = np.mean(waiting_times)
        median_wait = np.median(waiting_times)
        max_wait = np.max(waiting_times)

        ax1.axvline(
            avg_wait, color="red", linestyle="--", linewidth=2, label=f"Mean: {avg_wait:.1f}"
        )
        ax1.axvline(
            median_wait,
            color="green",
            linestyle="--",
            linewidth=2,
            label=f"Median: {median_wait:.1f}",
        )
        ax1.legend()

        # 箱型图
        ax2.boxplot(
            waiting_times,
            vert=True,
            patch_artist=True,
            boxprops=dict(facecolor="lightblue", alpha=0.7),
        )
        ax2.set_ylabel("Waiting Time (steps)", fontsize=12)
        ax2.set_title("Waiting Time Box Plot", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3, axis="y")

        # 添加统计文本
        stats_text = f"Mean: {avg_wait:.2f}\nMedian: {median_wait:.2f}\nMax: {max_wait:.2f}"
        ax2.text(
            1.15,
            max_wait * 0.5,
            stats_text,
            fontsize=11,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"图表已保存: {save_path}")
        else:
            save_path = self.output_dir / "waiting_time_distribution.png"
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"图表已保存: {save_path}")

        plt.close()

    def generate_all_plots(
        self, frames_csv: str, cars_csv: str, orders_csv: str = None, grid_size: int = 15
    ):
        """
        生成所有图表
        Args:
            frames_csv: 帧数据CSV路径
            cars_csv: 车辆数据CSV路径
            orders_csv: 订单数据CSV路径
            grid_size: 网格大小
        """
        print("开始生成所有图表...")

        frames_df, cars_df, orders_df = self.load_data(frames_csv, cars_csv, orders_csv)

        self.plot_order_completion_over_time(frames_df)
        self.plot_efficiency_metrics(frames_df)
        self.plot_distance_statistics(cars_df)
        self.plot_heatmap(cars_df, grid_size)

        if orders_df is not None:
            self.plot_order_waiting_time(orders_df)

        print("所有图表生成完成。")
