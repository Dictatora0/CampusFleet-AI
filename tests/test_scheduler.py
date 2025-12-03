"""
测试调度智能体模块
测试 SchedulerAgent 的不同调度策略
"""

import pytest

from agents import CarAgent, OrderAgent, SchedulerAgent, SchedulingStrategy
from env import GridEnvironment


@pytest.fixture
def grid_env():
    """创建测试用的网格环境"""
    return GridEnvironment(size=15)


@pytest.fixture
def scheduler_greedy():
    """创建使用贪心策略的调度器"""
    return SchedulerAgent(strategy=SchedulingStrategy.GREEDY_NEAREST)


@pytest.fixture
def scheduler_balanced():
    """创建使用负载均衡策略的调度器"""
    return SchedulerAgent(strategy=SchedulingStrategy.BALANCED_LOAD)


@pytest.fixture
def scheduler_hungarian():
    """创建使用匈牙利算法的调度器"""
    return SchedulerAgent(strategy=SchedulingStrategy.HUNGARIAN)


@pytest.fixture
def sample_cars():
    """创建一组测试用的车辆"""
    return [
        CarAgent(car_id=0, initial_position=(0, 0)),
        CarAgent(car_id=1, initial_position=(5, 5)),
        CarAgent(car_id=2, initial_position=(10, 10)),
    ]


@pytest.fixture
def sample_orders():
    """创建一组测试用的订单"""
    order_agent = OrderAgent()
    orders = []
    orders.append(order_agent.create_order((1, 1), (3, 3)))
    orders.append(order_agent.create_order((6, 6), (8, 8)))
    orders.append(order_agent.create_order((11, 11), (13, 13)))
    return order_agent.get_pending_orders()


class TestSchedulerInitialization:
    """测试调度器初始化"""

    def test_greedy_initialization(self, scheduler_greedy):
        """测试贪心策略初始化"""
        assert scheduler_greedy.strategy == SchedulingStrategy.GREEDY_NEAREST
        assert scheduler_greedy.total_assignments == 0
        assert len(scheduler_greedy.assignment_history) == 0

    def test_balanced_initialization(self, scheduler_balanced):
        """测试负载均衡策略初始化"""
        assert scheduler_balanced.strategy == SchedulingStrategy.BALANCED_LOAD
        assert scheduler_balanced.total_assignments == 0

    def test_hungarian_initialization(self, scheduler_hungarian):
        """测试匈牙利算法初始化"""
        assert scheduler_hungarian.strategy == SchedulingStrategy.HUNGARIAN
        assert scheduler_hungarian.total_assignments == 0

    def test_default_strategy(self):
        """测试默认策略"""
        scheduler = SchedulerAgent()
        assert scheduler.strategy == SchedulingStrategy.GREEDY_NEAREST


class TestSchedulerBasicFunctionality:
    """测试调度器基本功能"""

    def test_reset(self, scheduler_greedy):
        """测试重置功能"""
        scheduler_greedy.total_assignments = 10
        scheduler_greedy.assignment_history.append({"test": "data"})

        scheduler_greedy.reset()

        assert scheduler_greedy.total_assignments == 0
        assert len(scheduler_greedy.assignment_history) == 0

    def test_get_strategy_name(self, scheduler_greedy):
        """测试获取策略名称"""
        name = scheduler_greedy.get_strategy_name()
        assert name == "贪心最近"

    def test_set_strategy(self, scheduler_greedy):
        """测试设置策略"""
        scheduler_greedy.set_strategy(SchedulingStrategy.BALANCED_LOAD)
        assert scheduler_greedy.strategy == SchedulingStrategy.BALANCED_LOAD

    def test_report(self, scheduler_greedy):
        """测试报告功能"""
        report = scheduler_greedy.report()
        assert "strategy" in report
        assert "total_assignments" in report
        assert "history_length" in report
        assert report["total_assignments"] == 0


class TestGreedyStrategy:
    """测试贪心最近策略"""

    def test_schedule_single_order(self, scheduler_greedy, sample_cars, grid_env):
        """测试单个订单的调度"""
        order_agent = OrderAgent()
        order_agent.create_order((1, 1), (3, 3))
        orders = order_agent.get_pending_orders()

        assignments = scheduler_greedy.schedule(sample_cars, orders, grid_env)

        assert len(assignments) == 1
        car_id, order_id, pickup, delivery = assignments[0]
        assert car_id in [0, 1, 2]
        assert pickup == (1, 1)
        assert delivery == (3, 3)

    def test_schedule_multiple_orders(self, scheduler_greedy, sample_cars, sample_orders, grid_env):
        """测试多个订单的调度"""
        assignments = scheduler_greedy.schedule(sample_cars, sample_orders, grid_env)

        assert len(assignments) == 3  # 3个订单，3辆车

        # 检查每辆车只被分配一个订单
        assigned_cars = [a[0] for a in assignments]
        assert len(assigned_cars) == len(set(assigned_cars))

    def test_schedule_more_orders_than_cars(self, scheduler_greedy, sample_cars, grid_env):
        """测试订单多于车辆的情况"""
        order_agent = OrderAgent()
        for i in range(5):
            order_agent.create_order((i, i), (i + 2, i + 2))
        orders = order_agent.get_pending_orders()

        assignments = scheduler_greedy.schedule(sample_cars, orders, grid_env)

        # 只能分配3个订单给3辆车
        assert len(assignments) == 3

    def test_schedule_no_idle_cars(self, scheduler_greedy, sample_orders, grid_env):
        """测试没有空闲车辆的情况"""
        # 创建忙碌的车辆
        busy_cars = [
            CarAgent(car_id=0, initial_position=(0, 0)),
            CarAgent(car_id=1, initial_position=(5, 5)),
        ]
        for car in busy_cars:
            car.assign_task(order_id=99, pickup=(1, 1), delivery=(2, 2))

        assignments = scheduler_greedy.schedule(busy_cars, sample_orders, grid_env)

        assert len(assignments) == 0

    def test_schedule_empty_orders(self, scheduler_greedy, sample_cars, grid_env):
        """测试空订单列表"""
        assignments = scheduler_greedy.schedule(sample_cars, [], grid_env)
        assert len(assignments) == 0

    def test_greedy_selects_nearest(self, scheduler_greedy, grid_env):
        """测试贪心策略选择最近的车辆"""
        cars = [
            CarAgent(car_id=0, initial_position=(0, 0)),
            CarAgent(car_id=1, initial_position=(10, 10)),
        ]
        order_agent = OrderAgent()
        order_agent.create_order((1, 1), (3, 3))  # 更接近car 0
        orders = order_agent.get_pending_orders()

        assignments = scheduler_greedy.schedule(cars, orders, grid_env)

        assert len(assignments) == 1
        assert assignments[0][0] == 0  # 应该分配给car 0


class TestBalancedLoadStrategy:
    """测试负载均衡策略"""

    def test_balanced_considers_workload(self, scheduler_balanced, grid_env):
        """测试负载均衡考虑车辆工作量"""
        cars = [
            CarAgent(car_id=0, initial_position=(0, 0)),
            CarAgent(car_id=1, initial_position=(5, 5)),
        ]
        # 设置不同的完成订单数
        cars[0].completed_orders = 5
        cars[1].completed_orders = 1

        order_agent = OrderAgent()
        order_agent.create_order((3, 3), (6, 6))
        orders = order_agent.get_pending_orders()

        assignments = scheduler_balanced.schedule(cars, orders, grid_env)

        assert len(assignments) == 1
        # 应该优先分配给完成订单少的车辆（car 1）
        assert assignments[0][0] == 1

    def test_balanced_with_equal_workload(self, scheduler_balanced, grid_env):
        """测试相同工作量时的负载均衡"""
        cars = [
            CarAgent(car_id=0, initial_position=(1, 1)),
            CarAgent(car_id=1, initial_position=(10, 10)),
        ]
        # 相同的完成订单数
        cars[0].completed_orders = 3
        cars[1].completed_orders = 3

        order_agent = OrderAgent()
        order_agent.create_order((2, 2), (5, 5))  # 更接近car 0
        orders = order_agent.get_pending_orders()

        assignments = scheduler_balanced.schedule(cars, orders, grid_env)

        assert len(assignments) == 1
        # 相同工作量时，应该选择最近的（car 0）
        assert assignments[0][0] == 0


class TestHungarianStrategy:
    """测试匈牙利算法策略"""

    def test_hungarian_basic_scheduling(
        self, scheduler_hungarian, sample_cars, sample_orders, grid_env
    ):
        """测试匈牙利算法的基本调度"""
        assignments = scheduler_hungarian.schedule(sample_cars, sample_orders, grid_env)

        # 应该返回分配结果
        assert len(assignments) > 0
        assert len(assignments) <= min(len(sample_cars), len(sample_orders))

    def test_hungarian_with_single_order(self, scheduler_hungarian, sample_cars, grid_env):
        """测试单个订单的匈牙利算法"""
        order_agent = OrderAgent()
        order_agent.create_order((5, 5), (8, 8))
        orders = order_agent.get_pending_orders()

        assignments = scheduler_hungarian.schedule(sample_cars, orders, grid_env)

        assert len(assignments) == 1


class TestSchedulingWithAssignmentTracking:
    """测试调度的分配跟踪"""

    def test_assignment_history_tracking(
        self, scheduler_greedy, sample_cars, sample_orders, grid_env
    ):
        """测试分配历史跟踪"""
        initial_history_len = len(scheduler_greedy.assignment_history)

        assignments = scheduler_greedy.schedule(sample_cars, sample_orders, grid_env)

        if len(assignments) > 0:
            assert len(scheduler_greedy.assignment_history) == initial_history_len + 1
            last_history = scheduler_greedy.assignment_history[-1]
            assert "assignments" in last_history
            assert "strategy" in last_history

    def test_total_assignments_counter(self, scheduler_greedy, sample_cars, grid_env):
        """测试总分配次数计数"""
        initial_count = scheduler_greedy.total_assignments

        order_agent = OrderAgent()
        order_agent.create_order((1, 1), (3, 3))
        order_agent.create_order((6, 6), (8, 8))
        orders = order_agent.get_pending_orders()

        assignments = scheduler_greedy.schedule(sample_cars, orders, grid_env)

        # 总分配次数应该增加
        assert scheduler_greedy.total_assignments == initial_count + len(assignments)


class TestSchedulingEdgeCases:
    """测试调度边界情况"""

    def test_schedule_with_one_car(self, scheduler_greedy, sample_orders, grid_env):
        """测试只有一辆车的情况"""
        single_car = [CarAgent(car_id=0, initial_position=(5, 5))]

        assignments = scheduler_greedy.schedule(single_car, sample_orders, grid_env)

        # 一辆车只能接一个订单
        assert len(assignments) == 1

    def test_schedule_with_one_order(self, scheduler_greedy, sample_cars, grid_env):
        """测试只有一个订单的情况"""
        order_agent = OrderAgent()
        order_agent.create_order((5, 5), (8, 8))
        single_order = order_agent.get_pending_orders()

        assignments = scheduler_greedy.schedule(sample_cars, single_order, grid_env)

        assert len(assignments) == 1

    def test_schedule_preserves_order_data(self, scheduler_greedy, sample_cars, grid_env):
        """测试调度保留订单数据"""
        order_agent = OrderAgent()
        order_agent.create_order((2, 2), (7, 7))
        orders = order_agent.get_pending_orders()
        original_order = orders[0]

        assignments = scheduler_greedy.schedule(sample_cars, orders, grid_env)

        if len(assignments) > 0:
            _, order_id, pickup, delivery = assignments[0]
            assert order_id == original_order.order_id
            assert pickup == original_order.pickup_point
            assert delivery == original_order.delivery_point


class TestStrategyComparison:
    """测试不同策略的比较"""

    def test_all_strategies_produce_valid_assignments(self, sample_cars, sample_orders, grid_env):
        """测试所有策略都产生有效分配"""
        strategies = [
            SchedulingStrategy.GREEDY_NEAREST,
            SchedulingStrategy.BALANCED_LOAD,
            SchedulingStrategy.HUNGARIAN,
        ]

        for strategy in strategies:
            scheduler = SchedulerAgent(strategy=strategy)
            assignments = scheduler.schedule(sample_cars, sample_orders, grid_env)

            # 验证分配结果的有效性
            assert isinstance(assignments, list)
            for assignment in assignments:
                assert len(assignment) == 4
                car_id, order_id, pickup, delivery = assignment
                assert isinstance(car_id, int)
                assert isinstance(order_id, int)
                assert isinstance(pickup, tuple)
                assert isinstance(delivery, tuple)


class TestSchedulerStepMethod:
    """测试调度器的step方法"""

    def test_step_method(self, scheduler_greedy):
        """测试step方法（当前为空实现）"""
        # 应该不抛出异常
        scheduler_greedy.step()
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
