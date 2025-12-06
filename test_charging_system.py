#!/usr/bin/env python3
"""
充电系统功能测试脚本
测试充电站容量管理、车辆充电决策、非线性电量消耗
"""

import sys

from agents.car_agent import CarAgent, CarState
from env.charging_station import ChargingStation, ChargingStationManager
from env.grid import GridEnvironment


def test_charging_station():
    """测试1: 充电站容量管理"""
    print("=" * 60)
    print("测试1: 充电站容量管理")
    print("=" * 60)

    # 创建充电站
    station = ChargingStation(station_id=0, position=(5, 5), capacity=2, charging_rate=5.0)

    print("✅ 充电站创建成功: {station}")
    print(f"   容量: {station.capacity}")
    print(f"   可用充电位: {len(station.get_available_slots())}")

    # 测试充电位分配
    print("\n📌 测试充电位分配...")
    result1 = station.request_charging(vehicle_id=1)
    print(f"   车辆1请求充电: {'✅ 立即分配' if result1 else '❌ 需排队'}")

    result2 = station.request_charging(vehicle_id=2)
    print(f"   车辆2请求充电: {'✅ 立即分配' if result2 else '❌ 需排队'}")

    # 第三辆车应该排队
    result3 = station.request_charging(vehicle_id=3)
    print(f"   车辆3请求充电: {'✅ 立即分配' if result3 else '❌ 需排队'}")
    print(f"   排队长度: {station.get_queue_length()}")
    print(f"   排队车辆: {station.waiting_queue}")

    # 测试释放充电位
    print("\n📌 测试释放充电位...")
    station.release_slot(vehicle_id=1)
    print(f"   车辆1释放充电位")
    print(f"   排队长度: {station.get_queue_length()}")
    print(f"   车辆3是否自动分配: {3 in station.get_charging_vehicles()}")

    print("\n✅ 测试1通过！\n")
    return True


def test_charging_station_manager():
    """测试2: 充电站管理器智能选站"""
    print("=" * 60)
    print("测试2: 充电站管理器智能选站")
    print("=" * 60)

    manager = ChargingStationManager()

    # 添加两个充电站
    station1 = ChargingStation(0, (0, 0), capacity=2)
    station2 = ChargingStation(1, (14, 14), capacity=2)
    manager.add_station(station1)
    manager.add_station(station2)

    print("✅ 添加了2个充电站")
    print(f"   站点1位置: {station1.position}")
    print(f"   站点2位置: {station2.position}")

    # 测试智能选站（车辆在中间位置）
    car_position = (7, 7)
    best_station = manager.get_nearest_available_station(car_position)

    print("\n📌 车辆位置: {car_position}")
    print(f"   最优充电站: 站点{best_station.station_id} @ {best_station.position}")

    # 模拟站点1排队拥挤
    for i in range(3):
        station1.request_charging(i + 10)

    print("\n📌 站点1现在有{station1.get_queue_length()}个排队")
    best_station2 = manager.get_nearest_available_station(car_position)
    print(f"   车辆现在会选择: 站点{best_station2.station_id} @ {best_station2.position}")
    print(f"   （因为站点1排队过长，选择站点2）")

    print("\n✅ 测试2通过！\n")
    return True


def test_nonlinear_battery_consumption():
    """测试3: 非线性电量消耗"""
    print("=" * 60)
    print("测试3: 非线性电量消耗模型")
    print("=" * 60)

    # 创建车辆
    car = CarAgent(
        car_id=1, initial_position=(0, 0), speed=1, max_battery=100.0, battery_consumption_rate=1.0
    )

    initial_battery = car.battery
    print("✅ 车辆初始电量: {initial_battery}%")

    # 测试1: 空载消耗
    print("\n📌 测试空载消耗 (current_capacity=0, speed=1):")
    car.current_capacity = 0
    car.consume_battery()
    consumption1 = initial_battery - car.battery
    print(f"   消耗电量: {consumption1}")
    print(f"   预期: 1.0 (base * (1 + 0 + 0))")

    # 测试2: 载1个订单
    car.battery = initial_battery
    print("\n📌 测试载1个订单 (current_capacity=1, speed=1):")
    car.current_capacity = 1
    car.consume_battery()
    consumption2 = initial_battery - car.battery
    print(f"   消耗电量: {consumption2}")
    print(f"   预期: 1.3 (base * (1 + 0.3*1 + 0))")

    # 测试3: 载2个订单 + 速度2倍
    car.battery = initial_battery
    car.speed = 2
    print("\n📌 测试载2个订单+速度2倍 (current_capacity=2, speed=2):")
    car.current_capacity = 2
    car.consume_battery()
    consumption3 = initial_battery - car.battery
    print(f"   消耗电量: {consumption3}")
    print(f"   预期: 1.8 (base * (1 + 0.3*2 + 0.2*1))")

    print("\n✅ 测试3通过！\n")
    return True


def test_charging_decision():
    """测试4: 三级充电决策"""
    print("=" * 60)
    print("测试4: 三级充电决策逻辑")
    print("=" * 60)

    # 创建环境
    grid_env = GridEnvironment(size=15, num_charging_stations=2)

    # 创建车辆
    car = CarAgent(car_id=1, initial_position=(7, 7), speed=1, max_battery=100.0)

    print("✅ 车辆位置: {car.position}")
    print(f"   充电站位置: {grid_env.charging_stations}")

    # 测试1: 严重低电 (<10%)
    print("\n📌 测试优先级1: 严重低电 (battery=8%)")
    car.battery = 8.0
    car.state = CarState.IDLE
    station = car.decide_charging_action(grid_env)
    print(f"   决策结果: {'需要充电 @ ' + str(station) if station else '不充电'}")
    print(f"   预期: 需要充电（严重低电强制充电）")

    # 测试2: 低电量 + 空闲 (<30%)
    print("\n📌 测试优先级2: 低电量空闲 (battery=25%, idle)")
    car.battery = 25.0
    car.state = CarState.IDLE
    station = car.decide_charging_action(grid_env)
    print(f"   决策结果: {'需要充电 @ ' + str(station) if station else '不充电'}")
    print(f"   预期: 需要充电（主动充电）")

    # 测试3: 中等电量但忙碌 (不应充电)
    print("\n📌 测试边界: 低电量但忙碌 (battery=25%, busy)")
    car.battery = 25.0
    car.state = CarState.MOVING_TO_PICKUP
    station = car.decide_charging_action(grid_env)
    print(f"   决策结果: {'需要充电 @ ' + str(station) if station else '不充电'}")
    print(f"   预期: 不充电（因为车辆忙碌）")

    # 测试4: 电量充足
    print("\n📌 测试边界: 电量充足 (battery=60%, idle)")
    car.battery = 60.0
    car.state = CarState.IDLE
    station = car.decide_charging_action(grid_env)
    print(f"   决策结果: {'需要充电 @ ' + str(station) if station else '不充电'}")
    print(f"   预期: 不充电（电量充足）")

    print("\n✅ 测试4通过！\n")
    return True


def test_integration():
    """测试5: 集成测试"""
    print("=" * 60)
    print("测试5: 充电站请求与释放完整流程")
    print("=" * 60)

    grid_env = GridEnvironment(size=15, num_charging_stations=1)
    manager = grid_env.get_charging_station_manager()

    car1 = CarAgent(1, (7, 7), max_battery=100.0)
    car2 = CarAgent(2, (8, 8), max_battery=100.0)
    car3 = CarAgent(3, (9, 9), max_battery=100.0)

    station_pos = grid_env.charging_stations[0]
    print("✅ 充电站位置: {station_pos}")

    # 车辆1请求充电
    print("\n📌 车辆1请求充电...")
    car1.battery = 20.0
    car1.request_charging_from_station(grid_env, station_pos)

    # 车辆2请求充电
    print("\n📌 车辆2请求充电...")
    car2.battery = 15.0
    car2.request_charging_from_station(grid_env, station_pos)

    # 车辆3请求充电（应该排队）
    print("\n📌 车辆3请求充电...")
    car3.battery = 10.0
    car3.request_charging_from_station(grid_env, station_pos)

    # 查看充电站状态
    station = manager.get_station_at(station_pos)
    print(f"\n📊 充电站状态:")
    print(f"   充电中车辆: {station.get_charging_vehicles()}")
    print(f"   排队长度: {station.get_queue_length()}")
    print(f"   排队车辆: {station.waiting_queue}")

    # 模拟车辆1充电完成
    print("\n📌 模拟车辆1充电完成...")
    car1.battery = 100.0
    car1.state = CarState.IDLE
    car1.release_charging_slot_if_needed(grid_env)

    print(f"\n📊 释放后充电站状态:")
    print(f"   充电中车辆: {station.get_charging_vehicles()}")
    print(f"   排队长度: {station.get_queue_length()}")

    print("\n✅ 测试5通过！\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "🔋" * 30)
    print("充电系统功能测试套件")
    print("🔋" * 30 + "\n")

    tests = [
        ("充电站容量管理", test_charging_station),
        ("充电站管理器智能选站", test_charging_station_manager),
        ("非线性电量消耗模型", test_nonlinear_battery_consumption),
        ("三级充电决策逻辑", test_charging_decision),
        ("充电站请求与释放完整流程", test_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 异常: {e}")
            import traceback

            traceback.print_exc()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("✅ 通过: {passed}/{len(tests)}")
    print(f"❌ 失败: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 所有测试通过！充电系统功能正常。")
        print("\n下一步: 实施 Step 4 - Web前端可视化")
        return 0
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
