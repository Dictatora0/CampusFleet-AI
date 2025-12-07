"""
强化学习调度器
集成RL智能体到调度系统，实现智能决策调度策略
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.order_agent import Order

from .dqn_agent import DQNAgent
from .ppo_agent import PPOAgent
from .rl_environment import RewardCalculator, StateEncoder


class RLScheduler:
    """
    强化学习调度器
    将RL智能体集成到CampusFleet AI调度系统
    """

    def __init__(
        self,
        agent_type: str = "PPO",  # "DQN" or "PPO"
        grid_size: int = 15,
        max_cars: int = 10,
        max_orders: int = 20,
        model_path: Optional[str] = None,
        training_mode: bool = False,
    ):
        """
        初始化RL调度器

        Args:
            agent_type: 智能体类型 ("DQN" 或 "PPO")
            grid_size: 网格大小
            max_cars: 最大车辆数
            max_orders: 最大订单数
            model_path: 预训练模型路径
            training_mode: 是否训练模式
        """
        self.agent_type = agent_type
        self.grid_size = grid_size
        self.max_cars = max_cars
        self.max_orders = max_orders
        self.training_mode = training_mode

        # 初始化状态编码器和奖励计算器
        self.state_encoder = StateEncoder(grid_size, max_cars, max_orders)
        self.reward_calculator = RewardCalculator()

        # 计算状态和动作维度
        state_dim = self.state_encoder.state_dim
        action_dim = max_orders + 1  # +1 for "no assignment"

        # 创建RL智能体
        if agent_type.upper() == "DQN":
            self.agent = DQNAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                learning_rate=1e-3,
                gamma=0.95,
                epsilon_start=0.9 if training_mode else 0.01,
                epsilon_decay=10000,
            )
        elif agent_type.upper() == "PPO":
            self.agent = PPOAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                learning_rate=3e-4,
                gamma=0.99,
                clip_ratio=0.2,
            )
        else:
            raise ValueError(f"不支持的智能体类型: {agent_type}")

        # 加载预训练模型
        if model_path and os.path.exists(model_path):
            self.agent.load_model(model_path)

        # 历史状态 (用于训练)
        self.prev_state = None
        self.prev_action = None
        self.prev_log_prob = None
        self.prev_value = None

        print("🤖 RL调度器初始化完成")
        print(f"   智能体: {agent_type}")
        print(f"   状态维度: {state_dim}")
        print(f"   动作维度: {action_dim}")
        print(f"   训练模式: {training_mode}")

    def schedule(self, idle_cars: List, orders: List[Order], grid_env) -> List[Tuple]:
        """
        使用RL智能体进行调度决策

        Args:
            idle_cars: 空闲车辆列表
            orders: 待处理订单列表
            grid_env: 网格环境

        Returns:
            分配列表 [(car_id, order_id), ...]
        """
        if not idle_cars or not orders:
            return []

        # 获取当前上下文 (需要从调度器获取)
        context = self._get_simulation_context(idle_cars, orders, grid_env)
        if not context:
            return self._fallback_schedule(idle_cars, orders)

        # 编码当前状态
        current_state = self.state_encoder.encode_state(context)

        # 如果是训练模式且有历史状态，先更新智能体
        if self.training_mode and self.prev_state is not None:
            self._update_agent(context, current_state)

        # 使用RL智能体选择动作
        assignments = self._select_rl_actions(current_state, idle_cars, orders)

        # 保存当前状态 (用于下次更新)
        if self.training_mode:
            self._save_current_state(current_state, assignments, context)

        return assignments

    def _get_simulation_context(self, idle_cars, orders, grid_env):
        """尝试获取仿真上下文 (从全局状态或其他方式)"""

        # 简化版：直接构造一个简单的上下文对象用于状态编码
        # 包含必要的环境信息即可
        class SimpleContext:
            def __init__(self, cars, orders, grid_env):
                self.cars = cars
                self.orders = orders if hasattr(orders, "__iter__") else []
                self.grid_env = grid_env
                self.grid_size = grid_env.size if hasattr(grid_env, "size") else 15
                self.step_count = 0

                # 创建一个简化的 order_agent 模拟对象
                class SimpleOrderAgent:
                    def __init__(self, orders):
                        self._orders = orders

                    def get_pending_orders(self):
                        """返回待处理订单"""
                        return [o for o in self._orders if hasattr(o, "order_id")]

                self.order_agent = SimpleOrderAgent(orders)

            def get_statistics(self):
                """返回简单的统计信息"""
                return {
                    "total_orders": len(self.orders),
                    "total_completed_orders": 0,
                    "completion_rate": 0.0,
                    "avg_distance_per_order": 10.0,
                    "avg_completion_time": 50.0,
                    "current_active_orders": len(self.orders),
                    "idle_vehicles": len([c for c in self.cars if c.state.value == "Idle"]),
                    "avg_vehicle_utilization": 0.5,
                }

        return SimpleContext(idle_cars, orders, grid_env)

    def _select_rl_actions(
        self, state: np.ndarray, idle_cars: List, orders: List[Order]
    ) -> List[Tuple]:
        """
        使用RL智能体选择动作并转换为调度分配

        Args:
            state: 当前状态
            idle_cars: 空闲车辆
            orders: 待处理订单

        Returns:
            分配列表
        """
        assignments = []

        try:
            # 限制处理的车辆和订单数量
            limited_cars = idle_cars[: self.max_cars]
            limited_orders = orders[: self.max_orders]

            if self.agent_type.upper() == "DQN":
                # DQN: 为每个车辆单独选择动作
                for car_idx, car in enumerate(limited_cars):
                    action = self.agent.select_action(state, training=self.training_mode)

                    # 转换动作到订单分配
                    if action < len(limited_orders):
                        order = limited_orders[action]
                        assignments.append((car.car_id, order.order_id))

                    # 每个车辆只分配一个订单，避免冲突
                    if len(assignments) >= len(limited_cars):
                        break

            elif self.agent_type.upper() == "PPO":
                # PPO: 多智能体动作选择
                actions, log_probs, values = self.agent.select_action_multidiscrete(
                    state, len(limited_cars), len(limited_orders), self.training_mode
                )

                # 保存PPO特有的信息用于训练
                if self.training_mode:
                    self.prev_log_prob = log_probs[0] if log_probs else None
                    self.prev_value = values[0] if values else None

                # 转换动作到订单分配
                used_orders = set()
                for car_idx, action in enumerate(actions):
                    if car_idx < len(limited_cars) and action < len(limited_orders):
                        order = limited_orders[action]

                        # 避免重复分配同一订单
                        if order.order_id not in used_orders:
                            assignments.append((limited_cars[car_idx].car_id, order.order_id))
                            used_orders.add(order.order_id)

        except Exception as e:
            print(f"⚠️ RL调度出错: {e}")
            # 回退到简单策略
            assignments = self._fallback_schedule(idle_cars[:1], orders[:1])

        # 记录调度决策
        print(f"🤖 RL调度: {len(assignments)}个分配 (智能体: {self.agent_type})")

        return assignments

    def _update_agent(self, context, current_state: np.ndarray):
        """更新RL智能体"""
        if self.prev_state is None:
            return

        try:
            # 计算奖励
            reward = self.reward_calculator.calculate_reward(context, {"action": self.prev_action})

            # 检查是否episode结束
            done = self._check_episode_done(context)

            if self.agent_type.upper() == "DQN":
                # DQN更新
                if hasattr(self, "prev_action_int"):
                    self.agent.store_experience(
                        self.prev_state, self.prev_action_int, reward, current_state, done
                    )
                    loss = self.agent.train()

                    if loss and self.agent.steps % 100 == 0:
                        print(f"   DQN训练: 步数={self.agent.steps}, 损失={loss:.4f}")

            elif self.agent_type.upper() == "PPO":
                # PPO更新
                if hasattr(self, "prev_action_int") and self.prev_log_prob and self.prev_value:
                    self.agent.store_experience(
                        self.prev_state,
                        self.prev_action_int,
                        self.prev_log_prob,
                        reward,
                        self.prev_value,
                        done,
                    )

                    # PPO batch更新
                    if len(self.agent.memory.states) >= 32 or done:
                        stats = self.agent.update()
                        if stats and self.agent.episodes % 10 == 0:
                            print(
                                f"   PPO训练: Episodes={self.agent.episodes}, "
                                f"策略损失={stats.get('policy_loss', 0):.4f}"
                            )

        except Exception as e:
            print(f"⚠️ RL智能体更新出错: {e}")

    def _save_current_state(self, state: np.ndarray, assignments: List[Tuple], context):
        """保存当前状态用于下次训练"""
        self.prev_state = state.copy()
        self.prev_action = assignments

        # 将分配转换为整数动作 (简化)
        if assignments:
            self.prev_action_int = len(assignments)  # 使用分配数量作为代理动作
        else:
            self.prev_action_int = 0

    def _check_episode_done(self, context) -> bool:
        """检查episode是否结束"""
        # 简单的episode终止条件
        try:
            _ = context.get_statistics()
            pending_orders = getattr(context.order_agent, "pending_orders", [])

            # 如果没有待处理订单且所有车辆都空闲
            all_idle = all(car.is_idle() for car in context.cars)
            return len(pending_orders) == 0 and all_idle
        except Exception:
            return False

    def _fallback_schedule(self, idle_cars: List, orders: List[Order]) -> List[Tuple]:
        """回退调度策略 (贪心最近)"""
        assignments = []

        for car in idle_cars[:3]:  # 限制数量
            if not orders:
                break

            # 找最近的订单
            best_order = None
            min_distance = float("inf")

            for order in orders:
                distance = abs(car.position[0] - order.pickup_point[0]) + abs(
                    car.position[1] - order.pickup_point[1]
                )
                if distance < min_distance:
                    min_distance = distance
                    best_order = order

            if best_order:
                assignments.append((car.car_id, best_order.order_id))
                orders.remove(best_order)

        return assignments

    def save_model(self, filepath: str):
        """保存RL模型"""
        self.agent.save_model(filepath)

    def load_model(self, filepath: str):
        """加载RL模型"""
        self.agent.load_model(filepath)

    def get_stats(self) -> Dict[str, Any]:
        """获取RL调度统计信息"""
        agent_stats = self.agent.get_stats()
        return {
            "agent_type": self.agent_type,
            "training_mode": self.training_mode,
            "state_dim": self.state_encoder.state_dim,
            **agent_stats,
        }

    def set_training_mode(self, training: bool):
        """设置训练模式"""
        self.training_mode = training
        print(f"🔄 RL调度器设置为{'训练' if training else '推理'}模式")

    def reset_episode(self):
        """重置episode状态"""
        self.prev_state = None
        self.prev_action = None
        self.prev_log_prob = None
        self.prev_value = None

        # 重置奖励计算器
        # self.reward_calculator.reset_episode()  # 需要context参数


# RL调度策略枚举扩展
class RLSchedulingStrategy:
    """RL调度策略"""

    DQN_LEARNING = "DQN Learning"
    PPO_LEARNING = "PPO Learning"
    DQN_INFERENCE = "DQN Inference"
    PPO_INFERENCE = "PPO Inference"


# 示例使用
def test_rl_scheduler():
    """测试RL调度器"""
    print("🧪 测试RL调度器")

    # 创建PPO调度器
    scheduler = RLScheduler(
        agent_type="PPO", grid_size=10, max_cars=3, max_orders=5, training_mode=True
    )

    # 模拟调度请求
    class MockCar:
        def __init__(self, car_id, position):
            self.car_id = car_id
            self.position = position

    class MockOrder:
        def __init__(self, order_id, pickup, delivery):
            self.order_id = order_id
            self.pickup_point = pickup
            self.delivery_point = delivery

    cars = [MockCar(i, (i, i)) for i in range(3)]
    orders = [MockOrder(i, (i, i + 1), (i + 2, i + 3)) for i in range(5)]

    # 执行调度
    assignments = scheduler.schedule(cars, orders, None)

    print(f"调度结果: {assignments}")
    print(f"RL统计: {scheduler.get_stats()}")

    print("✅ RL调度器测试完成")


if __name__ == "__main__":
    test_rl_scheduler()
