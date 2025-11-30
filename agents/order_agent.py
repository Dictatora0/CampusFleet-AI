"""
订单智能体模块 - 管理订单队列和状态
"""
from typing import Tuple, List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import time


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "待分配"
    ASSIGNED = "已分配"
    IN_TRANSIT = "运输中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


@dataclass
class Order:
    """订单数据类"""
    order_id: int
    pickup_point: Tuple[int, int]
    delivery_point: Tuple[int, int]
    status: OrderStatus
    assigned_car_id: Optional[int] = None
    created_time: float = 0.0
    assigned_time: float = 0.0
    completed_time: float = 0.0
    
    def __post_init__(self):
        if self.created_time == 0.0:
            self.created_time = time.time()


class OrderAgent:
    """订单智能体类 - 负责管理所有订单"""
    
    def __init__(self):
        """初始化订单智能体"""
        self.orders: Dict[int, Order] = {}
        self.next_order_id = 1
        self.pending_orders: List[int] = []  # 待分配订单ID列表
    
    def reset(self):
        """重置订单系统"""
        self.orders.clear()
        self.next_order_id = 1
        self.pending_orders.clear()
    
    def create_order(self, pickup: Tuple[int, int], delivery: Tuple[int, int]) -> int:
        """
        创建新订单
        Args:
            pickup: 取货点坐标
            delivery: 配送点坐标
        Returns:
            订单ID
        """
        order_id = self.next_order_id
        self.next_order_id += 1
        
        order = Order(
            order_id=order_id,
            pickup_point=pickup,
            delivery_point=delivery,
            status=OrderStatus.PENDING
        )
        
        self.orders[order_id] = order
        self.pending_orders.append(order_id)
        
        return order_id
    
    def assign_order(self, order_id: int, car_id: int) -> bool:
        """
        将订单分配给车辆
        Args:
            order_id: 订单ID
            car_id: 车辆ID
        Returns:
            是否成功分配
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status != OrderStatus.PENDING:
            return False
        
        order.status = OrderStatus.ASSIGNED
        order.assigned_car_id = car_id
        order.assigned_time = time.time()
        
        # 从待分配列表中移除
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        
        return True
    
    def update_order_status(self, order_id: int, status: OrderStatus) -> bool:
        """
        更新订单状态
        Args:
            order_id: 订单ID
            status: 新状态
        Returns:
            是否成功更新
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        order.status = status
        
        if status == OrderStatus.COMPLETED:
            order.completed_time = time.time()
        
        return True
    
    def complete_order(self, order_id: int) -> bool:
        """
        标记订单为完成
        Args:
            order_id: 订单ID
        Returns:
            是否成功完成
        """
        return self.update_order_status(order_id, OrderStatus.COMPLETED)
    
    def cancel_order(self, order_id: int) -> bool:
        """
        取消订单
        Args:
            order_id: 订单ID
        Returns:
            是否成功取消
        """
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        return self.update_order_status(order_id, OrderStatus.CANCELLED)
    
    def get_pending_orders(self) -> List[Order]:
        """
        获取所有待分配订单
        Returns:
            待分配订单列表
        """
        return [self.orders[oid] for oid in self.pending_orders if oid in self.orders]
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """
        获取指定订单
        Args:
            order_id: 订单ID
        Returns:
            订单对象，如果不存在则返回None
        """
        return self.orders.get(order_id)
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """
        根据状态获取订单列表
        Args:
            status: 订单状态
        Returns:
            符合状态的订单列表
        """
        return [order for order in self.orders.values() if order.status == status]
    
    def get_orders_by_car(self, car_id: int) -> List[Order]:
        """
        获取分配给指定车辆的所有订单
        Args:
            car_id: 车辆ID
        Returns:
            订单列表
        """
        return [order for order in self.orders.values() 
                if order.assigned_car_id == car_id and order.status != OrderStatus.COMPLETED]
    
    def step(self):
        """
        执行一步更新（检查订单状态等）
        """
        # 这里可以添加订单超时检查、自动取消等逻辑
        pass
    
    def report(self) -> dict:
        """
        报告订单系统状态
        Returns:
            包含订单统计信息的字典
        """
        status_counts = {
            'pending': len([o for o in self.orders.values() if o.status == OrderStatus.PENDING]),
            'assigned': len([o for o in self.orders.values() if o.status == OrderStatus.ASSIGNED]),
            'in_transit': len([o for o in self.orders.values() if o.status == OrderStatus.IN_TRANSIT]),
            'completed': len([o for o in self.orders.values() if o.status == OrderStatus.COMPLETED]),
            'cancelled': len([o for o in self.orders.values() if o.status == OrderStatus.CANCELLED]),
        }
        
        return {
            'total_orders': len(self.orders),
            'pending_orders': len(self.pending_orders),
            'status_counts': status_counts
        }
    
    def get_orders_summary(self) -> str:
        """
        获取订单摘要字符串（用于显示）
        Returns:
            格式化的订单信息字符串
        """
        summary_lines = ["📋 订单状态:"]
        
        if not self.orders:
            summary_lines.append("  暂无订单")
            return "\n".join(summary_lines)
        
        report = self.report()
        status_counts = report['status_counts']
        
        summary_lines.append(f"  总订单数: {report['total_orders']}")
        summary_lines.append(f"  ⏳ 待分配: {status_counts['pending']}")
        summary_lines.append(f"  📌 已分配: {status_counts['assigned']}")
        summary_lines.append(f"  🚚 运输中: {status_counts['in_transit']}")
        summary_lines.append(f"  ✅ 已完成: {status_counts['completed']}")
        
        # 显示待分配订单详情
        if self.pending_orders:
            summary_lines.append("\n  待分配订单:")
            for oid in self.pending_orders[:5]:  # 最多显示5个
                order = self.orders.get(oid)
                if order:
                    summary_lines.append(
                        f"    #{order.order_id}: {order.pickup_point} → {order.delivery_point}"
                    )
        
        # 显示进行中的订单
        active_orders = [o for o in self.orders.values() 
                        if o.status in [OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT]]
        if active_orders:
            summary_lines.append("\n  进行中订单:")
            for order in active_orders[:5]:  # 最多显示5个
                summary_lines.append(
                    f"    #{order.order_id}: 车辆{order.assigned_car_id} - {order.status.value}"
                )
        
        return "\n".join(summary_lines)
