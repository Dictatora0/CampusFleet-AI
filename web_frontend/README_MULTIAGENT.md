# 多智能体 Web 界面使用指南

## 新增功能

Web 界面已增强，新增多智能体系统监控面板，包括：

### 1️⃣ **智能体状态面板**

展示所有智能体的实时状态：

- **车辆智能体**: 位置、状态、感知范围、决策方法、行动状态
- **调度智能体**: 策略、总分配次数、活跃车辆数
- **环境智能体**: 网格大小、当前步骤、订单统计

### 2️⃣ **通信日志窗口**

实时显示智能体间的通信消息：

- 车辆状态报告
- 任务分配消息
- 完成通知
- 通信统计数据

### 3️⃣ **协作决策可视化**

展示多车协作情况：

- 当前任务分配
- 车辆利用率
- 并行执行情况
- 决策原因说明

### 4️⃣ **实时性能图表**

系统性能监控：

- 完成率
- 已完成/待处理订单
- 车辆利用率
- 性能等级评定

---

## 快速开始

### 1. 启动后端（新增 API）

```bash
cd web_backend
python main.py
```

后端现在提供 4 个新的 API 端点：

- `GET /api/agents/status` - 获取所有智能体状态
- `GET /api/communication/logs` - 获取通信日志
- `GET /api/collaboration/decisions` - 获取协作决策信息
- `GET /api/performance/metrics` - 获取性能指标

### 2. 启动前端

```bash
cd web_frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 3. 使用多智能体面板

在前端应用中添加路由：

**修改 `src/main.js`** (或创建 router):

```javascript
import MultiAgentDashboard from './views/MultiAgentDashboard.vue'

// 在你的路由配置中添加
{
  path: '/multi-agent',
  component: MultiAgentDashboard
}
```

或直接在`App.vue`中使用：

```vue
<template>
  <div id="app">
    <MultiAgentDashboard />
  </div>
</template>

<script>
import MultiAgentDashboard from "./views/MultiAgentDashboard.vue";

export default {
  components: {
    MultiAgentDashboard,
  },
};
</script>
```

---

## API 接口说明

### 1. 获取智能体状态

**请求**:

```http
GET http://localhost:8001/api/agents/status
```

**响应示例**:

```json
{
  "status": "success",
  "timestamp": "2024-12-04T14:30:00",
  "agents": {
    "vehicles": [
      {
        "id": 0,
        "type": "vehicle",
        "position": [5, 3],
        "status": "busy",
        "current_order": 2,
        "route_length": 5,
        "completed_orders": 3,
        "perception": {
          "can_sense_orders": true,
          "range": 5
        },
        "decision": {
          "method": "A* pathfinding",
          "state": "planning"
        },
        "action": {
          "current": "moving",
          "next_position": [5, 4]
        }
      }
    ],
    "scheduler": {
      "type": "scheduler",
      "strategy": "DQN_INFERENCE",
      "total_assignments": 45,
      "pending_orders": 2,
      "active_vehicles": 3
    },
    "environment": {
      "type": "environment",
      "grid_size": 10,
      "current_step": 120,
      "total_orders": 10,
      "completed_orders": 7
    }
  }
}
```

### 2. 获取通信日志

**请求**:

```http
GET http://localhost:8001/api/communication/logs
```

**响应示例**:

```json
{
  "status": "success",
  "logs": [
    {
      "step": 120,
      "timestamp": "2024-12-04T14:30:00",
      "type": "status_report",
      "sender": "Vehicle-0",
      "receiver": "Scheduler",
      "message": "Position: (5, 3), Status: busy",
      "priority": "normal"
    },
    {
      "step": 120,
      "timestamp": "2024-12-04T14:30:01",
      "type": "task_assignment",
      "sender": "Scheduler",
      "receiver": "Vehicle-1",
      "message": "Assigned Order-5",
      "priority": "high"
    }
  ],
  "total_messages": 45,
  "communication_stats": {
    "status_reports": 4,
    "task_assignments": 2
  }
}
```

### 3. 获取协作决策

**请求**:

```http
GET http://localhost:8001/api/collaboration/decisions
```

**响应示例**:

```json
{
  "status": "success",
  "current_step": 120,
  "assignments": [
    {
      "vehicle_id": 0,
      "order_id": 3,
      "distance_to_pickup": 5,
      "eta_steps": 5,
      "decision_reason": "Optimal assignment"
    }
  ],
  "collaboration_metrics": {
    "vehicle_utilization": 0.75,
    "parallel_execution": 3
  }
}
```

### 4. 获取性能指标

**请求**:

```http
GET http://localhost:8001/api/performance/metrics
```

**响应示例**:

```json
{
  "status": "success",
  "current_step": 120,
  "metrics": {
    "completion_rate": 70.0,
    "completed_orders": 7,
    "total_orders": 10,
    "pending_orders": 1,
    "vehicle_utilization": 75.0
  },
  "performance_grade": "A"
}
```

---

## 界面截图说明

### 顶部统计卡片

- 🚗 车辆智能体：总数和活跃数
- 📦 订单智能体：总数和待处理数
- 📡 通信消息：总数和本轮消息
- 📊 完成率：百分比和性能等级

### 智能体状态面板（左侧）

三个标签页：

1. **车辆智能体** - 显示每辆车的详细状态
2. **调度智能体** - 显示调度策略和统计
3. **环境智能体** - 显示环境信息

### 通信日志窗口（中间）

- 实时滚动显示通信消息
- 按类型区分颜色
- 显示发送方和接收方
- 通信统计数据

### 协作决策可视化（右侧）

- 车辆利用率进度条
- 当前活跃任务分配列表
- 每个分配的距离和 ETA

### 实时性能图表（底部）

- 4 个关键指标统计
- 性能等级评定

---

## 自动刷新

界面每 2 秒自动刷新所有数据，确保实时性。

也可以点击每个面板右上角的"刷新"按钮手动刷新。

---

## 课程作业展示建议

1. **启动系统**：

   ```bash
   # 终端1：后端
   cd web_backend && python main.py

   # 终端2：前端
   cd web_frontend && npm run dev
   ```

2. **创建仿真**：
   通过 API 或 Web 界面创建仿真：

   ```bash
   curl -X POST http://localhost:8001/api/simulation/create \
     -H "Content-Type: application/json" \
     -d '{"grid_size": 10, "num_cars": 4, "strategy": "DQN_INFERENCE"}'
   ```

3. **启动仿真**：

   ```bash
   curl -X POST http://localhost:8001/api/simulation/start
   ```

4. **观察多智能体系统**：

   - 查看车辆智能体的感知、决策、行动
   - 观察通信日志中的消息流
   - 监控协作决策和任务分配
   - 追踪实时性能指标

5. **演示要点**：
   - **智能体角色**：指出 4 类智能体及其职责
   - **感知能力**：展示车辆感知范围和状态
   - **决策方法**：说明 A\*路径规划和调度策略
   - **协作机制**：展示任务分配和车辆利用
   - **通信机制**：展示智能体间的消息传递

---

## 故障排除

### 问题 1：前端无法连接后端

**解决**：

- 确认后端已启动（http://localhost:8001）
- 检查 CORS 配置
- 查看浏览器控制台错误

### 问题 2：数据不更新

**解决**：

- 确认仿真已创建并启动
- 检查 API 响应是否正常
- 刷新页面

### 问题 3：界面显示空白

**解决**：

- 先创建仿真
- 确认 API 返回数据
- 检查 Vue 组件是否正确挂载

---

## 技术栈

**后端**：

- FastAPI 0.104+
- Python 3.10+
- Pydantic

**前端**：

- Vue 3
- Element Plus
- Axios

---

## 下一步扩展

可以添加的功能：

- 📈 ECharts 图表集成
- 🎨 3D 可视化（Three.js）
- 🔔 实时告警系统
- 📊 历史数据分析
- 🎮 交互式控制面板

---

**祝展示成功！** 🚀
