"""
深度Q网络 (DQN) 智能体
实现基于价值函数的强化学习调度决策
"""

import os
import random
from collections import deque, namedtuple
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# 经验回放缓冲区
Experience = namedtuple("Experience", ["state", "action", "reward", "next_state", "done"])


class DQNNetwork(nn.Module):
    """
    深度Q网络架构
    使用全连接层处理状态向量，输出每个动作的Q值
    """

    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [512, 256, 128]):
        """
        初始化DQN网络

        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dims: 隐藏层维度列表
        """
        super(DQNNetwork, self).__init__()

        self.state_dim = state_dim
        self.action_dim = action_dim

        # 构建网络层
        layers = []
        prev_dim = state_dim

        for hidden_dim in hidden_dims:
            layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.2)])
            prev_dim = hidden_dim

        # 输出层
        layers.append(nn.Linear(prev_dim, action_dim))

        self.network = nn.Sequential(*layers)

        # 初始化权重
        self._init_weights()

    def _init_weights(self):
        """初始化网络权重"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        前向传播

        Args:
            state: 状态张量 (batch_size, state_dim)

        Returns:
            Q值张量 (batch_size, action_dim)
        """
        return self.network(state)


class ReplayBuffer:
    """经验回放缓冲区"""

    def __init__(self, capacity: int):
        """
        初始化回放缓冲区

        Args:
            capacity: 缓冲区容量
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity

    def push(
        self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool
    ):
        """
        添加经验到缓冲区

        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一状态
            done: 是否终止
        """
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> List[Experience]:
        """
        从缓冲区采样批次经验

        Args:
            batch_size: 批次大小

        Returns:
            经验批次
        """
        return random.sample(self.buffer, batch_size)

    def __len__(self) -> int:
        return len(self.buffer)


class DQNAgent:
    """
    DQN智能体
    实现深度Q学习算法用于调度决策
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        learning_rate: float = 1e-3,
        gamma: float = 0.95,
        epsilon_start: float = 0.9,
        epsilon_end: float = 0.01,
        epsilon_decay: int = 10000,
        memory_size: int = 50000,
        batch_size: int = 64,
        target_update: int = 100,
        hidden_dims: List[int] = [512, 256, 128],
        use_double_dqn: bool = False,
        device: Optional[str] = None,
    ):
        """
        初始化DQN智能体

        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            learning_rate: 学习率
            gamma: 折扣因子
            epsilon_start: 探索率初值
            epsilon_end: 探索率终值
            epsilon_decay: 探索率衰减步数
            memory_size: 经验回放缓冲区大小
            batch_size: 训练批次大小
            target_update: 目标网络更新频率
            device: 计算设备
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update = target_update
        self.use_double_dqn = use_double_dqn

        # 设备选择
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f" DQN智能体使用设备: {self.device}")

        # 神经网络
        self.q_network = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_network = DQNNetwork(state_dim, action_dim).to(self.device)

        # 复制参数到目标网络
        self.update_target_network()

        # 优化器
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

        # 经验回放
        self.memory = ReplayBuffer(memory_size)

        # 训练统计
        self.steps = 0
        self.episodes = 0
        self.total_reward = 0
        self.losses = []

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        选择动作 (epsilon-greedy策略)

        Args:
            state: 当前状态
            training: 是否训练模式

        Returns:
            选择的动作
        """
        # 计算当前epsilon
        epsilon = max(
            self.epsilon_end,
            self.epsilon_start
            - (self.epsilon_start - self.epsilon_end) * self.steps / self.epsilon_decay,
        )

        # epsilon-greedy探索
        if training and random.random() < epsilon:
            return random.randint(0, self.action_dim - 1)

        # 贪心动作选择
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()

    def select_action_multidiscrete(
        self, state: np.ndarray, num_cars: int, max_orders: int, training: bool = True
    ) -> np.ndarray:
        """
        为多智能体环境选择动作

        Args:
            state: 当前状态
            num_cars: 车辆数量
            max_orders: 最大订单数
            training: 是否训练模式

        Returns:
            动作数组 [car0_action, car1_action, ...]
        """
        actions = []

        for car_idx in range(num_cars):
            # 为每个车辆单独选择动作
            if training and random.random() < self._get_epsilon():
                # 随机探索
                action = random.randint(0, max_orders)  # +1 for "no assignment"
            else:
                # 使用Q网络选择动作
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                    q_values = self.q_network(state_tensor)

                    # 简化：为每个车辆选择相同的最优动作
                    # 实际实现中可以为每个车辆维护单独的动作空间
                    action = min(q_values.argmax().item(), max_orders)

            actions.append(action)

        return np.array(actions)

    def _get_epsilon(self) -> float:
        """获取当前epsilon值"""
        return max(
            self.epsilon_end,
            self.epsilon_start
            - (self.epsilon_start - self.epsilon_end) * self.steps / self.epsilon_decay,
        )

    def store_experience(
        self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool
    ):
        """
        存储经验到回放缓冲区

        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一状态
            done: 是否终止
        """
        self.memory.push(state, action, reward, next_state, done)

    def train(self) -> Optional[float]:
        """
        训练DQN网络

        Returns:
            损失值 (如果进行了训练)
        """
        if len(self.memory) < self.batch_size:
            return None

        # 从缓冲区采样
        experiences = self.memory.sample(self.batch_size)
        batch = Experience(*zip(*experiences))

        # 转换为张量
        states = torch.FloatTensor(np.array(batch.state)).to(self.device)
        actions = torch.LongTensor(batch.action).to(self.device)
        rewards = torch.FloatTensor(batch.reward).to(self.device)
        next_states = torch.FloatTensor(np.array(batch.next_state)).to(self.device)
        dones = torch.BoolTensor(batch.done).to(self.device)

        # 计算当前Q值
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))

        # 计算目标Q值
        with torch.no_grad():
            if self.use_double_dqn:
                # Double DQN: 用在线网络选择动作，用目标网络评估Q值
                next_actions = self.q_network(next_states).argmax(1)
                next_q_values = (
                    self.target_network(next_states).gather(1, next_actions.unsqueeze(1)).squeeze()
                )
            else:
                # 标准 DQN: 直接用目标网络选择最大Q值
                next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)

        # 计算损失
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)

        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()

        # 梯度裁剪
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=10.0)

        self.optimizer.step()

        # 更新统计
        self.steps += 1
        loss_value = loss.item()
        self.losses.append(loss_value)

        # 定期更新目标网络
        if self.steps % self.target_update == 0:
            self.update_target_network()

        return loss_value

    def update_target_network(self):
        """更新目标网络参数"""
        self.target_network.load_state_dict(self.q_network.state_dict())

    def save_model(self, filepath: str):
        """
        保存模型

        Args:
            filepath: 文件路径
        """
        torch.save(
            {
                "q_network_state_dict": self.q_network.state_dict(),
                "target_network_state_dict": self.target_network.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "steps": self.steps,
                "episodes": self.episodes,
                "hyperparameters": {
                    "state_dim": self.state_dim,
                    "action_dim": self.action_dim,
                    "gamma": self.gamma,
                    "epsilon_start": self.epsilon_start,
                    "epsilon_end": self.epsilon_end,
                    "epsilon_decay": self.epsilon_decay,
                    "batch_size": self.batch_size,
                    "target_update": self.target_update,
                },
            },
            filepath,
        )
        print(f"💾 DQN模型已保存: {filepath}")

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

        self.q_network.load_state_dict(checkpoint["q_network_state_dict"])
        self.target_network.load_state_dict(checkpoint["target_network_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.steps = checkpoint.get("steps", 0)
        self.episodes = checkpoint.get("episodes", 0)

        print(f"📂 DQN模型已加载: {filepath}")
        print(f"训练步数: {self.steps}, Episodes: {self.episodes}")

    def get_stats(self) -> Dict[str, float]:
        """获取训练统计信息"""
        recent_losses = self.losses[-100:] if self.losses else []
        return {
            "steps": self.steps,
            "episodes": self.episodes,
            "epsilon": self._get_epsilon(),
            "avg_loss": np.mean(recent_losses) if recent_losses else 0.0,
            "memory_size": len(self.memory),
        }


# DQN训练示例
def train_dqn_example():
    """DQN训练示例"""
    print(" 启动DQN训练示例")

    # 模拟环境参数
    state_dim = 100
    action_dim = 10

    # 创建DQN智能体
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        learning_rate=1e-3,
        gamma=0.95,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=5000,
    )

    # 模拟训练数据
    for episode in range(10):
        state = np.random.random(state_dim)
        total_reward = 0

        for step in range(50):
            # 选择动作
            action = agent.select_action(state)

            # 模拟环境反馈
            next_state = np.random.random(state_dim)
            reward = np.random.normal(0, 1)
            done = step == 49

            # 存储经验
            agent.store_experience(state, action, reward, next_state, done)

            # 训练
            loss = agent.train()

            total_reward += reward
            state = next_state

            if done:
                break

        agent.episodes += 1
        stats = agent.get_stats()
        print(
            f"Episode {episode}: 奖励={total_reward:.3f}, "
            f"ε={stats['epsilon']:.3f}, 损失={stats['avg_loss']:.4f}"
        )

    print(" DQN训练示例完成")


if __name__ == "__main__":
    # 测试DQN网络
    print("🧪 测试DQN网络")

    net = DQNNetwork(state_dim=50, action_dim=10)
    test_input = torch.randn(32, 50)  # batch_size=32, state_dim=50
    output = net(test_input)

    print(f"输入形状: {test_input.shape}")
    print(f"输出形状: {output.shape}")
    print(f"网络参数量: {sum(p.numel() for p in net.parameters())}")

    # 运行训练示例
    train_dqn_example()
