"""
车辆智能体模块 - 负责路径规划、移动和避障
"""
from typing import Tuple, Optional, List, Set
from enum import Enum


class CarState(Enum):
    """车辆状态枚举"""
    IDLE = "空闲"
    MOVING_TO_PICKUP = "前往取货点"
    MOVING_TO_DELIVERY = "配送中"
    WAITING = "等待"


class CarAgent:
    """车辆智能体类"""
    
    def __init__(self, car_id: int, initial_position: Tuple[int, int], speed: int = 1):
        """
        初始化车辆智能体
        Args:
            car_id: 车辆唯一标识
            initial_position: 初始位置 (x, y)
            speed: 移动速度（每步移动的格子数）
        """
        self.car_id = car_id
        self.position = initial_position
        self.speed = speed
        self.state = CarState.IDLE
        
        # 任务相关
        self.current_order_id: Optional[int] = None
        self.pickup_point: Optional[Tuple[int, int]] = None
        self.delivery_point: Optional[Tuple[int, int]] = None
        
        # 路径相关
        self.current_path: List[Tuple[int, int]] = []
        self.path_index = 0
        
        # 统计信息
        self.total_distance = 0
        self.completed_orders = 0
    
    def reset(self):
        """重置车辆状态"""
        self.state = CarState.IDLE
        self.current_order_id = None
        self.pickup_point = None
        self.delivery_point = None
        self.current_path = []
        self.path_index = 0
    
    def assign_task(self, order_id: int, pickup: Tuple[int, int], delivery: Tuple[int, int]):
        """
        分配配送任务
        Args:
            order_id: 订单ID
            pickup: 取货点坐标
            delivery: 配送点坐标
        """
        self.current_order_id = order_id
        self.pickup_point = pickup
        self.delivery_point = delivery
        self.state = CarState.MOVING_TO_PICKUP
        self.current_path = []
        self.path_index = 0
    
    def plan_path(self, target: Tuple[int, int], pathfinder, blocked_positions: Optional[Set] = None):
        """
        规划到目标点的路径
        Args:
            target: 目标位置
            pathfinder: 路径规划器对象
            blocked_positions: 被占用的位置集合
        """
        path = pathfinder.a_star(self.position, target, blocked_positions)
        if path:
            self.current_path = path
            self.path_index = 0
            return True
        return False
    
    def step(self, pathfinder, other_car_positions: Set[Tuple[int, int]]) -> bool:
        """
        执行一步移动
        Args:
            pathfinder: 路径规划器
            other_car_positions: 其他车辆的位置集合
        Returns:
            是否成功移动
        """
        if self.state == CarState.IDLE:
            return False
        
        # 确定当前目标
        if self.state == CarState.MOVING_TO_PICKUP:
            target = self.pickup_point
        elif self.state == CarState.MOVING_TO_DELIVERY:
            target = self.delivery_point
        else:
            return False
        
        # 如果没有路径或路径已完成，重新规划
        if not self.current_path or self.path_index >= len(self.current_path):
            if not self.plan_path(target, pathfinder, other_car_positions):
                # 无法规划路径，等待
                self.state = CarState.WAITING
                return False
            
        # 检查是否已到达目标
        if self.position == target:
            return self._handle_arrival()
        
        # 尝试沿路径移动
        moved = False
        for _ in range(self.speed):
            if self.path_index >= len(self.current_path):
                break
            
            next_position = self.current_path[self.path_index]
            
            # 避障：检查下一个位置是否被占用
            if next_position in other_car_positions and next_position != target:
                # 位置被占用，尝试重新规划路径
                if not self.plan_path(target, pathfinder, other_car_positions):
                    # 无法绕行，等待
                    break
                continue
            
            # 移动到下一个位置
            self.position = next_position
            self.path_index += 1
            self.total_distance += 1
            moved = True
            
            # 检查是否到达目标
            if self.position == target:
                self._handle_arrival()
                break
        
        return moved
    
    def _handle_arrival(self) -> bool:
        """
        处理到达目标点的逻辑
        Returns:
            是否完成了订单
        """
        if self.state == CarState.MOVING_TO_PICKUP:
            # 到达取货点，开始配送
            self.state = CarState.MOVING_TO_DELIVERY
            self.current_path = []
            self.path_index = 0
            return False
        
        elif self.state == CarState.MOVING_TO_DELIVERY:
            # 到达配送点，完成订单
            self.completed_orders += 1
            self.reset()
            return True
        
        return False
    
    def handle_collision(self, other_car_id: int, pathfinder, 
                        other_car_positions: Set[Tuple[int, int]]) -> bool:
        """
        处理碰撞/冲突：按ID优先级决定
        Args:
            other_car_id: 另一辆车的ID
            pathfinder: 路径规划器
            other_car_positions: 其他车辆位置
        Returns:
            是否成功处理冲突
        """
        if self.car_id < other_car_id:
            # 优先级高，保持当前路径
            return True
        else:
            # 优先级低，尝试避让
            return self._try_avoid(pathfinder, other_car_positions)
    
    def _try_avoid(self, pathfinder, blocked_positions: Set[Tuple[int, int]]) -> bool:
        """
        尝试避让策略
        Args:
            pathfinder: 路径规划器
            blocked_positions: 被占用的位置
        Returns:
            是否成功避让
        """
        # 重新规划路径，考虑被占用的位置
        target = self.pickup_point if self.state == CarState.MOVING_TO_PICKUP else self.delivery_point
        if target:
            return self.plan_path(target, pathfinder, blocked_positions)
        return False
    
    def report(self) -> dict:
        """
        报告车辆状态
        Returns:
            包含车辆状态信息的字典
        """
        return {
            'car_id': self.car_id,
            'position': self.position,
            'state': self.state.value,
            'current_order': self.current_order_id,
            'completed_orders': self.completed_orders,
            'total_distance': self.total_distance,
            'pickup_point': self.pickup_point,
            'delivery_point': self.delivery_point
        }
    
    def is_idle(self) -> bool:
        """检查车辆是否空闲"""
        return self.state == CarState.IDLE
    
    def get_status_symbol(self) -> str:
        """获取状态符号"""
        if self.state == CarState.IDLE:
            return "🅿️"
        elif self.state == CarState.MOVING_TO_PICKUP:
            return "🔍"
        elif self.state == CarState.MOVING_TO_DELIVERY:
            return "📦"
        else:
            return "⏸️"


def call_llm(prompt: str) -> str:
    """
    预留的LLM调用接口（用于未来智能决策扩展）
    Args:
        prompt: 输入提示
    Returns:
        LLM响应（当前返回占位符）
    """
    # 这是一个占位函数，可以在未来连接到实际的LLM服务
    return f"[LLM Response Placeholder for: {prompt[:50]}...]"
