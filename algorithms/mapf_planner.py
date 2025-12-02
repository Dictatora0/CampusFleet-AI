"""
多智能体路径规划 (MAPF) 模块
实现CBS (Conflict-Based Search) 算法
"""
from typing import List, Tuple, Dict, Set, Optional, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import heapq
import copy
from collections import defaultdict


class ConflictType(Enum):
    """冲突类型"""
    VERTEX = "vertex"  # 顶点冲突（同一时刻同一位置）
    EDGE = "edge"      # 边冲突（交换位置）


@dataclass
class Conflict:
    """冲突定义"""
    type: ConflictType
    time: int
    agent1: int
    agent2: int
    location1: Tuple[int, int]
    location2: Optional[Tuple[int, int]] = None  # 边冲突时使用
    
    def __hash__(self):
        return hash((self.type, self.time, self.agent1, self.agent2, self.location1, self.location2))


@dataclass
class Constraint:
    """约束定义"""
    agent: int
    time: int
    location: Tuple[int, int]
    type: ConflictType = ConflictType.VERTEX
    forbidden_from: Optional[Tuple[int, int]] = None  # 边约束的起点


@dataclass
class CBSNode:
    """CBS树节点"""
    constraints: Set[Constraint] = field(default_factory=set)
    solution: Dict[int, List[Tuple[int, int]]] = field(default_factory=dict)
    cost: float = 0.0
    conflicts: Set[Conflict] = field(default_factory=set)
    
    def __lt__(self, other):
        return self.cost < other.cost


class SpaceTimeAStar:
    """
    时空A*算法 - 考虑时间维度的路径规划
    """
    
    def __init__(self, grid_env):
        self.grid_env = grid_env
        self.max_time = 200  # 最大时间步数
    
    def plan_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  constraints: Set[Constraint]) -> Optional[List[Tuple[int, int]]]:
        """
        规划从起点到终点的路径，考虑约束
        Args:
            start: 起始位置
            goal: 目标位置
            constraints: 约束集合
        Returns:
            路径列表，如果无解返回None
        """
        # 构建约束表 {(time, location): True}
        vertex_constraints = set()
        edge_constraints = set()
        
        for constraint in constraints:
            if constraint.type == ConflictType.VERTEX:
                vertex_constraints.add((constraint.time, constraint.location))
            else:  # EDGE
                edge_constraints.add((constraint.time, constraint.forbidden_from, constraint.location))
        
        # A* 搜索
        open_list = [(self._heuristic(start, goal), 0, start, [])]  # (f, g, pos, path)
        closed_set = set()
        
        while open_list:
            f, g, current_pos, path = heapq.heappop(open_list)
            current_time = len(path)
            
            # 检查是否到达目标
            if current_pos == goal:
                return path + [current_pos]
            
            state = (current_time, current_pos)
            if state in closed_set:
                continue
            closed_set.add(state)
            
            # 时间限制
            if current_time >= self.max_time:
                continue
            
            # 生成后继状态
            successors = self._get_successors(current_pos, current_time, 
                                            vertex_constraints, edge_constraints)
            
            for next_pos in successors:
                next_time = current_time + 1
                next_state = (next_time, next_pos)
                
                if next_state not in closed_set:
                    new_path = path + [current_pos]
                    new_g = g + 1
                    new_f = new_g + self._heuristic(next_pos, goal)
                    
                    heapq.heappush(open_list, (new_f, new_g, next_pos, new_path))
        
        return None  # 无解
    
    def _get_successors(self, pos: Tuple[int, int], time: int,
                       vertex_constraints: Set, edge_constraints: Set) -> List[Tuple[int, int]]:
        """获取有效的后继位置"""
        successors = []
        
        # 等待动作（stay）
        if (time + 1, pos) not in vertex_constraints:
            successors.append(pos)
        
        # 移动动作
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 右、下、左、上
        
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            
            # 检查边界
            if not self.grid_env.is_valid_position(new_pos):
                continue
            
            # 检查障碍物
            if not self.grid_env.is_passable(new_pos):
                continue
            
            # 检查顶点约束
            if (time + 1, new_pos) in vertex_constraints:
                continue
            
            # 检查边约束
            if (time + 1, pos, new_pos) in edge_constraints:
                continue
                
            successors.append(new_pos)
        
        return successors
    
    def _heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """曼哈顿距离启发函数"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class ConflictBasedSearch:
    """
    冲突感知搜索 (CBS) 算法
    
    CBS是MAPF问题的完备算法，通过构建约束树来逐步解决冲突：
    1. 根节点：为每个agent单独规划最优路径
    2. 检测冲突：找到第一个时空冲突
    3. 分支：为冲突的两个agent分别添加约束
    4. 递归：对每个分支重新规划和检测冲突
    """
    
    def __init__(self, grid_env):
        self.grid_env = grid_env
        self.space_time_astar = SpaceTimeAStar(grid_env)
    
    def plan_paths(self, agents: List, goals: Dict[int, Tuple[int, int]]) -> Optional[Dict[int, List[Tuple[int, int]]]]:
        """
        为多个智能体规划无冲突路径
        Args:
            agents: 智能体列表
            goals: 目标位置字典 {agent_id: (x, y)}
        Returns:
            路径字典 {agent_id: path} 或 None (无解)
        """
        if not agents or not goals:
            return {}
        
        # 创建根节点
        root = CBSNode()
        
        # 为每个agent单独规划初始路径
        for agent in agents:
            agent_id = agent.car_id
            if agent_id not in goals:
                continue
                
            start = agent.position
            goal = goals[agent_id]
            
            # 单agent最优路径
            path = self.space_time_astar.plan_path(start, goal, set())
            if path is None:
                print(f"❌ Agent {agent_id}: 无法找到路径 {start} -> {goal}")
                return None
            
            root.solution[agent_id] = path
            root.cost += len(path) - 1  # 路径成本
        
        # 检测初始冲突
        root.conflicts = self._detect_conflicts(root.solution)
        
        if not root.conflicts:
            print("✅ 初始解无冲突")
            return root.solution
        
        # CBS搜索
        open_list = [root]
        expanded_nodes = 0
        max_expansions = 1000  # 防止无限搜索
        
        print(f"🔍 开始CBS搜索，初始冲突数: {len(root.conflicts)}")
        
        while open_list and expanded_nodes < max_expansions:
            # 选择成本最低的节点
            current_node = heapq.heappop(open_list)
            expanded_nodes += 1
            
            if expanded_nodes % 100 == 0:
                print(f"  - 已扩展 {expanded_nodes} 节点，当前成本: {current_node.cost:.1f}")
            
            # 如果无冲突，找到解
            if not current_node.conflicts:
                print(f"✅ CBS找到解! 扩展了 {expanded_nodes} 节点")
                return current_node.solution
            
            # 选择第一个冲突进行分支
            conflict = next(iter(current_node.conflicts))
            
            # 为冲突的两个agent分别创建约束
            child_nodes = self._create_child_nodes(current_node, conflict)
            
            # 将子节点加入open_list
            for child in child_nodes:
                if child is not None:
                    heapq.heappush(open_list, child)
        
        print(f"❌ CBS搜索失败，已扩展 {expanded_nodes} 节点")
        return None
    
    def _detect_conflicts(self, solution: Dict[int, List[Tuple[int, int]]]) -> Set[Conflict]:
        """
        检测路径解中的冲突
        """
        conflicts = set()
        
        agents = list(solution.keys())
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                path1 = solution[agent1]
                path2 = solution[agent2]
                
                # 检测顶点冲突和边冲突
                max_len = max(len(path1), len(path2))
                
                for t in range(max_len):
                    # 获取时刻t的位置（超出路径长度则停留在终点）
                    pos1 = path1[min(t, len(path1) - 1)]
                    pos2 = path2[min(t, len(path2) - 1)]
                    
                    # 顶点冲突：同一时刻同一位置
                    if pos1 == pos2:
                        conflict = Conflict(
                            type=ConflictType.VERTEX,
                            time=t,
                            agent1=agent1,
                            agent2=agent2,
                            location1=pos1
                        )
                        conflicts.add(conflict)
                    
                    # 边冲突：相邻时刻交换位置
                    if t > 0:
                        prev_pos1 = path1[min(t-1, len(path1) - 1)]
                        prev_pos2 = path2[min(t-1, len(path2) - 1)]
                        
                        if pos1 == prev_pos2 and pos2 == prev_pos1 and pos1 != pos2:
                            conflict = Conflict(
                                type=ConflictType.EDGE,
                                time=t,
                                agent1=agent1,
                                agent2=agent2,
                                location1=pos1,
                                location2=pos2
                            )
                            conflicts.add(conflict)
        
        return conflicts
    
    def _create_child_nodes(self, parent: CBSNode, conflict: Conflict) -> List[Optional[CBSNode]]:
        """
        根据冲突创建子节点
        """
        children = []
        
        # 为两个冲突的agent分别创建约束
        agents = [conflict.agent1, conflict.agent2]
        locations = [conflict.location1, conflict.location2 if conflict.location2 else conflict.location1]
        
        for i, (agent, location) in enumerate(zip(agents, locations)):
            child = CBSNode()
            child.constraints = copy.deepcopy(parent.constraints)
            child.solution = copy.deepcopy(parent.solution)
            
            # 添加新约束
            if conflict.type == ConflictType.VERTEX:
                constraint = Constraint(
                    agent=agent,
                    time=conflict.time,
                    location=location,
                    type=ConflictType.VERTEX
                )
            else:  # EDGE
                constraint = Constraint(
                    agent=agent,
                    time=conflict.time,
                    location=location,
                    type=ConflictType.EDGE,
                    forbidden_from=locations[1-i]  # 另一个位置
                )
            
            child.constraints.add(constraint)
            
            # 为受约束的agent重新规划路径
            agent_constraints = {c for c in child.constraints if c.agent == agent}
            
            # 获取agent的起点和终点
            original_path = parent.solution[agent]
            if not original_path:
                continue
                
            start = original_path[0]
            goal = original_path[-1]
            
            # 重新规划路径
            new_path = self.space_time_astar.plan_path(start, goal, agent_constraints)
            
            if new_path is None:
                # 无法重新规划，跳过这个子节点
                continue
            
            child.solution[agent] = new_path
            
            # 重新计算成本
            child.cost = sum(len(path) - 1 for path in child.solution.values())
            
            # 检测新的冲突
            child.conflicts = self._detect_conflicts(child.solution)
            
            children.append(child)
        
        return children


class MAPFPlanner:
    """
    多智能体路径规划器 - 统一接口
    """
    
    def __init__(self, grid_env, algorithm="CBS"):
        self.grid_env = grid_env
        self.algorithm = algorithm
        
        if algorithm == "CBS":
            self.planner = ConflictBasedSearch(grid_env)
        else:
            raise ValueError(f"不支持的MAPF算法: {algorithm}")
    
    def plan_multi_agent_paths(self, agents: List, goals: Dict[int, Tuple[int, int]]) -> Optional[Dict[int, List[Tuple[int, int]]]]:
        """
        统一的多智能体路径规划接口
        """
        return self.planner.plan_paths(agents, goals)
    
    def get_algorithm_info(self) -> Dict:
        """获取算法信息"""
        return {
            "name": "Conflict-Based Search (CBS)",
            "type": "Complete MAPF Algorithm", 
            "complexity": "Exponential in worst case",
            "optimality": "Optimal solutions",
            "completeness": "Complete for finite graphs"
        }
