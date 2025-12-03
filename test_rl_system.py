#!/usr/bin/env python3
"""
CampusFleet AI 强化学习系统测试
测试DQN和PPO智能体的训练和推理能力
"""
import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from core import SimulationContext
from agents import SchedulingStrategy


def test_rl_environment():
    """测试RL环境基础功能"""
    print("🧪 测试RL环境基础功能")
    print("=" * 50)
    
    try:
        from rl_agents.rl_environment import RLEnvironment
        
        # 创建环境
        env = RLEnvironment(
            grid_size=8,
            num_cars=2,
            max_steps=50,
            max_orders_per_episode=8
        )
        
        print(f"✅ 环境创建成功")
        print(f"   观察空间: {env.observation_space}")
        print(f"   动作空间: {env.action_space}")
        print(f"   状态维度: {env.observation_space.shape[0]}")
        
        # 测试reset和step
        obs, info = env.reset()
        print(f"✅ 环境重置成功，初始状态维度: {obs.shape}")
        
        for step in range(5):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            print(f"   Step {step}: reward={reward:.3f}, done={terminated or truncated}")
            
            if terminated or truncated:
                break
        
        env.close()
        print("✅ RL环境测试完成")
        return True
        
    except Exception as e:
        print(f"❌ RL环境测试失败: {e}")
        return False


def test_dqn_agent():
    """测试DQN智能体"""
    print("\n🤖 测试DQN智能体")
    print("=" * 50)
    
    try:
        from rl_agents.dqn_agent import DQNAgent
        
        # 创建DQN智能体
        agent = DQNAgent(
            state_dim=50,
            action_dim=10,
            learning_rate=1e-3,
            gamma=0.95,
            epsilon_start=0.9,
            epsilon_end=0.01,
            epsilon_decay=1000
        )
        
        print(f"✅ DQN智能体创建成功")
        print(f"   状态维度: {agent.state_dim}")
        print(f"   动作维度: {agent.action_dim}")
        print(f"   设备: {agent.device}")
        
        # 测试动作选择
        test_state = np.random.random(50)
        action = agent.select_action(test_state, training=True)
        print(f"✅ 动作选择测试: state_shape={test_state.shape}, action={action}")
        
        # 测试经验存储和训练
        for _ in range(100):
            state = np.random.random(50)
            action = np.random.randint(10)
            reward = np.random.normal(0, 1)
            next_state = np.random.random(50)
            done = np.random.random() < 0.1
            
            agent.store_experience(state, action, reward, next_state, done)
        
        # 训练几步
        losses = []
        for _ in range(10):
            loss = agent.train()
            if loss is not None:
                losses.append(loss)
        
        print(f"✅ DQN训练测试完成，平均损失: {np.mean(losses) if losses else 'N/A'}")
        
        # 测试模型保存和加载
        test_model_path = "test_dqn_model.pth"
        agent.save_model(test_model_path)
        agent.load_model(test_model_path)
        os.remove(test_model_path)
        print("✅ DQN模型保存/加载测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ DQN智能体测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ppo_agent():
    """测试PPO智能体"""
    print("\n🎯 测试PPO智能体")
    print("=" * 50)
    
    try:
        from rl_agents.ppo_agent import PPOAgent
        
        # 创建PPO智能体
        agent = PPOAgent(
            state_dim=50,
            action_dim=10,
            learning_rate=3e-4,
            gamma=0.99,
            clip_ratio=0.2
        )
        
        print(f"✅ PPO智能体创建成功")
        print(f"   状态维度: {agent.state_dim}")
        print(f"   动作维度: {agent.action_dim}")
        print(f"   设备: {agent.device}")
        
        # 测试动作选择
        test_state = np.random.random(50)
        action, log_prob, value = agent.select_action(test_state, training=True)
        print(f"✅ 动作选择测试: action={action}, log_prob={log_prob:.3f}, value={value:.3f}")
        
        # 测试经验存储和更新
        for _ in range(32):  # PPO需要批量数据
            state = np.random.random(50)
            action = np.random.randint(10)
            log_prob = np.random.normal(0, 1)
            reward = np.random.normal(0, 1)
            value = np.random.normal(0, 1)
            done = np.random.random() < 0.1
            
            agent.store_experience(state, action, log_prob, reward, value, done)
        
        # 测试更新
        update_stats = agent.update()
        print(f"✅ PPO更新测试完成: {update_stats}")
        
        # 测试模型保存和加载
        test_model_path = "test_ppo_model.pth"
        agent.save_model(test_model_path)
        agent.load_model(test_model_path)
        os.remove(test_model_path)
        print("✅ PPO模型保存/加载测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ PPO智能体测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rl_scheduler():
    """测试RL调度器"""
    print("\n📋 测试RL调度器")
    print("=" * 50)
    
    try:
        from rl_agents.rl_scheduler import RLScheduler
        
        # 创建PPO调度器
        scheduler = RLScheduler(
            agent_type="PPO",
            grid_size=8,
            max_cars=3,
            max_orders=5,
            training_mode=True
        )
        
        print(f"✅ RL调度器创建成功")
        print(f"   智能体类型: {scheduler.agent_type}")
        print(f"   状态维度: {scheduler.state_encoder.state_dim}")
        print(f"   训练模式: {scheduler.training_mode}")
        
        # 模拟调度请求
        class MockCar:
            def __init__(self, car_id, position):
                self.car_id = car_id
                self.position = position
                
            def is_available(self):
                return True
        
        class MockOrder:
            def __init__(self, order_id, pickup, delivery):
                self.order_id = order_id
                self.pickup_point = pickup
                self.delivery_point = delivery
        
        cars = [MockCar(i, (i, i)) for i in range(3)]
        orders = [MockOrder(i, (i, i+1), (i+2, i+3)) for i in range(5)]
        
        # 执行调度（会因为缺少context回退到简单策略）
        assignments = scheduler.schedule(cars, orders, None)
        print(f"✅ RL调度测试: 分配={assignments}")
        
        # 获取统计信息
        stats = scheduler.get_stats()
        print(f"✅ RL统计信息: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ RL调度器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rl_integration():
    """测试RL与主系统的集成"""
    print("\n🔗 测试RL系统集成")
    print("=" * 50)
    
    try:
        # 创建仿真环境 (小规模测试)
        context = SimulationContext(
            grid_size=8,
            num_cars=2,
            scheduling_strategy=SchedulingStrategy.PPO_LEARNING,
            enable_data_logging=False
        )
        
        print("✅ 创建RL集成环境成功")
        print(f"   调度策略: {context.scheduler.strategy.value}")
        print(f"   网格大小: {context.grid_env.size}")
        print(f"   车辆数量: {len(context.cars)}")
        
        # 添加测试订单
        for i in range(3):
            context.add_random_order()
        
        print(f"✅ 添加了{len(context.order_agent.pending_orders)}个测试订单")
        
        # 运行几步仿真
        for step in range(10):
            context.step()
            stats = context.get_statistics()
            
            if step % 3 == 0:
                print(f"   Step {step}: 完成{stats.get('total_completed_orders', 0)}订单")
        
        final_stats = context.get_statistics()
        print(f"✅ RL集成测试完成")
        print(f"   最终统计: {final_stats}")
        
        # 检查RL调度器状态
        if hasattr(context.scheduler, 'get_rl_stats'):
            rl_stats = context.scheduler.get_rl_stats()
            print(f"   RL统计: {rl_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ RL系统集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_training_manager():
    """测试训练管理器"""
    print("\n🎓 测试训练管理器")
    print("=" * 50)
    
    try:
        from rl_agents.training_manager import TrainingManager
        
        # 创建训练管理器（小规模配置）
        env_config = {
            'grid_size': 6,
            'num_cars': 2,
            'max_steps': 30,
            'max_orders_per_episode': 5
        }
        
        train_config = {
            'max_episodes': 10,  # 非常短的训练用于测试
            'eval_interval': 5,
            'save_interval': 10,
            'early_stop_threshold': 0.8,
            'patience': 20
        }
        
        trainer = TrainingManager(
            agent_type="PPO",
            environment_config=env_config,
            training_config=train_config,
            save_dir="test_rl_models"
        )
        
        print("✅ 训练管理器创建成功")
        print(f"   环境: {trainer.env_config}")
        print(f"   智能体: {trainer.agent_type}")
        
        # 运行短期训练测试
        print("🚀 开始短期训练测试...")
        results = trainer.train_agent()
        
        print(f"✅ 训练测试完成")
        print(f"   最佳性能: {results['best_performance']:.3f}")
        print(f"   训练时间: {results['training_time']:.2f}秒")
        print(f"   总episodes: {results['total_episodes']}")
        
        # 清理测试文件
        import shutil
        if os.path.exists("test_rl_models"):
            shutil.rmtree("test_rl_models")
        
        return True
        
    except Exception as e:
        print(f"❌ 训练管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def benchmark_rl_vs_traditional():
    """RL vs 传统算法性能对比"""
    print("\n📊 RL vs 传统算法性能对比")
    print("=" * 50)
    
    strategies_to_test = [
        SchedulingStrategy.GREEDY_NEAREST,
        SchedulingStrategy.HUNGARIAN,
        SchedulingStrategy.VRP_BATCHING,
        SchedulingStrategy.PPO_LEARNING  # RL策略
    ]
    
    results = {}
    
    for strategy in strategies_to_test:
        print(f"\n测试策略: {strategy.value}")
        
        try:
            # 创建仿真环境
            context = SimulationContext(
                grid_size=8,
                num_cars=3,
                scheduling_strategy=strategy,
                enable_data_logging=False
            )
            
            # 添加固定数量的订单
            for _ in range(6):
                context.add_random_order()
            
            start_time = time.time()
            
            # 运行固定步数
            for step in range(30):
                context.step()
                
                # 如果所有订单完成则提前结束
                if len(context.order_agent.pending_orders) == 0:
                    break
            
            elapsed_time = time.time() - start_time
            stats = context.get_statistics()
            
            results[strategy.value] = {
                'completion_time': elapsed_time,
                'completed_orders': stats.get('total_completed_orders', 0),
                'total_distance': stats.get('total_distance', 0),
                'avg_distance': stats.get('avg_distance_per_order', 0),
                'steps_taken': step + 1
            }
            
            print(f"  ✅ 完成: {stats.get('total_completed_orders', 0)}订单")
            print(f"  ⏱️ 用时: {elapsed_time:.2f}秒")
            print(f"  📏 总距离: {stats.get('total_distance', 0)}")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            results[strategy.value] = {'error': str(e)}
    
    # 打印对比结果
    print(f"\n📈 性能对比总结:")
    print("-" * 60)
    print(f"{'策略':<15} {'订单':<8} {'距离':<8} {'用时':<8} {'步数':<8}")
    print("-" * 60)
    
    for strategy, result in results.items():
        if 'error' not in result:
            print(f"{strategy:<15} "
                  f"{result['completed_orders']:<8} "
                  f"{result['total_distance']:<8.1f} "
                  f"{result['completion_time']:<8.2f} "
                  f"{result['steps_taken']:<8}")
        else:
            print(f"{strategy:<15} 测试失败")
    
    return results


def main():
    """主测试函数"""
    print("🚀 CampusFleet AI 强化学习系统全面测试")
    print("=" * 70)
    
    # 检查依赖
    try:
        import torch
        import gymnasium
        print(f"✅ 依赖检查通过: PyTorch {torch.__version__}, Gymnasium已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install torch gymnasium pandas matplotlib")
        return False
    
    test_results = {}
    
    # 运行各项测试
    tests = [
        ("RL环境", test_rl_environment),
        ("DQN智能体", test_dqn_agent),
        ("PPO智能体", test_ppo_agent),
        ("RL调度器", test_rl_scheduler),
        ("RL系统集成", test_rl_integration),
        ("训练管理器", test_training_manager),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            test_results[test_name] = False
    
    # 性能对比测试
    print(f"\n{'='*70}")
    try:
        benchmark_results = benchmark_rl_vs_traditional()
        test_results["性能对比"] = True
    except Exception as e:
        print(f"❌ 性能对比测试异常: {e}")
        test_results["性能对比"] = False
    
    # 总结
    print(f"\n🏆 测试总结")
    print("=" * 70)
    passed = sum(test_results.values())
    total = len(test_results)
    
    print(f"通过: {passed}/{total} 项测试")
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print(f"\n🎉 恭喜！CampusFleet AI强化学习系统全面测试通过！")
        print(f"🚀 系统已准备好进行强化学习训练和推理")
    else:
        print(f"\n⚠️ 部分测试失败，请检查相关组件")
    
    return passed == total


if __name__ == "__main__":
    # 设置matplotlib后端避免GUI问题
    import matplotlib
    matplotlib.use('Agg')
    
    success = main()
    
    if success:
        print(f"\n🎯 下一步:")
        print(f"   1. 运行长期训练: python -m rl_agents.training_manager")
        print(f"   2. 测试训练结果: 使用PPO_INFERENCE策略")
        print(f"   3. 集成到Web界面: 添加RL训练控制")
    
    sys.exit(0 if success else 1)
