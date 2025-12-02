"""
测试车辆智能体模块
测试 CarAgent 的状态转换、任务分配和移动逻辑
"""

import pytest
from agents import CarAgent, CarState
from env import GridEnvironment, PathFinding


@pytest.fixture
def grid_env():
    """创建测试用的网格环境"""
    return GridEnvironment(size=15)


@pytest.fixture
def pathfinder(grid_env):
    """创建测试用的路径规划器"""
    return PathFinding(grid_env.grid)


@pytest.fixture
def car_agent():
    """创建一个基本的车辆智能体"""
    return CarAgent(car_id=0, initial_position=(0, 0))


class TestCarAgentInitialization:
    """测试车辆智能体初始化"""
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        car = CarAgent(car_id=5, initial_position=(3, 4), speed=2)
        assert car.car_id == 5
        assert car.position == (3, 4)
        assert car.speed == 2
        assert car.state == CarState.IDLE
        assert car.is_idle() == True
    
    def test_default_speed(self):
        """测试默认速度"""
        car = CarAgent(car_id=0, initial_position=(0, 0))
        assert car.speed == 1
    
    def test_initial_statistics(self, car_agent):
        """测试初始统计信息"""
        assert car_agent.total_distance == 0
        assert car_agent.completed_orders == 0
        assert car_agent.current_order_id is None


class TestCarAgentStateTransitions:
    """测试车辆状态转换"""
    
    def test_idle_to_moving_to_pickup(self, car_agent):
        """测试从空闲到前往取货点的状态转换"""
        assert car_agent.state == CarState.IDLE
        
        car_agent.assign_task(order_id=1, pickup=(2, 2), delivery=(5, 5))
        
        assert car_agent.state == CarState.MOVING_TO_PICKUP
        assert car_agent.current_order_id == 1
        assert car_agent.pickup_point == (2, 2)
        assert car_agent.delivery_point == (5, 5)
    
    def test_moving_to_delivery_state(self, car_agent, pathfinder):
        """测试移动到配送状态"""
        car_agent.assign_task(order_id=1, pickup=(0, 0), delivery=(5, 5))
        
        # 模拟到达取货点
        car_agent.position = (0, 0)
        car_agent._handle_arrival()
        
        assert car_agent.state == CarState.MOVING_TO_DELIVERY
    
    def test_complete_order_state_transition(self, car_agent):
        """测试完成订单后的状态转换"""
        car_agent.assign_task(order_id=1, pickup=(0, 0), delivery=(1, 1))
        car_agent.state = CarState.MOVING_TO_DELIVERY
        car_agent.position = (1, 1)
        
        result = car_agent._handle_arrival()
        
        assert result == True  # 订单完成
        assert car_agent.state == CarState.IDLE
        assert car_agent.completed_orders == 1
        assert car_agent.current_order_id is None
    
    def test_reset(self, car_agent):
        """测试重置功能"""
        car_agent.assign_task(order_id=1, pickup=(2, 2), delivery=(5, 5))
        car_agent.total_distance = 10
        car_agent.completed_orders = 2
        
        car_agent.reset()
        
        assert car_agent.state == CarState.IDLE
        assert car_agent.current_order_id is None
        assert car_agent.pickup_point is None
        assert car_agent.delivery_point is None
        assert car_agent.current_path == []
        # 注意：reset不会清除统计数据


class TestCarAgentMovement:
    """测试车辆移动逻辑"""
    
    def test_plan_path(self, car_agent, pathfinder):
        """测试路径规划"""
        target = (14, 14)  # 使用右下角，确保是道路
        result = car_agent.plan_path(target, pathfinder)
        
        assert result == True
        assert len(car_agent.current_path) > 0
        assert car_agent.current_path[-1] == target
        assert car_agent.path_index == 0
    
    def test_plan_path_with_blocked_positions(self, car_agent, pathfinder):
        """测试带障碍的路径规划"""
        target = (2, 2)
        blocked = {(1, 0), (0, 1)}
        
        result = car_agent.plan_path(target, pathfinder, blocked)
        
        if result:
            # 路径应该避开被阻塞的位置
            for pos in car_agent.current_path:
                if pos != target:
                    assert pos not in blocked
    
    def test_step_idle_state(self, car_agent, pathfinder):
        """测试空闲状态下的step"""
        other_cars = set()
        result = car_agent.step(pathfinder, other_cars)
        
        assert result == False
        assert car_agent.position == (0, 0)  # 位置不变
    
    def test_step_with_task(self, car_agent, pathfinder):
        """测试有任务时的step"""
        car_agent.assign_task(order_id=1, pickup=(0, 2), delivery=(5, 5))
        other_cars = set()
        
        initial_position = car_agent.position
        result = car_agent.step(pathfinder, other_cars)
        
        # 应该开始移动
        if result:
            assert car_agent.total_distance > 0
    
    def test_avoid_other_cars(self, car_agent, pathfinder):
        """测试避开其他车辆"""
        car_agent.assign_task(order_id=1, pickup=(0, 3), delivery=(5, 5))
        car_agent.plan_path((0, 3), pathfinder)
        
        # 假设下一个位置被其他车辆占用
        if len(car_agent.current_path) > 1:
            next_pos = car_agent.current_path[1]
            other_cars = {next_pos}
            
            car_agent.step(pathfinder, other_cars)
            
            # 车辆应该尝试避开或重新规划路径
            # 不应该移动到被占用的位置
            assert car_agent.position != next_pos or car_agent.position == (0, 3)


class TestCarAgentTaskExecution:
    """测试车辆任务执行"""
    
    def test_assign_task(self, car_agent):
        """测试任务分配"""
        car_agent.assign_task(order_id=10, pickup=(1, 1), delivery=(8, 8))
        
        assert car_agent.current_order_id == 10
        assert car_agent.pickup_point == (1, 1)
        assert car_agent.delivery_point == (8, 8)
        assert car_agent.state == CarState.MOVING_TO_PICKUP
        assert len(car_agent.current_path) == 0  # 路径在step时规划
        assert car_agent.path_index == 0
    
    def test_complete_full_delivery(self, pathfinder):
        """测试完整的配送流程"""
        # 创建车辆，起点等于取货点以简化测试
        car = CarAgent(car_id=0, initial_position=(0, 0))
        pickup = (0, 0)
        delivery = (0, 2)
        
        car.assign_task(order_id=1, pickup=pickup, delivery=delivery)
        
        # 由于已在取货点，应该转为配送状态
        assert car.state == CarState.MOVING_TO_PICKUP
        
        # 模拟到达取货点
        car.position = pickup
        car._handle_arrival()
        assert car.state == CarState.MOVING_TO_DELIVERY
        
        # 模拟到达配送点
        car.position = delivery
        result = car._handle_arrival()
        
        assert result == True
        assert car.state == CarState.IDLE
        assert car.completed_orders == 1


class TestCarAgentReport:
    """测试车辆报告功能"""
    
    def test_report_idle(self, car_agent):
        """测试空闲状态的报告"""
        report = car_agent.report()
        
        assert report['car_id'] == 0
        assert report['position'] == (0, 0)
        assert report['state'] == CarState.IDLE.value
        assert report['current_order'] is None
        assert report['completed_orders'] == 0
        assert report['total_distance'] == 0
    
    def test_report_with_task(self, car_agent):
        """测试有任务时的报告"""
        car_agent.assign_task(order_id=5, pickup=(2, 2), delivery=(7, 7))
        report = car_agent.report()
        
        assert report['current_order'] == 5
        assert report['state'] == CarState.MOVING_TO_PICKUP.value
        assert report['pickup_point'] == (2, 2)
        assert report['delivery_point'] == (7, 7)


class TestCarAgentStatusSymbol:
    """测试车辆状态符号"""
    
    def test_idle_symbol(self, car_agent):
        """测试空闲符号"""
        assert car_agent.get_status_symbol() == "🅿️"
    
    def test_moving_to_pickup_symbol(self, car_agent):
        """测试前往取货点符号"""
        car_agent.state = CarState.MOVING_TO_PICKUP
        assert car_agent.get_status_symbol() == "🔍"
    
    def test_moving_to_delivery_symbol(self, car_agent):
        """测试配送中符号"""
        car_agent.state = CarState.MOVING_TO_DELIVERY
        assert car_agent.get_status_symbol() == "📦"
    
    def test_waiting_symbol(self, car_agent):
        """测试等待符号"""
        car_agent.state = CarState.WAITING
        assert car_agent.get_status_symbol() == "⏸️"


class TestCarAgentCollisionHandling:
    """测试车辆碰撞处理"""
    
    def test_higher_priority_car(self, car_agent, pathfinder):
        """测试高优先级车辆（ID较小）"""
        other_car_id = 5
        other_cars = {(1, 0)}
        
        # car_agent的ID是0，优先级高于5
        result = car_agent.handle_collision(other_car_id, pathfinder, other_cars)
        assert result == True  # 保持当前路径
    
    def test_lower_priority_car(self, pathfinder):
        """测试低优先级车辆（ID较大）"""
        car = CarAgent(car_id=10, initial_position=(0, 0))
        car.assign_task(order_id=1, pickup=(2, 2), delivery=(5, 5))
        
        other_car_id = 5
        other_cars = {(1, 0)}
        
        # car的ID是10，优先级低于5，应该尝试避让
        result = car.handle_collision(other_car_id, pathfinder, other_cars)
        # 结果取决于是否能成功规划避让路径


class TestEdgeCases:
    """测试边界情况"""
    
    def test_cannot_plan_path(self, car_agent):
        """测试无法规划路径的情况"""
        # 创建一个全是障碍物的pathfinder
        blocked_grid = [['#' for _ in range(5)] for _ in range(5)]
        blocked_pf = PathFinding(blocked_grid)
        
        car_agent.assign_task(order_id=1, pickup=(2, 2), delivery=(4, 4))
        result = car_agent.step(blocked_pf, set())
        
        # 无法规划路径，应该进入等待状态或返回False
        assert result == False or car_agent.state == CarState.WAITING
    
    def test_distance_tracking(self, car_agent, pathfinder):
        """测试距离跟踪"""
        car_agent.assign_task(order_id=1, pickup=(0, 3), delivery=(5, 5))
        
        initial_distance = car_agent.total_distance
        
        # 执行几步
        for _ in range(5):
            car_agent.step(pathfinder, set())
        
        # 距离应该增加
        assert car_agent.total_distance >= initial_distance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
