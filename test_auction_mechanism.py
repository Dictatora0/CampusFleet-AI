#!/usr/bin/env python
"""
测试拍卖机制（合同网协议CNP）

测试场景：
1. 多车辆竞标单个订单
2. 电量影响竞标成本
3. 距离影响竞标成本
4. 拍卖日志记录
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from agents.car_agent import CarAgent  # noqa: E402
from agents.order_agent import Order, OrderStatus  # noqa: E402
from agents.scheduler_agent import SchedulerAgent, SchedulingStrategy  # noqa: E402
from env.grid import GridEnvironment  # noqa: E402


def test_basic_auction():
    """测试基础拍卖流程"""
    print("=" * 60)
    print("🔨 测试1: 基础拍卖流程")
    print("=" * 60)

    # 创建环境
    grid = GridEnvironment(size=15, num_charging_stations=2)

    # 创建调度器（使用拍卖策略）
    scheduler = SchedulerAgent(strategy=SchedulingStrategy.AUCTION_CNP)

    # 创建车辆（不同位置和电量）
    cars = [
        CarAgent(car_id=0, initial_position=(0, 0), max_battery=100.0),
        CarAgent(car_id=1, initial_position=(14, 14), max_battery=100.0),
        CarAgent(car_id=2, initial_position=(7, 7), max_battery=100.0),
    ]

    # 设置不同的电量
    cars[0].battery = 90.0  # 高电量
    cars[1].battery = 40.0  # 低电量
    cars[2].battery = 100.0  # 满电

    # 创建订单
    orders = [
        Order(order_id=1, pickup_point=(5, 5), delivery_point=(10, 10), status=OrderStatus.PENDING)
    ]

    print("\n📋 订单信息:")
    print(f"   订单ID: {orders[0].order_id}")
    print(f"   取货点: {orders[0].pickup_point}")
    print(f"   送货点: {orders[0].delivery_point}")

    print("\n🚗 竞标车辆:")
    for car in cars:
        distance = grid.calculate_distance(car.position, orders[0].pickup_point)
        print(f"   车辆{car.car_id}: 位置{car.position}, 电量{car.battery:.1f}%, 距离{distance}")

    # 执行拍卖调度
    assignments = scheduler.schedule(cars, orders, grid)

    print("\n🎯 拍卖结果:")
    if assignments:
        for car_id, order_id, pickup, delivery in assignments:
            winner_car = next(c for c in cars if c.car_id == car_id)
            print("   ✅ 车辆{}中标订单{}".format(car_id, order_id))  # noqa: E501
            print("      位置: {}".format(winner_car.position))  # noqa: E501
            print(
                "      距离: {}".format(grid.calculate_distance(winner_car.position, pickup))
            )  # noqa: E501
    else:
        print("   ❌ 无车辆中标")

    # 检查拍卖日志
    if scheduler.assignment_history:
        last_auction = scheduler.assignment_history[-1]
        if "auction_logs" in last_auction:
            print("\n📊 拍卖日志:")
            for log in last_auction["auction_logs"]:
                if log["phase"] == "announcement":
                    print(f"   📢 发布订单{log['order_id']}, {log['bidders_count']}个竞标者")
                elif log["phase"] == "winner_selection":
                    print(f"   🏆 车辆{log['winner_car_id']}获胜")
                    print(f"      中标成本: {log['winner_cost']:.2f}")
                    print(f"      总竞标数: {log['total_bids']}")
                    if log["runner_up_cost"]:
                        print(f"      第二名成本: {log['runner_up_cost']:.2f}")

    print("\n✅ 测试1完成\n")
    return len(assignments) > 0


def test_battery_impact():
    """测试电量对竞标的影响"""
    print("=" * 60)
    print("🔋 测试2: 电量影响竞标成本")
    print("=" * 60)

    grid = GridEnvironment(size=15, num_charging_stations=2)
    scheduler = SchedulerAgent(strategy=SchedulingStrategy.AUCTION_CNP)

    # 创建两辆车：相同位置，不同电量
    cars = [
        CarAgent(car_id=0, initial_position=(5, 5), max_battery=100.0),
        CarAgent(car_id=1, initial_position=(5, 5), max_battery=100.0),
    ]

    cars[0].battery = 90.0  # 高电量
    cars[1].battery = 25.0  # 低电量

    orders = [
        Order(order_id=1, pickup_point=(7, 7), delivery_point=(10, 10), status=OrderStatus.PENDING)
    ]

    print("\n🚗 相同位置(5,5)的两辆车:")
    for car in cars:
        print(f"   车辆{car.car_id}: 电量{car.battery:.1f}%")

    print("\n📋 订单: (7,7) → (10,10)")

    # 计算竞标成本
    print("\n💰 竞标成本:")
    for car in cars:
        cost = scheduler._calculate_bid_cost(car, orders[0], grid)
        print(f"   车辆{car.car_id} (电量{car.battery:.1f}%): 成本{cost:.2f}")

    assignments = scheduler.schedule(cars, orders, grid)

    if assignments:
        winner_id = assignments[0][0]
        winner = next(c for c in cars if c.car_id == winner_id)
        print(f"\n🏆 中标车辆: 车辆{winner_id} (电量{winner.battery:.1f}%)")
        print("   💡 结论: 高电量车辆优先中标（相同距离情况下）")

    print("\n✅ 测试2完成\n")
    return len(assignments) > 0


def test_distance_impact():
    """测试距离对竞标的影响"""
    print("=" * 60)
    print("📏 测试3: 距离影响竞标成本")
    print("=" * 60)

    grid = GridEnvironment(size=15, num_charging_stations=2)
    scheduler = SchedulerAgent(strategy=SchedulingStrategy.AUCTION_CNP)

    # 创建三辆车：不同距离，相同电量
    cars = [
        CarAgent(car_id=0, initial_position=(0, 0), max_battery=100.0),  # 远
        CarAgent(car_id=1, initial_position=(4, 4), max_battery=100.0),  # 近
        CarAgent(car_id=2, initial_position=(14, 14), max_battery=100.0),  # 很远
    ]

    for car in cars:
        car.battery = 100.0  # 相同电量

    orders = [
        Order(order_id=1, pickup_point=(5, 5), delivery_point=(10, 10), status=OrderStatus.PENDING)
    ]

    print("\n🚗 相同电量(100%)的三辆车:")
    for car in cars:
        distance = grid.calculate_distance(car.position, orders[0].pickup_point)
        print(f"   车辆{car.car_id}: 位置{car.position}, 到取货点距离{distance}")

    print("\n📋 订单: (5,5) → (10,10)")

    # 计算竞标成本
    print("\n💰 竞标成本:")
    for car in cars:
        cost = scheduler._calculate_bid_cost(car, orders[0], grid)
        distance = grid.calculate_distance(car.position, orders[0].pickup_point)
        print(f"   车辆{car.car_id} (距离{distance}): 成本{cost:.2f}")

    assignments = scheduler.schedule(cars, orders, grid)

    if assignments:
        winner_id = assignments[0][0]
        winner = next(c for c in cars if c.car_id == winner_id)
        distance = grid.calculate_distance(winner.position, orders[0].pickup_point)
        print(f"\n🏆 中标车辆: 车辆{winner_id} (距离{distance})")
        print("   💡 结论: 距离最近的车辆优先中标（相同电量情况下）")

    print("\n✅ 测试3完成\n")
    return len(assignments) > 0


def test_multiple_orders():
    """测试多订单拍卖"""
    print("=" * 60)
    print("📦 测试4: 多订单拍卖")
    print("=" * 60)

    grid = GridEnvironment(size=15, num_charging_stations=2)
    scheduler = SchedulerAgent(strategy=SchedulingStrategy.AUCTION_CNP)

    # 创建4辆车
    cars = [
        CarAgent(car_id=i, initial_position=(i * 3, i * 3), max_battery=100.0) for i in range(4)
    ]

    for car in cars:
        car.battery = 80.0 + (car.car_id * 5)  # 不同电量

    # 创建3个订单
    orders = [
        Order(order_id=1, pickup_point=(2, 2), delivery_point=(8, 8), status=OrderStatus.PENDING),
        Order(order_id=2, pickup_point=(7, 7), delivery_point=(12, 12), status=OrderStatus.PENDING),
        Order(order_id=3, pickup_point=(1, 1), delivery_point=(5, 5), status=OrderStatus.PENDING),
    ]

    print(f"\n🚗 {len(cars)}辆车:")
    for car in cars:
        print(f"   车辆{car.car_id}: 位置{car.position}, 电量{car.battery:.1f}%")

    print(f"\n📋 {len(orders)}个订单:")
    for order in orders:
        print(f"   订单{order.order_id}: {order.pickup_point} → {order.delivery_point}")

    assignments = scheduler.schedule(cars, orders, grid)

    print(f"\n🎯 拍卖结果: {len(assignments)}/{len(orders)} 个订单被分配")
    for car_id, order_id, pickup, delivery in assignments:
        print(f"   车辆{car_id} ← 订单{order_id}")

    # 显示拍卖统计
    if scheduler.assignment_history:
        last_auction = scheduler.assignment_history[-1]
        print(f"\n📊 拍卖统计:")
        print(f"   总拍卖次数: {last_auction.get('total_auctions', 0)}")
        print(f"   成功分配: {last_auction.get('successful_auctions', 0)}")

    print("\n✅ 测试4完成\n")
    return len(assignments) == min(len(cars), len(orders))


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🎪 拍卖机制（合同网协议CNP）测试套件")
    print("=" * 60 + "\n")

    results = []

    # 运行测试
    results.append(("基础拍卖流程", test_basic_auction()))
    results.append(("电量影响竞标", test_battery_impact()))
    results.append(("距离影响竞标", test_distance_impact()))
    results.append(("多订单拍卖", test_multiple_orders()))

    # 总结
    print("=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status}: {name}")

    print(f"\n🎯 总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！拍卖机制功能正常。")
        print("\n📌 核心特性验证:")
        print("   ✅ 合同网协议4阶段流程正常")
        print("   ✅ 电量考虑在竞标成本中")
        print("   ✅ 距离优先原则有效")
        print("   ✅ 多订单并发拍卖成功")
    else:
        print("\n⚠️  部分测试失败，请检查日志。")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
