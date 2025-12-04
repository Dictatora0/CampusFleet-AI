"""
数据记录模块 - 记录仿真过程中的所有数据并导出为CSV
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class DataLogger:
    """数据记录器 - 记录每一帧的仿真数据"""

    def __init__(self, output_dir: str = "simulation_logs"):
        """
        初始化数据记录器
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 数据存储
        self.frame_data: List[Dict[str, Any]] = []
        self.car_positions: List[Dict[str, Any]] = []
        self.order_events: List[Dict[str, Any]] = []
        self.scheduler_events: List[Dict[str, Any]] = []

        # 元数据
        self.metadata = {
            "start_time": datetime.now().isoformat(),
            "grid_size": None,
            "num_cars": None,
            "scheduling_strategy": None,
        }

    def set_metadata(self, grid_size: int, num_cars: int, strategy: str):
        """设置仿真元数据"""
        self.metadata["grid_size"] = grid_size
        self.metadata["num_cars"] = num_cars
        self.metadata["scheduling_strategy"] = strategy

    def log_frame(self, step: int, cars: List, orders, scheduler):
        """
        记录一帧数据
        Args:
            step: 当前步数
            cars: 车辆列表
            orders: 订单智能体
            scheduler: 调度器
        """
        # 记录整体统计
        frame_stats = {
            "step": step,
            "total_cars": len(cars),
            "idle_cars": sum(1 for car in cars if car.is_idle()),
            "active_cars": sum(1 for car in cars if not car.is_idle()),
            "pending_orders": orders.report()["pending_orders"],
            "assigned_orders": orders.report()["assigned_orders"],
            "completed_orders": orders.report()["completed_orders"],
            "total_distance": sum(car.total_distance for car in cars),
        }
        self.frame_data.append(frame_stats)

        # 记录每辆车的位置和状态
        for car in cars:
            car_data = {
                "step": step,
                "car_id": car.car_id,
                "x": car.position[0],
                "y": car.position[1],
                "state": car.state.value,
                "current_order": car.current_order_id,
                "completed_orders": car.completed_orders,
                "total_distance": car.total_distance,
            }
            self.car_positions.append(car_data)

    def log_order_event(
        self,
        step: int,
        event_type: str,
        order_id: int,
        pickup: tuple = None,
        delivery: tuple = None,
        car_id: int = None,
    ):
        """
        记录订单事件
        Args:
            step: 当前步数
            event_type: 事件类型 (created, assigned, completed, cancelled)
            order_id: 订单ID
            pickup: 取货点
            delivery: 配送点
            car_id: 分配的车辆ID
        """
        event = {
            "step": step,
            "event_type": event_type,
            "order_id": order_id,
            "car_id": car_id,
            "pickup_x": pickup[0] if pickup else None,
            "pickup_y": pickup[1] if pickup else None,
            "delivery_x": delivery[0] if delivery else None,
            "delivery_y": delivery[1] if delivery else None,
        }
        self.order_events.append(event)

    def log_scheduler_event(self, step: int, num_assignments: int, avg_distance: float = None):
        """
        记录调度事件
        Args:
            step: 当前步数
            num_assignments: 分配数量
            avg_distance: 平均分配距离
        """
        event = {"step": step, "num_assignments": num_assignments, "avg_distance": avg_distance}
        self.scheduler_events.append(event)

    def export_to_csv(self, filename_prefix: str = "simulation"):
        """
        导出数据到CSV文件
        Args:
            filename_prefix: 文件名前缀
        Returns:
            导出的文件路径列表
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = []

        # 导出帧数据
        frame_file = self.output_dir / f"{filename_prefix}_frames_{timestamp}.csv"
        if self.frame_data:
            with open(frame_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.frame_data[0].keys())
                writer.writeheader()
                writer.writerows(self.frame_data)
            exported_files.append(str(frame_file))

        # 导出车辆位置数据
        car_file = self.output_dir / f"{filename_prefix}_cars_{timestamp}.csv"
        if self.car_positions:
            with open(car_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.car_positions[0].keys())
                writer.writeheader()
                writer.writerows(self.car_positions)
            exported_files.append(str(car_file))

        # 导出订单事件
        order_file = self.output_dir / f"{filename_prefix}_orders_{timestamp}.csv"
        if self.order_events:
            with open(order_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.order_events[0].keys())
                writer.writeheader()
                writer.writerows(self.order_events)
            exported_files.append(str(order_file))

        # 导出调度事件
        scheduler_file = self.output_dir / f"{filename_prefix}_scheduler_{timestamp}.csv"
        if self.scheduler_events:
            with open(scheduler_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.scheduler_events[0].keys())
                writer.writeheader()
                writer.writerows(self.scheduler_events)
            exported_files.append(str(scheduler_file))

        # 导出元数据
        metadata_file = self.output_dir / f"{filename_prefix}_metadata_{timestamp}.json"
        self.metadata["end_time"] = datetime.now().isoformat()
        self.metadata["total_frames"] = len(self.frame_data)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        exported_files.append(str(metadata_file))

        return exported_files

    def export_to_csv_string(self) -> str:
        """
        导出帧数据为CSV字符串（用于API响应）
        Returns:
            CSV格式的字符串
        """
        if not self.frame_data:
            return ""
        
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.frame_data[0].keys())
        writer.writeheader()
        writer.writerows(self.frame_data)
        return output.getvalue()
    
    def clear(self):
        """清空所有记录的数据"""
        self.frame_data.clear()
        self.car_positions.clear()
        self.order_events.clear()
        self.scheduler_events.clear()

    def get_summary(self) -> Dict[str, Any]:
        """
        获取数据摘要
        Returns:
            数据摘要字典
        """
        return {
            "total_frames": len(self.frame_data),
            "total_car_records": len(self.car_positions),
            "total_order_events": len(self.order_events),
            "total_scheduler_events": len(self.scheduler_events),
            "metadata": self.metadata,
        }
