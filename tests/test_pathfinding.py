"""
测试路径规划模块
测试 PathFinding 类的 A* 和 BFS 算法
"""

import pytest

from env import PathFinding


@pytest.fixture
def simple_grid():
    """创建一个简单的5x5测试网格"""
    return [
        [".", ".", ".", ".", "."],
        [".", "#", "#", "#", "."],
        [".", ".", ".", "#", "."],
        [".", "#", ".", ".", "."],
        [".", ".", ".", ".", "."],
    ]


@pytest.fixture
def blocked_grid():
    """创建一个有完全阻隔的网格"""
    return [
        [".", ".", ".", ".", "."],
        [".", "#", "#", "#", "#"],
        [".", "#", ".", ".", "."],
        [".", "#", ".", ".", "."],
        [".", "#", ".", ".", "."],
    ]


@pytest.fixture
def pathfinder_simple(simple_grid):
    """创建一个使用简单网格的路径规划器"""
    return PathFinding(simple_grid)


@pytest.fixture
def pathfinder_blocked(blocked_grid):
    """创建一个使用阻隔网格的路径规划器"""
    return PathFinding(blocked_grid)


class TestPathFindingBasics:
    """测试路径规划的基本功能"""

    def test_initialization(self, simple_grid):
        """测试路径规划器初始化"""
        pf = PathFinding(simple_grid)
        assert pf.rows == 5
        assert pf.cols == 5
        assert pf.grid == simple_grid

    def test_is_valid_position(self, pathfinder_simple):
        """测试位置有效性检查"""
        # 有效位置
        assert pathfinder_simple.is_valid((0, 0)) is True
        assert pathfinder_simple.is_valid((4, 4)) is True

        # 无效位置（越界）
        assert pathfinder_simple.is_valid((-1, 0)) is False
        assert pathfinder_simple.is_valid((5, 0)) is False
        assert pathfinder_simple.is_valid((0, -1)) is False
        assert pathfinder_simple.is_valid((0, 5)) is False

        # 无效位置（障碍物）
        assert pathfinder_simple.is_valid((1, 1)) is False  # '#'
        assert pathfinder_simple.is_valid((1, 2)) is False  # '#'

    def test_get_neighbors(self, pathfinder_simple):
        """测试获取邻居节点"""
        # 中心位置，有4个邻居
        neighbors = pathfinder_simple.get_neighbors((2, 2))
        assert len(neighbors) == 2  # 上和下都是障碍物，只有左右

        # 角落位置
        neighbors = pathfinder_simple.get_neighbors((0, 0))
        assert len(neighbors) == 2  # 右和下

        # 被障碍物包围的位置
        neighbors = pathfinder_simple.get_neighbors((2, 0))
        assert len(neighbors) >= 1

    def test_heuristic(self, pathfinder_simple):
        """测试启发式函数（曼哈顿距离）"""
        # 水平距离
        assert pathfinder_simple.heuristic((0, 0), (0, 4)) == 4

        # 垂直距离
        assert pathfinder_simple.heuristic((0, 0), (4, 0)) == 4

        # 对角距离
        assert pathfinder_simple.heuristic((0, 0), (3, 4)) == 7

        # 同一位置
        assert pathfinder_simple.heuristic((2, 2), (2, 2)) == 0


class TestAStarAlgorithm:
    """测试 A* 算法"""

    def test_simple_path(self, pathfinder_simple):
        """测试简单路径规划"""
        path = pathfinder_simple.a_star((0, 0), (0, 4))
        assert path is not None
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (0, 4)

    def test_path_with_obstacles(self, pathfinder_simple):
        """测试绕过障碍物的路径"""
        path = pathfinder_simple.a_star((0, 2), (4, 2))
        assert path is not None
        assert len(path) > 0
        assert path[0] == (0, 2)
        assert path[-1] == (4, 2)

        # 确保路径不包含障碍物
        for pos in path:
            assert pathfinder_simple.grid[pos[0]][pos[1]] != "#"

    def test_same_start_and_goal(self, pathfinder_simple):
        """测试起点和终点相同的情况"""
        path = pathfinder_simple.a_star((0, 0), (0, 0))
        assert path is not None
        assert len(path) == 1
        assert path[0] == (0, 0)

    def test_invalid_start(self, pathfinder_simple):
        """测试无效起点"""
        path = pathfinder_simple.a_star((1, 1), (4, 4))  # (1,1)是障碍物
        assert path is None

    def test_invalid_goal(self, pathfinder_simple):
        """测试无效终点"""
        path = pathfinder_simple.a_star((0, 0), (1, 1))  # (1,1)是障碍物
        assert path is None

    def test_no_path_exists(self, pathfinder_blocked):
        """测试无路径可达的情况"""
        # 尝试从左边到右边，但被墙完全阻隔
        path = pathfinder_blocked.a_star((0, 0), (2, 4))
        assert path is None

    def test_path_with_blocked_positions(self, pathfinder_simple):
        """测试带有临时阻塞位置的路径规划"""
        # 阻塞某些位置（模拟其他车辆）
        blocked = {(0, 1), (0, 2)}
        path = pathfinder_simple.a_star((0, 0), (0, 4), blocked_positions=blocked)

        assert path is not None
        # 路径应该绕过被阻塞的位置
        for pos in path:
            if pos != (0, 4):  # 终点除外
                assert pos not in blocked

    def test_path_continuity(self, pathfinder_simple):
        """测试路径的连续性"""
        path = pathfinder_simple.a_star((0, 0), (4, 4))
        if path:
            # 检查相邻节点之间的距离为1
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                distance = abs(x2 - x1) + abs(y2 - y1)
                assert distance == 1, "路径中的相邻节点应该直接相连"


class TestBFSAlgorithm:
    """测试 BFS 算法"""

    def test_bfs_simple_path(self, pathfinder_simple):
        """测试BFS简单路径"""
        path = pathfinder_simple.bfs((0, 0), (0, 4))
        assert path is not None
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (0, 4)

    def test_bfs_with_obstacles(self, pathfinder_simple):
        """测试BFS绕过障碍物"""
        path = pathfinder_simple.bfs((0, 2), (4, 2))
        assert path is not None
        assert path[0] == (0, 2)
        assert path[-1] == (4, 2)

    def test_bfs_same_start_and_goal(self, pathfinder_simple):
        """测试BFS起点和终点相同"""
        path = pathfinder_simple.bfs((0, 0), (0, 0))
        assert path is not None
        assert len(path) == 1

    def test_bfs_no_path(self, pathfinder_blocked):
        """测试BFS无路径情况"""
        path = pathfinder_blocked.bfs((0, 0), (2, 4))
        assert path is None


class TestAlternativePosition:
    """测试替代位置查找"""

    def test_find_alternative_position(self, pathfinder_simple):
        """测试找到替代位置"""
        blocked = {(0, 1)}
        alternative = pathfinder_simple.find_alternative_position((0, 0), blocked)

        assert alternative is not None
        assert alternative not in blocked
        assert pathfinder_simple.is_valid(alternative)

    def test_no_alternative_when_surrounded(self, pathfinder_simple):
        """测试被完全包围时无替代位置"""
        # 假设某个位置的所有邻居都被阻塞
        pos = (2, 2)
        neighbors = pathfinder_simple.get_neighbors(pos)
        blocked = set(neighbors)

        alternative = pathfinder_simple.find_alternative_position(pos, blocked)
        # 如果所有邻居都被阻塞，应该返回None
        if len(neighbors) == len(blocked):
            assert alternative is None


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_grid(self):
        """测试空网格"""
        pf = PathFinding([])
        assert pf.rows == 0
        assert pf.cols == 0
        path = pf.a_star((0, 0), (1, 1))
        assert path is None

    def test_single_cell_grid(self):
        """测试单格网格"""
        grid = [
            ["."],
        ]
        pf = PathFinding(grid)
        path = pf.a_star((0, 0), (0, 0))
        assert path == [(0, 0)]

    def test_all_obstacles_grid(self):
        """测试全是障碍物的网格"""
        grid = [["#", "#", "#"], ["#", "#", "#"], ["#", "#", "#"]]
        pf = PathFinding(grid)
        path = pf.a_star((0, 0), (2, 2))
        assert path is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
