"""
CampusFleet AI - FastAPI Web后端
现代化Web接口，支持实时仿真控制和数据可视化
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import sys
import os
import threading
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core import SimulationContext
from agents import SchedulingStrategy
from analytics import DataLogger


# FastAPI应用实例
app = FastAPI(
    title="CampusFleet AI Web API",
    description="智能校园配送系统 - Web控制接口",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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
        
    def create_simulation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建新仿真"""
        try:
            # 停止现有仿真
            self.stop_simulation()
            
            # 创建仿真上下文
            self.context = SimulationContext(
                grid_size=config.get('grid_size', 15),
                num_cars=config.get('num_cars', 5),
                scheduling_strategy=SchedulingStrategy[config.get('strategy', 'GREEDY_NEAREST')],
                enable_data_logging=config.get('enable_logging', True)
            )
            
            self.step_count = 0
            self.is_running = False
            
            # 初始化数据记录
            if config.get('enable_logging', True):
                self.data_logger = DataLogger()
            
            return {
                "status": "success",
                "message": "仿真创建成功",
                "simulation_id": id(self.context),
                "config": config
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"仿真创建失败: {str(e)}"
            }
    
    def start_simulation(self, auto_step: bool = True) -> Dict[str, Any]:
        """启动仿真"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}
        
        self.is_running = True
        
        if auto_step:
            # 启动自动步进线程
            self.simulation_thread = threading.Thread(
                target=self._auto_step_loop,
                daemon=True
            )
            self.simulation_thread.start()
        
        return {
            "status": "success",
            "message": "仿真已启动",
            "auto_step": auto_step
        }
    
    def stop_simulation(self) -> Dict[str, Any]:
        """停止仿真"""
        self.is_running = False
        
        if self.simulation_thread:
            self.simulation_thread.join(timeout=2.0)
        
        return {
            "status": "success",
            "message": "仿真已停止"
        }
    
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
                frame_data = {
                    'step': self.step_count,
                    'timestamp': datetime.now().isoformat(),
                    'vehicles': [car.report() for car in self.context.cars],
                    'orders': self.context.order_agent.report(),
                    'statistics': self.context.get_statistics()
                }
                self.data_logger.log_frame(frame_data)
            
            # 广播更新到WebSocket客户端
            asyncio.create_task(self._broadcast_state_update())
            
            return {
                "status": "success",
                "step": self.step_count,
                "statistics": self.context.get_statistics()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"仿真步进失败: {str(e)}"
            }
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前仿真状态"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}
        
        return {
            "status": "success",
            "step": self.step_count,
            "is_running": self.is_running,
            "vehicles": [
                {
                    "id": car.car_id,
                    "position": car.position,
                    "state": car.state.value,
                    "battery": car.get_battery_percentage(),
                    "current_order": car.current_order_id,
                    "path": car.current_path[:10] if car.current_path else [],  # 限制路径长度
                    "coordinated": getattr(car, 'use_coordinated_path', False)
                }
                for car in self.context.cars
            ],
            "orders": {
                "pending": [
                    {
                        "id": order.order_id,
                        "pickup": order.pickup_point,
                        "delivery": order.delivery_point,
                        "priority": getattr(order, 'priority', 'normal')
                    }
                    for order in self.context.order_agent.pending_orders
                ],
                "statistics": self.context.order_agent.report()
            },
            "grid": {
                "size": self.context.grid_env.size,
                "obstacles": self._get_obstacles(),
                "charging_stations": self.context.grid_env.charging_stations
            },
            "statistics": self.context.get_statistics(),
            "config": {
                "strategy": self.context.scheduler.strategy.value,
                "grid_size": self.context.grid_env.size,
                "num_cars": len(self.context.cars)
            }
        }
    
    def add_order(self, pickup: List[int], delivery: List[int]) -> Dict[str, Any]:
        """添加新订单"""
        if not self.context:
            return {"status": "error", "message": "仿真未初始化"}
        
        try:
            order = self.context.order_agent.create_order(
                tuple(pickup), tuple(delivery)
            )
            return {
                "status": "success",
                "order": {
                    "id": order.order_id,
                    "pickup": order.pickup_point,
                    "delivery": order.delivery_point
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"订单创建失败: {str(e)}"
            }
    
    def _get_obstacles(self) -> List[List[int]]:
        """获取障碍物位置"""
        obstacles = []
        grid = self.context.grid_env.grid
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell == '#':
                    obstacles.append([j, i])  # 转换为(x,y)坐标
        return obstacles
    
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
        message = json.dumps({
            "type": "state_update",
            "data": state
        })
        
        # 向所有连接的客户端发送消息
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send_text(message)
            except:
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
            "RESTful Control API"
        ]
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
    elif command.command == "stop":
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
    """获取可用的调度策略"""
    return {
        "strategies": [
            {
                "key": "GREEDY_NEAREST",
                "name": "贪心最近策略",
                "description": "为每个订单选择最近的车辆"
            },
            {
                "key": "HUNGARIAN",
                "name": "匈牙利算法",
                "description": "全局最优分配算法"
            },
            {
                "key": "VRP_BATCHING", 
                "name": "VRP拼单策略",
                "description": "车辆路径优化，支持多订单拼单"
            },
            {
                "key": "MAPF_CBS",
                "name": "MAPF CBS协调",
                "description": "冲突感知搜索，全局协调规划"
            }
        ]
    }


@app.get("/api/analytics/export")
async def export_analytics():
    """导出分析数据"""
    if not sim_manager.data_logger:
        raise HTTPException(status_code=400, detail="数据记录未启用")
    
    try:
        # 导出CSV数据
        csv_data = sim_manager.data_logger.export_to_csv()
        return {
            "status": "success",
            "format": "csv",
            "data": csv_data,
            "record_count": len(sim_manager.data_logger.frame_records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据导出失败: {str(e)}")


# ========== WebSocket 端点 ==========

@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时仿真数据推送"""
    await websocket.accept()
    sim_manager.add_websocket_client(websocket)
    
    try:
        # 发送初始状态
        initial_state = sim_manager.get_state()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "data": initial_state
        }))
        
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
                    await websocket.send_text(json.dumps({
                        "type": "state_response",
                        "data": state
                    }))
                    
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
    print("📡 API文档: http://localhost:8001/api/docs")  
    print("🔗 WebSocket: ws://localhost:8001/ws/simulation")
    print("🎯 前端地址: http://localhost:3000 (开发中)")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
