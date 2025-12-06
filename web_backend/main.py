"""
CampusFleet AI - FastAPI Web后端
现代化Web接口，支持实时仿真控制和数据可视化
"""

import asyncio
import json
import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents import SchedulingStrategy  # noqa: E402
from analytics import DataLogger  # noqa: E402
from core import SimulationContext  # noqa: E402

# FastAPI应用实例
app = FastAPI(
    title="CampusFleet AI Web API",
    description="智能校园配送系统 - Web控制接口",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局仿真管理器
class SimulationManager:
    """仿真管理器 - 控制仿真生命周期"""

    def __init__(self):
        self.context: Optional[SimulationContext] = None
        self.is_running = False
        self.step_count = 0
        self.data_logger: Optional[DataLogger] = None
        self.websocket_clients: List[WebSocket] = []
        self.simulation_thread: Optional[threading.Thread] = None
        self.auto_step_interval = 1.0  # 自动步进间隔（秒）
        self.event_loop = None  # 保存事件循环引用

    def create_simulation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建新仿真"""
        try:
            # 停止现有仿真
            self.stop_simulation()

            # 创建仿真上下文
            self.context = SimulationContext(
                grid_size=config.get("grid_size", 15),
                num_cars=config.get("num_cars", 5),
                scheduling_strategy=SchedulingStrategy[config.get("strategy", "GREEDY_NEAREST")],
                enable_data_logging=config.get("enable_logging", True),
            )

            self.step_count = 0
            self.is_running = False

            # 初始化数据记录
            if config.get("enable_logging", True):
                self.data_logger = DataLogger()

            return {
                "status": "success",
                "message": "仿真创建成功",
                "simulation_id": id(self.context),
                "config": config,
            }

        except Exception as e:
            return {"status": "error", "message": f"仿真创建失败: {str(e)}"}

    def start_simulation(self, auto_step: bool = True) -> Dict[str, Any]:
        """启动仿真"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}

        self.is_running = True

        if auto_step:
            # 启动自动步进线程
            self.simulation_thread = threading.Thread(target=self._auto_step_loop, daemon=True)
            self.simulation_thread.start()

        return {"status": "success", "message": "仿真已启动", "auto_step": auto_step}

    def stop_simulation(self) -> Dict[str, Any]:
        """停止仿真"""
        self.is_running = False

        if self.simulation_thread:
            self.simulation_thread.join(timeout=2.0)

        return {"status": "success", "message": "仿真已停止"}

    def step_simulation(self) -> Dict[str, Any]:
        """执行单步仿真"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}

        try:
            # 执行一步
            self.context.step()
            self.step_count += 1

            # 记录数据
            if self.data_logger:
                self.data_logger.log_frame(
                    step=self.step_count,
                    cars=self.context.cars,
                    orders=self.context.order_agent,
                    scheduler=self.context.scheduler,
                )

            # 广播更新到WebSocket客户端（从同步线程安全调度）
            if self.event_loop and self.websocket_clients:
                asyncio.run_coroutine_threadsafe(self._broadcast_state_update(), self.event_loop)

            return {
                "status": "success",
                "step": self.step_count,
                "statistics": self.context.get_statistics(),
            }

        except Exception as e:
            return {"status": "error", "message": f"仿真步进失败: {str(e)}"}

    def get_state(self) -> Dict[str, Any]:
        """获取当前仿真状态"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}

        return {
            "status": "success",
            "step": self.step_count,
            "is_running": self.is_running,
            "strategy": self.context.scheduler.strategy.name,  # 调度策略名称（枚举key）
            "vehicles": [
                {
                    "id": car.car_id,
                    "position": car.position,
                    "state": car.state.value,
                    "battery": car.get_battery_percentage(),
                    "current_order": car.current_order_id,
                    "path": car.current_path[:10] if car.current_path else [],  # 限制路径长度
                    "coordinated": getattr(car, "use_coordinated_path", False),
                }
                for car in self.context.cars
            ],
            "orders": {
                "pending": [
                    {
                        "id": order.order_id,
                        "pickup": order.pickup_point,
                        "delivery": order.delivery_point,
                        "priority": getattr(order, "priority", 1),
                    }
                    for order in self.context.order_agent.get_pending_orders()
                ],
                "statistics": self.context.order_agent.report(),
            },
            "grid": {
                "size": self.context.grid_env.size,
                "obstacles": self._get_obstacles(),
                "charging_stations": self._get_charging_stations_status(),
            },
            "statistics": self.context.get_statistics(),
            "config": {
                "strategy": self.context.scheduler.strategy.name,
                "grid_size": self.context.grid_env.size,
                "num_cars": len(self.context.cars),
            },
        }

    def add_order(self, pickup: List[int], delivery: List[int]) -> Dict[str, Any]:
        """添加新订单"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}

        try:
            order_id = self.context.order_agent.create_order(tuple(pickup), tuple(delivery))
            order = self.context.order_agent.orders.get(order_id)
            return {
                "status": "success",
                "order": {
                    "id": order_id,
                    "pickup": list(order.pickup_point),
                    "delivery": list(order.delivery_point),
                },
            }
        except Exception as e:
            return {"status": "error", "message": f"订单创建失败: {str(e)}"}

    def _get_obstacles(self) -> List[List[int]]:
        """获取障碍物位置"""
        obstacles = []
        grid = self.context.grid_env.grid
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell == "#":
                    obstacles.append([j, i])  # 转换为(x,y)坐标
        return obstacles

    def _get_charging_stations_status(self) -> List[Dict]:
        """
        获取充电站详细状态
        Returns:
            充电站状态列表，包含位置、排队、使用率等信息
        """
        manager = self.context.grid_env.get_charging_station_manager()
        stations_status = []

        for station in manager.stations.values():
            status = station.get_status_summary()
            # 转换为前端友好的格式
            stations_status.append(
                {
                    "id": status["station_id"],
                    "position": list(status["position"]),
                    "capacity": status["capacity"],
                    "available_slots": status["available_slots"],
                    "charging_vehicles": status["charging_vehicles"],
                    "queue_length": status["queue_length"],
                    "waiting_queue": status["waiting_queue"],
                    "utilization_rate": status["utilization_rate"],
                    "total_charged": status["total_charged"],
                }
            )

        return stations_status

    def _auto_step_loop(self):
        """自动步进循环"""
        while self.is_running:
            if self.context:
                self.step_simulation()
            time.sleep(self.auto_step_interval)

    async def _broadcast_state_update(self):
        """向所有WebSocket客户端广播状态更新"""
        if not self.websocket_clients:
            return

        state = self.get_state()
        message = json.dumps({"type": "state_update", "data": state})

        # 向所有连接的客户端发送消息
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send_text(message)
            except Exception:
                disconnected_clients.append(client)

        # 清理断开的连接
        for client in disconnected_clients:
            self.websocket_clients.remove(client)

    def add_websocket_client(self, websocket: WebSocket):
        """添加WebSocket客户端"""
        self.websocket_clients.append(websocket)

    def remove_websocket_client(self, websocket: WebSocket):
        """移除WebSocket客户端"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)


# 全局仿真管理器实例
sim_manager = SimulationManager()


# Pydantic模型定义
class SimulationConfig(BaseModel):
    grid_size: int = 15
    num_cars: int = 5
    strategy: str = "GREEDY_NEAREST"
    enable_logging: bool = True
    auto_step_interval: float = 1.0


class OrderCreate(BaseModel):
    pickup: List[int]  # [x, y]
    delivery: List[int]  # [x, y]


class ControlCommand(BaseModel):
    command: str  # "start", "stop", "step", "reset"
    params: Optional[Dict[str, Any]] = None


# ========== REST API 端点 ==========


@app.get("/")
async def root():
    """API根端点"""
    return {
        "message": "CampusFleet AI Web Backend",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "VRP Multi-Order Batching",
            "MAPF CBS Coordination",
            "Real-time WebSocket Updates",
            "RESTful Control API",
        ],
    }


@app.post("/api/simulation/create")
async def create_simulation(config: SimulationConfig):
    """创建新仿真"""
    result = sim_manager.create_simulation(config.dict())

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.get("/api/simulation/state")
async def get_simulation_state():
    """获取仿真状态"""
    result = sim_manager.get_state()

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.post("/api/simulation/control")
async def control_simulation(command: ControlCommand):
    """仿真控制"""
    if command.command == "start":
        auto_step = command.params.get("auto_step", True) if command.params else True
        result = sim_manager.start_simulation(auto_step)
    elif command.command == "stop" or command.command == "pause":
        result = sim_manager.stop_simulation()
    elif command.command == "step":
        result = sim_manager.step_simulation()
    elif command.command == "reset":
        result = sim_manager.stop_simulation()
        # 重新创建仿真
        if command.params:
            config = SimulationConfig(**command.params)
            result = sim_manager.create_simulation(config.dict())
    else:
        raise HTTPException(status_code=400, detail=f"未知命令: {command.command}")

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.post("/api/orders/create")
async def create_order(order: OrderCreate):
    """创建新订单"""
    result = sim_manager.add_order(order.pickup, order.delivery)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.get("/api/strategies")
async def get_strategies():
    """获取可用的调度策略（课程实验版 - 3个核心AI策略）"""
    return {
        "strategies": [
            {
                "key": "GREEDY_NEAREST",
                "name": "贪心最近算法",
                "description": "启发式算法 - 为每个订单选择最近的车辆",
                "category": "启发式",
            },
            {
                "key": "AUCTION_CNP",
                "name": "拍卖机制(CNP)",
                "description": "多智能体协商 - 合同网协议车辆竞标",
                "category": "多智能体",
            },
            {
                "key": "RL_SCHEDULER",
                "name": "强化学习调度",
                "description": "深度强化学习 - DQN/PPO智能决策",
                "category": "深度学习",
            },
        ]
    }


@app.get("/api/auction/logs")
async def get_auction_logs():
    """获取拍卖日志"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    scheduler = sim_manager.context.scheduler

    # 获取最近的拍卖历史
    auction_history = []
    if hasattr(scheduler, "assignment_history") and scheduler.assignment_history:
        # 获取最近10条记录
        recent_history = scheduler.assignment_history[-10:]

        for record in recent_history:
            if "auction_logs" in record:
                auction_history.append(
                    {
                        "timestamp": record.get("timestamp", ""),
                        "strategy": record.get("strategy", ""),
                        "total_auctions": record.get("total_auctions", 0),
                        "successful_auctions": record.get("successful_auctions", 0),
                        "logs": record.get("auction_logs", []),
                    }
                )

    return {
        "status": "success",
        "auction_history": auction_history,
        "total_records": len(auction_history),
    }


@app.get("/api/analytics/export")
async def export_analytics():
    """导出分析数据（返回CSV字符串）"""
    if not sim_manager.data_logger:
        raise HTTPException(status_code=400, detail="数据记录未启用")

    try:
        # 导出CSV数据为字符串
        csv_data = sim_manager.data_logger.export_to_csv_string()
        return {
            "status": "success",
            "format": "csv",
            "data": csv_data,
            "record_count": len(sim_manager.data_logger.frame_data),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据导出失败: {str(e)}")


@app.get("/api/simulation/status")
async def get_simulation_status():
    """获取仿真状态（兼容端点）"""
    return await get_simulation_state()


@app.post("/api/orders/add")
async def add_order(order: OrderCreate):
    """添加订单（兼容端点）"""
    return await create_order(order)


@app.post("/api/orders/random")
async def add_random_order():
    """添加随机订单（确保不在障碍物上）"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    import random

    grid_size = sim_manager.context.grid_env.size
    grid = sim_manager.context.grid_env.grid

    def is_obstacle(x, y):
        """检查位置是否为障碍物"""
        return grid[x][y] == "#"

    def get_valid_position():
        """生成一个不在障碍物上的随机位置"""
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)
            if not is_obstacle(x, y):
                return (x, y)
        # 如果100次都没找到，返回第一个非障碍物位置
        for x in range(grid_size):
            for y in range(grid_size):
                if not is_obstacle(x, y):
                    return (x, y)
        raise HTTPException(status_code=500, detail="无法找到有效位置，地图可能被障碍物填满")

    pickup = get_valid_position()
    delivery = get_valid_position()

    # 确保取货点和送货点不同
    while pickup == delivery:
        delivery = get_valid_position()

    result = sim_manager.add_order(pickup, delivery)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.get("/api/orders")
async def get_all_orders():
    """获取所有订单"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    orders = []
    for order in sim_manager.context.order_agent.orders.values():
        orders.append(
            {
                "id": order.order_id,
                "status": order.status.name,
                "pickup": list(order.pickup_point),
                "delivery": list(order.delivery_point),
                "assigned_vehicle": None,  # 需要通过车辆查找
                "priority": 1,
            }
        )

    return {"status": "success", "orders": orders, "total": len(orders)}


@app.get("/api/vehicles")
async def get_all_vehicles():
    """获取所有车辆"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    vehicles = []
    for car in sim_manager.context.cars:
        completed = getattr(car, "completed_orders", 0)
        vehicles.append(
            {
                "id": car.car_id,
                "position": list(car.position),
                "state": car.state.value if hasattr(car.state, "value") else str(car.state),
                "battery": getattr(car, "battery", 100),
                "current_order": getattr(car, "current_order_id", None),
                "completed_orders": completed if isinstance(completed, int) else len(completed),
            }
        )

    return {"status": "success", "vehicles": vehicles, "total": len(vehicles)}


@app.post("/api/simulation/step")
async def step_simulation(steps: int = 1):
    """执行仿真步骤"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    for _ in range(steps):
        result = sim_manager.step_simulation()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "success", "current_step": sim_manager.step_count, "steps_executed": steps}


# ========== 多智能体系统增强API ==========


@app.get("/api/agents/status")
async def get_agents_status():
    """获取所有智能体状态（用于智能体状态面板）"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    # 车辆智能体状态
    vehicles = []
    for car in sim_manager.context.cars:
        vehicle_status = {
            "id": car.car_id,
            "type": "vehicle",
            "position": list(car.position),
            "status": "idle" if car.is_idle() else "busy",
            "current_order": car.current_order_id if hasattr(car, "current_order_id") else None,
            "route_length": len(car.current_path)
            if hasattr(car, "current_path") and car.current_path
            else 0,
            "completed_orders": car.completed_orders
            if isinstance(getattr(car, "completed_orders", 0), int)
            else len(getattr(car, "completed_orders", [])),
            "perception": {
                "can_sense_orders": True,
                "range": 5,
            },
            "decision": {
                "method": "A* pathfinding",
                "state": "planning"
                if hasattr(car, "current_path") and car.current_path
                else "waiting",
            },
            "action": {
                "current": "moving" if not car.is_idle() else "idle",
                "next_position": car.current_path[0]
                if hasattr(car, "current_path") and car.current_path
                else None,
            },
        }
        vehicles.append(vehicle_status)

    # 订单智能体状态
    orders = []
    for order in sim_manager.context.order_agent.orders.values():
        order_status = {
            "id": order.order_id,
            "type": "order",
            "status": order.status.name,
            "pickup": list(order.pickup_point),
            "delivery": list(order.delivery_point),
        }
        orders.append(order_status)

    # 调度智能体状态
    scheduler = {
        "type": "scheduler",
        "strategy": sim_manager.context.scheduler.strategy.name
        if hasattr(sim_manager.context.scheduler, "strategy")
        else "GREEDY_NEAREST",
        "total_assignments": sim_manager.step_count,
        "pending_orders": len(
            [
                o
                for o in sim_manager.context.order_agent.orders.values()
                if o.status.name == "PENDING"
            ]
        ),
        "active_vehicles": len([c for c in sim_manager.context.cars if not c.is_idle()]),
    }

    # 环境智能体状态
    environment = {
        "type": "environment",
        "grid_size": sim_manager.context.grid_env.size,
        "current_step": sim_manager.step_count,
        "total_orders": len(sim_manager.context.order_agent.orders),
        "completed_orders": len(
            [
                o
                for o in sim_manager.context.order_agent.orders.values()
                if o.status.name == "COMPLETED"
            ]
        ),
    }

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "vehicles": vehicles,
            "orders": orders,
            "scheduler": scheduler,
            "environment": environment,
        },
    }


@app.get("/api/communication/logs")
async def get_communication_logs():
    """获取智能体通信日志（用于通信日志窗口）"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    logs = []
    current_step = sim_manager.step_count

    # 车辆状态报告
    for car in sim_manager.context.cars:
        logs.append(
            {
                "step": current_step,
                "timestamp": datetime.now().isoformat(),
                "type": "status_report",
                "sender": f"Vehicle-{car.car_id}",
                "receiver": "Scheduler",
                "message": (
                    f"Position: {car.position}, " f"Status: {'idle' if car.is_idle() else 'busy'}"
                ),
                "priority": "normal",
            }
        )

    # 任务分配消息
    for car in sim_manager.context.cars:
        if not car.is_idle() and car.current_order_id:
            logs.append(
                {
                    "step": current_step,
                    "timestamp": datetime.now().isoformat(),
                    "type": "task_assignment",
                    "sender": "Scheduler",
                    "receiver": f"Vehicle-{car.car_id}",
                    "message": f"Assigned Order-{car.current_order_id}",
                    "priority": "high",
                }
            )

    return {
        "status": "success",
        "logs": logs[-20:],
        "total_messages": len(logs),
        "communication_stats": {
            "status_reports": len([log for log in logs if log["type"] == "status_report"]),
            "task_assignments": len([log for log in logs if log["type"] == "task_assignment"]),
        },
    }


@app.get("/api/collaboration/decisions")
async def get_collaboration_decisions():
    """获取协作决策信息（用于协作决策可视化）"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    assignments = []
    for car in sim_manager.context.cars:
        if not car.is_idle() and car.current_order_id:
            # 通过 order_id 查找订单对象
            order = sim_manager.context.order_agent.orders.get(car.current_order_id)
            if order:
                distance = abs(order.pickup_point[0] - car.position[0]) + abs(
                    order.pickup_point[1] - car.position[1]
                )

                assignments.append(
                    {
                        "vehicle_id": car.car_id,
                        "order_id": order.order_id,
                        "distance_to_pickup": distance,
                        "eta_steps": len(car.current_path)
                        if hasattr(car, "current_path") and car.current_path
                        else 0,
                        "decision_reason": "Optimal assignment",
                    }
                )

    active_vehicles = len([c for c in sim_manager.context.cars if not c.is_idle()])
    total_vehicles = len(sim_manager.context.cars)

    return {
        "status": "success",
        "current_step": sim_manager.step_count,
        "assignments": assignments,
        "collaboration_metrics": {
            "vehicle_utilization": active_vehicles / total_vehicles if total_vehicles > 0 else 0,
            "parallel_execution": active_vehicles,
        },
    }


@app.get("/api/performance/metrics")
async def get_performance_metrics():
    """获取实时性能指标（用于实时性能图表）"""
    if not sim_manager.context:
        raise HTTPException(status_code=400, detail="仿真未创建")

    total_orders = len(sim_manager.context.order_agent.orders)
    completed_orders = len(
        [o for o in sim_manager.context.order_agent.orders.values() if o.status.name == "COMPLETED"]
    )
    pending_orders = len(
        [o for o in sim_manager.context.order_agent.orders.values() if o.status.name == "PENDING"]
    )

    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0

    return {
        "status": "success",
        "current_step": sim_manager.step_count,
        "metrics": {
            "completion_rate": round(completion_rate, 2),
            "completed_orders": completed_orders,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "vehicle_utilization": round(
                len([c for c in sim_manager.context.cars if not c.is_idle()])
                / len(sim_manager.context.cars)
                * 100,
                2,
            ),
        },
        "performance_grade": "A" if completion_rate > 60 else "B" if completion_rate > 40 else "C",
    }


# ========== WebSocket 端点 ==========


@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时仿真数据推送"""
    await websocket.accept()

    # 保存事件循环引用（用于从同步线程调度异步任务）
    if sim_manager.event_loop is None:
        sim_manager.event_loop = asyncio.get_event_loop()

    sim_manager.add_websocket_client(websocket)

    try:
        # 发送初始状态
        initial_state = sim_manager.get_state()
        await websocket.send_text(json.dumps({"type": "initial_state", "data": initial_state}))

        # 保持连接并处理客户端消息
        while True:
            try:
                # 等待客户端消息（心跳、命令等）
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "get_state":
                    state = sim_manager.get_state()
                    await websocket.send_text(json.dumps({"type": "state_response", "data": state}))

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket错误: {e}")
                break

    finally:
        sim_manager.remove_websocket_client(websocket)


if __name__ == "__main__":
    import uvicorn

    print("🌐 启动CampusFleet AI Web后端...")
    print("=" * 50)
    print(" API文档: http://localhost:8001/api/docs")
    print(" WebSocket: ws://localhost:8001/ws/simulation")
    print(" 前端地址: http://localhost:3000 (开发中)")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
