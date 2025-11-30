#!/usr/bin/env python3
"""
系统测试脚本 - 验证所有模块正常工作
"""

import sys
import time

def test_imports():
    """测试所有模块导入"""
    print("📦 测试模块导入...")
    try:
        from agents import CarAgent, OrderAgent, SchedulerAgent
        from env import GridEnvironment, PathFinding
        from core import SimulationContext, Simulation
        print("✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_environment():
    """测试环境模块"""
    print("\n🗺️ 测试环境模块...")
    try:
        from env import GridEnvironment, PathFinding
        
        # 创建环境
        env = GridEnvironment(size=15)
        print(f"  ✅ 地图创建成功 ({env.size}x{env.size})")
        
        # 测试路径规划
        pathfinder = PathFinding(env.grid)
        path = pathfinder.a_star((0, 0), (14, 14))
        if path:
            print(f"  ✅ A*路径规划成功 (路径长度: {len(path)})")
        else:
            print("  ⚠️ 路径规划返回空")
        
        return True
    except Exception as e:
        print(f"  ❌ 环境模块测试失败: {e}")
        return False

def test_agents():
    """测试智能体模块"""
    print("\n🤖 测试智能体模块...")
    try:
        from agents import CarAgent, OrderAgent, SchedulerAgent
        
        # 测试车辆智能体
        car = CarAgent(car_id=0, initial_position=(0, 0))
        print(f"  ✅ 车辆智能体创建成功 (ID: {car.car_id})")
        
        # 测试订单智能体
        order_agent = OrderAgent()
        order_id = order_agent.create_order((0, 0), (10, 10))
        print(f"  ✅ 订单智能体创建成功 (订单ID: {order_id})")
        
        # 测试调度智能体
        scheduler = SchedulerAgent()
        print(f"  ✅ 调度智能体创建成功 (策略: {scheduler.strategy.value})")
        
        return True
    except Exception as e:
        print(f"  ❌ 智能体模块测试失败: {e}")
        return False

def test_simulation():
    """测试仿真系统"""
    print("\n⚙️ 测试仿真系统...")
    try:
        from core import SimulationContext
        
        # 创建仿真上下文
        context = SimulationContext(grid_size=15, num_cars=3)
        print(f"  ✅ 仿真上下文创建成功 (车辆数: {len(context.cars)})")
        
        # 添加订单
        order_id = context.add_random_order()
        print(f"  ✅ 订单添加成功 (订单ID: {order_id})")
        
        # 执行几步仿真
        for i in range(5):
            context.step()
        print(f"  ✅ 仿真执行成功 (步数: {context.current_step})")
        
        # 获取统计
        stats = context.get_statistics()
        print(f"  ✅ 统计数据获取成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 仿真系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_workflow():
    """测试完整工作流"""
    print("\n🔄 测试完整工作流...")
    try:
        from core import SimulationContext
        
        # 创建系统
        context = SimulationContext(grid_size=15, num_cars=2)
        
        # 添加多个订单
        for i in range(3):
            context.add_random_order()
        print(f"  ✅ 添加了3个订单")
        
        # 运行10步
        completed_before = context.total_completed_orders
        for i in range(10):
            context.step()
        completed_after = context.total_completed_orders
        
        print(f"  ✅ 运行10步成功")
        print(f"  📊 完成订单: {completed_after - completed_before}个")
        
        # 检查车辆状态
        for car in context.cars:
            report = car.report()
            print(f"  🚗 车辆{car.car_id}: {report['state']}")
        
        return True
    except Exception as e:
        print(f"  ❌ 完整工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 CampusFleet AI 系统测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("环境模块", test_environment),
        ("智能体模块", test_agents),
        ("仿真系统", test_simulation),
        ("完整工作流", test_full_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        time.sleep(0.5)
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"总计: {passed}个通过, {failed}个失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！系统运行正常！")
        print("\n💡 现在可以运行主程序：")
        print("   python main.py --demo")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
