"""
车辆智能体模块 - 负责路径规划、移动和避障
"""
from typing import Tuple, Optional, List, Set, Dict
from enum import Enum


class CarState(Enum):
    """车辆状态枚举"""
    IDLE = "Idle"
    MOVING_TO_PICKUP = "To Pickup"
    MOVING_TO_DELIVERY = "Delivering"
    WAITING = "Waiting"
    CHARGING = "Charging"
    MOVING_TO_CHARGE = "To Charger"


class CarAgent:
    """车辆智能体类"""
    
    def __init__(self, car_id: int, initial_position: Tuple[int, int], speed: int = 1,
                 max_battery: float = 100.0, battery_consumption_rate: float = 1.0):
        """
        初始化车辆智能体
        Args:
            car_id: 车辆唯一标识
            initial_position: 初始位置 (x, y)
            speed: 移动速度（每步移动的格子数）
            max_battery: 最大电量
            battery_consumption_rate: 每移动一格消耗的电量
        """
        self.car_id = car_id
        self.position = initial_position
        self.speed = speed
        self.state = CarState.IDLE
        
        # 电量系统
        self.max_battery = max_battery
        self.battery = max_battery  # 当前电量
        self.battery_consumption_rate = battery_consumption_rate
        self.low_battery_threshold = max_battery * 0.2  # 20%低电量阈值
        self.critical_battery_threshold = max_battery * 0.1  # 10%严重低电
        self.charging_rate = 5.0  # 每步充电量
        self.charging_station: Optional[Tuple[int, int]] = None  # 目标充电站
        
        # 任务相关 - 支持多订单
        self.current_order_id: Optional[str] = None
        self.pickup_point: Optional[Tuple[int, int]] = None
        self.delivery_point: Optional[Tuple[int, int]] = None
        
        # VRP多订单支持
        self.task_queue: List[Dict] = []  # 任务队列 [{'type': 'pickup'/'delivery', 'order_id': str, 'location': tuple}]
        self.current_capacity = 0  # 当前载货量
        self.max_capacity = 3  # 最大载货量
        
        # MAPF协调路径支持
        self.coordinated_path: Optional[List[Tuple[int, int]]] = None  # CBS规划的协调路径
        self.path_time_step = 0  # 当前路径执行步数
        self.use_coordinated_path = False  # 是否使用协调路径
        
        # 路径相关
        self.current_path: List[Tuple[int, int]] = []
        self.path_index = 0
        
        # 避障相关
        self.wait_counter = 0  # 等待计数器
        self.max_wait_time = 3  # 最大等待步数
        self.replan_attempts = 0  # 重新规划尝试次数
        self.max_replan_attempts = 3  # 最大重新规划次数
        
        # 死锁检测与处理
        self.stuck_counter = 0  # 被卡住计数器
        self.max_stuck_time = 10  # 最大被卡时间，超过后触发死锁处理
        self.last_position = initial_position  # 上一步的位置
        self.deadlock_recovery_mode = False  # 是否处于死锁恢复模式
        
        # 统计信息
        self.total_distance = 0
        self.completed_orders = 0
        self.total_charging_time = 0  # 总充电时间
    
    def reset(self):
        """重置车辆状态"""
        self.state = CarState.IDLE
        self.current_order_id = None
        self.pickup_point = None
        self.delivery_point = None
        self.current_path = []
        self.path_index = 0
        self.wait_counter = 0
        self.replan_attempts = 0
        self.stuck_counter = 0
        self.last_position = self.position
        self.deadlock_recovery_mode = False
        self.battery = self.max_battery
        self.charging_station = None
        
        # 重置VRP相关状态
        self.task_queue.clear()
        self.current_capacity = 0
        
        # 重置MAPF协调状态
        self.clear_coordinated_path()
    
    def assign_task(self, order_id: str, pickup: Tuple[int, int], delivery: Tuple[int, int]):
        """
        分配新任务（兼容原有接口）
        Args:
            order_id: 订单ID
            pickup: 取货点
            delivery: 配送点
        """
        if self.state != CarState.IDLE:
            return False
        
        self.current_order_id = order_id
        self.pickup_point = pickup
        self.delivery_point = delivery
        self.state = CarState.MOVING_TO_PICKUP
        
        # 清空之前的路径
        self.current_path = []
        self.path_index = 0
        
        return True
    
    def assign_vrp_route(self, task_queue: List[Dict]):
        """
        分配VRP路线（多订单任务队列）
        Args:
            task_queue: 任务队列，格式: [{'type': 'pickup'/'delivery', 'order_id': str, 'location': tuple}]
        """
        if self.state != CarState.IDLE or self.current_capacity != 0:
            return False
        
        self.task_queue = task_queue.copy()
        
        if self.task_queue:
            # 开始执行第一个任务
            self._process_next_task()
        
        return True
    
    def _process_next_task(self):
        """处理队列中的下一个任务"""
        if not self.task_queue:
            # 所有任务完成，回到空闲状态
            self.state = CarState.IDLE
            self.current_order_id = None
            self.pickup_point = None
            self.delivery_point = None
            return
        
        # 获取下一个任务
        next_task = self.task_queue[0]
        
        self.current_order_id = next_task['order_id']
        
        if next_task['type'] == 'pickup':
            self.pickup_point = next_task['location']
            self.state = CarState.MOVING_TO_PICKUP
        else:  # delivery
            self.delivery_point = next_task['location']
            self.state = CarState.MOVING_TO_DELIVERY
        
        # 清空路径，重新规划
        self.current_path = []
        self.path_index = 0
    
    def set_coordinated_path(self, path: List[Tuple[int, int]]):
        """
        设置CBS协调路径
        Args:
            path: CBS规划的无冲突路径
        """
        self.coordinated_path = path.copy()
        self.path_time_step = 0
        self.use_coordinated_path = True
        print(f"🧠 车辆{self.car_id}设置协调路径，长度{len(path)}")
    
    def clear_coordinated_path(self):
        """清除协调路径，回到传统规划"""
        self.coordinated_path = None
        self.path_time_step = 0
        self.use_coordinated_path = False
    
    def _execute_coordinated_step(self) -> bool:
        """
        执行协调路径的一步
        Returns:
            是否完成移动或到达目标
        """
        if not self.coordinated_path or self.path_time_step >= len(self.coordinated_path):
            # 协调路径执行完毕，切换回传统模式
            self.clear_coordinated_path()
            return False
        
        # 获取当前应该到达的位置
        target_position = self.coordinated_path[self.path_time_step]
        
        # 移动到目标位置
        if self.position != target_position:
            # 消耗电量
            self.consume_battery()
            
            # 更新位置
            self.position = target_position
            self.total_distance += 1
            
        # 增加时间步
        self.path_time_step += 1
        
        # 检查是否到达任务目标
        target = None
        if self.state == CarState.MOVING_TO_PICKUP:
            target = self.pickup_point
        elif self.state == CarState.MOVING_TO_DELIVERY:
            target = self.delivery_point
        elif self.state == CarState.MOVING_TO_CHARGE:
            target = self.charging_station
        
        if target and self.position == target:
            # 到达目标，处理任务完成
            self.clear_coordinated_path()  # 清除协调路径
            return self._handle_arrival()
        
        return True
    
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
        执行一步移动（增强版：包含MAPF协调、智能避让、死锁检测）
        Args:
            pathfinder: 路径规划器
            other_car_positions: 其他车辆的位置集合
        Returns:
            是否成功移动
        """
        if self.state == CarState.IDLE:
            return False
        
        # 优先使用协调路径（MAPF CBS）
        if self.use_coordinated_path and self.coordinated_path:
            return self._execute_coordinated_step()
        
        # 检测是否被卡住（位置没有变化）
        if self.position == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.deadlock_recovery_mode = False
        
        self.last_position = self.position
        
        # 如果被卡住时间过长，进入死锁恢复模式
        if self.stuck_counter >= self.max_stuck_time:
            return self._handle_deadlock(pathfinder, other_car_positions)
        
        # 处理等待状态
        if self.state == CarState.WAITING:
            self.wait_counter += 1
            if self.wait_counter >= self.max_wait_time:
                # 等待超时，尝试重新规划
                self.wait_counter = 0
                self.state = CarState.MOVING_TO_PICKUP if self.pickup_point else CarState.MOVING_TO_DELIVERY
                self.current_path = []
            return False
        
        # 确定当前目标
        if self.state == CarState.MOVING_TO_PICKUP:
            target = self.pickup_point
        elif self.state == CarState.MOVING_TO_DELIVERY:
            target = self.delivery_point
        else:
            return False
        
        # 检查是否已到达目标
        if self.position == target:
            self.replan_attempts = 0
            return self._handle_arrival()
        
        # 如果没有路径或路径已完成，重新规划
        if not self.current_path or self.path_index >= len(self.current_path):
            if not self.plan_path(target, pathfinder, other_car_positions):
                # 无法规划路径，进入等待状态
                self.state = CarState.WAITING
                self.wait_counter = 0
                return False
            self.replan_attempts = 0
        
        # 尝试沿路径移动
        moved = False
        for _ in range(self.speed):
            if self.path_index >= len(self.current_path):
                break
            
            next_position = self.current_path[self.path_index]
            
            # 避障：检查下一个位置是否被占用
            if next_position in other_car_positions and next_position != target:
                # 位置被占用，尝试智能避让
                if self._smart_avoidance(target, next_position, pathfinder, other_car_positions):
                    continue
                else:
                    # 无法避让，等待一步
                    break
            
            # 移动到下一个位置
            self.position = next_position
            self.path_index += 1
            self.total_distance += 1
            moved = True
            self.wait_counter = 0  # 重置等待计数器
            
            # 消耗电量
            self.battery = max(0, self.battery - self.battery_consumption_rate)
            
            # 检查是否到达目标
            if self.position == target:
                self.replan_attempts = 0
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
            # 到达取货点
            self.current_capacity += 1  # 增加载货量
            
            # 如果使用任务队列，移除完成的任务并处理下一个
            if self.task_queue:
                self.task_queue.pop(0)  # 移除当前取货任务
                self._process_next_task()
            else:
                # 传统模式：开始配送
                self.state = CarState.MOVING_TO_DELIVERY
                self.current_path = []
                self.path_index = 0
            return False
        
        elif self.state == CarState.MOVING_TO_DELIVERY:
            # 到达配送点
            self.current_capacity -= 1  # 减少载货量
            self.completed_orders += 1
            
            # 如果使用任务队列，移除完成的任务并处理下一个
            if self.task_queue:
                self.task_queue.pop(0)  # 移除当前送货任务
                self._process_next_task()
                return self.current_capacity == 0 and not self.task_queue  # 所有任务完成时返回True
            else:
                # 传统模式：重置车辆状态
                self.reset()
                return True
        
        elif self.state == CarState.MOVING_TO_CHARGE:
            # 到达充电站，开始充电
            self.state = CarState.CHARGING
            self.current_path = []
            self.path_index = 0
            return False
        
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
    
    def _smart_avoidance(self, target: Tuple[int, int], blocked_position: Tuple[int, int],
                        pathfinder, other_car_positions: Set[Tuple[int, int]]) -> bool:
        """
        智能避让策略：尝试多种避让方案
        Args:
            target: 目标位置
            blocked_position: 被占用的位置
            pathfinder: 路径规划器
            other_car_positions: 其他车辆位置
        Returns:
            是否成功避让
        """
        # 策略 1：尝试重新规划路径绕过障碍
        if self.replan_attempts < self.max_replan_attempts:
            self.replan_attempts += 1
            if self.plan_path(target, pathfinder, other_car_positions):
                return True
        
        # 策略 2：寻找临时避让点
        alternative_pos = pathfinder.find_alternative_position(self.position, other_car_positions)
        if alternative_pos and alternative_pos != self.position:
            # 移动到避让点
            self.position = alternative_pos
            self.total_distance += 1
            self.current_path = []  # 清空路径，下一步重新规划
            self.replan_attempts = 0
            return True
        
        # 策略 3：无法避让，进入等待状态
        return False
    
    def _handle_deadlock(self, pathfinder, other_car_positions: Set[Tuple[int, int]]) -> bool:
        """
        处理死锁情况：当车辆长时间被卡住时
        Args:
            pathfinder: 路径规划器
            other_car_positions: 其他车辆位置
        Returns:
            是否成功解决死锁
        """
        import random
        
        self.deadlock_recovery_mode = True
        
        # 策略 1：随机移动到相邻的可用位置（破坏死锁循环）
        neighbors = pathfinder.get_neighbors(self.position)
        available_neighbors = [
            pos for pos in neighbors 
            if pos not in other_car_positions
        ]
        
        if available_neighbors:
            # 随机选择一个方向移动
            random_pos = random.choice(available_neighbors)
            self.position = random_pos
            self.total_distance += 1
            self.current_path = []  # 清空路径
            self.stuck_counter = 0
            self.replan_attempts = 0
            return True
        
        # 策略 2：如果没有可用相邻，等待一步（随机等待避免同步）
        if random.random() < 0.3:  # 30%的概率主动等待
            self.stuck_counter = max(0, self.stuck_counter - 2)  # 减少被卡计数
            return False
        
        # 策略 3：完全重置路径规划
        target = self.pickup_point if self.state == CarState.MOVING_TO_PICKUP else self.delivery_point
        if target:
            self.current_path = []
            self.replan_attempts = 0
            if self.plan_path(target, pathfinder, set()):  # 忽略其他车辆，尝试找到任何路径
                self.stuck_counter = 0
                return False
        
        return False
    
    def needs_charging(self) -> bool:
        """
        检查是否需要充电
        Returns:
            是否需要充电
        """
        return self.battery <= self.low_battery_threshold
    
    def is_critical_battery(self) -> bool:
        """
        检查是否为严重低电（必须立即充电）
        Returns:
            是否为严重低电
        """
        return self.battery <= self.critical_battery_threshold
    
    def start_charging(self, charging_station: Tuple[int, int]):
        """
        开始前往充电站
        Args:
            charging_station: 充电站位置
        """
        self.charging_station = charging_station
        self.state = CarState.MOVING_TO_CHARGE
        self.current_path = []
        self.path_index = 0
    
    def charge_step(self) -> bool:
        """
        执行一步充电
        Returns:
            是否充电完成
        """
        if self.state != CarState.CHARGING:
            return False
        
        self.battery = min(self.max_battery, self.battery + self.charging_rate)
        self.total_charging_time += 1
        
        # 如果电量充满，重置为空闲状态
        if self.battery >= self.max_battery:
            self.state = CarState.IDLE
            self.charging_station = None
            return True
        
        return False
    
    def consume_battery(self):
        """消耗电量（移动时调用）"""
        self.battery = max(0, self.battery - self.battery_consumption_rate)
    
    def get_battery_percentage(self) -> float:
        """
        获取电量百分比
        Returns:
            电量百分比 (0-100)
        """
        return (self.battery / self.max_battery) * 100
    
    def _try_avoid(self, pathfinder, blocked_positions: Set[Tuple[int, int]]) -> bool:
        """
        尝试避让策略（保留兼容性）
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
            'delivery_point': self.delivery_point,
            'battery': self.battery,
            'battery_percentage': self.get_battery_percentage(),
            'total_charging_time': self.total_charging_time
        }
    
    def is_idle(self) -> bool:
        """检查车辆是否空闲"""
        return self.state == CarState.IDLE
    
    def is_available_for_task(self) -> bool:
        """
        检查车辆是否可用于接受新任务（空闲且电量充足）
        Returns:
            是否可用
        """
        return self.is_idle() and not self.is_critical_battery()
    
    def get_status_symbol(self) -> str:
        """获取状态符号"""
        if self.deadlock_recovery_mode:
            return "⚠️"  # 死锁恢复模式
        elif self.state == CarState.CHARGING:
            return "🔋"  # 充电中
        elif self.state == CarState.MOVING_TO_CHARGE:
            return "🔋"  # 前往充电站
        elif self.is_critical_battery():
            return "🚫"  # 严重低电
        elif self.state == CarState.IDLE:
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
