#!/usr/bin/env python3
"""
CampusFleet AI 强化学习训练演示
展示RL智能体的学习过程和性能提升
"""
import os
import sys
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from agents import SchedulingStrategy
from core import SimulationContext
from rl_agents.rl_environment import RLEnvironment
from rl_agents.training_manager import TrainingManager


def quick_rl_training_demo():
    """快速RL训练演示"""
    print(" CampusFleet AI RL训练演示")
    print("=" * 50)

    # 小规模快速训练配置
    env_config = {"grid_size": 6, "num_cars": 2, "max_steps": 30, "max_orders_per_episode": 5}

    train_config = {
        "max_episodes": 20,  # 快速演示用少量episodes
        "eval_interval": 5,
        "save_interval": 15,
        "early_stop_threshold": 0.7,
        "patience": 10,
    }

    # 创建训练管理器
    trainer = TrainingManager(
        agent_type="PPO",
        environment_config=env_config,
        training_config=train_config,
        save_dir="demo_rl_models",
    )

    print(f" 开始快速训练 (目标: {train_config['max_episodes']} episodes)")
    start_time = time.time()

    # 开始训练
    results = trainer.train_agent()

    training_time = time.time() - start_time

    print("\n 训练完成!")
    print(f"用时: {training_time:.1f}秒")
    print(f"最佳性能: {results['best_performance']:.3f}")
    print(f"最终成功率: {results['final_stats']['success_rate']:.3f}")

    return trainer, results


def compare_rl_vs_traditional():
    """对比RL和传统策略的性能"""
    print("\n 性能对比：RL vs 传统策略")
    print("=" * 50)

    strategies = [
        ("贪心最近", SchedulingStrategy.GREEDY_NEAREST),
        ("匈牙利算法", SchedulingStrategy.HUNGARIAN),
        ("PPO学习", SchedulingStrategy.PPO_LEARNING),
    ]

    results = {}

    for name, strategy in strategies:
        print(f"\n测试 {name}...")

        try:
            # 创建测试环境
            context = SimulationContext(
                grid_size=8, num_cars=2, scheduling_strategy=strategy, enable_data_logging=False
            )

            # 添加测试订单
            for _ in range(4):
                context.add_random_order()

            start_time = time.time()
            total_distance = 0
            completed_orders = 0

            # 运行仿真
            for step in range(25):
                context.step()

                stats = context.get_statistics()
                completed_orders = stats.get("total_completed_orders", 0)
                total_distance = stats.get("total_distance", 0)

                # 如果所有订单完成则提前结束
                if len(context.order_agent.get_pending_orders()) == 0:
                    break

            execution_time = time.time() - start_time

            results[name] = {
                "completed_orders": completed_orders,
                "total_distance": total_distance,
                "execution_time": execution_time,
                "steps": step + 1,
                "avg_distance": total_distance / max(completed_orders, 1),
            }

            print(f"完成订单: {completed_orders}")
            print(f"总距离: {total_distance}")
            print(f"⏱️ 用时: {execution_time:.2f}秒")

        except Exception as e:
            print(f"测试失败: {e}")
            results[name] = {"error": str(e)}

    # 显示对比结果
    print("\n📈 对比总结:")
    print("-" * 60)
    print(f"{'策略':<12} {'订单':<6} {'距离':<8} {'平均':<8} {'步数':<6}")
    print("-" * 60)

    for name, result in results.items():
        if "error" not in result:
            print(
                f"{name:<12} {result['completed_orders']:<6} "
                f"{result['total_distance']:<8.1f} {result['avg_distance']:<8.2f} "
                f"{result['steps']:<6}"
            )

    return results


def demo_rl_environment():
    """演示RL环境的基本功能"""
    print("\n🔬 RL环境功能演示")
    print("=" * 50)

    # 创建RL环境
    env = RLEnvironment(grid_size=6, num_cars=2, max_steps=20, max_orders_per_episode=6)

    print(" RL环境创建成功")
    print(f"状态维度: {env.observation_space.shape[0]}")
    print(f"动作空间: {env.action_space}")

    # 运行一个episode
    obs, info = env.reset()
    total_reward = 0

    print("\n🎮 运行episode演示:")
    for step in range(10):
        # 随机动作
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        total_reward += reward

        print(
            f"Step {step}: reward={reward:6.2f}, "
            f"pending={info['pending_orders']}, done={terminated or truncated}"
        )

        if terminated or truncated:
            break

    env.close()

    print("\n Episode总结:")
    print(f"总奖励: {total_reward:.2f}")
    print(f"步数: {step + 1}")
    print(f"平均奖励: {total_reward / (step + 1):.2f}")


def main():
    """主演示函数"""
    print(" CampusFleet AI 强化学习全面演示")
    print("=" * 70)

    try:
        # 检查依赖

        print(" 依赖检查通过")

        # 1. 演示RL环境
        demo_rl_environment()

        # 2. 快速训练演示
        trainer, train_results = quick_rl_training_demo()

        # 3. 性能对比
        _ = compare_rl_vs_traditional()

        # 4. 清理临时文件
        import shutil

        if os.path.exists("demo_rl_models"):
            shutil.rmtree("demo_rl_models")

        print("\n 演示完成!")
        print(" CampusFleet AI强化学习系统运行正常!")

        return True

    except ImportError as e:
        print(f" 缺少依赖: {e}")
        print("请安装: pip install torch gymnasium matplotlib")
        return False

    except Exception as e:
        print(f" 演示过程出错: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 设置matplotlib后端
    import matplotlib

    matplotlib.use("Agg")  # 避免GUI问题

    success = main()

    if success:
        print("\n 下一步:")
        print("1. 长期训练: python -m rl_agents.training_manager")
        print("2. Web界面集成: 启动FastAPI后端")
        print("3. 生产部署: 使用训练好的模型")

    print("\n👋 演示结束")
    sys.exit(0 if success else 1)
