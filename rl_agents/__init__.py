"""
CampusFleet AI - 强化学习模块
=================================

实现智能调度决策系统，从规则驱动升级到学习驱动

核心组件：
- RLEnvironment: 强化学习环境封装
- DQNAgent: 深度Q网络智能体  
- PPOAgent: 近端策略优化智能体
- RLScheduler: RL调度策略集成
- TrainingManager: 训练和评估管理

技术特性：
- 状态空间：车辆分布、订单状况、环境信息
- 动作空间：车辆-订单分配决策
- 奖励函数：效率、距离、完成时间的综合优化
"""

from .rl_environment import RLEnvironment, StateEncoder, RewardCalculator
from .dqn_agent import DQNAgent, DQNNetwork
from .ppo_agent import PPOAgent, ActorCriticNetwork
from .rl_scheduler import RLScheduler
from .training_manager import TrainingManager, EvaluationMetrics

__version__ = "1.0.0"
__author__ = "CampusFleet AI Team"

__all__ = [
    "RLEnvironment",
    "StateEncoder", 
    "RewardCalculator",
    "DQNAgent",
    "DQNNetwork",
    "PPOAgent", 
    "ActorCriticNetwork",
    "RLScheduler",
    "TrainingManager",
    "EvaluationMetrics"
]
