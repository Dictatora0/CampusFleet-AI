#!/usr/bin/env python3
"""
使用Pygame图形界面运行仿真
"""
from core import SimulationContext
from agents import SchedulingStrategy
from visualization import PygameViewer
import sys


def main():
    """主函数"""
    print("🚀 正在启动图形界面仿真...")
    
    # 配置参数
    grid_size = 15
    num_cars = 3
    num_orders = 10
    max_steps = 500
    
    # 选择调度策略
    print("\n请选择调度策略:")
    print("1. 贪心最近策略 (GREEDY_NEAREST)")
    print("2. 负载均衡策略 (BALANCED_LOAD)")
    print("3. 匈牙利算法 (HUNGARIAN)")
    
    choice = input("输入选择 (1/2/3, 默认1): ").strip() or "1"
    
    if choice == "2":
        strategy = SchedulingStrategy.BALANCED_LOAD
    elif choice == "3":
        strategy = SchedulingStrategy.HUNGARIAN
    else:
        strategy = SchedulingStrategy.GREEDY_NEAREST
    
    # 初始化仿真上下文
    context = SimulationContext(
        grid_size=grid_size,
        num_cars=num_cars,
        scheduling_strategy=strategy,
        enable_data_logging=True
    )
    
    # 预先生成订单
    print(f"\n生成 {num_orders} 个随机订单...")
    for _ in range(num_orders):
        context.add_random_order()
    
    # 初始化Pygame查看器
    try:
        viewer = PygameViewer(grid_size=grid_size, cell_size=40, fps=10)
    except ImportError as e:
        print(f"❌ 错误: {e}")
        print("请安装pygame: pip install pygame")
        sys.exit(1)
    
    print("\n✅ 图形界面已启动！")
    print("提示: 按 ESC 键退出仿真\n")
    
    # 仿真主循环
    step = 0
    running = True
    idle_count = 0
    
    while running and step < max_steps:
        # 处理事件
        if not viewer.handle_events():
            break
        
        # 执行仿真步骤
        if not context.step():
            break
        
        # 渲染界面
        viewer.render(context)
        
        step += 1
        
        # 检查是否所有订单都已完成
        pending = context.order_agent.report()['pending_orders']
        all_idle = all(car.is_idle() for car in context.cars)
        
        if pending == 0 and all_idle:
            idle_count += 1
            if idle_count >= 10:
                print(f"\n✅ 所有订单已完成！（步骤 {step}）")
                # 继续显示5秒
                import time
                for _ in range(50):
                    if not viewer.handle_events():
                        break
                    viewer.render(context)
                    time.sleep(0.1)
                break
        else:
            idle_count = 0
    
    # 显示最终统计
    print("\n" + "=" * 60)
    print("🏁 仿真完成 - 最终统计")
    print("=" * 60)
    stats = context.get_statistics()
    print(f"✅ 总完成订单数: {stats['total_completed_orders']}")
    print(f"📏 总移动距离: {stats['total_distance']}")
    if stats['total_completed_orders'] > 0:
        print(f"📊 平均每订单距离: {stats['avg_distance_per_order']:.2f}")
    
    print("\n车辆表现:")
    for car_info in stats['cars']:
        print(f"  车辆{car_info['car_id']}: "
              f"完成{car_info['completed_orders']}单, "
              f"行驶{car_info['total_distance']}格, "
              f"充电{car_info['total_charging_time']}步")
    print("=" * 60)
    
    # 导出数据
    print("\n📊 正在导出数据和生成图表...")
    exported_files = context.export_data()
    
    if exported_files:
        try:
            from analytics import DataVisualizer
            
            frames_csv = None
            cars_csv = None
            orders_csv = None
            
            for file_path in exported_files:
                if 'frames' in file_path and file_path.endswith('.csv'):
                    frames_csv = file_path
                elif 'cars' in file_path and file_path.endswith('.csv'):
                    cars_csv = file_path
                elif 'orders' in file_path and file_path.endswith('.csv'):
                    orders_csv = file_path
            
            if frames_csv and cars_csv:
                visualizer = DataVisualizer()
                visualizer.generate_all_plots(frames_csv, cars_csv, orders_csv, grid_size)
                print("✅ 图表生成完成！")
        except Exception as e:
            print(f"⚠️ 生成图表时出错: {e}")
    
    # 关闭Pygame
    viewer.close()


if __name__ == "__main__":
    main()
