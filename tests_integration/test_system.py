#!/usr/bin/env python3
"""
系统集成测试 - 验证所有模块协同工作
使用 pytest 框架进行自动化测试

运行方式:
    pytest test_system.py -v
    pytest test_system.py -v --cov=. --cov-report=html
"""

import pytest


def test_imports():
    """测试所有模块导入"""
    from agents import CarAgent, OrderAgent, SchedulerAgent
    from core import Simulation, SimulationContext
    from env import GridEnvironment, PathFinding

    # 验证类是否正确导入
    assert CarAgent is not None
    assert OrderAgent is not None
    assert SchedulerAgent is not None
    assert GridEnvironment is not None
    assert PathFinding is not None
    assert SimulationContext is not None
    assert Simulation is not None


def test_environment():
    """测试环境模块"""
    from env import GridEnvironment, PathFinding

    # 创建环境
    env = GridEnvironment(size=15)
    assert env is not None
    assert env.size == 15
    assert len(env.grid) == 15
    assert len(env.grid[0]) == 15

    # 测试路径规划
    pathfinder = PathFinding(env.grid)
    assert pathfinder is not None

    path = pathfinder.a_star((0, 0), (14, 14))
    assert path is not None, "A*路径规划应该找到一条路径"
    assert len(path) > 0, "路径长度应该大于0"
    assert path[0] == (0, 0), "路径起点应该是(0, 0)"
    assert path[-1] == (14, 14), "路径终点应该是(14, 14)"


def test_agents():
    """测试智能体模块"""
    from agents import CarAgent, CarState, OrderAgent, SchedulerAgent

    # 测试车辆智能体
    car = CarAgent(car_id=0, initial_position=(0, 0))
    assert car is not None
    assert car.car_id == 0
    assert car.position == (0, 0)
    assert car.state == CarState.IDLE
    assert car.is_idle() is True

    # 测试订单智能体
    order_agent = OrderAgent()
    assert order_agent is not None
    order_id = order_agent.create_order((0, 0), (10, 10))
    assert order_id == 1, "第一个订单ID应该是1"
    assert len(order_agent.orders) == 1
    assert len(order_agent.pending_orders) == 1

    # 测试调度智能体
    scheduler = SchedulerAgent()
    assert scheduler is not None
    assert scheduler.strategy is not None
    assert scheduler.total_assignments == 0


def test_simulation():
    """测试仿真系统"""
    from core import SimulationContext

    # 创建仿真上下文
    context = SimulationContext(grid_size=15, num_cars=3)
    assert context is not None
    assert len(context.cars) == 3, "应该创建3辆车"
    assert context.current_step == 0
    assert context.total_completed_orders == 0

    # 添加订单
    initial_orders = len(context.order_agent.orders)
    order_id = context.add_random_order()
    assert order_id is not None, "应该成功创建订单"
    assert len(context.order_agent.orders) == initial_orders + 1

    # 执行几步仿真
    for i in range(5):
        result = context.step()
        assert result is True, f"第{i+1}步仿真应该成功"
    assert context.current_step == 5, "应该执行了5步"

    # 获取统计
    stats = context.get_statistics()
    assert stats is not None
    assert "current_step" in stats
    assert "total_completed_orders" in stats
    assert "cars" in stats
    assert len(stats["cars"]) == 3


def test_full_workflow():
    """测试完整工作流"""
    from core import SimulationContext

    # 创建系统
    context = SimulationContext(grid_size=15, num_cars=2)
    assert len(context.cars) == 2

    # 添加多个订单
    order_ids = []
    for i in range(3):
        order_id = context.add_random_order()
        assert order_id is not None
        order_ids.append(order_id)
    assert len(context.order_agent.orders) >= 3

    # 运行10步
    completed_before = context.total_completed_orders
    for i in range(10):
        context.step()
    completed_after = context.total_completed_orders

    assert context.current_step == 10, "应该执行了10步"
    assert completed_after >= completed_before, "完成订单数不应该减少"

    # 检查车辆状态
    for car in context.cars:
        report = car.report()
        assert "state" in report
        assert "car_id" in report
        assert report["car_id"] == car.car_id


# 使用pytest的fixture来提供通用的测试数据
@pytest.fixture
def simulation_context():
    """创建一个标准的仿真上下文用于测试"""
    from core import SimulationContext

    return SimulationContext(grid_size=15, num_cars=3)


@pytest.fixture
def grid_environment():
    """创建一个标准的网格环境用于测试"""
    from env import GridEnvironment

    return GridEnvironment(size=15)


if __name__ == "__main__":
    # 当直接运行此文件时，使用pytest执行测试
    pytest.main([__file__, "-v"])
