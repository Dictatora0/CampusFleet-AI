#!/usr/bin/env python3
"""
MAPF演示 - 简化版本
"""
from core import SimulationContext
from agents import SchedulingStrategy
from visualization import PygameViewer
import time


def simple_mapf_demo():
    """简单的MAPF演示"""
    print("🧠 MAPF CBS简单演示")
    print("=" * 50)
    
    # 创建小规模测试
    context = SimulationContext(
        grid_size=8,  # 小网格
        num_cars=2,   # 2辆车
        scheduling_strategy=SchedulingStrategy.MAPF_CBS,
        enable_data_logging=False
    )
    
    # 添加订单
    for _ in range(3):
        context.add_random_order()
    
    print("✅ 创建完成，开始MAPF演示")
    
    # 运行30步看效果
    for step in range(30):
        context.step()
        
        if step % 10 == 0:
            stats = context.get_statistics()
            print(f"步骤 {step}: 完成 {stats['total_completed_orders']} 订单")
            
            # 显示车辆状态
            for car in context.cars:
                coord_status = "CBS路径" if (hasattr(car, 'use_coordinated_path') 
                                          and car.use_coordinated_path) else "传统"
                print(f"  车辆{car.car_id}: {car.state.value} | {coord_status}")
    
    print("\n✅ MAPF演示完成")
    
    # 最终统计
    final_stats = context.get_statistics()
    print(f"📊 最终结果:")
    print(f"  - 完成订单: {final_stats['total_completed_orders']}")
    print(f"  - 总距离: {final_stats['total_distance']}")
    print(f"  - 平均效率: {final_stats['avg_distance_per_order']:.2f}")


def compare_strategies():
    """简单的策略对比"""
    print("\n🔄 策略对比测试")
    print("=" * 50)
    
    strategies = [
        SchedulingStrategy.GREEDY_NEAREST,
        SchedulingStrategy.MAPF_CBS
    ]
    
    for strategy in strategies:
        print(f"\n测试策略: {strategy.value}")
        
        context = SimulationContext(
            grid_size=8,
            num_cars=2,
            scheduling_strategy=strategy,
            enable_data_logging=False
        )
        
        # 添加相同数量的订单
        for _ in range(4):
            context.add_random_order()
        
        # 运行固定步数
        for step in range(40):
            context.step()
            
            # 检查完成情况
            pending = context.order_agent.report()['pending_orders']
            all_idle = all(car.is_idle() for car in context.cars)
            
            if pending == 0 and all_idle:
                print(f"  ✅ {step}步内完成所有订单")
                break
        else:
            print(f"  ⏰ 40步内未完全完成")
        
        stats = context.get_statistics()
        print(f"  📊 完成: {stats['total_completed_orders']} 订单")
        print(f"  📏 距离: {stats['total_distance']} 格")


if __name__ == "__main__":
    try:
        simple_mapf_demo()
        compare_strategies()
    except Exception as e:
        print(f"❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
