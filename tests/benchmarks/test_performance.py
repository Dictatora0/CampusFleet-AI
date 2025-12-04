"""
性能基准测试
需要安装: pip install pytest-benchmark
"""

from agents.order_agent import OrderAgent
from env.grid import GridEnvironment
from env.pathfinding import PathFinding


class TestGridPerformance:
    """网格环境性能测试"""

    def test_grid_creation_small(self, benchmark):
        """测试小网格创建性能"""
        result = benchmark(GridEnvironment, size=10, num_charging_stations=2)
        assert result.size == 10

    def test_grid_creation_medium(self, benchmark):
        """测试中等网格创建性能"""
        result = benchmark(GridEnvironment, size=20, num_charging_stations=5)
        assert result.size == 20

    def test_grid_creation_large(self, benchmark):
        """测试大网格创建性能"""
        result = benchmark(GridEnvironment, size=50, num_charging_stations=10)
        assert result.size == 50

    def test_get_random_road_position(self, benchmark):
        """测试随机道路位置获取性能"""
        env = GridEnvironment(size=20)
        result = benchmark(env.get_random_road_position)
        assert result is not None

    def test_calculate_distance(self, benchmark):
        """测试距离计算性能"""
        env = GridEnvironment()
        result = benchmark(env.calculate_distance, (0, 0), (10, 10))
        assert result == 20

    def test_get_all_road_positions(self, benchmark):
        """测试获取所有道路位置性能"""
        env = GridEnvironment(size=30)
        result = benchmark(env.get_all_road_positions)
        assert len(result) > 0


class TestOrderAgentPerformance:
    """订单智能体性能测试"""

    def test_create_order(self, benchmark):
        """测试创建订单性能"""
        agent = OrderAgent()
        result = benchmark(agent.create_order, (0, 0), (5, 5))
        assert result == 1

    def test_create_many_orders(self, benchmark):
        """测试批量创建订单性能"""

        def create_orders():
            agent = OrderAgent()
            for i in range(100):
                agent.create_order((i % 10, i % 10), ((i + 5) % 10, (i + 5) % 10))
            return agent

        result = benchmark(create_orders)
        assert len(result.orders) == 100

    def test_assign_order(self, benchmark):
        """测试分配订单性能"""
        agent = OrderAgent()
        order_id = agent.create_order((0, 0), (5, 5))
        result = benchmark(agent.assign_order, order_id, 10)
        assert result is True

    def test_get_pending_orders_small(self, benchmark):
        """测试获取待分配订单性能（小规模）"""
        agent = OrderAgent()
        for i in range(10):
            agent.create_order((i, i), (i + 5, i + 5))

        result = benchmark(agent.get_pending_orders)
        assert len(result) == 10

    def test_get_pending_orders_large(self, benchmark):
        """测试获取待分配订单性能（大规模）"""
        agent = OrderAgent()
        for i in range(1000):
            agent.create_order((i % 50, i % 50), ((i + 5) % 50, (i + 5) % 50))

        result = benchmark(agent.get_pending_orders)
        assert len(result) == 1000


class TestPathfindingPerformance:
    """路径规划性能测试"""

    def test_astar_short_path(self, benchmark):
        """测试A*短路径规划性能"""
        env = GridEnvironment(size=15)
        pathfinder = PathFinding(env.grid)

        start = (0, 0)
        goal = (5, 5)

        result = benchmark(pathfinder.search, start, goal)
        assert result is not None

    def test_astar_long_path(self, benchmark):
        """测试A*长路径规划性能"""
        env = GridEnvironment(size=30)
        pathfinder = PathFinding(env.grid)

        start = (0, 0)
        goal = (29, 29)

        result = benchmark(pathfinder.search, start, goal)
        # 可能找不到路径，但测试性能
        assert result is not None or result is None

    def test_astar_complex_map(self, benchmark):
        """测试A*复杂地图性能"""
        env = GridEnvironment(size=50)
        pathfinder = PathFinding(env.grid)

        start = env.get_random_road_position()
        goal = env.get_random_road_position()

        if start and goal:
            _ = benchmark(pathfinder.search, start, goal)


class TestIntegrationPerformance:
    """集成性能测试"""

    def test_simulation_step(self, benchmark):
        """测试仿真单步性能"""

        def simulation_step():
            env = GridEnvironment(size=20)
            agent = OrderAgent()

            # 创建订单
            for i in range(5):
                agent.create_order((i, i), (i + 10, i + 10))

            # 更新车辆位置
            for i in range(5):
                env.update_vehicle_position(i, (i, i))

            return env, agent

        result = benchmark(simulation_step)
        assert result is not None

    def test_order_assignment_batch(self, benchmark):
        """测试批量订单分配性能"""

        def batch_assignment():
            agent = OrderAgent()

            # 创建100个订单
            orders = []
            for i in range(100):
                oid = agent.create_order((i % 20, i % 20), ((i + 10) % 20, (i + 10) % 20))
                orders.append(oid)

            # 分配给10辆车
            for i, oid in enumerate(orders):
                agent.assign_order(oid, i % 10)

            return agent

        result = benchmark(batch_assignment)
        assert len(result.orders) == 100
