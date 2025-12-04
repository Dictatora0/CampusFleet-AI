"""
严谨的强化学习算法对比实验
对比标准 DQN 与 Double DQN，进行多次独立运行并统计分析

实验设置:
- 运行次数: 5 次独立实验
- 训练轮数: 1000 episodes (完全收敛)
- 统计指标: 均值、标准差、置信区间
- 输出: 详细对比报告 + 专业图表
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rl_agents.training_manager import TrainingManager


def run_single_experiment(algorithm_name, use_double_dqn, run_id, base_save_dir):
    """运行单次实验"""
    print(f"\n{'='*80}")
    print(f"运行 {algorithm_name} - 第 {run_id}/5 次")
    print(f"{'='*80}")
    
    # 环境配置（优化版）
    env_config = {
        "grid_size": 10,
        "num_cars": 3,
        "max_steps": 350,
        "max_orders_per_episode": 10,
    }
    
    # 训练配置（严谨版）
    training_config = {
        "max_episodes": 1000,  # 完全收敛
        "eval_interval": 50,   # 减少评估频率
        "save_interval": 200,
        "early_stop_threshold": 0.6,
        "patience": 400,  # 更大的耐心值
    }
    
    # Agent 配置
    agent_config = {
        "use_double_dqn": use_double_dqn,
    }
    
    # 保存目录
    save_dir = f"{base_save_dir}/run_{run_id}"
    
    # 创建训练器
    trainer = TrainingManager(
        agent_type="DQN",
        environment_config=env_config,
        training_config=training_config,
        agent_config=agent_config,
        save_dir=save_dir,
    )
    
    # 训练
    results = trainer.train_agent()
    
    return results, env_config, training_config


def run_rigorous_comparison(num_runs=5):
    """运行严谨的对比实验"""
    
    start_time = datetime.now()
    
    print("=" * 80)
    print("严谨的 RL 算法对比实验")
    print(f"运行次数: {num_runs} 次独立实验")
    print(f"训练轮数: 1000 episodes/run")
    print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 存储所有运行的结果
    all_results = {
        "standard_dqn": [],
        "double_dqn": [],
    }
    
    # 运行标准 DQN（多次）
    print(f"\n{'#'*80}")
    print(f"阶段 1/2: 训练标准 DQN ({num_runs} 次)")
    print(f"{'#'*80}")
    
    for run_id in range(1, num_runs + 1):
        results, env_config, training_config = run_single_experiment(
            algorithm_name="Standard DQN",
            use_double_dqn=False,
            run_id=run_id,
            base_save_dir="experiments/results/rigorous/standard_dqn"
        )
        all_results["standard_dqn"].append(results)
    
    # 运行 Double DQN（多次）
    print(f"\n{'#'*80}")
    print(f"阶段 2/2: 训练 Double DQN ({num_runs} 次)")
    print(f"{'#'*80}")
    
    for run_id in range(1, num_runs + 1):
        results, _, _ = run_single_experiment(
            algorithm_name="Double DQN",
            use_double_dqn=True,
            run_id=run_id,
            base_save_dir="experiments/results/rigorous/double_dqn"
        )
        all_results["double_dqn"].append(results)
    
    # 统计分析
    print(f"\n{'='*80}")
    print("统计分析中...")
    print(f"{'='*80}")
    
    stats = compute_statistics(all_results)
    
    # 生成报告和图表
    output_dir = Path("experiments/results/rigorous")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    save_detailed_report(stats, env_config, training_config, output_dir, num_runs)
    plot_comparison_with_uncertainty(all_results, stats, output_dir)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 3600
    
    print(f"\n{'='*80}")
    print(f"实验完成!")
    print(f"总用时: {duration:.2f} 小时")
    print(f"结果保存在: {output_dir}")
    print(f"{'='*80}")
    
    return stats


def compute_statistics(all_results):
    """计算统计指标（均值、标准差、置信区间）"""
    
    def get_final_stats(results_list):
        """从多次运行中提取最终统计"""
        final_rewards = []
        final_completion_rates = []
        final_distances = []
        best_rewards = []
        
        for results in results_list:
            # 最后100个episodes的平均值
            if results.get("episode_rewards"):
                last_100_rewards = results["episode_rewards"][-100:]
                final_rewards.append(np.mean(last_100_rewards) if last_100_rewards else 0)
                best_rewards.append(max(results["episode_rewards"]))
            
            if results.get("completion_rates"):
                last_100_completion = results["completion_rates"][-100:]
                final_completion_rates.append(np.mean(last_100_completion) if last_100_completion else 0)
            
            if results.get("avg_distances"):
                last_100_distances = results["avg_distances"][-100:]
                final_distances.append(np.mean(last_100_distances) if last_100_distances else 0)
        
        return {
            "rewards": np.array(final_rewards),
            "completion_rates": np.array(final_completion_rates),
            "distances": np.array(final_distances),
            "best_rewards": np.array(best_rewards),
        }
    
    # 计算两个算法的统计数据
    dqn_stats = get_final_stats(all_results["standard_dqn"])
    ddqn_stats = get_final_stats(all_results["double_dqn"])
    
    # 计算均值、标准差、95%置信区间
    def compute_ci(data):
        """计算95%置信区间"""
        mean = np.mean(data)
        std = np.std(data, ddof=1)  # 样本标准差
        n = len(data)
        # t分布的95%置信区间（小样本）
        from scipy import stats as scipy_stats
        ci = scipy_stats.t.interval(0.95, n-1, loc=mean, scale=std/np.sqrt(n))
        return mean, std, ci
    
    # 尝试导入scipy，如果没有则使用简化版本
    try:
        from scipy import stats as scipy_stats
        has_scipy = True
    except ImportError:
        has_scipy = False
        print("⚠️  scipy未安装，使用简化版置信区间（正态分布近似）")
    
    def compute_metrics(data):
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        
        if has_scipy and n > 1:
            ci = scipy_stats.t.interval(0.95, n-1, loc=mean, scale=std/np.sqrt(n))
        else:
            # 简化版本：使用1.96*SE
            margin = 1.96 * std / np.sqrt(n) if n > 0 else 0
            ci = (mean - margin, mean + margin)
        
        return {
            "mean": float(mean),
            "std": float(std),
            "ci_lower": float(ci[0]),
            "ci_upper": float(ci[1]),
        }
    
    stats = {
        "standard_dqn": {
            "final_reward": compute_metrics(dqn_stats["rewards"]),
            "final_completion_rate": compute_metrics(dqn_stats["completion_rates"]),
            "final_distance": compute_metrics(dqn_stats["distances"]),
            "best_reward": compute_metrics(dqn_stats["best_rewards"]),
        },
        "double_dqn": {
            "final_reward": compute_metrics(ddqn_stats["rewards"]),
            "final_completion_rate": compute_metrics(ddqn_stats["completion_rates"]),
            "final_distance": compute_metrics(ddqn_stats["distances"]),
            "best_reward": compute_metrics(ddqn_stats["best_rewards"]),
        },
        "raw_data": {
            "standard_dqn": dqn_stats,
            "double_dqn": ddqn_stats,
        }
    }
    
    # 计算统计显著性（t检验）
    if has_scipy:
        # Reward差异的t检验
        t_stat, p_value = scipy_stats.ttest_ind(dqn_stats["rewards"], ddqn_stats["rewards"])
        stats["significance_test"] = {
            "reward_t_statistic": float(t_stat),
            "reward_p_value": float(p_value),
            "is_significant": bool(p_value < 0.05),  # 转换为Python bool
        }
    
    return stats


def save_detailed_report(stats, env_config, training_config, output_dir, num_runs):
    """保存详细报告"""
    
    # 创建不包含 raw_data 的统计数据副本（用于 JSON 序列化）
    stats_for_json = {
        "standard_dqn": stats["standard_dqn"],
        "double_dqn": stats["double_dqn"],
    }
    
    # 如果有显著性检验，也包含进去
    if "significance_test" in stats:
        stats_for_json["significance_test"] = stats["significance_test"]
    
    # JSON格式保存
    report_data = {
        "experiment": "Rigorous DQN vs Double DQN Comparison",
        "num_runs": num_runs,
        "environment_config": env_config,
        "training_config": training_config,
        "statistics": stats_for_json,
        "timestamp": datetime.now().isoformat(),
    }
    
    with open(output_dir / "rigorous_comparison_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    # 文本格式报告
    report_text = generate_text_report(stats, num_runs)
    with open(output_dir / "rigorous_comparison_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print("\n" + report_text)
    print(f"\n✓ 详细报告已保存:")
    print(f"  - {output_dir / 'rigorous_comparison_report.json'}")
    print(f"  - {output_dir / 'rigorous_comparison_report.txt'}")


def generate_text_report(stats, num_runs):
    """生成文本格式报告"""
    
    dqn = stats["standard_dqn"]
    ddqn = stats["double_dqn"]
    
    report = []
    report.append("=" * 80)
    report.append("严谨对比实验报告 - Standard DQN vs Double DQN")
    report.append("=" * 80)
    report.append(f"\n实验设置:")
    report.append(f"  • 独立运行次数: {num_runs}")
    report.append(f"  • 训练轮数: 1000 episodes/run")
    report.append(f"  • 统计方法: 均值 ± 标准差, 95% 置信区间")
    
    report.append(f"\n{'-'*80}")
    report.append("Standard DQN 结果:")
    report.append(f"{'-'*80}")
    report.append(f"  平均奖励:      {dqn['final_reward']['mean']:.2f} ± {dqn['final_reward']['std']:.2f}")
    report.append(f"    95% CI:      [{dqn['final_reward']['ci_lower']:.2f}, {dqn['final_reward']['ci_upper']:.2f}]")
    report.append(f"  完成率:        {dqn['final_completion_rate']['mean']:.1f}% ± {dqn['final_completion_rate']['std']:.1f}%")
    report.append(f"    95% CI:      [{dqn['final_completion_rate']['ci_lower']:.1f}%, {dqn['final_completion_rate']['ci_upper']:.1f}%]")
    report.append(f"  平均距离:      {dqn['final_distance']['mean']:.2f} ± {dqn['final_distance']['std']:.2f}")
    report.append(f"  最佳奖励:      {dqn['best_reward']['mean']:.2f} ± {dqn['best_reward']['std']:.2f}")
    
    report.append(f"\n{'-'*80}")
    report.append("Double DQN 结果:")
    report.append(f"{'-'*80}")
    report.append(f"  平均奖励:      {ddqn['final_reward']['mean']:.2f} ± {ddqn['final_reward']['std']:.2f}")
    report.append(f"    95% CI:      [{ddqn['final_reward']['ci_lower']:.2f}, {ddqn['final_reward']['ci_upper']:.2f}]")
    report.append(f"  完成率:        {ddqn['final_completion_rate']['mean']:.1f}% ± {ddqn['final_completion_rate']['std']:.1f}%")
    report.append(f"    95% CI:      [{ddqn['final_completion_rate']['ci_lower']:.1f}%, {ddqn['final_completion_rate']['ci_upper']:.1f}%]")
    report.append(f"  平均距离:      {ddqn['final_distance']['mean']:.2f} ± {ddqn['final_distance']['std']:.2f}")
    report.append(f"  最佳奖励:      {ddqn['best_reward']['mean']:.2f} ± {ddqn['best_reward']['std']:.2f}")
    
    # 相对改进
    reward_improvement = ((ddqn['final_reward']['mean'] - dqn['final_reward']['mean']) 
                          / dqn['final_reward']['mean'] * 100)
    completion_improvement = ddqn['final_completion_rate']['mean'] - dqn['final_completion_rate']['mean']
    distance_improvement = ((dqn['final_distance']['mean'] - ddqn['final_distance']['mean']) 
                            / dqn['final_distance']['mean'] * 100)
    
    report.append(f"\n{'-'*80}")
    report.append("相对改进 (Double DQN vs Standard DQN):")
    report.append(f"{'-'*80}")
    report.append(f"  奖励提升:      {reward_improvement:+.1f}%")
    report.append(f"  完成率提升:    {completion_improvement:+.1f}%")
    report.append(f"  距离优化:      {distance_improvement:+.1f}%")
    
    # 统计显著性
    if "significance_test" in stats:
        sig = stats["significance_test"]
        report.append(f"\n{'-'*80}")
        report.append("统计显著性检验 (Independent t-test):")
        report.append(f"{'-'*80}")
        report.append(f"  t统计量:       {sig['reward_t_statistic']:.3f}")
        report.append(f"  p值:           {sig['reward_p_value']:.4f}")
        report.append(f"  结论:          {'显著差异 (p < 0.05)' if sig['is_significant'] else '无显著差异 (p ≥ 0.05)'}")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)


def plot_comparison_with_uncertainty(all_results, stats, output_dir):
    """绘制带不确定性的对比图"""
    
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Rigorous Comparison: Standard DQN vs Double DQN\n(Mean ± Std, N=5 runs)", 
                 fontsize=16, fontweight="bold")
    
    # 1. 奖励曲线（多次运行）
    ax = axes[0, 0]
    plot_multi_run_curves(ax, all_results["standard_dqn"], "Standard DQN", "blue", "episode_rewards")
    plot_multi_run_curves(ax, all_results["double_dqn"], "Double DQN", "red", "episode_rewards")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Total Reward")
    ax.set_title("Episode Rewards (Mean ± Std)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. 完成率曲线
    ax = axes[0, 1]
    plot_multi_run_curves(ax, all_results["standard_dqn"], "Standard DQN", "blue", "completion_rates")
    plot_multi_run_curves(ax, all_results["double_dqn"], "Double DQN", "red", "completion_rates")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Completion Rate (%)")
    ax.set_title("Order Completion Rate (Mean ± Std)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 105])
    
    # 3. Bar plot with error bars
    ax = axes[1, 0]
    plot_bar_comparison(ax, stats)
    
    # 4. Box plot
    ax = axes[1, 1]
    plot_box_comparison(ax, stats)
    
    plt.tight_layout()
    plt.savefig(output_dir / "rigorous_comparison_plots.png", dpi=300, bbox_inches="tight")
    print(f"对比图表已保存: {output_dir / 'rigorous_comparison_plots.png'}")
    plt.close()


def plot_multi_run_curves(ax, results_list, label, color, metric_key):
    """绘制多次运行的曲线（均值±标准差）"""
    # 收集所有运行的数据
    all_curves = []
    for results in results_list:
        if metric_key in results and results[metric_key]:
            all_curves.append(results[metric_key])
    
    if not all_curves:
        return
    
    # 找到最小长度
    min_len = min(len(curve) for curve in all_curves)
    all_curves = [curve[:min_len] for curve in all_curves]
    
    # 计算均值和标准差
    all_curves = np.array(all_curves)
    mean_curve = np.mean(all_curves, axis=0)
    std_curve = np.std(all_curves, axis=0)
    
    episodes = range(len(mean_curve))
    
    # 绘制均值
    ax.plot(episodes, mean_curve, label=label, color=color, linewidth=2)
    
    # 绘制标准差阴影
    ax.fill_between(episodes, 
                     mean_curve - std_curve, 
                     mean_curve + std_curve, 
                     color=color, alpha=0.2)


def plot_bar_comparison(ax, stats):
    """绘制bar图对比（带误差棒）"""
    metrics = ['final_reward', 'final_completion_rate', 'final_distance']
    labels = ['Avg Reward', 'Completion Rate (%)', 'Avg Distance']
    
    x = np.arange(len(metrics))
    width = 0.35
    
    dqn_means = [stats['standard_dqn'][m]['mean'] for m in metrics]
    dqn_stds = [stats['standard_dqn'][m]['std'] for m in metrics]
    
    ddqn_means = [stats['double_dqn'][m]['mean'] for m in metrics]
    ddqn_stds = [stats['double_dqn'][m]['std'] for m in metrics]
    
    # 归一化显示（避免scale差异）
    max_vals = [max(dqn_means[i], ddqn_means[i]) for i in range(len(metrics))]
    dqn_normalized = [dqn_means[i] / max_vals[i] * 100 for i in range(len(metrics))]
    ddqn_normalized = [ddqn_means[i] / max_vals[i] * 100 for i in range(len(metrics))]
    
    ax.bar(x - width/2, dqn_normalized, width, label='Standard DQN', 
           color='blue', alpha=0.7, yerr=[dqn_stds[i]/max_vals[i]*100 for i in range(len(metrics))],
           capsize=5)
    ax.bar(x + width/2, ddqn_normalized, width, label='Double DQN', 
           color='red', alpha=0.7, yerr=[ddqn_stds[i]/max_vals[i]*100 for i in range(len(metrics))],
           capsize=5)
    
    ax.set_ylabel('Normalized Score (%)')
    ax.set_title('Performance Comparison (Normalized, Mean ± Std)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


def plot_box_comparison(ax, stats):
    """绘制box plot对比"""
    dqn_rewards = stats['raw_data']['standard_dqn']['rewards']
    ddqn_rewards = stats['raw_data']['double_dqn']['rewards']
    
    box_data = [dqn_rewards, ddqn_rewards]
    positions = [1, 2]
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6,
                    patch_artist=True, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='yellow', markersize=8))
    
    # 设置颜色
    colors = ['lightblue', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_xticklabels(['Standard DQN', 'Double DQN'])
    ax.set_ylabel('Final Avg Reward (last 100 episodes)')
    ax.set_title('Reward Distribution Comparison (N=5)')
    ax.grid(True, alpha=0.3, axis='y')


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="严谨的RL算法对比实验")
    parser.add_argument("--runs", type=int, default=5, help="独立运行次数 (默认: 5)")
    args = parser.parse_args()
    
    stats = run_rigorous_comparison(num_runs=args.runs)
