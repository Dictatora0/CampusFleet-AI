"""
调度智能体模块 - 负责订单与车辆的匹配调度
"""
from typing import List, Dict, Tuple, Optional
from enum import Enum
import sys


class SchedulingStrategy(Enum):
    """调度策略枚举"""
    GREEDY_NEAREST = "贪心最近"
    BALANCED_LOAD = "负载均衡"
    HUNGARIAN = "匈牙利算法"


class SchedulerAgent:
    """调度智能体类 - 负责将订单分配给车辆"""
    
    def __init__(self, strategy: SchedulingStrategy = SchedulingStrategy.GREEDY_NEAREST):
        """
        初始化调度智能体
        Args:
            strategy: 调度策略
        """
        self.strategy = strategy
        self.assignment_history: List[Dict] = []
        self.total_assignments = 0
    
    def reset(self):
        """重置调度器"""
        self.assignment_history.clear()
        self.total_assignments = 0
    
    def schedule(self, cars: List, orders: List, grid_env) -> List[Tuple[int, int, Tuple, Tuple]]:
        """
        执行调度 - 将订单分配给车辆
        Args:
            cars: 车辆智能体列表
            orders: 待分配订单列表
            grid_env: 网格环境对象
        Returns:
            分配结果列表: [(car_id, order_id, pickup, delivery), ...]
        """
        if not orders:
            return []
        
        # 筛选空闲车辆
        idle_cars = [car for car in cars if car.is_idle()]
        
        if not idle_cars:
            return []
        
        # 根据策略执行调度
        if self.strategy == SchedulingStrategy.GREEDY_NEAREST:
            return self._greedy_nearest_schedule(idle_cars, orders, grid_env)
        elif self.strategy == SchedulingStrategy.BALANCED_LOAD:
            return self._balanced_load_schedule(idle_cars, orders, grid_env)
        elif self.strategy == SchedulingStrategy.HUNGARIAN:
            return self._hungarian_schedule(idle_cars, orders, grid_env)
        else:
            return self._greedy_nearest_schedule(idle_cars, orders, grid_env)
    
    def _greedy_nearest_schedule(self, cars: List, orders: List, grid_env) -> List[Tuple]:
        """
        贪心最近策略：为每个订单选择最近的空闲车辆
        Args:
            cars: 空闲车辆列表
            orders: 待分配订单列表
            grid_env: 网格环境
        Returns:
            分配结果列表
        """
        assignments = []
        available_cars = cars.copy()
        
        for order in orders:
            if not available_cars:
                break
            
            # 找到距离订单取货点最近的车辆
            best_car = None
            min_distance = sys.maxsize
            
            for car in available_cars:
                distance = grid_env.calculate_distance(car.position, order.pickup_point)
                if distance < min_distance:
                    min_distance = distance
                    best_car = car
            
            if best_car:
                assignments.append((
                    best_car.car_id,
                    order.order_id,
                    order.pickup_point,
                    order.delivery_point
                ))
                available_cars.remove(best_car)
                self.total_assignments += 1
        
        # 记录分配历史
        if assignments:
            self.assignment_history.append({
                'assignments': assignments,
                'strategy': self.strategy.value
            })
        
        return assignments
    
    def _balanced_load_schedule(self, cars: List, orders: List, grid_env) -> List[Tuple]:
        """
        负载均衡策略：考虑车辆已完成的订单数，优先分配给完成订单少的车辆
        Args:
            cars: 空闲车辆列表
            orders: 待分配订单列表
            grid_env: 网格环境
        Returns:
            分配结果列表
        """
        assignments = []
        available_cars = sorted(cars, key=lambda c: c.completed_orders)
        
        for order in orders:
            if not available_cars:
                break
            
            # 在完成订单数最少的车辆中，选择距离最近的
            min_completed = available_cars[0].completed_orders
            candidate_cars = [c for c in available_cars if c.completed_orders == min_completed]
            
            best_car = None
            min_distance = sys.maxsize
            
            for car in candidate_cars:
                distance = grid_env.calculate_distance(car.position, order.pickup_point)
                if distance < min_distance:
                    min_distance = distance
                    best_car = car
            
            if best_car:
                assignments.append((
                    best_car.car_id,
                    order.order_id,
                    order.pickup_point,
                    order.delivery_point
                ))
                available_cars.remove(best_car)
                self.total_assignments += 1
        
        if assignments:
            self.assignment_history.append({
                'assignments': assignments,
                'strategy': self.strategy.value
            })
        
        return assignments
    
    def _hungarian_schedule(self, cars: List, orders: List, grid_env) -> List[Tuple]:
        """
        匈牙利算法策略：最优匹配（预留接口，简化实现）
        Args:
            cars: 空闲车辆列表
            orders: 待分配订单列表
            grid_env: 网格环境
        Returns:
            分配结果列表
        """
        # 简化实现：使用贪心策略
        # 真正的匈牙利算法需要引入 scipy 或自己实现
        # 这里提供接口，可以后续扩展
        return self._greedy_nearest_schedule(cars, orders, grid_env)
    
    def step(self):
        """执行一步更新（预留接口）"""
        pass
    
    def report(self) -> dict:
        """
        报告调度器状态
        Returns:
            包含调度统计信息的字典
        """
        return {
            'strategy': self.strategy.value,
            'total_assignments': self.total_assignments,
            'history_length': len(self.assignment_history)
        }
    
    def get_strategy_name(self) -> str:
        """获取当前策略名称"""
        return self.strategy.value
    
    def set_strategy(self, strategy: SchedulingStrategy):
        """
        设置调度策略
        Args:
            strategy: 新的调度策略
        """
        self.strategy = strategy


def call_llm_for_scheduling(context: dict) -> str:
    """
    预留的LLM调用接口（用于未来智能调度决策）
    Args:
        context: 调度上下文信息
    Returns:
        LLM建议的调度方案
    """
    # 这是一个占位函数，可以在未来连接到实际的LLM服务
    # 例如：根据历史数据、交通状况等，让LLM给出最优调度建议
    return f"[LLM Scheduling Suggestion Placeholder]"
