"""
路径规划模块 - A*算法实现 + MAPF集成
"""
import heapq
from typing import Dict, List, Optional, Set, Tuple


class PathFinding:
    """路径规划类，支持 A* 和 BFS 算法 + MAPF协调"""
    
    def __init__(self, grid: List[List[str]]):
        """
        初始化路径规划器
        Args:
            grid: 二维网格地图，'#' 表示障碍，'.' 表示道路
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
    
    def is_valid(self, pos: Tuple[int, int]) -> bool:
        """检查位置是否有效且可通行"""
        x, y = pos
        if 0 <= x < self.rows and 0 <= y < self.cols:
            return self.grid[x][y] != '#'
        return False
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """获取相邻的可通行节点（上下左右四个方向）"""
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上、下、左、右
        neighbors = []
        for dx, dy in directions:
            new_pos = (x + dx, y + dy)
            if self.is_valid(new_pos):
                neighbors.append(new_pos)
        return neighbors
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """曼哈顿距离作为启发函数"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def a_star(self, start: Tuple[int, int], goal: Tuple[int, int], 
               blocked_positions: Optional[Set[Tuple[int, int]]] = None) -> Optional[List[Tuple[int, int]]]:
        """
        A* 路径规划算法
        Args:
            start: 起点坐标
            goal: 终点坐标
            blocked_positions: 临时被占用的位置集合（用于避障）
        Returns:
            路径列表，如果无法到达则返回 None
        """
        if blocked_positions is None:
            blocked_positions = set()
        
        if not self.is_valid(start) or not self.is_valid(goal):
            return None
        
        if start == goal:
            return [start]
        
        # 优先队列：(f值, 计数器, 当前位置, 路径)
        counter = 0
        open_set = [(0, counter, start, [start])]
        closed_set = set()
        g_scores = {start: 0}
        
        while open_set:
            f_score, _, current, path = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
            
            if current == goal:
                return path
            
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                # 跳过被临时占用的位置（除了目标点）
                if neighbor in blocked_positions and neighbor != goal:
                    continue
                
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_scores[current] + 1
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    h_score = self.heuristic(neighbor, goal)
                    f_score = tentative_g + h_score
                    counter += 1
                    new_path = path + [neighbor]
                    heapq.heappush(open_set, (f_score, counter, neighbor, new_path))
        
        return None  # 无法到达目标
    
    def bfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        BFS 路径规划算法（备用）
        Args:
            start: 起点坐标
            goal: 终点坐标
        Returns:
            路径列表，如果无法到达则返回 None
        """
        if not self.is_valid(start) or not self.is_valid(goal):
            return None
        
        if start == goal:
            return [start]
        
        from collections import deque
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                new_path = path + [neighbor]
                
                if neighbor == goal:
                    return new_path
                
                visited.add(neighbor)
                queue.append((neighbor, new_path))
        
        return None
    
    def find_alternative_position(self, pos: Tuple[int, int], 
                                  blocked: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        找到附近的可用位置（用于避让）
        Args:
            pos: 当前位置
            blocked: 被占用的位置集合
        Returns:
            可用的替代位置，如果没有则返回 None
        """
        neighbors = self.get_neighbors(pos)
        for neighbor in neighbors:
            if neighbor not in blocked:
                return neighbor
        return None
    
    def enable_mapf_mode(self, mapf_planner=None):
        """
        启用MAPF协调模式
        Args:
            mapf_planner: MAPF规划器实例
        """
        self.mapf_planner = mapf_planner
        self.mapf_enabled = True
        print("✅ 启用MAPF协调模式")
    
    def disable_mapf_mode(self):
        """禁用MAPF模式，回到传统避障"""
        self.mapf_enabled = False
        self.mapf_planner = None
        print("🔄 回到传统避障模式")
    
    def plan_coordinated_paths(self, agents: List, goals: Dict[int, Tuple[int, int]]) -> Optional[Dict[int, List[Tuple[int, int]]]]:
        """
        协调规划多个智能体的路径 (MAPF)
        Args:
            agents: 智能体列表
            goals: 目标位置字典 {agent_id: (x, y)}
        Returns:
            路径字典 {agent_id: path} 或 None
        """
        if not hasattr(self, 'mapf_planner') or self.mapf_planner is None:
            print("⚠️  MAPF规划器未初始化")
            return None
        
        return self.mapf_planner.plan_multi_agent_paths(agents, goals)
