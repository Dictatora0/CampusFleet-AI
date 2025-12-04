"""
近端策略优化 (PPO) 智能体
实现基于策略梯度的强化学习调度决策
"""

import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical, MultivariateNormal


class ActorCriticNetwork(nn.Module):
    """
    Actor-Critic网络架构
    Actor输出动作概率分布，Critic输出状态价值
    """

    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [512, 256]):
        """
        初始化Actor-Critic网络

        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dims: 隐藏层维度列表
        """
        super(ActorCriticNetwork, self).__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim

        # 共享特征提取层
        shared_layers = []
        prev_dim = state_dim

        for hidden_dim in hidden_dims[:-1]:
            shared_layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.1)])
            prev_dim = hidden_dim

        self.shared_network = nn.Sequential(*shared_layers)

        # Actor网络 (策略)
        self.actor = nn.Sequential(
            nn.Linear(prev_dim, hidden_dims[-1]),
            nn.ReLU(),
            nn.Linear(hidden_dims[-1], action_dim),
            nn.Softmax(dim=-1),
        )

        # Critic网络 (价值函数)
        self.critic = nn.Sequential(
            nn.Linear(prev_dim, hidden_dims[-1]), nn.ReLU(), nn.Linear(hidden_dims[-1], 1)
        )

        # 初始化权重
        self._init_weights()

    def _init_weights(self):
        """初始化网络权重"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        前向传播

        Args:
            state: 状态张量 (batch_size, state_dim)

        Returns:
            action_probs: 动作概率 (batch_size, action_dim)
            state_value: 状态价值 (batch_size, 1)
        """
        features = self.shared_network(state)
        action_probs = self.actor(features)
        state_value = self.critic(features)
        return action_probs, state_value

    def get_action_and_value(
        self, state: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        获取动作、对数概率和状态价值

        Args:
            state: 状态张量

        Returns:
            action: 选择的动作
            log_prob: 动作的对数概率
            state_value: 状态价值
        """
        action_probs, state_value = self.forward(state)

        # 创建分类分布
        dist = Categorical(action_probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)

        return action, log_prob, state_value


class PPOMemory:
    """PPO经验缓冲区"""

    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.values = []
        self.dones = []

    def store(
        self,
        state: np.ndarray,
        action: int,
        log_prob: float,
        reward: float,
        value: float,
        done: bool,
    ):
        """存储经验"""
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.values.append(value)
        self.dones.append(done)

    def clear(self):
        """清空缓冲区"""
        self.states.clear()
        self.actions.clear()
        self.log_probs.clear()
        self.rewards.clear()
        self.values.clear()
        self.dones.clear()

    def get_batches(self, batch_size: int):
        """获取训练批次"""
        n = len(self.states)
        indices = np.random.permutation(n)

        for start in range(0, n, batch_size):
            end = start + batch_size
            batch_indices = indices[start:end]

            yield {
                "states": torch.FloatTensor([self.states[i] for i in batch_indices]),
                "actions": torch.LongTensor([self.actions[i] for i in batch_indices]),
                "log_probs": torch.FloatTensor([self.log_probs[i] for i in batch_indices]),
                "rewards": torch.FloatTensor([self.rewards[i] for i in batch_indices]),
                "values": torch.FloatTensor([self.values[i] for i in batch_indices]),
                "dones": torch.BoolTensor([self.dones[i] for i in batch_indices]),
            }


class PPOAgent:
    """
    PPO智能体
    实现近端策略优化算法用于调度决策
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_ratio: float = 0.2,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
        max_grad_norm: float = 0.5,
        update_epochs: int = 10,
        batch_size: int = 64,
        device: str = None,
    ):
        """
        初始化PPO智能体

        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            learning_rate: 学习率
            gamma: 折扣因子
            gae_lambda: GAE参数
            clip_ratio: 裁剪比例
            entropy_coef: 熵系数
            value_coef: 价值函数系数
            max_grad_norm: 梯度裁剪阈值
            update_epochs: 更新轮数
            batch_size: 批次大小
            device: 计算设备
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_ratio = clip_ratio
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm
        self.update_epochs = update_epochs
        self.batch_size = batch_size

        # 设备选择
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f" PPO智能体使用设备: {self.device}")

        # Actor-Critic网络
        self.network = ActorCriticNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=learning_rate)

        # 经验缓冲区
        self.memory = PPOMemory()

        # 训练统计
        self.episodes = 0
        self.total_steps = 0
        self.policy_losses = []
        self.value_losses = []
        self.entropy_losses = []

    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[int, float, float]:
        """
        选择动作

        Args:
            state: 当前状态
            training: 是否训练模式

        Returns:
            action: 选择的动作
            log_prob: 动作对数概率
            value: 状态价值
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            action, log_prob, value = self.network.get_action_and_value(state_tensor)

            return action.item(), log_prob.item(), value.item()

    def select_action_multidiscrete(
        self, state: np.ndarray, num_cars: int, max_orders: int, training: bool = True
    ) -> Tuple[np.ndarray, List[float], List[float]]:
        """
        为多智能体环境选择动作

        Args:
            state: 当前状态
            num_cars: 车辆数量
            max_orders: 最大订单数
            training: 是否训练模式

        Returns:
            actions: 动作数组
            log_probs: 对数概率列表
            values: 价值列表
        """
        actions = []
        log_probs = []
        values = []

        # 为每个车辆选择动作
        for car_idx in range(num_cars):
            action, log_prob, value = self.select_action(state, training)
            # 限制动作范围到有效订单数
            action = min(action, max_orders)

            actions.append(action)
            log_probs.append(log_prob)
            values.append(value)

        return np.array(actions), log_probs, values

    def store_experience(
        self,
        state: np.ndarray,
        action: int,
        log_prob: float,
        reward: float,
        value: float,
        done: bool,
    ):
        """存储经验"""
        self.memory.store(state, action, log_prob, reward, value, done)

    def compute_gae_returns(
        self, rewards: List[float], values: List[float], dones: List[bool], next_value: float = 0.0
    ) -> Tuple[List[float], List[float]]:
        """
        计算GAE优势和回报

        Args:
            rewards: 奖励列表
            values: 价值列表
            dones: 终止标志列表
            next_value: 下一状态价值

        Returns:
            returns: 回报列表
            advantages: 优势列表
        """
        returns = []
        advantages = []
        gae = 0.0

        # 反向计算GAE
        for step in reversed(range(len(rewards))):
            if step == len(rewards) - 1:
                next_non_terminal = 1.0 - dones[step]
                next_val = next_value
            else:
                next_non_terminal = 1.0 - dones[step + 1]
                next_val = values[step + 1]

            # TD误差
            delta = rewards[step] + self.gamma * next_val * next_non_terminal - values[step]

            # GAE计算
            gae = delta + self.gamma * self.gae_lambda * next_non_terminal * gae
            advantages.insert(0, gae)

            # 回报 = 优势 + 价值
            returns.insert(0, gae + values[step])

        return returns, advantages

    def update(self) -> Dict[str, float]:
        """
        更新策略网络

        Returns:
            训练统计信息
        """
        if len(self.memory.states) == 0:
            return {}

        # 计算GAE优势和回报
        returns, advantages = self.compute_gae_returns(
            self.memory.rewards, self.memory.values, self.memory.dones
        )

        # 标准化优势
        advantages = np.array(advantages)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # 转换为张量
        _ = torch.FloatTensor(self.memory.states).to(self.device)
        _ = torch.LongTensor(self.memory.actions).to(self.device)
        _ = torch.FloatTensor(self.memory.log_probs).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)
        advantages = torch.FloatTensor(advantages).to(self.device)

        # 多轮更新
        policy_losses = []
        value_losses = []
        entropy_losses = []

        for _ in range(self.update_epochs):
            for batch in self.memory.get_batches(self.batch_size):
                # 获取批次数据
                batch_states = batch["states"].to(self.device)
                batch_actions = batch["actions"].to(self.device)
                batch_old_log_probs = batch["log_probs"].to(self.device)
                batch_returns = batch["rewards"].to(self.device)  # 使用实际奖励作为目标
                batch_advantages = advantages[: len(batch_states)]

                # 前向传播
                action_probs, values = self.network(batch_states)
                dist = Categorical(action_probs)

                # 计算新的对数概率和熵
                new_log_probs = dist.log_prob(batch_actions)
                entropy = dist.entropy().mean()

                # 重要性采样比率
                ratio = torch.exp(new_log_probs - batch_old_log_probs)

                # PPO裁剪目标
                surr1 = ratio * batch_advantages
                surr2 = (
                    torch.clamp(ratio, 1.0 - self.clip_ratio, 1.0 + self.clip_ratio)
                    * batch_advantages
                )
                policy_loss = -torch.min(surr1, surr2).mean()

                # 价值函数损失
                value_loss = F.mse_loss(values.squeeze(), batch_returns)

                # 熵损失 (鼓励探索)
                entropy_loss = -entropy

                # 总损失
                total_loss = (
                    policy_loss + self.value_coef * value_loss + self.entropy_coef * entropy_loss
                )

                # 反向传播
                self.optimizer.zero_grad()
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.network.parameters(), self.max_grad_norm)
                self.optimizer.step()

                # 记录损失
                policy_losses.append(policy_loss.item())
                value_losses.append(value_loss.item())
                entropy_losses.append(entropy_loss.item())

        # 清空缓冲区
        self.memory.clear()

        # 更新统计
        self.policy_losses.extend(policy_losses)
        self.value_losses.extend(value_losses)
        self.entropy_losses.extend(entropy_losses)

        return {
            "policy_loss": np.mean(policy_losses),
            "value_loss": np.mean(value_losses),
            "entropy_loss": np.mean(entropy_losses),
            "total_loss": np.mean(
                [
                    p + self.value_coef * v + self.entropy_coef * e
                    for p, v, e in zip(policy_losses, value_losses, entropy_losses)
                ]
            ),
        }

    def save_model(self, filepath: str):
        """
        保存模型

        Args:
            filepath: 文件路径
        """
        torch.save(
            {
                "network_state_dict": self.network.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "episodes": self.episodes,
                "total_steps": self.total_steps,
                "hyperparameters": {
                    "state_dim": self.state_dim,
                    "action_dim": self.action_dim,
                    "gamma": self.gamma,
                    "gae_lambda": self.gae_lambda,
                    "clip_ratio": self.clip_ratio,
                    "entropy_coef": self.entropy_coef,
                    "value_coef": self.value_coef,
                },
            },
            filepath,
        )
        print(f"💾 PPO模型已保存: {filepath}")

    def load_model(self, filepath: str):
        """
        加载模型

        Args:
            filepath: 文件路径
        """
        if not os.path.exists(filepath):
            print(f" 模型文件不存在: {filepath}")
            return

        checkpoint = torch.load(filepath, map_location=self.device)

        self.network.load_state_dict(checkpoint["network_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.episodes = checkpoint.get("episodes", 0)
        self.total_steps = checkpoint.get("total_steps", 0)

        print(f"📂 PPO模型已加载: {filepath}")
        print(f"Episodes: {self.episodes}, 步数: {self.total_steps}")

    def get_stats(self) -> Dict[str, float]:
        """获取训练统计信息"""
        recent_policy_losses = self.policy_losses[-100:]
        recent_value_losses = self.value_losses[-100:]
        recent_entropy_losses = self.entropy_losses[-100:]

        return {
            "episodes": self.episodes,
            "total_steps": self.total_steps,
            "avg_policy_loss": np.mean(recent_policy_losses) if recent_policy_losses else 0.0,
            "avg_value_loss": np.mean(recent_value_losses) if recent_value_losses else 0.0,
            "avg_entropy_loss": np.mean(recent_entropy_losses) if recent_entropy_losses else 0.0,
            "memory_size": len(self.memory.states),
        }


# PPO训练示例
def train_ppo_example():
    """PPO训练示例"""
    print(" 启动PPO训练示例")

    # 模拟环境参数
    state_dim = 100
    action_dim = 10

    # 创建PPO智能体
    agent = PPOAgent(
        state_dim=state_dim, action_dim=action_dim, learning_rate=3e-4, gamma=0.99, clip_ratio=0.2
    )

    # 模拟训练
    for episode in range(5):
        state = np.random.random(state_dim)
        episode_reward = 0

        for step in range(50):
            # 选择动作
            action, log_prob, value = agent.select_action(state)

            # 模拟环境反馈
            next_state = np.random.random(state_dim)
            reward = np.random.normal(0, 1)
            done = step == 49

            # 存储经验
            agent.store_experience(state, action, log_prob, reward, value, done)

            episode_reward += reward
            state = next_state

            if done:
                break

        # 更新策略
        stats = agent.update()
        agent.episodes += 1

        print(
            f"Episode {episode}: 奖励={episode_reward:.3f}, "
            f"策略损失={stats.get('policy_loss', 0):.4f}"
        )

    print(" PPO训练示例完成")


if __name__ == "__main__":
    # 测试Actor-Critic网络
    print("🧪 测试Actor-Critic网络")

    net = ActorCriticNetwork(state_dim=50, action_dim=10)
    test_input = torch.randn(32, 50)
    action_probs, values = net(test_input)

    print(f"输入形状: {test_input.shape}")
    print(f"动作概率形状: {action_probs.shape}")
    print(f"状态价值形状: {values.shape}")
    print(f"网络参数量: {sum(p.numel() for p in net.parameters())}")

    # 运行训练示例
    train_ppo_example()
