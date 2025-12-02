#!/usr/bin/env python3
"""
测试Pygame图形界面功能
运行一个简短的演示来验证GUI可用性
"""
from core import SimulationContext
from agents import SchedulingStrategy
import sys


def test_gui():
    """测试GUI界面"""
    print("=" * 60)
    print("🎨 测试Pygame图形界面")
    print("=" * 60)
    
    # 检查Pygame是否可用
    try:
        from visualization import PygameViewer
        print("✅ Pygame模块导入成功")
    except ImportError as e:
        print(f"❌ Pygame未安装: {e}")
        print("\n请安装pygame:")
        print("  pip install pygame")
        return False
    
    # 创建仿真上下文
    print("\n📦 初始化仿真环境...")
    context = SimulationContext(
        grid_size=15,
        num_cars=3,
        scheduling_strategy=SchedulingStrategy.HUNGARIAN,
        enable_data_logging=True
    )
    
    # 添加一些订单
    print("📋 生成测试订单...")
    for i in range(5):
        context.add_random_order()
    
    # 创建查看器
    print("🖼️  初始化Pygame窗口...")
    try:
        viewer = PygameViewer(grid_size=15, cell_size=40, fps=10)
        print("✅ Pygame窗口创建成功")
    except Exception as e:
        print(f"❌ 创建窗口失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🚀 开始仿真演示（30步）")
    print("=" * 60)
    print("提示:")
    print("  - 观察车辆移动和订单分配")
    print("  - 注意电量条变化（绿→黄→红）")
    print("  - 充电站标记为 'C'")
    print("  - 按 ESC 键可随时退出")
    print("=" * 60)
    
    # 运行仿真演示
    step = 0
    max_steps = 30
    
    try:
        while step < max_steps and viewer.running:
            # 处理事件
            if not viewer.handle_events():
                print("\n用户关闭窗口")
                break
            
            # 执行仿真步骤
            context.step()
            
            # 渲染界面
            viewer.render(context)
            
            step += 1
            
            # 每10步输出一次状态
            if step % 10 == 0:
                stats = context.get_statistics()
                print(f"步骤 {step}: 完成 {stats['total_completed_orders']} 单, "
                      f"总距离 {stats['total_distance']}")
        
        print("\n" + "=" * 60)
        print("📊 演示完成")
        print("=" * 60)
        
        # 显示最终统计
        stats = context.get_statistics()
        print(f"✅ 完成订单数: {stats['total_completed_orders']}")
        print(f"📏 总移动距离: {stats['total_distance']}")
        
        print("\n车辆状态:")
        for car in context.cars:
            battery_pct = car.get_battery_percentage()
            print(f"  车辆 {car.car_id}: "
                  f"完成 {car.completed_orders} 单, "
                  f"电量 {battery_pct:.0f}%, "
                  f"充电 {car.total_charging_time} 步")
        
        print("\n⏳ 窗口将在5秒后自动关闭...")
        
        # 保持窗口显示5秒
        import time
        for _ in range(50):
            if not viewer.handle_events():
                break
            viewer.render(context)
            time.sleep(0.1)
        
        # 关闭窗口
        viewer.close()
        
        print("\n✅ GUI测试成功完成！")
        return True
        
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
        viewer.close()
        return True
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        try:
            viewer.close()
        except:
            pass
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🧪 校园无人配送车系统 - GUI测试")
    print("=" * 60)
    
    success = test_gui()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 图形界面测试通过！")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 运行完整仿真: python run_with_gui.py")
        print("  2. 查看改进文档: IMPROVEMENTS_GUIDE.md")
        print("  3. 运行所有测试: python test_improvements.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  图形界面测试未通过")
        print("=" * 60)
        print("\n可能的原因:")
        print("  1. Pygame未正确安装")
        print("  2. 无图形显示环境（SSH/远程连接）")
        print("  3. 系统不支持SDL")
        print("\n解决方案:")
        print("  - 安装Pygame: pip install pygame")
        print("  - 使用ASCII界面: python main.py")
        print("=" * 60)


if __name__ == "__main__":
    main()
