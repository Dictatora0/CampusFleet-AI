"""
强化学习算法对比实验
对比标准 DQN 与 Double DQN 在多智能体调度任务中的表现
"""
import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rl_agents.training_manager import TrainingManager


def run_comparison_experiment():
    """运行 DQN vs Double DQN 对比实验"""

    print("=" * 80)
    print("强化学习算法对比实验: 标准 DQN vs Double DQN")
    print("=" * 80)

    # 实验配置
    env_config = {"grid_size": 12, "num_cars": 3, "max_steps": 200, "max_orders_per_episode": 15}

    training_config = {
        "max_episodes": 300,
        "eval_interval": 20,
        "save_interval": 100,
        "early_stop_threshold": 0.85,
        "patience": 150,
    }

    # 标准 DQN
    print("\n[1/2] 训练标准 DQN...")
    dqn_agent_config = {
        "use_double_dqn": False,  # 标准 DQN
    }

    trainer_dqn = TrainingManager(
        agent_type="DQN",
        environment_config=env_config,
        training_config=training_config,
        agent_config=dqn_agent_config,
        save_dir="experiments/results/standard_dqn",
    )

    results_dqn = trainer_dqn.train_agent()

    # Double DQN
    print("\n[2/2] 训练 Double DQN...")
    double_dqn_agent_config = {
        "use_double_dqn": True,  # Double DQN
    }

    trainer_double_dqn = TrainingManager(
        agent_type="DQN",
        environment_config=env_config,
        training_config=training_config,
        agent_config=double_dqn_agent_config,
        save_dir="experiments/results/double_dqn",
    )

    results_double_dqn = trainer_double_dqn.train_agent()

    # 生成对比图表
    print("\n生成对比图表...")
    plot_comparison(results_dqn, results_double_dqn)

    # 保存对比结果
    save_comparison_results(results_dqn, results_double_dqn, env_config, training_config)

    print("\n" + "=" * 80)
    print("实验完成！结果已保存到 experiments/results/")
    print("=" * 80)


def plot_comparison(results_dqn, results_double_dqn):
    """绘制对比图表"""

    output_dir = Path("experiments/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 设置中文字体
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("标准 DQN vs Double DQN 性能对比", fontsize=16, fontweight="bold")

    # 1. 奖励曲线
    ax = axes[0, 0]
    if "episode_rewards" in results_dqn:
        ax.plot(results_dqn["episode_rewards"], label="标准 DQN", alpha=0.7, linewidth=2)
    if "episode_rewards" in results_double_dqn:
        ax.plot(results_double_dqn["episode_rewards"], label="Double DQN", alpha=0.7, linewidth=2)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Total Reward")
    ax.set_title("Episode 奖励对比")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. 完成率曲线
    ax = axes[0, 1]
    if "completion_rates" in results_dqn:
        ax.plot(results_dqn["completion_rates"], label="标准 DQN", alpha=0.7, linewidth=2)
    if "completion_rates" in results_double_dqn:
        ax.plot(results_double_dqn["completion_rates"], label="Double DQN", alpha=0.7, linewidth=2)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Completion Rate (%)")
    ax.set_title("订单完成率对比")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 105])

    # 3. 平均距离对比
    ax = axes[1, 0]
    if "avg_distances" in results_dqn:
        ax.plot(results_dqn["avg_distances"], label="标准 DQN", alpha=0.7, linewidth=2)
    if "avg_distances" in results_double_dqn:
        ax.plot(results_double_dqn["avg_distances"], label="Double DQN", alpha=0.7, linewidth=2)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Average Distance")
    ax.set_title("平均配送距离对比")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. 损失曲线
    ax = axes[1, 1]
    if "losses" in results_dqn:
        # 平滑处理
        window = 10
        dqn_losses_smooth = np.convolve(
            results_dqn["losses"], np.ones(window) / window, mode="valid"
        )
        ax.plot(dqn_losses_smooth, label="标准 DQN", alpha=0.7, linewidth=2)
    if "losses" in results_double_dqn:
        double_dqn_losses_smooth = np.convolve(
            results_double_dqn["losses"], np.ones(window) / window, mode="valid"
        )
        ax.plot(double_dqn_losses_smooth, label="Double DQN", alpha=0.7, linewidth=2)
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Loss")
    ax.set_title("训练损失对比（平滑）")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "dqn_comparison.png", dpi=300, bbox_inches="tight")
    print(f"对比图表已保存: {output_dir / 'dqn_comparison.png'}")

    plt.close()


def save_comparison_results(results_dqn, results_double_dqn, env_config, training_config):
    """保存对比结果到 JSON"""

    output_dir = Path("experiments/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 计算统计数据
    def get_stats(results, name):
        if "episode_rewards" not in results:
            return {}

        last_100_rewards = results["episode_rewards"][-100:]
        last_100_completion = results.get("completion_rates", [])[-100:]
        last_100_distances = results.get("avg_distances", [])[-100:]

        return {
            "algorithm": name,
            "final_avg_reward": float(np.mean(last_100_rewards)) if last_100_rewards else 0,
            "final_avg_completion_rate": float(np.mean(last_100_completion))
            if last_100_completion
            else 0,
            "final_avg_distance": float(np.mean(last_100_distances)) if last_100_distances else 0,
            "best_reward": float(max(results["episode_rewards"]))
            if results["episode_rewards"]
            else 0,
            "total_episodes": len(results.get("episode_rewards", [])),
        }

    comparison_data = {
        "experiment": "DQN vs Double DQN Comparison",
        "environment_config": env_config,
        "training_config": training_config,
        "results": {
            "standard_dqn": get_stats(results_dqn, "Standard DQN"),
            "double_dqn": get_stats(results_double_dqn, "Double DQN"),
        },
        "improvement": {},
    }

    # 计算改进幅度
    dqn_stats = comparison_data["results"]["standard_dqn"]
    ddqn_stats = comparison_data["results"]["double_dqn"]

    if dqn_stats.get("final_avg_reward", 0) > 0:
        comparison_data["improvement"]["reward"] = (
            (ddqn_stats.get("final_avg_reward", 0) - dqn_stats.get("final_avg_reward", 0))
            / dqn_stats.get("final_avg_reward", 1)
            * 100
        )

    if dqn_stats.get("final_avg_distance", 0) > 0:
        comparison_data["improvement"]["distance"] = (
            (dqn_stats.get("final_avg_distance", 0) - ddqn_stats.get("final_avg_distance", 0))
            / dqn_stats.get("final_avg_distance", 1)
            * 100
        )

    # 保存
    with open(output_dir / "comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)

    print(f"对比数据已保存: {output_dir / 'comparison_results.json'}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("实验结果摘要")
    print("=" * 60)
    print(f"标准 DQN:")
    print(f"  平均奖励: {dqn_stats.get('final_avg_reward', 0):.2f}")
    print(f"  完成率: {dqn_stats.get('final_avg_completion_rate', 0):.1f}%")
    print(f"  平均距离: {dqn_stats.get('final_avg_distance', 0):.2f}")
    print(f"\nDouble DQN:")
    print(f"  平均奖励: {ddqn_stats.get('final_avg_reward', 0):.2f}")
    print(f"  完成率: {ddqn_stats.get('final_avg_completion_rate', 0):.1f}%")
    print(f"  平均距离: {ddqn_stats.get('final_avg_distance', 0):.2f}")

    if "reward" in comparison_data["improvement"]:
        print(f"\n改进幅度:")
        print(f"  奖励提升: {comparison_data['improvement']['reward']:.1f}%")
    if "distance" in comparison_data["improvement"]:
        print(f"  距离优化: {comparison_data['improvement']['distance']:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    run_comparison_experiment()
