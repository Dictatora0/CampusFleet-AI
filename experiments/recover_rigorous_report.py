"""
从已完成的严谨实验结果中恢复报告
用于当训练完成但报告生成失败时
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_results_from_directory(base_dir):
    """从目录中加载所有运行的结果（从CSV文件）"""
    results_list = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"⚠️  目录不存在: {base_dir}")
        return results_list
    
    # 查找所有 run_* 目录
    run_dirs = sorted([d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("run_")])
    
    print(f"找到 {len(run_dirs)} 个运行目录")
    
    for run_dir in run_dirs:
        csv_file = run_dir / "dqn_training_metrics.csv"
        if csv_file.exists():
            # 从CSV读取详细训练数据
            episode_rewards = []
            completion_rates = []
            avg_distances = []
            
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    episode_rewards.append(float(row['reward']))
                    completion_rates.append(float(row['completion_rate']))
                    avg_distances.append(float(row['avg_distance']))
            
            results = {
                "episode_rewards": episode_rewards,
                "completion_rates": completion_rates,
                "avg_distances": avg_distances,
            }
            results_list.append(results)
            print(f"  ✓ 加载: {run_dir.name} ({len(episode_rewards)} episodes)")
        else:
            print(f"  ⚠️  未找到CSV文件: {run_dir.name}")
    
    return results_list


def compute_statistics(all_results):
    """计算统计指标（与原脚本相同）"""
    
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
    
    # 尝试导入scipy
    try:
        from scipy import stats as scipy_stats
        has_scipy = True
    except ImportError:
        has_scipy = False
        print("⚠️  scipy未安装，使用简化版置信区间")
    
    def compute_metrics(data):
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        
        if has_scipy and n > 1:
            ci = scipy_stats.t.interval(0.95, n-1, loc=mean, scale=std/np.sqrt(n))
        else:
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
    
    # 统计显著性
    if has_scipy:
        t_stat, p_value = scipy_stats.ttest_ind(dqn_stats["rewards"], ddqn_stats["rewards"])
        stats["significance_test"] = {
            "reward_t_statistic": float(t_stat),
            "reward_p_value": float(p_value),
            "is_significant": bool(p_value < 0.05),  # 转换为Python bool
        }
    
    return stats


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
    """绘制对比图（简化版）"""
    
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Rigorous Comparison: Standard DQN vs Double DQN\n(Mean ± Std, N=5 runs)", 
                 fontsize=16, fontweight="bold")
    
    # 1. Bar plot with error bars
    ax = axes[0, 0]
    metrics = ['final_reward', 'final_completion_rate', 'final_distance']
    labels = ['Avg Reward', 'Completion Rate (%)', 'Avg Distance']
    
    x = np.arange(len(metrics))
    width = 0.35
    
    dqn_means = [stats['standard_dqn'][m]['mean'] for m in metrics]
    dqn_stds = [stats['standard_dqn'][m]['std'] for m in metrics]
    
    ddqn_means = [stats['double_dqn'][m]['mean'] for m in metrics]
    ddqn_stds = [stats['double_dqn'][m]['std'] for m in metrics]
    
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
    
    # 2. Box plot
    ax = axes[0, 1]
    dqn_rewards = stats['raw_data']['standard_dqn']['rewards']
    ddqn_rewards = stats['raw_data']['double_dqn']['rewards']
    
    box_data = [dqn_rewards, ddqn_rewards]
    bp = ax.boxplot(box_data, positions=[1, 2], widths=0.6,
                    patch_artist=True, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='yellow', markersize=8))
    
    colors = ['lightblue', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_xticklabels(['Standard DQN', 'Double DQN'])
    ax.set_ylabel('Final Avg Reward (last 100 episodes)')
    ax.set_title('Reward Distribution Comparison (N=5)')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 3-4. 留空或显示其他指标
    for idx in [(1, 0), (1, 1)]:
        axes[idx].text(0.5, 0.5, 'See individual run files\nfor detailed curves', 
                       ha='center', va='center', fontsize=14, color='gray')
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / "rigorous_comparison_plots.png", dpi=300, bbox_inches="tight")
    print(f"✓ 对比图表已保存: {output_dir / 'rigorous_comparison_plots.png'}")
    plt.close()


def main():
    """主函数"""
    print("=" * 80)
    print("从已完成的训练结果中恢复报告")
    print("=" * 80)
    
    base_dir = Path("experiments/results/rigorous")
    
    # 加载结果
    print("\n加载 Standard DQN 结果...")
    dqn_results = load_results_from_directory(base_dir / "standard_dqn")
    
    print("\n加载 Double DQN 结果...")
    ddqn_results = load_results_from_directory(base_dir / "double_dqn")
    
    if not dqn_results or not ddqn_results:
        print("\n❌ 未找到足够的结果文件！")
        print("请确保以下目录存在且包含训练结果:")
        print(f"  - {base_dir / 'standard_dqn'}")
        print(f"  - {base_dir / 'double_dqn'}")
        return
    
    print(f"\n总共找到: {len(dqn_results)} 个 Standard DQN, {len(ddqn_results)} 个 Double DQN")
    
    all_results = {
        "standard_dqn": dqn_results,
        "double_dqn": ddqn_results,
    }
    
    # 计算统计
    print("\n计算统计指标...")
    stats = compute_statistics(all_results)
    
    # 生成报告
    print("\n生成报告...")
    output_dir = base_dir
    num_runs = len(dqn_results)
    
    # 保存 JSON（不包含 raw_data）
    stats_for_json = {
        "standard_dqn": stats["standard_dqn"],
        "double_dqn": stats["double_dqn"],
    }
    if "significance_test" in stats:
        stats_for_json["significance_test"] = stats["significance_test"]
    
    report_data = {
        "experiment": "Rigorous DQN vs Double DQN Comparison",
        "num_runs": num_runs,
        "statistics": stats_for_json,
        "timestamp": datetime.now().isoformat(),
        "note": "Report recovered from completed training results"
    }
    
    with open(output_dir / "rigorous_comparison_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON报告已保存: {output_dir / 'rigorous_comparison_report.json'}")
    
    # 保存文本报告
    report_text = generate_text_report(stats, num_runs)
    with open(output_dir / "rigorous_comparison_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"✓ 文本报告已保存: {output_dir / 'rigorous_comparison_report.txt'}")
    
    # 绘制图表
    print("\n生成图表...")
    plot_comparison_with_uncertainty(all_results, stats, output_dir)
    
    print("\n" + "=" * 80)
    print(report_text)
    print("=" * 80)
    print(f"\n✅ 报告恢复完成！所有文件保存在: {output_dir}")


if __name__ == "__main__":
    main()
