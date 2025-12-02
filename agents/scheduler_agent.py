"""
调度智能体模块 - 负责订单与车辆的匹配调度
"""
from typing import List, Dict, Tuple, Optional
from enum import Enum
import sys


class SchedulingStrategy(Enum):
    """调度策略枚举"""
    GREEDY_NEAREST = "Greedy Nearest"
    BALANCED_LOAD = "Balanced Load"
    HUNGARIAN = "Hungarian"
    VRP_BATCHING = "VRP Batching"  # VRP拼单策略
    MAPF_CBS = "MAPF CBS"  # 新增：CBS协调规划


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
        
        # 筛选可用车辆（空闲且电量充足）
        idle_cars = [car for car in cars if car.is_available_for_task()]
        
        if not idle_cars:
            return []
        
        # 根据策略选择调度方法
        if self.strategy == SchedulingStrategy.GREEDY_NEAREST:
            assignments = self._greedy_nearest_schedule(idle_cars, orders, grid_env)
        elif self.strategy == SchedulingStrategy.BALANCED_LOAD:
            assignments = self._balanced_load_schedule(idle_cars, orders, grid_env)
        elif self.strategy == SchedulingStrategy.HUNGARIAN:
            assignments = self._hungarian_schedule(idle_cars, orders, grid_env)
        elif self.strategy == SchedulingStrategy.VRP_BATCHING:
            assignments = self._vrp_batching_schedule(idle_cars, orders, grid_env)
        elif self.strategy == SchedulingStrategy.MAPF_CBS:
            assignments = self._mapf_cbs_schedule(idle_cars, orders, grid_env)
        else:
            assignments = self._greedy_nearest_schedule(idle_cars, orders, grid_env)
        
        return assignments
    
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
        匈牙利算法策略：最优匹配
        使用scipy.optimize.linear_sum_assignment实现全局最优分配
        Args:
            cars: 空闲车辆列表
            orders: 待分配订单列表
            grid_env: 网格环境
        Returns:
            分配结果列表
        """
        if not cars or not orders:
            return []
        
        try:
            from scipy.optimize import linear_sum_assignment
            import numpy as np
        except ImportError:
            # 如果scipy未安装，回退到贪心策略
            print("⚠️ scipy未安装，匈牙利算法回退到贪心策略")
            return self._greedy_nearest_schedule(cars, orders, grid_env)
        
        # 构建成本矩阵：车辆到订单取货点的距离
        num_cars = len(cars)
        num_orders = len(orders)
        
        # 创建成本矩阵（车辆 x 订单）
        cost_matrix = np.zeros((num_cars, num_orders))
        
        for i, car in enumerate(cars):
            for j, order in enumerate(orders):
                # 计算车辆当前位置到订单取货点的距离
                distance = grid_env.calculate_distance(car.position, order.pickup_point)
                cost_matrix[i, j] = distance
        
        # 使用匈牙利算法求解最优分配
        # linear_sum_assignment返回行索引和列索引
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        
        # 构建分配结果
        assignments = []
        for car_idx, order_idx in zip(row_indices, col_indices):
            car = cars[car_idx]
            order = orders[order_idx]
            assignments.append((
                car.car_id,
                order.order_id,
                order.pickup_point,
                order.delivery_point
            ))
            self.total_assignments += 1
        
        # 记录分配历史
        if assignments:
            self.assignment_history.append({
                'assignments': assignments,
                'strategy': self.strategy.value,
                'cost_matrix_shape': cost_matrix.shape,
                'total_cost': cost_matrix[row_indices, col_indices].sum()
            })
        
        return assignments
    
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
    
    def _vrp_batching_schedule(self, cars: List, orders: List, grid_env) -> List[Tuple]:
        """
        VRP拼单策略：使用车辆路径问题算法，允许车辆一次处理多个订单
        Args:
            cars: 空闲车辆列表
            orders: 待分配订单列表
            grid_env: 网格环境
        Returns:
            分配结果列表，格式扩展为 [(car_id, [order_ids], route_tasks)]
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from algorithms.vrp_solver import VRPSolver
        except ImportError as e:
            print(f"⚠️  VRP模块未找到: {e}，回退到贪心策略")
            return self._greedy_nearest_schedule(cars, orders, grid_env)
        
        if not cars or not orders:
            return []
        
        # 创建VRP求解器
        vrp_solver = VRPSolver(vehicle_capacity=3)  # 每辆车最多同时处理3个订单
        
        # 距离函数
        def distance_func(pos1, pos2):
            return grid_env.calculate_distance(pos1, pos2)
        
        # 求解VRP
        routes = vrp_solver.solve(cars, orders, distance_func)
        
        # 转换为传统格式的分配结果
        assignments = []
        
        for vehicle_id, route in routes.items():
            if not route.tasks:
                continue
                
            # 将路线任务分组为订单
            order_groups = {}
            for task in route.tasks:
                if task.order_id not in order_groups:
                    order_groups[task.order_id] = {'pickup': None, 'delivery': None}
                
                if task.task_type.value == 'pickup':
                    order_groups[task.order_id]['pickup'] = task.location
                else:
                    order_groups[task.order_id]['delivery'] = task.location
            
            # 为每个完整的订单创建分配记录
            for order_id, locations in order_groups.items():
                if locations['pickup'] and locations['delivery']:
                    assignments.append((
                        vehicle_id,
                        order_id,
                        locations['pickup'],
                        locations['delivery']
                    ))
                    self.total_assignments += 1
        
        # 记录VRP分配历史
        if assignments:
            self.assignment_history.append({
                'assignments': assignments,
                'strategy': self.strategy.value,
                'vrp_routes': len(routes),
                'total_orders': len(orders),
                'total_vehicles': len(cars)
            })
        
        return assignments
    
    def _mapf_cbs_schedule(self, cars: List, orders: List, grid_env) -> List[Tuple]:
        """
        MAPF CBS策略：使用冲突感知搜索进行全局协调规划
        Args:
            cars: 空闲车辆列表
            orders: 待分配订单列表
            grid_env: 网格环境
        Returns:
            分配结果列表
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from algorithms.mapf_planner import MAPFPlanner
        except ImportError as e:
            print(f"⚠️  MAPF模块未找到: {e}，回退到贪心策略")
            return self._greedy_nearest_schedule(cars, orders, grid_env)
        
        if not cars or not orders:
            return []
        
        # 只处理数量匹配的情况（1车1单）
        assignments = []
        available_cars = cars.copy()
        
        # 批处理：每次最多处理N个车辆和订单
        batch_size = min(len(available_cars), len(orders), 5)  # 限制批处理大小
        
        processed_orders = 0
        while available_cars and processed_orders < len(orders):
            # 选择当前批次的车辆和订单
            current_cars = available_cars[:batch_size]
            current_orders = orders[processed_orders:processed_orders + len(current_cars)]
            
            if not current_orders:
                break
            
            # 创建MAPF规划器
            mapf_planner = MAPFPlanner(grid_env, algorithm="CBS")
            
            # 构建目标字典 {car_id: pickup_location}
            goals = {}
            car_order_mapping = {}
            
            for i, (car, order) in enumerate(zip(current_cars, current_orders)):
                goals[car.car_id] = order.pickup_point
                car_order_mapping[car.car_id] = order
            
            print(f"🧠 CBS规划: {len(current_cars)}车 -> {len(current_orders)}单")
            
            # 执行MAPF规划
            coordinated_paths = mapf_planner.plan_multi_agent_paths(current_cars, goals)
            
            if coordinated_paths:
                # 成功规划，创建分配
                for car_id, path in coordinated_paths.items():
                    if car_id in car_order_mapping:
                        order = car_order_mapping[car_id]
                        
                        # 找到对应的车辆
                        car = next(c for c in current_cars if c.car_id == car_id)
                        
                        # 将CBS路径设置到车辆（扩展功能）
                        if hasattr(car, 'set_coordinated_path'):
                            car.set_coordinated_path(path)
                        
                        assignments.append((
                            car_id,
                            order.order_id,
                            order.pickup_point,
                            order.delivery_point
                        ))
                        self.total_assignments += 1
                
                # 移除已分配的车辆
                available_cars = [c for c in available_cars if c.car_id not in coordinated_paths]
                processed_orders += len(current_orders)
                
                print(f"✅ CBS成功分配 {len(coordinated_paths)} 对")
                
            else:
                # CBS规划失败，回退到贪心策略
                print("❌ CBS规划失败，回退到贪心策略")
                
                # 为当前批次使用贪心分配
                greedy_assignments = self._greedy_nearest_schedule(current_cars, current_orders, grid_env)
                assignments.extend(greedy_assignments)
                
                # 移除已分配的车辆
                assigned_car_ids = {a[0] for a in greedy_assignments}
                available_cars = [c for c in available_cars if c.car_id not in assigned_car_ids]
                processed_orders += len(greedy_assignments)
        
        # 记录MAPF分配历史
        if assignments:
            self.assignment_history.append({
                'assignments': assignments,
                'strategy': self.strategy.value,
                'mapf_success': True,
                'total_orders': len(orders),
                'total_vehicles': len(cars)
            })
        
        return assignments


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
