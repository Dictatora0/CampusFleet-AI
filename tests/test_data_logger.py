"""
数据记录模块的单元测试
"""

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from analytics.data_logger import DataLogger


class TestDataLogger:
    """DataLogger 类测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录fixture"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def logger(self, temp_dir):
        """创建数据记录器fixture"""
        return DataLogger(output_dir=temp_dir)

    def test_initialization(self, logger, temp_dir):
        """测试初始化"""
        assert logger.output_dir == Path(temp_dir)
        assert logger.output_dir.exists()
        assert len(logger.frame_data) == 0
        assert len(logger.car_positions) == 0
        assert len(logger.order_events) == 0
        assert len(logger.scheduler_events) == 0

    def test_initialization_creates_directory(self):
        """测试初始化创建目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "new_logs"
            logger = DataLogger(output_dir=str(test_dir))
            assert test_dir.exists()

    def test_set_metadata(self, logger):
        """测试设置元数据"""
        logger.set_metadata(grid_size=15, num_cars=5, strategy="greedy")

        assert logger.metadata["grid_size"] == 15
        assert logger.metadata["num_cars"] == 5
        assert logger.metadata["scheduling_strategy"] == "greedy"

    def test_log_frame(self, logger):
        """测试记录帧数据"""
        # 创建模拟对象
        mock_car1 = Mock()
        mock_car1.is_idle.return_value = True
        mock_car1.total_distance = 10.5
        mock_car1.car_id = 1
        mock_car1.position = (5, 5)
        mock_car1.state = Mock(value="idle")
        mock_car1.current_order_id = None
        mock_car1.completed_orders = 0

        mock_car2 = Mock()
        mock_car2.is_idle.return_value = False
        mock_car2.total_distance = 20.3
        mock_car2.car_id = 2
        mock_car2.position = (6, 6)
        mock_car2.state = Mock(value="delivering")
        mock_car2.current_order_id = 1
        mock_car2.completed_orders = 2

        cars = [mock_car1, mock_car2]

        mock_orders = Mock()
        mock_orders.report.return_value = {
            "pending_orders": 3,
            "assigned_orders": 2,
            "completed_orders": 5,
        }

        mock_scheduler = Mock()

        # 记录帧
        logger.log_frame(step=10, cars=cars, orders=mock_orders, scheduler=mock_scheduler)

        # 验证帧数据
        assert len(logger.frame_data) == 1
        frame = logger.frame_data[0]
        assert frame["step"] == 10
        assert frame["total_cars"] == 2
        assert frame["idle_cars"] == 1
        assert frame["active_cars"] == 1
        assert frame["pending_orders"] == 3
        assert frame["total_distance"] == pytest.approx(30.8)

        # 验证车辆位置数据
        assert len(logger.car_positions) == 2
        assert any(cp["car_id"] == 1 for cp in logger.car_positions)
        assert any(cp["car_id"] == 2 for cp in logger.car_positions)

    def test_log_multiple_frames(self, logger):
        """测试记录多帧"""
        mock_car = Mock()
        mock_car.is_idle.return_value = True
        mock_car.total_distance = 0
        mock_car.car_id = 1
        mock_car.position = (0, 0)  # 设置为元组
        mock_car.state = Mock(value="idle")
        mock_car.current_order_id = None
        mock_car.completed_orders = 0

        mock_cars = [mock_car]
        mock_orders = Mock(
            report=Mock(
                return_value={"pending_orders": 0, "assigned_orders": 0, "completed_orders": 0}
            )
        )
        mock_scheduler = Mock()

        for step in range(5):
            logger.log_frame(
                step=step, cars=mock_cars, orders=mock_orders, scheduler=mock_scheduler
            )

        assert len(logger.frame_data) == 5
        assert [f["step"] for f in logger.frame_data] == [0, 1, 2, 3, 4]

    def test_log_order_event(self, logger):
        """测试记录订单事件"""
        logger.log_order_event(
            step=10, event_type="created", order_id=1, pickup=(0, 0), delivery=(5, 5)
        )

        assert len(logger.order_events) == 1
        event = logger.order_events[0]
        assert event["step"] == 10
        assert event["event_type"] == "created"
        assert event["order_id"] == 1
        assert event["pickup_x"] == 0
        assert event["pickup_y"] == 0
        assert event["delivery_x"] == 5
        assert event["delivery_y"] == 5

    def test_log_order_event_assigned(self, logger):
        """测试记录订单分配事件"""
        logger.log_order_event(step=15, event_type="assigned", order_id=2, car_id=10)

        event = logger.order_events[0]
        assert event["event_type"] == "assigned"
        assert event["car_id"] == 10
        assert event["pickup_x"] is None

    def test_log_scheduler_event(self, logger):
        """测试记录调度事件"""
        logger.log_scheduler_event(step=20, num_assignments=3, avg_distance=12.5)

        assert len(logger.scheduler_events) == 1
        event = logger.scheduler_events[0]
        assert event["step"] == 20
        assert event["num_assignments"] == 3
        assert event["avg_distance"] == 12.5

    def test_export_to_csv(self, logger, temp_dir):
        """测试导出CSV文件"""
        # 添加一些数据
        logger.set_metadata(15, 5, "greedy")

        # 添加帧数据
        logger.frame_data.append(
            {
                "step": 0,
                "total_cars": 5,
                "idle_cars": 3,
                "active_cars": 2,
                "pending_orders": 2,
                "assigned_orders": 1,
                "completed_orders": 0,
                "total_distance": 10.5,
            }
        )

        # 添加车辆数据
        logger.car_positions.append(
            {
                "step": 0,
                "car_id": 1,
                "x": 5,
                "y": 5,
                "state": "idle",
                "current_order": None,
                "completed_orders": 0,
                "total_distance": 0,
            }
        )

        # 添加订单事件
        logger.order_events.append(
            {
                "step": 0,
                "event_type": "created",
                "order_id": 1,
                "car_id": None,
                "pickup_x": 0,
                "pickup_y": 0,
                "delivery_x": 5,
                "delivery_y": 5,
            }
        )

        # 添加调度事件
        logger.scheduler_events.append({"step": 0, "num_assignments": 1, "avg_distance": 10.0})

        # 导出
        exported_files = logger.export_to_csv(filename_prefix="test")

        assert len(exported_files) == 5  # frames, cars, orders, scheduler, metadata
        assert all(Path(f).exists() for f in exported_files)

    def test_export_csv_content(self, logger, temp_dir):
        """测试导出CSV内容正确性"""
        logger.frame_data.append({"step": 0, "total_cars": 5})

        exported_files = logger.export_to_csv("test")

        # 找到frames文件
        frames_file = [f for f in exported_files if "frames" in f][0]

        # 读取并验证
        with open(frames_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["step"] == "0"
            assert rows[0]["total_cars"] == "5"

    def test_export_metadata_json(self, logger, temp_dir):
        """测试元数据JSON导出"""
        logger.set_metadata(15, 5, "greedy")
        logger.frame_data.append({"step": 0})

        exported_files = logger.export_to_csv("test")

        # 找到metadata文件
        metadata_file = [f for f in exported_files if "metadata" in f][0]

        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["grid_size"] == 15
            assert data["num_cars"] == 5
            assert data["scheduling_strategy"] == "greedy"
            assert "start_time" in data
            assert "end_time" in data
            assert data["total_frames"] == 1

    def test_clear(self, logger):
        """测试清空数据"""
        logger.frame_data.append({"step": 0})
        logger.car_positions.append({"car_id": 1})
        logger.order_events.append({"event_type": "created"})
        logger.scheduler_events.append({"num_assignments": 1})

        logger.clear()

        assert len(logger.frame_data) == 0
        assert len(logger.car_positions) == 0
        assert len(logger.order_events) == 0
        assert len(logger.scheduler_events) == 0

    def test_get_summary(self, logger):
        """测试获取摘要"""
        logger.set_metadata(15, 5, "greedy")
        logger.frame_data.append({"step": 0})
        logger.frame_data.append({"step": 1})
        logger.car_positions.append({"car_id": 1})
        logger.order_events.append({"event_type": "created"})
        logger.scheduler_events.append({"num_assignments": 1})

        summary = logger.get_summary()

        assert summary["total_frames"] == 2
        assert summary["total_car_records"] == 1
        assert summary["total_order_events"] == 1
        assert summary["total_scheduler_events"] == 1
        assert summary["metadata"]["grid_size"] == 15


class TestDataLoggerEdgeCases:
    """边界情况测试"""

    def test_export_empty_data(self):
        """测试导出空数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DataLogger(output_dir=tmpdir)
            exported_files = logger.export_to_csv("empty")

            # 应该只有metadata文件
            assert len(exported_files) == 1
            assert "metadata" in exported_files[0]

    def test_large_number_of_frames(self):
        """测试大量帧数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DataLogger(output_dir=tmpdir)

            mock_car = Mock()
            mock_car.is_idle.return_value = True
            mock_car.total_distance = 0
            mock_car.car_id = 1
            mock_car.position = (0, 0)
            mock_car.state = Mock(value="idle")
            mock_car.current_order_id = None
            mock_car.completed_orders = 0

            mock_cars = [mock_car]
            mock_orders = Mock(
                report=Mock(
                    return_value={"pending_orders": 0, "assigned_orders": 0, "completed_orders": 0}
                )
            )
            mock_scheduler = Mock()

            # 记录1000帧
            for i in range(1000):
                logger.log_frame(
                    step=i, cars=mock_cars, orders=mock_orders, scheduler=mock_scheduler
                )

            assert len(logger.frame_data) == 1000

            # 导出应该成功
            exported_files = logger.export_to_csv("large")
            assert len(exported_files) > 0

    def test_special_characters_in_directory(self):
        """测试目录名包含特殊字符"""
        with tempfile.TemporaryDirectory() as tmpdir:
            special_dir = Path(tmpdir) / "logs_测试_123"
            logger = DataLogger(output_dir=str(special_dir))
            assert special_dir.exists()

    def test_multiple_exports(self):
        """测试多次导出"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DataLogger(output_dir=tmpdir)
            logger.frame_data.append({"step": 0})

            files1 = logger.export_to_csv("test1")
            files2 = logger.export_to_csv("test2")

            # 应该生成不同的文件
            assert files1 != files2
            assert all(Path(f).exists() for f in files1)
            assert all(Path(f).exists() for f in files2)


class TestDataLoggerIntegration:
    """集成测试"""

    def test_complete_simulation_workflow(self):
        """测试完整仿真流程"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DataLogger(output_dir=tmpdir)

            # 设置元数据
            logger.set_metadata(15, 3, "greedy")

            # 模拟几步
            for step in range(5):
                # 创建模拟车辆
                cars = []
                for i in range(3):
                    car = Mock()
                    car.is_idle.return_value = (step + i) % 2 == 0
                    car.total_distance = step * (i + 1)
                    car.car_id = i
                    car.position = (step, i)
                    car.state = Mock(value="idle" if car.is_idle() else "busy")
                    car.current_order_id = None if car.is_idle() else i
                    car.completed_orders = step
                    cars.append(car)

                # 模拟订单系统
                orders = Mock()
                orders.report.return_value = {
                    "pending_orders": max(0, 5 - step),
                    "assigned_orders": min(step, 3),
                    "completed_orders": step * 2,
                }

                scheduler = Mock()

                # 记录帧
                logger.log_frame(step=step, cars=cars, orders=orders, scheduler=scheduler)

                # 记录一些事件
                if step % 2 == 0:
                    logger.log_order_event(
                        step=step,
                        event_type="created",
                        order_id=step,
                        pickup=(step, 0),
                        delivery=(step, 5),
                    )

                if step > 0:
                    logger.log_scheduler_event(
                        step=step, num_assignments=step % 3, avg_distance=10.0 + step
                    )

            # 导出数据
            exported_files = logger.export_to_csv("simulation")

            # 验证导出
            assert len(exported_files) == 5

            # 验证frames文件
            frames_file = [f for f in exported_files if "frames" in f][0]
            with open(frames_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 5

            # 验证cars文件
            cars_file = [f for f in exported_files if "cars" in f][0]
            with open(cars_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 15  # 5 steps * 3 cars

            # 获取摘要
            summary = logger.get_summary()
            assert summary["total_frames"] == 5
            assert summary["total_car_records"] == 15

    def test_clear_and_reuse(self):
        """测试清空后重新使用"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DataLogger(output_dir=tmpdir)

            # 第一轮记录
            logger.frame_data.append({"step": 0})
            assert len(logger.frame_data) == 1

            # 清空
            logger.clear()
            assert len(logger.frame_data) == 0

            # 第二轮记录
            logger.frame_data.append({"step": 100})
            assert len(logger.frame_data) == 1
            assert logger.frame_data[0]["step"] == 100

    def test_concurrent_data_types(self):
        """测试同时记录多种数据类型"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = DataLogger(output_dir=tmpdir)

            # 同时记录各种事件
            logger.log_order_event(0, "created", 1, (0, 0), (5, 5))
            logger.log_order_event(1, "assigned", 1, car_id=1)
            logger.log_order_event(2, "completed", 1)

            logger.log_scheduler_event(0, 1, 10.0)
            logger.log_scheduler_event(1, 2, 15.0)

            # 验证数据独立性
            assert len(logger.order_events) == 3
            assert len(logger.scheduler_events) == 2

            # 导出验证
            exported_files = logger.export_to_csv("concurrent")
            assert any("orders" in f for f in exported_files)
            assert any("scheduler" in f for f in exported_files)
