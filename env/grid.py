"""
网格环境模块 - 管理校园地图和车辆显示
"""
import os
import time
from typing import Dict, List, Optional, Tuple


class GridEnvironment:
    """校园网格环境类"""
    
    def __init__(self, size: int = 15, num_charging_stations: int = 2):
        """
        初始化网格环境
        Args:
            size: 网格大小（N×N）
            num_charging_stations: 充电站数量
        """
        self.size = size
        self.grid = self._create_default_grid()
        self.vehicle_positions: Dict[int, Tuple[int, int]] = {}  # 车辆ID -> 位置
        self.charging_stations: List[Tuple[int, int]] = []  # 充电站位置列表
        self._initialize_charging_stations(num_charging_stations)
        
    def _create_default_grid(self) -> List[List[str]]:
        """
        创建默认的校园地图
        '#' 代表建筑/障碍
        '.' 代表道路
        """
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        
        # 根据网格大小动态添加建筑物/障碍
        if self.size >= 15:
            # 大型地图：添加多个建筑
            # 中心建筑群
            for i in range(5, 10):
                for j in range(5, 10):
                    grid[i][j] = '#'
            
            # 左上角建筑
            for i in range(1, 4):
                for j in range(1, 4):
                    grid[i][j] = '#'
            
            # 右上角建筑
            for i in range(1, 4):
                for j in range(11, 14):
                    grid[i][j] = '#'
            
            # 左下角建筑
            for i in range(11, 14):
                for j in range(1, 4):
                    grid[i][j] = '#'
            
            # 右下角建筑
            for i in range(11, 14):
                for j in range(11, 14):
                    grid[i][j] = '#'
        
        elif self.size >= 10:
            # 中型地图：添加少量建筑
            center = self.size // 2
            size = max(2, self.size // 5)
            
            # 中心建筑
            for i in range(center - size, min(center + size, self.size)):
                for j in range(center - size, min(center + size, self.size)):
                    if 0 <= i < self.size and 0 <= j < self.size:
                        grid[i][j] = '#'
            
            # 四个角落的小建筑
            corner_size = max(1, self.size // 10)
            corners = [
                (1, 1),
                (1, self.size - corner_size - 1),
                (self.size - corner_size - 1, 1),
                (self.size - corner_size - 1, self.size - corner_size - 1)
            ]
            
            for cx, cy in corners:
                for i in range(cx, min(cx + corner_size, self.size)):
                    for j in range(cy, min(cy + corner_size, self.size)):
                        if 0 <= i < self.size and 0 <= j < self.size:
                            grid[i][j] = '#'
        
        # 小型地图（< 10）：只添加中心小障碍
        elif self.size >= 5:
            center = self.size // 2
            if center > 0 and center < self.size - 1:
                grid[center][center] = '#'
        
        return grid
    
    def _initialize_charging_stations(self, num_stations: int):
        """
        初始化充电站位置（在地图边缘选择）
        Args:
            num_stations: 充电站数量
        """
        import random

        # 优先选择地图边缘的道路位置
        edge_positions = []
        
        # 上边和下边
        for j in range(self.size):
            if self.grid[0][j] == '.':
                edge_positions.append((0, j))
            if self.grid[self.size-1][j] == '.':
                edge_positions.append((self.size-1, j))
        
        # 左边和右边
        for i in range(1, self.size-1):
            if self.grid[i][0] == '.':
                edge_positions.append((i, 0))
            if self.grid[i][self.size-1] == '.':
                edge_positions.append((i, self.size-1))
        
        # 如果边缘位置不够，从所有道路位置中选择
        if len(edge_positions) < num_stations:
            edge_positions = self.get_all_road_positions()
        
        if edge_positions:
            selected = random.sample(edge_positions, min(num_stations, len(edge_positions)))
            self.charging_stations = selected
    
    def get_charging_stations(self) -> List[Tuple[int, int]]:
        """获取所有充电站位置"""
        return self.charging_stations
    
    def get_nearest_charging_station(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        获取离指定位置最近的充电站
        Args:
            pos: 当前位置
        Returns:
            最近的充电站位置
        """
        if not self.charging_stations:
            return None
        
        min_distance = float('inf')
        nearest_station = None
        
        for station in self.charging_stations:
            distance = self.calculate_distance(pos, station)
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        
        return nearest_station
    
    def get_occupied_positions(self) -> set:
        """获取所有被车辆占用的位置"""
        return set(self.vehicle_positions.values())
    
    def update_vehicle_position(self, vehicle_id: int, position: Tuple[int, int]) -> None:
        """
        更新车辆位置
        
        Args:
            vehicle_id: 车辆ID
            position: 新位置坐标 (x, y)
        """
        self.vehicle_positions[vehicle_id] = position
    
    def remove_vehicle(self, vehicle_id: int) -> None:
        """
        移除车辆（当车辆离开系统时）
        
        Args:
            vehicle_id: 要移除的车辆ID
        """
        if vehicle_id in self.vehicle_positions:
            del self.vehicle_positions[vehicle_id]
    
    def get_vehicle_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """获取指定位置的车辆ID"""
        for vid, vpos in self.vehicle_positions.items():
            if vpos == pos:
                return vid
        return None
    
    def display(self, orders_info: str = "", step_info: str = ""):
        """
        在控制台显示当前网格状态
        Args:
            orders_info: 订单信息字符串
            step_info: 步骤信息字符串
        """
        # 清屏（跨平台）
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 60)
        print("🚗 校园无人配送车多智能体系统 🚗")
        print("=" * 60)
        print(step_info)
        print()
        
        # 创建显示网格
        display_grid = [row[:] for row in self.grid]
        
        # 在网格上标记充电站
        for x, y in self.charging_stations:
            display_grid[x][y] = 'C'
        
        # 在网格上标记车辆（覆盖充电站标记）
        for vehicle_id, (x, y) in self.vehicle_positions.items():
            # 用车辆ID的个位数表示车辆
            display_grid[x][y] = str(vehicle_id % 10)
        
        # 打印网格（带边框）
        print("  " + " ".join([str(i % 10) for i in range(self.size)]))
        for i, row in enumerate(display_grid):
            print(f"{i % 10} " + " ".join(row))
        
        print()
        print("图例: '.' = 道路, '#' = 建筑, 'C' = 充电站, 数字 = 车辆ID")
        print()
        print(orders_info)
        print("=" * 60)
    
    def get_random_road_position(self) -> Optional[Tuple[int, int]]:
        """获取一个随机的道路位置"""
        import random
        road_positions = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == '.':
                    road_positions.append((i, j))
        
        if road_positions:
            return random.choice(road_positions)
        return None
    
    def get_all_road_positions(self) -> List[Tuple[int, int]]:
        """获取所有道路位置"""
        positions = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == '.':
                    positions.append((i, j))
        return positions
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """计算两点之间的曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """
        检查位置是否在网格范围内
        Args:
            pos: 位置坐标 (x, y)
        Returns:
            是否有效
        """
        x, y = pos
        return 0 <= x < self.size and 0 <= y < self.size
    
    def is_passable(self, pos: Tuple[int, int]) -> bool:
        """
        检查位置是否可通行（不是障碍物）
        Args:
            pos: 位置坐标 (x, y)  
        Returns:
            是否可通行
        """
        if not self.is_valid_position(pos):
            return False
        x, y = pos
        return self.grid[y][x] != '#'  # 注意：grid[y][x]因为grid是按行存储的
