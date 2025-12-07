#!/usr/bin/env python3
"""测试 RL 模型是否能正常加载和使用"""
import os

from agents import SchedulerAgent, SchedulingStrategy
from core.config import config

# 加载配置
if os.path.exists("config.default.json"):
    config.load_from_file("config.default.json")

print("=" * 60)
print("测试 RL 调度器初始化")
print("=" * 60)

# 创建调度器
scheduler = SchedulerAgent(
    strategy=SchedulingStrategy.RL_SCHEDULER, grid_size=15, max_cars=3, max_orders=10
)

print("\n✅ RL 调度器创建成功")
print(f"   策略: {scheduler.strategy.value}")
print(f"   可用的 RL 调度器: {list(scheduler.rl_schedulers.keys())}")

# 检查 DQN_INFERENCE 是否存在
if "DQN_INFERENCE" in scheduler.rl_schedulers:
    dqn_scheduler = scheduler.rl_schedulers["DQN_INFERENCE"]
    print(f"\n✅ DQN 推理模型已加载")
    print(f"   训练模式: {dqn_scheduler.training_mode}")
    print(f"   模型路径: {dqn_scheduler.model_path if hasattr(dqn_scheduler, 'model_path') else 'N/A'}")
else:
    print("\n⚠️  DQN 推理模型未找到")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
