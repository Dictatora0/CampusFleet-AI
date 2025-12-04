"""
强化学习算法对比实验 - 优化版
对比标准 DQN 与 Double DQN 在多智能体调度任务中的表现

优化版本 v3.1:
环境优化：
  - 网格: 10×10（适中复杂度）
  - 车辆: 5辆（从4→5，+25%吞吐量）
  - 步数: 600步（从500→600，+20%时间）
  - 订单: 10个（从12→10，降低难度）

训练优化：
  - Episodes: 600轮（充分训练）
  - 早停阈值: 45%完成率（从60%→45%，更易达到）
  - 评估间隔: 每30轮
  - 耐心值: 200轮

可视化增强：
  - 主图：2×2网格，带移动平均平滑
  - 额外图表：累积奖励、最后100轮性能分析
  - 3张高分辨率图表（300 DPI）

预期改进：
  - 完成率：40-60%（更好展现算法差异）
  - 图表更专业（适合论文使用）
"""

import json
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

    # 实验配置（v3.1优化：进一步提高完成率，目标40-60%）
    env_config = {
        "grid_size": 10,  # 10×10网格（适中复杂度）
        "num_cars": 5,  # 从4→5辆车（+25%吞吐量）
        "max_steps": 600,  # 从500→600步（+20%时间）
        "max_orders_per_episode": 10,  # 从12→10订单（更易完成）
    }

    training_config = {
        "max_episodes": 600,  # 增加到600确保充分训练
        "eval_interval": 30,  # 每30轮评估一次
        "save_interval": 200,
        "early_stop_threshold": 0.45,  # 降低到0.45（45%完成率）更易达到
        "patience": 200,  # 耐心值200轮
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

    # Use default font (no Chinese font needed)
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    # === 主图：2x2 网格 ===
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "Standard DQN vs Double DQN Performance Comparison (Optimized v3.0)", 
        fontsize=16, fontweight="bold"
    )

    # 1. 奖励曲线（原始+平滑）
    ax = axes[0, 0]
    window = 50  # 移动平均窗口
    if "episode_rewards" in results_dqn and len(results_dqn["episode_rewards"]) > 0:
        # 原始曲线（半透明）
        ax.plot(results_dqn["episode_rewards"], color='blue', alpha=0.2, linewidth=1)
        # 平滑曲线
        if len(results_dqn["episode_rewards"]) > window:
            smooth_rewards = np.convolve(
                results_dqn["episode_rewards"], np.ones(window)/window, mode='valid'
            )
            ax.plot(range(window-1, len(results_dqn["episode_rewards"])), 
                   smooth_rewards, label="Standard DQN", color='blue', linewidth=2.5)
        else:
            ax.plot(results_dqn["episode_rewards"], label="Standard DQN", 
                   color='blue', alpha=0.8, linewidth=2)
    
    if "episode_rewards" in results_double_dqn and len(results_double_dqn["episode_rewards"]) > 0:
        # 原始曲线（半透明）
        ax.plot(results_double_dqn["episode_rewards"], color='red', alpha=0.2, linewidth=1)
        # 平滑曲线
        if len(results_double_dqn["episode_rewards"]) > window:
            smooth_rewards = np.convolve(
                results_double_dqn["episode_rewards"], np.ones(window)/window, mode='valid'
            )
            ax.plot(range(window-1, len(results_double_dqn["episode_rewards"])), 
                   smooth_rewards, label="Double DQN", color='red', linewidth=2.5)
        else:
            ax.plot(results_double_dqn["episode_rewards"], label="Double DQN", 
                   color='red', alpha=0.8, linewidth=2)
    
    ax.set_xlabel("Episode", fontsize=11)
    ax.set_ylabel("Total Reward", fontsize=11)
    ax.set_title("Episode Rewards (Raw + 50-ep Moving Average)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # 2. 完成率曲线（带平滑）
    ax = axes[0, 1]
    window_comp = 30
    if "completion_rates" in results_dqn and len(results_dqn["completion_rates"]) > 0:
        ax.plot(results_dqn["completion_rates"], color='blue', alpha=0.3, linewidth=1)
        if len(results_dqn["completion_rates"]) > window_comp:
            smooth_comp = np.convolve(
                results_dqn["completion_rates"], np.ones(window_comp)/window_comp, mode='valid'
            )
            ax.plot(range(window_comp-1, len(results_dqn["completion_rates"])), 
                   smooth_comp, label="Standard DQN", color='blue', linewidth=2.5)
        else:
            ax.plot(results_dqn["completion_rates"], label="Standard DQN", 
                   color='blue', alpha=0.8, linewidth=2)
    
    if "completion_rates" in results_double_dqn and len(results_double_dqn["completion_rates"]) > 0:
        ax.plot(results_double_dqn["completion_rates"], color='red', alpha=0.3, linewidth=1)
        if len(results_double_dqn["completion_rates"]) > window_comp:
            smooth_comp = np.convolve(
                results_double_dqn["completion_rates"], np.ones(window_comp)/window_comp, mode='valid'
            )
            ax.plot(range(window_comp-1, len(results_double_dqn["completion_rates"])), 
                   smooth_comp, label="Double DQN", color='red', linewidth=2.5)
        else:
            ax.plot(results_double_dqn["completion_rates"], label="Double DQN", 
                   color='red', alpha=0.8, linewidth=2)
    
    # 添加目标线
    ax.axhline(y=45, color='green', linestyle='--', alpha=0.5, linewidth=1.5, label='Target (45%)')
    ax.set_xlabel("Episode", fontsize=11)
    ax.set_ylabel("Completion Rate (%)", fontsize=11)
    ax.set_title("Order Completion Rate (30-ep Moving Average)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 105])

    # 3. 成功率对比（新增）
    ax = axes[1, 0]
    if "success_rates" in results_dqn and len(results_dqn["success_rates"]) > 0:
        window_sr = 20
        if len(results_dqn["success_rates"]) > window_sr:
            smooth_sr = np.convolve(
                results_dqn["success_rates"], np.ones(window_sr)/window_sr, mode='valid'
            )
            ax.plot(range(window_sr-1, len(results_dqn["success_rates"])), 
                   smooth_sr, label="Standard DQN", color='blue', linewidth=2.5, alpha=0.8)
        else:
            ax.plot(results_dqn["success_rates"], label="Standard DQN", 
                   color='blue', linewidth=2, alpha=0.8)
    
    if "success_rates" in results_double_dqn and len(results_double_dqn["success_rates"]) > 0:
        if len(results_double_dqn["success_rates"]) > window_sr:
            smooth_sr = np.convolve(
                results_double_dqn["success_rates"], np.ones(window_sr)/window_sr, mode='valid'
            )
            ax.plot(range(window_sr-1, len(results_double_dqn["success_rates"])), 
                   smooth_sr, label="Double DQN", color='red', linewidth=2.5, alpha=0.8)
        else:
            ax.plot(results_double_dqn["success_rates"], label="Double DQN", 
                   color='red', linewidth=2, alpha=0.8)
    
    ax.set_xlabel("Episode", fontsize=11)
    ax.set_ylabel("Success Rate", fontsize=11)
    ax.set_title("Evaluation Success Rate (20-ep Moving Average)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])

    # 4. 损失曲线（改进）
    ax = axes[1, 1]
    window_loss = 100
    if "losses" in results_dqn and len(results_dqn["losses"]) > window_loss:
        dqn_losses_smooth = np.convolve(
            results_dqn["losses"], np.ones(window_loss) / window_loss, mode="valid"
        )
        ax.plot(dqn_losses_smooth, label="Standard DQN", color='blue', alpha=0.8, linewidth=2)
    elif "losses" in results_dqn and len(results_dqn["losses"]) > 0:
        ax.plot(results_dqn["losses"], label="Standard DQN", color='blue', alpha=0.6, linewidth=1.5)
    
    if "losses" in results_double_dqn and len(results_double_dqn["losses"]) > window_loss:
        double_dqn_losses_smooth = np.convolve(
            results_double_dqn["losses"], np.ones(window_loss) / window_loss, mode="valid"
        )
        ax.plot(double_dqn_losses_smooth, label="Double DQN", color='red', alpha=0.8, linewidth=2)
    elif "losses" in results_double_dqn and len(results_double_dqn["losses"]) > 0:
        ax.plot(results_double_dqn["losses"], label="Double DQN", color='red', alpha=0.6, linewidth=1.5)
    
    ax.set_xlabel("Training Step", fontsize=11)
    ax.set_ylabel("Loss", fontsize=11)
    ax.set_title("Training Loss (100-step Moving Average)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "dqn_comparison.png", dpi=300, bbox_inches="tight")
    print(f"✓ Main comparison chart saved: {output_dir / 'dqn_comparison.png'}")

    plt.close()
    
    # === 生成额外的详细图表 ===
    print("Generating additional detailed charts...")
    
    # 详细图1：累积奖励对比
    fig, ax = plt.subplots(figsize=(10, 6))
    if "episode_rewards" in results_dqn and len(results_dqn["episode_rewards"]) > 0:
        cumsum_dqn = np.cumsum(results_dqn["episode_rewards"])
        ax.plot(cumsum_dqn, label="Standard DQN", color='blue', linewidth=2.5)
    if "episode_rewards" in results_double_dqn and len(results_double_dqn["episode_rewards"]) > 0:
        cumsum_ddqn = np.cumsum(results_double_dqn["episode_rewards"])
        ax.plot(cumsum_ddqn, label="Double DQN", color='red', linewidth=2.5)
    ax.set_xlabel("Episode", fontsize=12)
    ax.set_ylabel("Cumulative Reward", fontsize=12)
    ax.set_title("Cumulative Reward Comparison", fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "cumulative_rewards.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    # 详细图2：最后100轮性能对比
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Final Performance (Last 100 Episodes)", fontsize=14, fontweight='bold')
    
    # 子图1：奖励分布
    ax = axes[0]
    if "episode_rewards" in results_dqn and len(results_dqn["episode_rewards"]) >= 100:
        last_100_dqn = results_dqn["episode_rewards"][-100:]
        ax.hist(last_100_dqn, bins=20, alpha=0.6, label=f"DQN\nμ={np.mean(last_100_dqn):.1f}", color='blue')
    if "episode_rewards" in results_double_dqn and len(results_double_dqn["episode_rewards"]) >= 100:
        last_100_ddqn = results_double_dqn["episode_rewards"][-100:]
        ax.hist(last_100_ddqn, bins=20, alpha=0.6, label=f"Double DQN\nμ={np.mean(last_100_ddqn):.1f}", color='red')
    ax.set_xlabel("Reward", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.set_title("Reward Distribution", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 子图2：完成率分布
    ax = axes[1]
    if "completion_rates" in results_dqn and len(results_dqn["completion_rates"]) >= 100:
        last_100_comp_dqn = results_dqn["completion_rates"][-100:]
        ax.hist(last_100_comp_dqn, bins=15, alpha=0.6, 
               label=f"DQN\nμ={np.mean(last_100_comp_dqn):.1f}%", color='blue')
    if "completion_rates" in results_double_dqn and len(results_double_dqn["completion_rates"]) >= 100:
        last_100_comp_ddqn = results_double_dqn["completion_rates"][-100:]
        ax.hist(last_100_comp_ddqn, bins=15, alpha=0.6, 
               label=f"Double DQN\nμ={np.mean(last_100_comp_ddqn):.1f}%", color='red')
    ax.set_xlabel("Completion Rate (%)", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.set_title("Completion Rate Distribution", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 子图3：Bar对比
    ax = axes[2]
    metrics = ['Reward', 'Completion\nRate (%)']
    dqn_vals = []
    ddqn_vals = []
    
    if "episode_rewards" in results_dqn and len(results_dqn["episode_rewards"]) >= 100:
        dqn_vals.append(np.mean(results_dqn["episode_rewards"][-100:]))
    else:
        dqn_vals.append(0)
    
    if "completion_rates" in results_dqn and len(results_dqn["completion_rates"]) >= 100:
        dqn_vals.append(np.mean(results_dqn["completion_rates"][-100:]))
    else:
        dqn_vals.append(0)
    
    if "episode_rewards" in results_double_dqn and len(results_double_dqn["episode_rewards"]) >= 100:
        ddqn_vals.append(np.mean(results_double_dqn["episode_rewards"][-100:]))
    else:
        ddqn_vals.append(0)
    
    if "completion_rates" in results_double_dqn and len(results_double_dqn["completion_rates"]) >= 100:
        ddqn_vals.append(np.mean(results_double_dqn["completion_rates"][-100:]))
    else:
        ddqn_vals.append(0)
    
    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(x - width/2, dqn_vals, width, label='Standard DQN', color='blue', alpha=0.7)
    ax.bar(x + width/2, ddqn_vals, width, label='Double DQN', color='red', alpha=0.7)
    ax.set_ylabel('Value', fontsize=11)
    ax.set_title('Average Performance', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_dir / "final_performance.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"✓ Additional charts saved:")
    print(f"  - {output_dir / 'cumulative_rewards.png'}")
    print(f"  - {output_dir / 'final_performance.png'}")


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
            "final_avg_completion_rate": (
                float(np.mean(last_100_completion)) if last_100_completion else 0
            ),
            "final_avg_distance": float(np.mean(last_100_distances)) if last_100_distances else 0,
            "best_reward": (
                float(max(results["episode_rewards"])) if results["episode_rewards"] else 0
            ),
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
    print("标准 DQN:")
    print(f"  平均奖励: {dqn_stats.get('final_avg_reward', 0):.2f}")
    print(f"  完成率: {dqn_stats.get('final_avg_completion_rate', 0):.1f}%")
    print(f"  平均距离: {dqn_stats.get('final_avg_distance', 0):.2f}")
    print("\nDouble DQN:")
    print(f"  平均奖励: {ddqn_stats.get('final_avg_reward', 0):.2f}")
    print(f"  完成率: {ddqn_stats.get('final_avg_completion_rate', 0):.1f}%")
    print(f"  平均距离: {ddqn_stats.get('final_avg_distance', 0):.2f}")

    if "reward" in comparison_data["improvement"]:
        print("\n改进幅度:")
        print(f"  奖励提升: {comparison_data['improvement']['reward']:.1f}%")
    if "distance" in comparison_data["improvement"]:
        print(f"  距离优化: {comparison_data['improvement']['distance']:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    run_comparison_experiment()
