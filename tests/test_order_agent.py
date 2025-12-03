"""
订单智能体模块的单元测试
"""

import time

import pytest

from agents.order_agent import Order, OrderAgent, OrderStatus


class TestOrderStatus:
    """OrderStatus 枚举测试"""

    def test_status_values(self):
        """测试状态值"""
        assert OrderStatus.PENDING.value == "待分配"
        assert OrderStatus.ASSIGNED.value == "已分配"
        assert OrderStatus.IN_TRANSIT.value == "运输中"
        assert OrderStatus.COMPLETED.value == "已完成"
        assert OrderStatus.CANCELLED.value == "已取消"

    def test_status_comparison(self):
        """测试状态比较"""
        assert OrderStatus.PENDING == OrderStatus.PENDING
        assert OrderStatus.PENDING != OrderStatus.ASSIGNED


class TestOrder:
    """Order 数据类测试"""

    def test_order_creation(self):
        """测试订单创建"""
        order = Order(
            order_id=1, pickup_point=(0, 0), delivery_point=(5, 5), status=OrderStatus.PENDING
        )
        assert order.order_id == 1
        assert order.pickup_point == (0, 0)
        assert order.delivery_point == (5, 5)
        assert order.status == OrderStatus.PENDING
        assert order.assigned_car_id is None

    def test_order_with_car_assignment(self):
        """测试带车辆分配的订单"""
        order = Order(
            order_id=2,
            pickup_point=(1, 1),
            delivery_point=(6, 6),
            status=OrderStatus.ASSIGNED,
            assigned_car_id=5,
        )
        assert order.assigned_car_id == 5
        assert order.status == OrderStatus.ASSIGNED

    def test_order_auto_timestamp(self):
        """测试自动时间戳"""
        before = time.time()
        order = Order(
            order_id=1, pickup_point=(0, 0), delivery_point=(5, 5), status=OrderStatus.PENDING
        )
        after = time.time()

        assert before <= order.created_time <= after

    def test_order_custom_timestamp(self):
        """测试自定义时间戳"""
        custom_time = 1000.0
        order = Order(
            order_id=1,
            pickup_point=(0, 0),
            delivery_point=(5, 5),
            status=OrderStatus.PENDING,
            created_time=custom_time,
        )
        assert order.created_time == custom_time


class TestOrderAgent:
    """OrderAgent 类测试"""

    @pytest.fixture
    def agent(self):
        """创建订单智能体fixture"""
        return OrderAgent()

    def test_initialization(self, agent):
        """测试初始化"""
        assert len(agent.orders) == 0
        assert agent.next_order_id == 1
        assert len(agent.pending_orders) == 0

    def test_create_order(self, agent):
        """测试创建订单"""
        order_id = agent.create_order((0, 0), (5, 5))

        assert order_id == 1
        assert order_id in agent.orders
        assert order_id in agent.pending_orders

        order = agent.orders[order_id]
        assert order.pickup_point == (0, 0)
        assert order.delivery_point == (5, 5)
        assert order.status == OrderStatus.PENDING

    def test_create_multiple_orders(self, agent):
        """测试创建多个订单"""
        id1 = agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))
        id3 = agent.create_order((2, 2), (7, 7))

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3
        assert len(agent.orders) == 3
        assert len(agent.pending_orders) == 3

    def test_assign_order(self, agent):
        """测试分配订单"""
        order_id = agent.create_order((0, 0), (5, 5))

        result = agent.assign_order(order_id, car_id=10)
        assert result is True

        order = agent.orders[order_id]
        assert order.status == OrderStatus.ASSIGNED
        assert order.assigned_car_id == 10
        assert order.assigned_time > 0
        assert order_id not in agent.pending_orders

    def test_assign_nonexistent_order(self, agent):
        """测试分配不存在的订单"""
        result = agent.assign_order(999, car_id=10)
        assert result is False

    def test_assign_already_assigned_order(self, agent):
        """测试重复分配订单"""
        order_id = agent.create_order((0, 0), (5, 5))
        agent.assign_order(order_id, car_id=10)

        # 尝试再次分配
        result = agent.assign_order(order_id, car_id=20)
        assert result is False

        # 车辆ID不应改变
        assert agent.orders[order_id].assigned_car_id == 10

    def test_update_order_status(self, agent):
        """测试更新订单状态"""
        order_id = agent.create_order((0, 0), (5, 5))

        result = agent.update_order_status(order_id, OrderStatus.IN_TRANSIT)
        assert result is True
        assert agent.orders[order_id].status == OrderStatus.IN_TRANSIT

    def test_update_nonexistent_order_status(self, agent):
        """测试更新不存在订单的状态"""
        result = agent.update_order_status(999, OrderStatus.COMPLETED)
        assert result is False

    def test_complete_order(self, agent):
        """测试完成订单"""
        order_id = agent.create_order((0, 0), (5, 5))
        agent.assign_order(order_id, car_id=10)

        before = time.time()
        result = agent.complete_order(order_id)
        after = time.time()

        assert result is True
        order = agent.orders[order_id]
        assert order.status == OrderStatus.COMPLETED
        assert before <= order.completed_time <= after

    def test_cancel_order(self, agent):
        """测试取消订单"""
        order_id = agent.create_order((0, 0), (5, 5))

        result = agent.cancel_order(order_id)
        assert result is True
        assert agent.orders[order_id].status == OrderStatus.CANCELLED
        assert order_id not in agent.pending_orders

    def test_cancel_assigned_order(self, agent):
        """测试取消已分配的订单"""
        order_id = agent.create_order((0, 0), (5, 5))
        agent.assign_order(order_id, car_id=10)

        result = agent.cancel_order(order_id)
        assert result is True
        assert agent.orders[order_id].status == OrderStatus.CANCELLED

    def test_get_pending_orders(self, agent):
        """测试获取待分配订单"""
        id1 = agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))
        agent.assign_order(id2, car_id=10)

        pending = agent.get_pending_orders()
        assert len(pending) == 1
        assert pending[0].order_id == id1

    def test_get_order(self, agent):
        """测试获取指定订单"""
        order_id = agent.create_order((0, 0), (5, 5))

        order = agent.get_order(order_id)
        assert order is not None
        assert order.order_id == order_id

        nonexistent = agent.get_order(999)
        assert nonexistent is None

    def test_get_orders_by_status(self, agent):
        """测试根据状态获取订单"""
        id1 = agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))
        id3 = agent.create_order((2, 2), (7, 7))

        agent.assign_order(id2, car_id=10)
        agent.complete_order(id3)

        pending = agent.get_orders_by_status(OrderStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].order_id == id1

        assigned = agent.get_orders_by_status(OrderStatus.ASSIGNED)
        assert len(assigned) == 1
        assert assigned[0].order_id == id2

    def test_get_orders_by_car(self, agent):
        """测试获取车辆的订单"""
        id1 = agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))
        id3 = agent.create_order((2, 2), (7, 7))

        agent.assign_order(id1, car_id=10)
        agent.assign_order(id2, car_id=10)
        agent.assign_order(id3, car_id=20)

        car10_orders = agent.get_orders_by_car(10)
        assert len(car10_orders) == 2
        assert all(o.assigned_car_id == 10 for o in car10_orders)

        car20_orders = agent.get_orders_by_car(20)
        assert len(car20_orders) == 1
        assert car20_orders[0].order_id == id3

    def test_get_orders_by_car_excludes_completed(self, agent):
        """测试获取车辆订单时排除已完成订单"""
        id1 = agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))

        agent.assign_order(id1, car_id=10)
        agent.assign_order(id2, car_id=10)
        agent.complete_order(id1)

        car_orders = agent.get_orders_by_car(10)
        assert len(car_orders) == 1
        assert car_orders[0].order_id == id2

    def test_reset(self, agent):
        """测试重置"""
        agent.create_order((0, 0), (5, 5))
        agent.create_order((1, 1), (6, 6))

        agent.reset()

        assert len(agent.orders) == 0
        assert agent.next_order_id == 1
        assert len(agent.pending_orders) == 0

    def test_step(self, agent):
        """测试step方法"""
        agent.create_order((0, 0), (5, 5))
        # step方法当前是空的，只测试不报错
        agent.step()

    def test_report(self, agent):
        """测试报告功能"""
        agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))
        id3 = agent.create_order((2, 2), (7, 7))

        agent.assign_order(id2, car_id=10)
        # complete_order 只改变状态，不从 pending_orders 移除
        # 所以我们需要先 assign 再 complete
        agent.assign_order(id3, car_id=10)
        agent.complete_order(id3)

        report = agent.report()

        assert report["total_orders"] == 3
        assert report["pending_orders"] == 1  # 只有 id1 pending
        assert report["assigned_orders"] == 1  # id2 assigned
        assert report["completed_orders"] == 1  # id3 completed
        assert report["status_counts"]["pending"] == 1
        assert report["status_counts"]["assigned"] == 1
        assert report["status_counts"]["completed"] == 1

    def test_get_orders_summary_empty(self, agent):
        """测试空订单摘要"""
        summary = agent.get_orders_summary()
        assert "暂无订单" in summary

    def test_get_orders_summary_with_orders(self, agent):
        """测试有订单的摘要"""
        agent.create_order((0, 0), (5, 5))
        agent.create_order((1, 1), (6, 6))

        summary = agent.get_orders_summary()
        assert "总订单数: 2" in summary
        assert "待分配: 2" in summary

    def test_get_orders_summary_with_active_orders(self, agent):
        """测试活跃订单摘要"""
        id1 = agent.create_order((0, 0), (5, 5))
        agent.assign_order(id1, car_id=10)

        summary = agent.get_orders_summary()
        assert "进行中订单" in summary
        assert "车辆10" in summary


class TestOrderAgentEdgeCases:
    """边界情况测试"""

    def test_many_orders(self):
        """测试大量订单"""
        agent = OrderAgent()
        num_orders = 1000

        for i in range(num_orders):
            agent.create_order((i % 10, i % 10), ((i + 5) % 10, (i + 5) % 10))

        assert len(agent.orders) == num_orders
        assert agent.next_order_id == num_orders + 1

    def test_order_id_sequence(self):
        """测试订单ID序列"""
        agent = OrderAgent()
        ids = [agent.create_order((0, 0), (5, 5)) for _ in range(10)]
        assert ids == list(range(1, 11))

    def test_multiple_status_transitions(self):
        """测试多次状态转换"""
        agent = OrderAgent()
        order_id = agent.create_order((0, 0), (5, 5))

        # PENDING -> ASSIGNED -> IN_TRANSIT -> COMPLETED
        agent.update_order_status(order_id, OrderStatus.ASSIGNED)
        assert agent.orders[order_id].status == OrderStatus.ASSIGNED

        agent.update_order_status(order_id, OrderStatus.IN_TRANSIT)
        assert agent.orders[order_id].status == OrderStatus.IN_TRANSIT

        agent.complete_order(order_id)
        assert agent.orders[order_id].status == OrderStatus.COMPLETED

    def test_cancelled_order_not_in_pending(self):
        """测试取消的订单不在待分配列表中"""
        agent = OrderAgent()
        order_id = agent.create_order((0, 0), (5, 5))
        agent.cancel_order(order_id)

        assert order_id not in agent.pending_orders
        assert agent.orders[order_id].status == OrderStatus.CANCELLED


class TestOrderAgentIntegration:
    """集成测试"""

    def test_complete_order_lifecycle(self):
        """测试完整订单生命周期"""
        agent = OrderAgent()

        # 创建订单
        order_id = agent.create_order((0, 0), (5, 5))
        assert agent.orders[order_id].status == OrderStatus.PENDING

        # 分配订单
        agent.assign_order(order_id, car_id=10)
        assert agent.orders[order_id].status == OrderStatus.ASSIGNED
        assert agent.orders[order_id].assigned_car_id == 10

        # 运输中
        agent.update_order_status(order_id, OrderStatus.IN_TRANSIT)
        assert agent.orders[order_id].status == OrderStatus.IN_TRANSIT

        # 完成
        agent.complete_order(order_id)
        assert agent.orders[order_id].status == OrderStatus.COMPLETED
        assert agent.orders[order_id].completed_time > 0

    def test_multiple_cars_workflow(self):
        """测试多车辆工作流"""
        agent = OrderAgent()

        # 创建多个订单
        orders = [agent.create_order((i, i), (i + 5, i + 5)) for i in range(6)]

        # 分配给不同车辆
        agent.assign_order(orders[0], car_id=1)
        agent.assign_order(orders[1], car_id=1)
        agent.assign_order(orders[2], car_id=2)
        agent.assign_order(orders[3], car_id=2)
        # 保留2个未分配

        # 检查各车辆的订单
        car1_orders = agent.get_orders_by_car(1)
        car2_orders = agent.get_orders_by_car(2)
        pending = agent.get_pending_orders()

        assert len(car1_orders) == 2
        assert len(car2_orders) == 2
        assert len(pending) == 2

        # 完成一些订单
        agent.complete_order(orders[0])
        agent.complete_order(orders[2])

        # 再次检查
        car1_orders = agent.get_orders_by_car(1)
        car2_orders = agent.get_orders_by_car(2)

        assert len(car1_orders) == 1  # 排除已完成的
        assert len(car2_orders) == 1

    def test_report_consistency(self):
        """测试报告一致性"""
        agent = OrderAgent()

        # 创建不同状态的订单
        agent.create_order((0, 0), (5, 5))
        id2 = agent.create_order((1, 1), (6, 6))
        id3 = agent.create_order((2, 2), (7, 7))
        id4 = agent.create_order((3, 3), (8, 8))
        id5 = agent.create_order((4, 4), (9, 9))

        agent.assign_order(id2, car_id=10)
        agent.update_order_status(id3, OrderStatus.IN_TRANSIT)
        agent.complete_order(id4)
        agent.cancel_order(id5)

        report = agent.report()

        # 验证总数
        assert report["total_orders"] == 5

        # 验证各状态数量
        assert report["status_counts"]["pending"] == 1
        assert report["status_counts"]["assigned"] == 1
        assert report["status_counts"]["in_transit"] == 1
        assert report["status_counts"]["completed"] == 1
        assert report["status_counts"]["cancelled"] == 1

        # 验证总和
        total = sum(report["status_counts"].values())
        assert total == report["total_orders"]
