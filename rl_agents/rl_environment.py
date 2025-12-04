"""
强化学习环境封装
为CampusFleet AI系统提供标准的Gym接口
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents import SchedulingStrategy
from core import SimulationContext


class StateEncoder:
    """状态编码器 - 将仿真状态转换为RL可用的向量"""

    def __init__(self, grid_size: int = 15, max_cars: int = 10, max_orders: int = 20):
        """
        初始化状态编码器

        Args:
            grid_size: 网格大小
            max_cars: 最大车辆数
            max_orders: 最大订单数
        """
        self.grid_size = grid_size
        self.max_cars = max_cars
        self.max_orders = max_orders

        # 状态维度计算
        self.vehicle_features = 6  # x, y, state, battery, capacity, current_order
        self.order_features = 5  # pickup_x, pickup_y, delivery_x, delivery_y, priority
        self.global_features = 8  # step, total_orders, completed_orders, avg_distance, etc.

        self.state_dim = (
            self.vehicle_features * max_cars
            + self.order_features * max_orders
            + self.global_features
        )

    def encode_state(self, context: SimulationContext) -> np.ndarray:
        """
        编码仿真状态为RL状态向量

        Args:
            context: 仿真上下文

        Returns:
            状态向量 (state_dim,)
        """
        state = np.zeros(self.state_dim, dtype=np.float32)
        idx = 0

        # 1. 车辆状态编码
        cars = context.cars[: self.max_cars]  # 限制车辆数量
        for i, car in enumerate(cars):
            if i < self.max_cars:
                # 位置信息 (归一化到 [0, 1])
                state[idx : idx + 2] = [
                    car.position[0] / self.grid_size,
                    car.position[1] / self.grid_size,
                ]
                idx += 2

                # 状态编码 (one-hot)
                state_mapping = {"Idle": 0, "To Pickup": 1, "Delivering": 2, "Charging": 3}
                state[idx] = state_mapping.get(car.state.value, 0) / 3.0
                idx += 1

                # 电量 (归一化)
                state[idx] = car.battery / car.max_battery
                idx += 1

                # 载货量 (归一化)
                state[idx] = car.current_capacity / car.max_capacity
                idx += 1

                # 当前订单 (0=无订单, 1=有订单)
                state[idx] = 1.0 if car.current_order_id else 0.0
                idx += 1

        # 如果车辆数不足，跳过剩余位置
        idx = self.vehicle_features * self.max_cars

        # 2. 订单状态编码
        pending_orders = context.order_agent.get_pending_orders()[: self.max_orders]
        for i, order in enumerate(pending_orders):
            if i < self.max_orders:
                # 取货点和配送点 (归一化)
                state[idx : idx + 4] = [
                    order.pickup_point[0] / self.grid_size,
                    order.pickup_point[1] / self.grid_size,
                    order.delivery_point[0] / self.grid_size,
                    order.delivery_point[1] / self.grid_size,
                ]
                idx += 4

                # 优先级 (假设为0-1)
                state[idx] = getattr(order, "priority", 0.5)
                idx += 1

        # 跳过剩余订单位置
        idx = self.vehicle_features * self.max_cars + self.order_features * self.max_orders

        # 3. 全局状态信息
        stats = context.get_statistics()

        state[idx : idx + 8] = [
            # 时间步 (归一化，假设最大1000步)
            getattr(context, "step_count", 0) / 1000.0,
            # 订单统计
            stats.get("total_orders", 0) / 100.0,  # 归一化
            stats.get("total_completed_orders", 0) / 100.0,
            stats.get("completion_rate", 0.0),
            # 效率指标
            min(stats.get("avg_distance_per_order", 0) / 50.0, 1.0),  # 限制最大值
            min(stats.get("avg_completion_time", 0) / 100.0, 1.0),
            # 车辆利用率
            len([c for c in cars if not c.is_idle()]) / max(len(cars), 1),
            # 待处理订单比例
            len(pending_orders) / max(stats.get("total_orders", 1), 1),
        ]

        return state

    def get_state_info(self) -> Dict[str, Any]:
        """获取状态空间信息"""
        return {
            "state_dim": self.state_dim,
            "vehicle_features": self.vehicle_features,
            "order_features": self.order_features,
            "global_features": self.global_features,
            "max_cars": self.max_cars,
            "max_orders": self.max_orders,
        }


class RewardCalculator:
    """奖励函数计算器 - 设计综合奖励信号"""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化奖励计算器

        Args:
            weights: 奖励权重配置
        """
        self.weights = weights or {
            "completion": 10.0,  # 完成订单奖励
            "efficiency": 5.0,  # 效率奖励
            "distance_penalty": -0.1,  # 距离惩罚
            "time_penalty": -0.05,  # 时间惩罚
            "idle_penalty": -0.02,  # 空闲惩罚
            "deadlock_penalty": -50.0,  # 死锁严重惩罚
        }

        self.prev_stats = {}
        self.episode_start_stats = {}

    def calculate_reward(
        self, context: SimulationContext, action_taken: Dict, prev_state: Optional[Dict] = None
    ) -> float:
        """
        计算即时奖励

        Args:
            context: 当前仿真上下文
            action_taken: 执行的动作
            prev_state: 前一状态（用于计算差值）

        Returns:
            奖励值
        """
        current_stats = context.get_statistics()
        reward = 0.0

        # 1. 订单完成奖励
        if self.prev_stats.get("total_completed_orders", 0) < current_stats.get(
            "total_completed_orders", 0
        ):
            completed_diff = current_stats.get("total_completed_orders", 0) - self.prev_stats.get(
                "total_completed_orders", 0
            )
            reward += self.weights["completion"] * completed_diff

        # 2. 效率奖励 (基于平均距离的改善)
        current_avg_dist = current_stats.get("avg_distance_per_order", 0)
        prev_avg_dist = self.prev_stats.get("avg_distance_per_order", current_avg_dist)

        if prev_avg_dist > 0 and current_avg_dist > 0:
            # 如果平均距离减少，给予奖励
            efficiency_improvement = (prev_avg_dist - current_avg_dist) / prev_avg_dist
            reward += self.weights["efficiency"] * efficiency_improvement

        # 3. 距离惩罚 (鼓励短距离分配)
        total_distance = current_stats.get("total_distance", 0)
        prev_distance = self.prev_stats.get("total_distance", 0)
        distance_increase = total_distance - prev_distance
        reward += self.weights["distance_penalty"] * distance_increase

        # 4. 时间惩罚 (每步都有小惩罚，鼓励快速完成)
        reward += self.weights["time_penalty"]

        # 5. 空闲车辆惩罚
        idle_cars = len([car for car in context.cars if car.is_idle()])
        pending_orders = len(context.order_agent.pending_orders)
        if pending_orders > 0 and idle_cars > 0:
            reward += self.weights["idle_penalty"] * idle_cars

        # 6. 死锁检测和严重惩罚
        if self._detect_potential_deadlock(context):
            reward += self.weights["deadlock_penalty"]

        # 更新历史状态
        self.prev_stats = current_stats.copy()

        return reward

    def _detect_potential_deadlock(self, context: SimulationContext) -> bool:
        """简单的死锁检测"""
        # 如果有待处理订单但所有车都卡住不动，可能是死锁
        if len(context.order_agent.pending_orders) > 0:
            moving_cars = 0
            for car in context.cars:
                if hasattr(car, "last_position") and car.position != car.last_position:
                    moving_cars += 1

            if moving_cars == 0:  # 所有车都没在移动
                return True

        return False

    def reset_episode(self, context: SimulationContext):
        """重置episode统计"""
        self.prev_stats = context.get_statistics().copy()
        self.episode_start_stats = self.prev_stats.copy()

    def get_episode_reward_summary(self, context: SimulationContext) -> Dict[str, float]:
        """获取episode奖励总结"""
        current_stats = context.get_statistics()
        start_stats = self.episode_start_stats

        return {
            "total_completed": current_stats.get("total_completed_orders", 0)
            - start_stats.get("total_completed_orders", 0),
            "efficiency_change": (
                start_stats.get("avg_distance_per_order", 0)
                - current_stats.get("avg_distance_per_order", 0)
            ),
            "total_distance": current_stats.get("total_distance", 0)
            - start_stats.get("total_distance", 0),
            "completion_rate": current_stats.get("completion_rate", 0.0),
        }


class RLEnvironment(gym.Env):
    """
    强化学习环境 - Gymnasium接口实现
    为CampusFleet AI提供标准的RL训练环境
    """

    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
        self,
        grid_size: int = 10,
        num_cars: int = 3,
        max_steps: int = 200,
        max_orders_per_episode: int = 15,
    ):
        """
        初始化RL环境

        Args:
            grid_size: 网格大小
            num_cars: 车辆数量
            max_steps: 最大步数
            max_orders_per_episode: 每episode最大订单数
        """
        super().__init__()

        self.grid_size = grid_size
        self.num_cars = num_cars
        self.max_steps = max_steps
        self.max_orders_per_episode = max_orders_per_episode

        # 初始化状态编码器和奖励计算器
        self.state_encoder = StateEncoder(grid_size, num_cars, max_orders_per_episode)
        self.reward_calculator = RewardCalculator()

        # 定义动作和观察空间
        # 动作空间：为每个车辆选择一个订单 (num_cars, num_orders + 1)
        # +1 表示"不分配订单"
        self.action_space = spaces.MultiDiscrete([max_orders_per_episode + 1] * num_cars)

        # 观察空间：连续状态向量
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(self.state_encoder.state_dim,), dtype=np.float32
        )

        # 仿真环境
        self.context = None
        self.current_step = 0
        self.total_orders_generated = 0

        print(" RL环境初始化完成")
        print(f"状态维度: {self.state_encoder.state_dim}")
        print(f"动作空间: {self.action_space}")
        print(f"🔄 最大步数: {max_steps}")

    def reset(self, seed: Optional[int] = None, **kwargs) -> Tuple[np.ndarray, Dict]:
        """
        重置环境

        Returns:
            observation: 初始观察
            info: 环境信息
        """
        super().reset(seed=seed)

        # 创建新的仿真上下文
        self.context = SimulationContext(
            grid_size=self.grid_size,
            num_cars=self.num_cars,
            scheduling_strategy=SchedulingStrategy.GREEDY_NEAREST,  # 临时使用
            enable_data_logging=False,
        )

        self.current_step = 0
        self.total_orders_generated = 0

        # 生成初始订单
        self._generate_orders()

        # 重置奖励计算器
        self.reward_calculator.reset_episode(self.context)

        # 获取初始状态
        observation = self.state_encoder.encode_state(self.context)

        info = {
            "step": self.current_step,
            "orders_generated": self.total_orders_generated,
            "pending_orders": len(self.context.order_agent.pending_orders),
        }

        return observation, info

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        执行动作

        Args:
            action: 动作数组 [car0_order_idx, car1_order_idx, ...]

        Returns:
            observation: 新观察
            reward: 奖励
            terminated: 是否终止
            truncated: 是否截断
            info: 信息字典
        """
        # 执行RL调度决策
        assignments = self._action_to_assignments(action)
        self._apply_assignments(assignments)

        # 执行一步仿真
        self.context.step()
        self.current_step += 1

        # 计算奖励
        reward = self.reward_calculator.calculate_reward(
            self.context, {"action": action, "assignments": assignments}
        )

        # 随机生成新订单
        if np.random.random() < 0.3 and self.total_orders_generated < self.max_orders_per_episode:
            self._generate_orders()

        # 获取新状态
        observation = self.state_encoder.encode_state(self.context)

        # 检查终止条件
        terminated = self._check_terminated()
        truncated = self.current_step >= self.max_steps

        info = {
            "step": self.current_step,
            "assignments_made": len([a for a in assignments if a]),
            "pending_orders": len(self.context.order_agent.pending_orders),
            "reward_breakdown": reward,
            "statistics": self.context.get_statistics(),
        }

        return observation, reward, terminated, truncated, info

    def _action_to_assignments(self, action: np.ndarray) -> List[Optional[int]]:
        """
        将动作向量转换为车辆-订单分配

        Args:
            action: 动作数组

        Returns:
            分配列表 [order_id_for_car0, order_id_for_car1, ...]
        """
        assignments = []
        pending_orders = self.context.order_agent.get_pending_orders()

        for car_idx, order_idx in enumerate(action):
            if car_idx < len(self.context.cars):
                car = self.context.cars[car_idx]

                # 检查车辆是否可用
                if not car.is_available_for_task():
                    assignments.append(None)
                    continue

                # 检查订单索引是否有效
                if order_idx < len(pending_orders):
                    order = pending_orders[order_idx]
                    assignments.append(order.order_id)
                else:
                    assignments.append(None)  # 不分配订单
            else:
                assignments.append(None)

        return assignments

    def _apply_assignments(self, assignments: List[Optional[int]]):
        """应用车辆-订单分配"""
        for car_idx, order_id in enumerate(assignments):
            if order_id is not None and car_idx < len(self.context.cars):
                car = self.context.cars[car_idx]
                order = self.context.order_agent.get_order(order_id)

                if car.is_available_for_task() and order:
                    # 直接分配订单给车辆
                    car.assign_task(order_id, order.pickup_point, order.delivery_point)
                    self.context.order_agent.assign_order(order_id, car.car_id)

    def _generate_orders(self, num_orders: int = 1):
        """生成随机订单"""
        for _ in range(num_orders):
            if self.total_orders_generated < self.max_orders_per_episode:
                self.context.add_random_order()
                self.total_orders_generated += 1

    def _check_terminated(self) -> bool:
        """检查是否满足终止条件"""
        # 如果所有订单都完成了
        pending_orders = len(self.context.order_agent.pending_orders)
        all_cars_idle = all(car.is_idle() for car in self.context.cars)

        return (
            pending_orders == 0
            and all_cars_idle
            and self.total_orders_generated >= self.max_orders_per_episode
        )

    def render(self, mode: str = "human"):
        """渲染环境 (可选实现)"""
        if mode == "human":
            stats = self.context.get_statistics()
            print(
                f"Step {self.current_step}: "
                f"Completed={stats.get('total_completed_orders', 0)}, "
                f"Pending={len(self.context.order_agent.pending_orders)}"
            )

    def close(self):
        """关闭环境"""
        if self.context:
            self.context = None


# 测试环境
if __name__ == "__main__":
    print("🧪 测试RL环境")

    env = RLEnvironment(grid_size=8, num_cars=2, max_steps=50)

    obs, info = env.reset()
    print(f"初始观察维度: {obs.shape}")
    print(f"初始信息: {info}")

    for step in range(10):
        # 随机动作
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        print(f"Step {step}: reward={reward:.3f}, pending={info['pending_orders']}")

        if terminated or truncated:
            break

    env.close()
    print(" RL环境测试完成")
