"""
车辆路径问题 (VRP) 求解器
支持拼单逻辑和容量约束
"""
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import random
import copy
from enum import Enum


class TaskType(Enum):
    """任务类型"""
    PICKUP = "pickup"
    DELIVERY = "delivery"


@dataclass
class PickupDeliveryTask:
    """取送货任务"""
    order_id: str
    task_type: TaskType
    location: Tuple[int, int]
    load_change: int  # 取货为正，送货为负
    priority: int = 1


@dataclass 
class VehicleRoute:
    """车辆路线"""
    vehicle_id: int
    tasks: List[PickupDeliveryTask]
    total_distance: float = 0.0
    max_load: int = 0
    
    def is_valid(self, vehicle_capacity: int) -> bool:
        """检查路线是否有效（不超载）"""
        current_load = 0
        for task in self.tasks:
            current_load += task.load_change
            if current_load > vehicle_capacity or current_load < 0:
                return False
        return current_load == 0  # 最终负载应为0
    
    def calculate_distance(self, distance_func) -> float:
        """计算路线总距离"""
        if not self.tasks:
            return 0.0
        
        total_dist = 0.0
        current_pos = None  # 需要从车辆当前位置开始
        
        for task in self.tasks:
            if current_pos is not None:
                total_dist += distance_func(current_pos, task.location)
            current_pos = task.location
            
        self.total_distance = total_dist
        return total_dist


class VRPSolver:
    """
    Vehicle Routing Problem 求解器
    使用改进的贪心算法求解PDPTW (Pickup and Delivery Problem with Time Windows)
    """
    
    def __init__(self, vehicle_capacity: int = 3):
        """
        初始化VRP求解器
        Args:
            vehicle_capacity: 车辆容量（同时携带的订单数）
        """
        self.vehicle_capacity = vehicle_capacity
        
    def solve(self, vehicles: List, orders: List, distance_func) -> Dict[int, VehicleRoute]:
        """
        求解VRP问题
        Args:
            vehicles: 可用车辆列表
            orders: 待分配订单列表  
            distance_func: 距离计算函数
        Returns:
            车辆路线字典 {vehicle_id: VehicleRoute}
        """
        if not vehicles or not orders:
            return {}
            
        # 创建任务列表（每个订单包含取货和送货两个任务）
        tasks = []
        for order in orders:
            # 取货任务
            pickup_task = PickupDeliveryTask(
                order_id=order.order_id,
                task_type=TaskType.PICKUP,
                location=order.pickup_point,
                load_change=1  # 取货增加负载
            )
            # 送货任务  
            delivery_task = PickupDeliveryTask(
                order_id=order.order_id,
                task_type=TaskType.DELIVERY,
                location=order.delivery_point,
                load_change=-1  # 送货减少负载
            )
            tasks.extend([pickup_task, delivery_task])
        
        # 使用改进贪心算法分配任务
        return self._greedy_assignment(vehicles, tasks, distance_func)
    
    def _greedy_assignment(self, vehicles: List, tasks: List[PickupDeliveryTask], 
                          distance_func) -> Dict[int, VehicleRoute]:
        """
        贪心任务分配算法
        """
        routes = {}
        available_tasks = tasks.copy()
        
        # 为每个车辆初始化路线
        for vehicle in vehicles:
            if not vehicle.is_available_for_task():
                continue
                
            route = VehicleRoute(vehicle_id=vehicle.car_id, tasks=[])
            
            # 贪心选择任务
            while available_tasks and len([t for t in route.tasks if t.task_type == TaskType.PICKUP]) < self.vehicle_capacity:
                best_task = self._select_best_task(vehicle.position, route, available_tasks, distance_func)
                
                if best_task is None:
                    break
                    
                route.tasks.append(best_task)
                available_tasks.remove(best_task)
                
                # 如果是取货任务，必须确保对应的送货任务也能加入
                if best_task.task_type == TaskType.PICKUP:
                    delivery_task = self._find_delivery_task(best_task.order_id, available_tasks)
                    if delivery_task:
                        # 尝试插入送货任务到最佳位置
                        self._insert_delivery_task(route, delivery_task, distance_func)
                        available_tasks.remove(delivery_task)
            
            # 验证路线有效性
            if route.tasks and route.is_valid(self.vehicle_capacity):
                route.calculate_distance(distance_func)
                routes[vehicle.car_id] = route
        
        return routes
    
    def _select_best_task(self, current_pos: Tuple[int, int], route: VehicleRoute, 
                         available_tasks: List[PickupDeliveryTask], distance_func) -> Optional[PickupDeliveryTask]:
        """
        选择最佳下一个任务
        优先考虑取货任务，选择距离最近的
        """
        # 优先选择取货任务
        pickup_tasks = [t for t in available_tasks if t.task_type == TaskType.PICKUP]
        
        if not pickup_tasks:
            return None
            
        # 计算到各个取货点的距离
        best_task = None
        min_distance = float('inf')
        
        for task in pickup_tasks:
            # 检查是否会超过容量限制
            current_pickups = len([t for t in route.tasks if t.task_type == TaskType.PICKUP])
            if current_pickups >= self.vehicle_capacity:
                continue
                
            distance = distance_func(current_pos, task.location)
            if distance < min_distance:
                min_distance = distance
                best_task = task
        
        return best_task
    
    def _find_delivery_task(self, order_id: str, available_tasks: List[PickupDeliveryTask]) -> Optional[PickupDeliveryTask]:
        """查找对应的送货任务"""
        for task in available_tasks:
            if task.order_id == order_id and task.task_type == TaskType.DELIVERY:
                return task
        return None
    
    def _insert_delivery_task(self, route: VehicleRoute, delivery_task: PickupDeliveryTask, distance_func):
        """
        将送货任务插入到路线的最佳位置
        必须在对应取货任务之后
        """
        pickup_index = -1
        for i, task in enumerate(route.tasks):
            if task.order_id == delivery_task.order_id and task.task_type == TaskType.PICKUP:
                pickup_index = i
                break
        
        if pickup_index == -1:
            return  # 没找到对应的取货任务
        
        # 尝试在取货任务之后的所有位置插入，选择距离增加最小的位置
        best_position = len(route.tasks)
        min_distance_increase = float('inf')
        
        for pos in range(pickup_index + 1, len(route.tasks) + 1):
            # 计算插入此位置的距离增加量
            distance_increase = self._calculate_insertion_cost(route, delivery_task, pos, distance_func)
            if distance_increase < min_distance_increase:
                min_distance_increase = distance_increase
                best_position = pos
        
        route.tasks.insert(best_position, delivery_task)
    
    def _calculate_insertion_cost(self, route: VehicleRoute, task: PickupDeliveryTask, 
                                position: int, distance_func) -> float:
        """计算在指定位置插入任务的代价"""
        if position == 0:
            if not route.tasks:
                return 0.0
            return distance_func(task.location, route.tasks[0].location)
        
        if position >= len(route.tasks):
            if not route.tasks:
                return 0.0
            return distance_func(route.tasks[-1].location, task.location)
        
        # 计算插入中间位置的额外距离
        prev_task = route.tasks[position - 1]
        next_task = route.tasks[position]
        
        original_distance = distance_func(prev_task.location, next_task.location)
        new_distance = (distance_func(prev_task.location, task.location) + 
                       distance_func(task.location, next_task.location))
        
        return new_distance - original_distance
    
    def optimize_route(self, route: VehicleRoute, distance_func) -> VehicleRoute:
        """
        使用2-opt算法优化路线
        保持取货-送货的顺序约束
        """
        if len(route.tasks) <= 2:
            return route
            
        optimized_route = copy.deepcopy(route)
        improved = True
        
        while improved:
            improved = False
            
            # 尝试所有可能的2-opt交换
            for i in range(len(optimized_route.tasks) - 1):
                for j in range(i + 2, len(optimized_route.tasks)):
                    # 检查交换是否违反取货-送货顺序约束
                    if self._is_valid_swap(optimized_route.tasks, i, j):
                        # 尝试交换
                        new_tasks = optimized_route.tasks.copy()
                        new_tasks[i+1:j+1] = reversed(new_tasks[i+1:j+1])
                        
                        # 计算新路线的距离
                        test_route = VehicleRoute(
                            vehicle_id=optimized_route.vehicle_id,
                            tasks=new_tasks
                        )
                        
                        if test_route.is_valid(self.vehicle_capacity):
                            new_distance = test_route.calculate_distance(distance_func)
                            if new_distance < optimized_route.total_distance:
                                optimized_route = test_route
                                improved = True
        
        return optimized_route
    
    def _is_valid_swap(self, tasks: List[PickupDeliveryTask], i: int, j: int) -> bool:
        """
        检查2-opt交换是否保持取货-送货顺序约束
        """
        # 收集所有受影响的订单
        affected_orders = set()
        for idx in range(i+1, j+1):
            affected_orders.add(tasks[idx].order_id)
        
        # 检查每个订单的取货是否在送货之前
        for order_id in affected_orders:
            pickup_pos = delivery_pos = -1
            
            # 查找取货和送货位置（交换后）
            new_tasks = tasks.copy()
            new_tasks[i+1:j+1] = reversed(new_tasks[i+1:j+1])
            
            for idx, task in enumerate(new_tasks):
                if task.order_id == order_id:
                    if task.task_type == TaskType.PICKUP:
                        pickup_pos = idx
                    else:
                        delivery_pos = idx
            
            if pickup_pos > delivery_pos:
                return False
        
        return True


def calculate_manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """计算曼哈顿距离"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
