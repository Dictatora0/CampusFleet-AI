"""
上下文管理模块 - 管理全局状态和智能体间的通信
"""
from typing import List, Dict, Optional, Tuple
from agents import CarAgent, OrderAgent, SchedulerAgent, SchedulingStrategy
from env import GridEnvironment, PathFinding


class SimulationContext:
    """仿真上下文类 - 管理所有智能体和环境"""
    
    def __init__(self, grid_size: int = 15, num_cars: int = 3, 
                 scheduling_strategy: SchedulingStrategy = SchedulingStrategy.GREEDY_NEAREST):
        """
        初始化仿真上下文
        Args:
            grid_size: 网格大小
            num_cars: 车辆数量
            scheduling_strategy: 调度策略
        """
        # 环境
        self.grid_env = GridEnvironment(size=grid_size)
        self.pathfinder = PathFinding(self.grid_env.grid)
        
        # 智能体
        self.cars: List[CarAgent] = []
        self.order_agent = OrderAgent()
        self.scheduler = SchedulerAgent(strategy=scheduling_strategy)
        
        # 仿真状态
        self.current_step = 0
        self.is_running = False
        self.max_steps = 1000
        
        # 统计信息
        self.total_completed_orders = 0
        self.total_distance_traveled = 0
        
        # 初始化车辆
        self._initialize_cars(num_cars)
    
    def _initialize_cars(self, num_cars: int):
        """
        初始化车辆并放置在地图上
        Args:
            num_cars: 车辆数量
        """
        import random
        road_positions = self.grid_env.get_all_road_positions()
        
        if not road_positions:
            raise ValueError("地图上没有可用的道路位置")
        
        # 随机选择不重复的初始位置
        if len(road_positions) < num_cars:
            num_cars = len(road_positions)
        
        selected_positions = random.sample(road_positions, num_cars)
        
        for i in range(num_cars):
            car = CarAgent(car_id=i, initial_position=selected_positions[i])
            self.cars.append(car)
            self.grid_env.update_vehicle_position(i, selected_positions[i])
    
    def add_order(self, pickup: Tuple[int, int], delivery: Tuple[int, int]) -> Optional[int]:
        """
        添加新订单
        Args:
            pickup: 取货点
            delivery: 配送点
        Returns:
            订单ID，如果添加失败则返回None
        """
        # 验证位置有效性
        if not self.grid_env.is_valid_position(pickup):
            print(f"❌ 无效的取货点: {pickup}")
            return None
        if not self.grid_env.is_valid_position(delivery):
            print(f"❌ 无效的配送点: {delivery}")
            return None
        
        order_id = self.order_agent.create_order(pickup, delivery)
        print(f"✅ 订单 #{order_id} 已创建: {pickup} → {delivery}")
        return order_id
    
    def add_random_order(self) -> Optional[int]:
        """
        添加随机订单
        Returns:
            订单ID
        """
        pickup = self.grid_env.get_random_road_position()
        delivery = self.grid_env.get_random_road_position()
        
        if pickup and delivery and pickup != delivery:
            return self.add_order(pickup, delivery)
        return None
    
    def step(self) -> bool:
        """
        执行一步仿真
        Returns:
            是否继续运行
        """
        if self.current_step >= self.max_steps:
            self.is_running = False
            return False
        
        self.current_step += 1
        
        # 1. 订单智能体更新
        self.order_agent.step()
        
        # 2. 调度智能体进行订单分配
        pending_orders = self.order_agent.get_pending_orders()
        if pending_orders:
            assignments = self.scheduler.schedule(self.cars, pending_orders, self.grid_env)
            
            # 执行分配
            for car_id, order_id, pickup, delivery in assignments:
                car = self.get_car_by_id(car_id)
                if car:
                    car.assign_task(order_id, pickup, delivery)
                    self.order_agent.assign_order(order_id, car_id)
        
        # 3. 车辆智能体更新（移动）
        for car in self.cars:
            if not car.is_idle():
                # 获取其他车辆的位置（用于避障）
                other_positions = set()
                for other_car in self.cars:
                    if other_car.car_id != car.car_id:
                        other_positions.add(other_car.position)
                
                # 执行移动
                order_completed = car.step(self.pathfinder, other_positions)
                
                # 更新环境中的车辆位置
                self.grid_env.update_vehicle_position(car.car_id, car.position)
                
                # 如果订单完成，更新订单状态
                if order_completed and car.current_order_id:
                    self.order_agent.complete_order(car.current_order_id)
                    self.total_completed_orders += 1
        
        # 4. 调度器更新
        self.scheduler.step()
        
        return True
    
    def get_car_by_id(self, car_id: int) -> Optional[CarAgent]:
        """
        根据ID获取车辆
        Args:
            car_id: 车辆ID
        Returns:
            车辆对象，如果不存在则返回None
        """
        for car in self.cars:
            if car.car_id == car_id:
                return car
        return None
    
    def get_status_summary(self) -> str:
        """
        获取系统状态摘要
        Returns:
            状态摘要字符串
        """
        lines = []
        lines.append(f"🕐 步数: {self.current_step} / {self.max_steps}")
        lines.append(f"📊 调度策略: {self.scheduler.get_strategy_name()}")
        lines.append(f"✅ 已完成订单: {self.total_completed_orders}")
        
        # 车辆状态
        lines.append("\n🚗 车辆状态:")
        for car in self.cars:
            state = car.state.value
            pos = car.position
            status = f"  车辆{car.car_id} @ {pos} - {state}"
            if car.current_order_id:
                status += f" [订单#{car.current_order_id}]"
            status += f" (已完成:{car.completed_orders})"
            lines.append(status)
        
        return "\n".join(lines)
    
    def display(self):
        """在控制台显示当前状态"""
        orders_info = self.order_agent.get_orders_summary()
        step_info = self.get_status_summary()
        self.grid_env.display(orders_info, step_info)
    
    def reset(self):
        """重置仿真"""
        self.current_step = 0
        self.is_running = False
        self.total_completed_orders = 0
        self.total_distance_traveled = 0
        
        # 重置所有智能体
        for car in self.cars:
            car.reset()
        self.order_agent.reset()
        self.scheduler.reset()
        
        # 重新初始化车辆位置
        self._initialize_cars(len(self.cars))
    
    def get_statistics(self) -> Dict:
        """
        获取详细统计信息
        Returns:
            统计信息字典
        """
        stats = {
            'current_step': self.current_step,
            'total_completed_orders': self.total_completed_orders,
            'cars': [car.report() for car in self.cars],
            'orders': self.order_agent.report(),
            'scheduler': self.scheduler.report()
        }
        
        # 计算平均距离
        total_distance = sum(car.total_distance for car in self.cars)
        stats['total_distance'] = total_distance
        if self.total_completed_orders > 0:
            stats['avg_distance_per_order'] = total_distance / self.total_completed_orders
        else:
            stats['avg_distance_per_order'] = 0
        
        return stats
