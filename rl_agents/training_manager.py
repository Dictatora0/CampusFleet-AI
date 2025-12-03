"""
强化学习训练管理器
负责RL智能体的训练、评估和模型管理
"""

import json
import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .dqn_agent import DQNAgent
from .ppo_agent import PPOAgent
from .rl_environment import RLEnvironment
from .rl_scheduler import RLScheduler


class EvaluationMetrics:
    """评估指标计算和管理"""

    def __init__(self):
        self.episode_rewards = []
        self.episode_lengths = []
        self.completion_rates = []
        self.avg_distances = []
        self.efficiency_scores = []
        self.success_rates = []

    def add_episode(
        self,
        reward: float,
        length: int,
        completion_rate: float,
        avg_distance: float,
        efficiency_score: float,
    ):
        """添加episode结果"""
        self.episode_rewards.append(reward)
        self.episode_lengths.append(length)
        self.completion_rates.append(completion_rate)
        self.avg_distances.append(avg_distance)
        self.efficiency_scores.append(efficiency_score)
        self.success_rates.append(1.0 if completion_rate > 0.8 else 0.0)

    def get_recent_stats(self, window: int = 100) -> Dict[str, float]:
        """获取最近N个episode的统计"""
        recent_rewards = self.episode_rewards[-window:]
        recent_completion = self.completion_rates[-window:]
        recent_distances = self.avg_distances[-window:]
        recent_efficiency = self.efficiency_scores[-window:]
        recent_success = self.success_rates[-window:]

        return {
            "avg_reward": np.mean(recent_rewards) if recent_rewards else 0.0,
            "std_reward": np.std(recent_rewards) if recent_rewards else 0.0,
            "avg_completion_rate": np.mean(recent_completion) if recent_completion else 0.0,
            "avg_distance": np.mean(recent_distances) if recent_distances else 0.0,
            "avg_efficiency": np.mean(recent_efficiency) if recent_efficiency else 0.0,
            "success_rate": np.mean(recent_success) if recent_success else 0.0,
            "episodes": len(self.episode_rewards),
        }

    def save_to_csv(self, filepath: str):
        """保存指标到CSV文件"""
        df = pd.DataFrame(
            {
                "episode": range(len(self.episode_rewards)),
                "reward": self.episode_rewards,
                "length": self.episode_lengths,
                "completion_rate": self.completion_rates,
                "avg_distance": self.avg_distances,
                "efficiency_score": self.efficiency_scores,
                "success_rate": self.success_rates,
            }
        )
        df.to_csv(filepath, index=False)
        print(f" 评估指标已保存到: {filepath}")


class TrainingManager:
    """
    RL训练管理器
    统一管理RL智能体的训练、评估和模型保存
    """

    def __init__(
        self,
        agent_type: str = "PPO",
        environment_config: Dict[str, Any] = None,
        training_config: Dict[str, Any] = None,
        save_dir: str = "rl_models",
    ):
        """
        初始化训练管理器

        Args:
            agent_type: 智能体类型 ("DQN" 或 "PPO")
            environment_config: 环境配置
            training_config: 训练配置
            save_dir: 模型保存目录
        """
        self.agent_type = agent_type
        self.save_dir = save_dir

        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)

        # 默认环境配置
        self.env_config = environment_config or {
            "grid_size": 10,
            "num_cars": 3,
            "max_steps": 200,
            "max_orders_per_episode": 15,
        }

        # 默认训练配置
        self.train_config = training_config or {
            "max_episodes": 1000,
            "eval_interval": 50,
            "save_interval": 100,
            "early_stop_threshold": 0.95,
            "patience": 200,
        }

        # 创建环境
        self.env = RLEnvironment(**self.env_config)

        # 创建智能体
        state_dim = self.env.observation_space.shape[0]
        action_dim = self.env.action_space.nvec[0]  # MultiDiscrete空间

        if agent_type.upper() == "DQN":
            self.agent = DQNAgent(
                state_dim=state_dim,
                action_dim=action_dim,
                learning_rate=1e-3,
                gamma=0.95,
                epsilon_start=0.9,
                epsilon_end=0.01,
                epsilon_decay=int(self.train_config["max_episodes"] * 0.8),
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

        # 评估指标
        self.metrics = EvaluationMetrics()

        # 训练状态
        self.training = False
        self.best_performance = -float("inf")
        self.no_improvement_count = 0

        print(f" 训练管理器初始化完成")
        print(f"智能体: {agent_type}")
        print(f"环境: {self.env_config}")
        print(f"训练目标: {self.train_config['max_episodes']} episodes")

    def train_agent(self, resume_from: Optional[str] = None) -> Dict[str, Any]:
        """
        训练RL智能体

        Args:
            resume_from: 恢复训练的模型路径

        Returns:
            训练结果统计
        """
        print(f" 开始训练{self.agent_type}智能体")

        # 恢复训练
        if resume_from and os.path.exists(resume_from):
            self.agent.load_model(resume_from)
            print(f"📂 从{resume_from}恢复训练")

        self.training = True
        start_time = time.time()

        try:
            for episode in range(self.train_config["max_episodes"]):
                if not self.training:  # 支持提前停止
                    break

                # 执行一个episode
                episode_stats = self._run_episode(training=True)

                # 记录指标
                self.metrics.add_episode(
                    episode_stats["total_reward"],
                    episode_stats["steps"],
                    episode_stats["completion_rate"],
                    episode_stats["avg_distance"],
                    episode_stats["efficiency_score"],
                )

                # 定期评估
                if (episode + 1) % self.train_config["eval_interval"] == 0:
                    eval_stats = self._evaluate_agent()
                    self._log_progress(episode + 1, episode_stats, eval_stats)

                    # 检查是否需要保存最佳模型
                    if eval_stats["avg_reward"] > self.best_performance:
                        self.best_performance = eval_stats["avg_reward"]
                        self.no_improvement_count = 0
                        self._save_best_model()
                    else:
                        self.no_improvement_count += self.train_config["eval_interval"]

                # 定期保存
                if (episode + 1) % self.train_config["save_interval"] == 0:
                    self._save_checkpoint(episode + 1)

                # 早停检查
                if self._check_early_stop():
                    print(f" 达到早停条件，训练提前结束")
                    break

        except KeyboardInterrupt:
            print(f"警告: 训练被用户中断")

        finally:
            self.training = False

        training_time = time.time() - start_time
        final_stats = self.metrics.get_recent_stats()

        # 保存最终结果
        self._save_training_results(final_stats, training_time)

        print(f" 训练完成! 用时: {training_time/3600:.2f}小时")
        print(f"最佳性能: {self.best_performance:.3f}")
        print(f"最终成功率: {final_stats['success_rate']:.3f}")

        return {
            "final_stats": final_stats,
            "training_time": training_time,
            "best_performance": self.best_performance,
            "total_episodes": len(self.metrics.episode_rewards),
        }

    def _run_episode(self, training: bool = True) -> Dict[str, Any]:
        """运行一个episode"""
        obs, info = self.env.reset()
        total_reward = 0
        steps = 0

        while True:
            # 根据智能体类型选择动作
            if self.agent_type.upper() == "DQN":
                action_int = self.agent.select_action(obs, training)
                # 转换为MultiDiscrete动作
                action = np.array(
                    [
                        action_int % self.env.action_space.nvec[i]
                        for i in range(len(self.env.action_space.nvec))
                    ]
                )
            elif self.agent_type.upper() == "PPO":
                if training:
                    action, log_prob, value = self.agent.select_action(obs, training)
                    action = np.array([action] * len(self.env.action_space.nvec))
                else:
                    action, _, _ = self.agent.select_action(obs, training)
                    action = np.array([action] * len(self.env.action_space.nvec))

            # 执行动作
            next_obs, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated

            # 训练模式下存储经验
            if training:
                if self.agent_type.upper() == "DQN":
                    self.agent.store_experience(obs, action_int, reward, next_obs, done)
                    loss = self.agent.train()
                elif self.agent_type.upper() == "PPO":
                    self.agent.store_experience(obs, action[0], log_prob, reward, value, done)
                    if done or steps % 32 == 0:  # 批量更新
                        self.agent.update()

            total_reward += reward
            steps += 1
            obs = next_obs

            if done:
                break

        # 计算episode统计
        stats = info.get("statistics", {})
        completion_rate = stats.get("completion_rate", 0.0)
        avg_distance = stats.get("avg_distance_per_order", 0.0)
        efficiency_score = max(0.0, 1.0 - avg_distance / 50.0)  # 简单效率分数

        return {
            "total_reward": total_reward,
            "steps": steps,
            "completion_rate": completion_rate,
            "avg_distance": avg_distance,
            "efficiency_score": efficiency_score,
        }

    def _evaluate_agent(self, num_episodes: int = 10) -> Dict[str, float]:
        """评估智能体性能"""
        eval_rewards = []
        eval_completion_rates = []

        for _ in range(num_episodes):
            episode_stats = self._run_episode(training=False)
            eval_rewards.append(episode_stats["total_reward"])
            eval_completion_rates.append(episode_stats["completion_rate"])

        return {
            "avg_reward": np.mean(eval_rewards),
            "std_reward": np.std(eval_rewards),
            "avg_completion_rate": np.mean(eval_completion_rates),
            "success_rate": np.mean([1.0 if cr > 0.8 else 0.0 for cr in eval_completion_rates]),
        }

    def _log_progress(self, episode: int, episode_stats: Dict, eval_stats: Dict):
        """记录训练进度"""
        agent_stats = self.agent.get_stats()

        print(f"\n Episode {episode} 训练进度:")
        print(f"本轮奖励: {episode_stats['total_reward']:.3f}")
        print(f"完成率: {episode_stats['completion_rate']:.3f}")
        print(f"评估奖励: {eval_stats['avg_reward']:.3f} ± {eval_stats['std_reward']:.3f}")
        print(f"评估成功率: {eval_stats['success_rate']:.3f}")

        if self.agent_type.upper() == "DQN":
            print(f"Epsilon: {agent_stats['epsilon']:.3f}")
            print(f"平均损失: {agent_stats['avg_loss']:.4f}")
        elif self.agent_type.upper() == "PPO":
            print(f"策略损失: {agent_stats['avg_policy_loss']:.4f}")
            print(f"价值损失: {agent_stats['avg_value_loss']:.4f}")

    def _check_early_stop(self) -> bool:
        """检查是否满足早停条件"""
        recent_stats = self.metrics.get_recent_stats(50)

        # 如果成功率达到阈值且没有改进
        if (
            recent_stats["success_rate"] >= self.train_config["early_stop_threshold"]
            and self.no_improvement_count >= self.train_config["patience"]
        ):
            return True

        return False

    def _save_best_model(self):
        """保存最佳模型"""
        best_model_path = os.path.join(self.save_dir, f"best_{self.agent_type.lower()}_model.pth")
        self.agent.save_model(best_model_path)
        print(f"💾 保存最佳模型: {best_model_path}")

    def _save_checkpoint(self, episode: int):
        """保存训练检查点"""
        checkpoint_path = os.path.join(
            self.save_dir, f"{self.agent_type.lower()}_checkpoint_ep{episode}.pth"
        )
        self.agent.save_model(checkpoint_path)
        print(f"💾 保存检查点: {checkpoint_path}")

    def _save_training_results(self, final_stats: Dict, training_time: float):
        """保存训练结果"""
        # 保存指标CSV
        metrics_path = os.path.join(
            self.save_dir, f"{self.agent_type.lower()}_training_metrics.csv"
        )
        self.metrics.save_to_csv(metrics_path)

        # 保存配置和结果JSON
        results = {
            "agent_type": self.agent_type,
            "environment_config": self.env_config,
            "training_config": self.train_config,
            "final_statistics": final_stats,
            "training_time_hours": training_time / 3600,
            "best_performance": self.best_performance,
            "timestamp": datetime.now().isoformat(),
        }

        results_path = os.path.join(
            self.save_dir, f"{self.agent_type.lower()}_training_results.json"
        )
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📋 训练结果已保存: {results_path}")

    def plot_training_progress(self, save_path: Optional[str] = None):
        """绘制训练进度图"""
        if len(self.metrics.episode_rewards) < 10:
            print("警告: 训练数据不足，无法绘制图表")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"{self.agent_type} 训练进度", fontsize=16)

        episodes = range(len(self.metrics.episode_rewards))

        # 奖励曲线
        axes[0, 0].plot(episodes, self.metrics.episode_rewards, alpha=0.7)
        axes[0, 0].plot(
            episodes, pd.Series(self.metrics.episode_rewards).rolling(50).mean(), "r-", linewidth=2
        )
        axes[0, 0].set_title("Episode奖励")
        axes[0, 0].set_xlabel("Episode")
        axes[0, 0].set_ylabel("总奖励")
        axes[0, 0].grid(True)

        # 完成率
        axes[0, 1].plot(episodes, self.metrics.completion_rates, alpha=0.7)
        axes[0, 1].plot(
            episodes, pd.Series(self.metrics.completion_rates).rolling(50).mean(), "g-", linewidth=2
        )
        axes[0, 1].set_title("订单完成率")
        axes[0, 1].set_xlabel("Episode")
        axes[0, 1].set_ylabel("完成率")
        axes[0, 1].grid(True)

        # 平均距离
        axes[1, 0].plot(episodes, self.metrics.avg_distances, alpha=0.7)
        axes[1, 0].plot(
            episodes, pd.Series(self.metrics.avg_distances).rolling(50).mean(), "b-", linewidth=2
        )
        axes[1, 0].set_title("平均配送距离")
        axes[1, 0].set_xlabel("Episode")
        axes[1, 0].set_ylabel("距离")
        axes[1, 0].grid(True)

        # 成功率
        axes[1, 1].plot(episodes, self.metrics.success_rates, alpha=0.7)
        axes[1, 1].plot(
            episodes,
            pd.Series(self.metrics.success_rates).rolling(50).mean(),
            "orange",
            linewidth=2,
        )
        axes[1, 1].set_title("任务成功率")
        axes[1, 1].set_xlabel("Episode")
        axes[1, 1].set_ylabel("成功率")
        axes[1, 1].grid(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📈 训练图表已保存: {save_path}")
        else:
            plt.savefig(
                os.path.join(self.save_dir, f"{self.agent_type.lower()}_training_progress.png"),
                dpi=300,
                bbox_inches="tight",
            )

        plt.show()

    def stop_training(self):
        """停止训练"""
        self.training = False
        print("🛑 训练停止指令已发送")

    def compare_with_baseline(self, baseline_stats: Dict[str, float]) -> Dict[str, float]:
        """与基线算法比较性能"""
        recent_stats = self.metrics.get_recent_stats()

        comparison = {}
        for key in baseline_stats:
            if key in recent_stats:
                improvement = (recent_stats[key] - baseline_stats[key]) / max(
                    baseline_stats[key], 1e-6
                )
                comparison[f"{key}_improvement"] = improvement * 100  # 百分比改进

        return comparison


# 使用示例
def train_rl_example():
    """RL训练示例"""
    print(" 开始RL训练示例")

    # 环境配置
    env_config = {"grid_size": 8, "num_cars": 2, "max_steps": 100, "max_orders_per_episode": 10}

    # 训练配置
    train_config = {
        "max_episodes": 50,  # 示例用较少episodes
        "eval_interval": 10,
        "save_interval": 20,
        "early_stop_threshold": 0.8,
        "patience": 30,
    }

    # 创建训练管理器
    trainer = TrainingManager(
        agent_type="PPO",
        environment_config=env_config,
        training_config=train_config,
        save_dir="test_rl_models",
    )

    # 开始训练
    results = trainer.train_agent()

    print(f" 训练完成!")
    print(f"最佳性能: {results['best_performance']:.3f}")
    print(f"总时长: {results['training_time']/60:.2f}分钟")

    # 绘制进度图
    # trainer.plot_training_progress()


if __name__ == "__main__":
    # 安装依赖提示
    try:
        import gymnasium
        import matplotlib
        import pandas
        import torch
    except ImportError as e:
        print(f" 缺少依赖包: {e}")
        print("请安装: pip install torch gymnasium pandas matplotlib")
        exit(1)

    # 运行训练示例
    train_rl_example()
