# 🌐 CampusFleet AI Web 部署指南

## 📋 系统架构

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Vue.js 前端   │ ←─────────────────→ │  FastAPI 后端   │
│  (Port: 3000)   │                      │  (Port: 8000)   │
├─────────────────┤                      ├─────────────────┤
│ • 实时可视化    │                      │ • REST API      │
│ • 交互控制      │                      │ • WebSocket     │
│ • 数据展示      │                      │ • 仿真管理      │
└─────────────────┘                      └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │  仿真核心引擎   │
                                         │ • VRP算法       │
                                         │ • MAPF CBS      │
                                         │ • 数据记录      │
                                         └─────────────────┘
```

## 🚀 快速启动

### 1. 后端启动

```bash
# 进入项目目录
cd /Users/lifulin/Desktop/CampusFleet\ AI

# 安装Web后端依赖
pip install -r requirements-web.txt

# 启动FastAPI后端
cd web_backend
python main.py

# 或使用uvicorn直接启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**后端服务地址：**

- 🌐 API 服务: http://localhost:8000
- 📚 API 文档: http://localhost:8000/api/docs
- 🔗 WebSocket: ws://localhost:8000/ws/simulation

### 2. 前端启动

```bash
# 进入前端目录
cd web_frontend

# 安装Node.js依赖
npm install
# 或使用yarn
yarn install

# 启动开发服务器
npm run dev
# 或
yarn dev
```

**前端访问地址：**

- 🖥️ Web 界面: http://localhost:3000
- 📱 移动端: http://localhost:3000 (响应式设计)

## 🎯 功能特性

### 🔧 仿真控制

- ✅ **预设配置**: 小/中/大规模、VRP 演示、MAPF 演示
- ✅ **实时控制**: 启动/停止/单步/重置
- ✅ **策略切换**: 贪心/匈牙利/VRP/MAPF CBS
- ✅ **动态参数**: 网格大小、车辆数量、步进间隔

### 📊 数据可视化

- ✅ **实时网格**: 车辆位置、订单状态、障碍物
- ✅ **路径显示**: 传统路径 vs CBS 协调路径
- ✅ **状态监控**: 电量、载货、任务进度
- ✅ **统计面板**: 完成订单、总距离、效率指标

### 🎮 交互功能

- ✅ **点击选择**: 车辆详情、订单信息
- ✅ **手动创建**: 鼠标点击添加订单
- ✅ **视图切换**: 显示/隐藏路径、网格
- ✅ **实时更新**: WebSocket 推送状态

## 📡 API 接口文档

### 🔄 仿真管理

#### 创建仿真

```http
POST /api/simulation/create
Content-Type: application/json

{
  "grid_size": 15,
  "num_cars": 5,
  "strategy": "MAPF_CBS",
  "enable_logging": true,
  "auto_step_interval": 1.0
}
```

#### 控制仿真

```http
POST /api/simulation/control
Content-Type: application/json

{
  "command": "start",  // start/stop/step/reset
  "params": {
    "auto_step": true
  }
}
```

#### 获取状态

```http
GET /api/simulation/state

Response:
{
  "status": "success",
  "step": 42,
  "is_running": true,
  "vehicles": [...],
  "orders": {...},
  "statistics": {...}
}
```

### 📦 订单管理

#### 创建订单

```http
POST /api/orders/create
Content-Type: application/json

{
  "pickup": [2, 3],
  "delivery": [8, 7]
}
```

### 📈 数据分析

#### 导出数据

```http
GET /api/analytics/export

Response:
{
  "status": "success",
  "format": "csv",
  "data": "step,timestamp,vehicle_id,...",
  "record_count": 1500
}
```

## 🔌 WebSocket 协议

### 连接地址

```
ws://localhost:8000/ws/simulation
```

### 消息格式

#### 服务端 → 客户端

```json
{
  "type": "state_update",
  "data": {
    "step": 42,
    "vehicles": [...],
    "orders": {...},
    "statistics": {...}
  }
}
```

#### 客户端 → 服务端

```json
{
  "type": "ping" // 心跳检测
}
```

## 🛠️ 开发环境配置

### 环境要求

- **Python**: ≥ 3.8
- **Node.js**: ≥ 16.0
- **内存**: ≥ 4GB
- **浏览器**: Chrome/Firefox/Safari (支持 WebSocket)

### 开发工具

```bash
# Python依赖管理
pip install -r requirements-web.txt

# 前端依赖管理
npm install -g @vue/cli
npm install -g vite

# 代码质量检查
pip install black flake8
npm install -g eslint prettier
```

### 调试模式

```bash
# 后端调试模式（自动重载）
uvicorn main:app --reload --log-level debug

# 前端热更新模式
npm run dev -- --mode development
```

## 🌍 生产部署

### 1. 后端生产部署

#### 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements-web.txt .
RUN pip install -r requirements-web.txt

COPY web_backend/ .
COPY core/ core/
COPY agents/ agents/
COPY algorithms/ algorithms/
COPY env/ env/
COPY analytics/ analytics/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name campusfleet.ai;

    # 静态文件
    location / {
        root /var/www/campusfleet-frontend;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket代理
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. 前端生产构建

```bash
# 构建生产版本
npm run build

# 生成文件在 dist/ 目录
ls dist/
# index.html  assets/  favicon.ico
```

## 📊 性能优化

### 后端优化

- ✅ **异步处理**: FastAPI + async/await
- ✅ **连接池**: WebSocket 连接管理
- ✅ **数据压缩**: JSON 响应 gzip 压缩
- ✅ **缓存策略**: 状态数据内存缓存

### 前端优化

- ✅ **代码分割**: Vue Router 懒加载
- ✅ **资源压缩**: Vite 自动优化
- ✅ **CDN 加速**: Element Plus 等库 CDN
- ✅ **PWA 支持**: 离线访问能力

## 🔐 安全考虑

### 生产安全

```python
# 环境变量配置
import os

# CORS配置
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

# API密钥验证
API_KEY = os.getenv("API_KEY")

# WebSocket认证
def authenticate_websocket(websocket):
    # 实现认证逻辑
    pass
```

### 网络安全

- 🔒 **HTTPS**: SSL/TLS 加密传输
- 🛡️ **CORS**: 跨域请求限制
- 🔑 **认证**: JWT Token 验证
- 🚫 **限流**: 请求频率限制

## 📈 监控运维

### 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campusfleet.log'),
        logging.StreamHandler()
    ]
)
```

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/

# WebSocket连接测试
wscat -c ws://localhost:8000/ws/simulation
```

## 🎯 下一步计划

### 即将实现

- 🔄 **用户认证**: 登录/注册系统
- 📊 **高级分析**: 性能对比图表
- 🎮 **游戏模式**: 交互式挑战
- 📱 **移动应用**: React Native 版本

### 长期规划

- 🤖 **AI 助手**: 智能调度建议
- 🌐 **多租户**: 企业级部署
- 📡 **IoT 集成**: 真实设备连接
- ☁️ **云部署**: AWS/Azure 支持

---

🚀 **CampusFleet AI v3.0** - 从桌面应用到现代化 Web 平台的完美蜕变！
