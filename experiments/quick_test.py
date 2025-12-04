"""
快速测试版本 - 仅用于验证代码是否正常运行
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rl_agents.training_manager import TrainingManager

# 最小配置
env_config = {"grid_size": 8, "num_cars": 2, "max_steps": 100, "max_orders_per_episode": 5}

training_config = {
    "max_episodes": 10,  # 只训练10轮
    "eval_interval": 5,
    "save_interval": 100,
    "early_stop_threshold": 0.95,  # 早停阈值
    "patience": 50,  # 耐心值
}

print("测试标准 DQN...")
trainer1 = TrainingManager(
    agent_type="DQN",
    environment_config=env_config,
    training_config=training_config,
    agent_config={"use_double_dqn": False},
    save_dir="experiments/results/test_dqn",
)
results1 = trainer1.train_agent()

print("\n测试 Double DQN...")
trainer2 = TrainingManager(
    agent_type="DQN",
    environment_config=env_config,
    training_config=training_config,
    agent_config={"use_double_dqn": True},
    save_dir="experiments/results/test_double_dqn",
)
results2 = trainer2.train_agent()

print("\n✅ 测试通过！代码运行正常")
dqn_reward = results1["episode_rewards"][-1] if results1.get("episode_rewards") else "N/A"
ddqn_reward = results2["episode_rewards"][-1] if results2.get("episode_rewards") else "N/A"
print(f"标准 DQN 最终奖励: {dqn_reward}")
print(f"Double DQN 最终奖励: {ddqn_reward}")
