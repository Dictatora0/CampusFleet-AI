# CampusFleet AI 深度改进计划

## 📋 改进概览

本文档详细规划了 CampusFleet AI 系统的四大维度改进方案，旨在从"课程项目"提升至"学术研究级别"。

---

## 🎯 Phase 1: 高优先级改进（2-3 天完成）

### 1.1 充电桩与电量焦虑机制 ✅

**当前状态：**

- ✅ 基础电量系统已实现（battery, consume, charge）
- ✅ 充电站位置初始化（边缘随机生成）
- ❌ 缺少充电站容量管理
- ❌ 缺少智能充电决策
- ❌ Web 前端未可视化充电站

**改进内容：**

1. **充电站容量管理**

   - 新增 `ChargingStation` 类，管理排队队列
   - 每个充电桩同时最多服务 N 辆车（默认 2 辆）
   - 车辆到达已满的充电桩时，加入等待队列或寻找下一个桩

2. **非线性电量消耗模型**

   - 基础消耗：`base_consumption = 1.0`
   - 载货惩罚：`+0.3 * (当前订单数)`
   - 加速惩罚：`+0.2 * (移动速度 - 1)`
   - 最终公式：`total_consumption = base * (1 + 载货系数 + 加速系数)`

3. **智能充电决策**

   - **优先级判断**：
     - `battery < 10%`：立即放弃当前任务，强制充电
     - `battery < 30% && 无任务`：主动寻找最近充电站
     - `battery < 50% && 距充电站很近`：顺路充电
   - **充电站选择算法**：
     - 考虑距离 + 排队人数 + 剩余电量
     - 公式：`score = distance * 1.0 + queue_length * 5.0 + urgency`

4. **Web 前端可视化**
   - Canvas 增加充电站图标（⚡ 或闪电符号）
   - 车辆低电量时改变颜色（黄色 < 30%，红色 < 10%）
   - 鼠标悬停充电站时显示：当前队列、可用充电位

**修改文件：**

- `env/grid.py`：新增 `ChargingStation` 类
- `agents/car_agent.py`：升级电量消耗逻辑、充电决策
- `web_frontend/src/components/SimulationCanvas.vue`：可视化充电站
- `web_backend/main.py`：返回充电站状态（队列信息）

**验证指标：**

- [ ] 车辆电量低于阈值时自动寻找充电站
- [ ] 充电站满载时车辆能正确排队或选择其他桩
- [ ] Web 界面显示充电站及排队情况
- [ ] 日志记录"充电决策事件"

---

### 1.2 合同网拍卖协议（分布式调度） 🎯

**理论基础：**
合同网协议（Contract Net Protocol, CNP）是经典的多智能体协商机制：

1. **Manager** (订单智能体) 发布任务公告
2. **Contractors** (车辆智能体) 计算成本并竞标
3. **Manager** 选择最优报价并授标
4. **Contractor** 执行任务并反馈结果

**实现方案：**

1. **新增拍卖管理器**

   - 文件：`agents/auction_manager.py`
   - 功能：
     - `announce_task(order)`: 广播订单拍卖信息
     - `collect_bids(deadline)`: 收集车辆报价
     - `select_winner(bids)`: 根据策略选择中标者
     - `award_contract(winner, order)`: 分配订单给中标车辆

2. **车辆竞标逻辑**

   - 在 `agents/car_agent.py` 新增方法：
     ```python
     def calculate_bid(self, order: Order) -> float:
         """
         计算竞标价格（成本）
         - 距离成本：distance_to_pickup * 1.0
         - 电量成本：(100 - battery) * 0.5
         - 任务负载：current_task_queue_length * 2.0
         - 返回总成本（越低越优先）
         """
     ```

3. **订单智能体升级**

   - `agents/order_agent.py` 新增：
     - `auction_order(order_id)`: 启动拍卖流程
     - `assign_to_winner(order_id, winner_id)`: 授标后分配

4. **通信日志记录**

   - 新增数据表：`auction_log`
   - 记录字段：
     ```json
     {
       "order_id": 101,
       "auction_time": "2024-12-06 21:00:00",
       "bids": [
         { "car_id": 1, "bid": 5.2, "reason": "距离远" },
         { "car_id": 3, "bid": 3.1, "reason": "最近且电量充足" }
       ],
       "winner": 3,
       "award_time": "2024-12-06 21:00:01"
     }
     ```

5. **Web 前端展示**
   - 新增"拍卖日志"面板，实时显示：
     ```
     订单 #101 拍卖中...
       车辆1 报价: 5.2 (距离8格, 电量60%)
       车辆3 报价: 3.1 (距离3格, 电量90%)  ← 中标
     结果: 车辆3 以成本3.1中标
     ```

**修改文件：**

- `agents/auction_manager.py` [新建]
- `agents/car_agent.py`：新增 `calculate_bid()`
- `agents/order_agent.py`：集成拍卖流程
- `core/context.py`：协调拍卖流程
- `web_backend/main.py`：新增拍卖日志 API
- `web_frontend/src/views/SimulationView.vue`：拍卖日志面板

**验证指标：**

- [ ] 订单发布时触发拍卖
- [ ] 所有空闲车辆参与竞标
- [ ] 日志记录完整拍卖过程
- [ ] Web 界面实时显示拍卖详情

---

### 1.3 OSM 真实地图集成 🗺️

**技术栈：**

- `osmnx`：下载 OpenStreetMap 数据
- `networkx`：图论路径规划
- `folium`：可视化（可选）

**实现步骤：**

1. **地图数据获取**

   ```python
   import osmnx as ox

   # 下载某大学校园的路网数据
   G = ox.graph_from_place("清华大学, 北京, 中国", network_type='drive')
   ox.save_graphml(G, "campus_map.graphml")
   ```

2. **地图转网格映射**

   - 方案 A（简化）：将 OSM 路网栅格化为网格，保留道路拓扑
   - 方案 B（高级）：直接使用图结构，节点=路口，边=道路段

3. **Web 前端底图**

   - 导出 OSM 地图为 SVG/PNG
   - 作为 Canvas 背景图层
   - 车辆/订单坐标映射到真实经纬度

4. **路径规划适配**
   - 使用 `networkx.shortest_path()` 替代 A\*
   - 考虑真实路网的单行线、限速等约束

**修改文件：**

- `env/osm_map.py` [新建]：OSM 数据加载与转换
- `env/grid.py`：兼容图结构环境
- `web_frontend/src/components/SimulationCanvas.vue`：底图渲染
- `config/map_configs.json` [新建]：地图配置文件

**验证指标：**

- [ ] 成功加载真实校园 OSM 数据
- [ ] 车辆在真实路网上移动
- [ ] Web 界面显示真实地图底图
- [ ] 路径规划符合道路拓扑

---

## 🚀 Phase 2: 高级算法改进（1-2 周）

### 2.1 多智能体强化学习（MARL）

**算法选择：QMIX**

- 适用场景：合作型多智能体
- 核心思想：单调性约束（Monotonic Value Function）
- 优势：解决信用分配问题

**实现框架：**

- 使用 `PyTorch` 实现
- 参考论文：[QMIX: Monotonic Value Function Factorisation for Decentralised Multi-Agent Reinforcement Learning](https://arxiv.org/abs/1803.11485)

**文件结构：**

```
rl_agents/
├── qmix/
│   ├── qmix_agent.py      # 单智能体Q网络
│   ├── qmix_mixer.py      # Mixing Network
│   ├── replay_buffer.py   # 经验回放
│   └── trainer.py         # 训练逻辑
```

---

### 2.2 需求预测模块

**模型：LSTM 时序预测**

- 输入：历史订单时空序列（过去 1 小时）
- 输出：未来 15 分钟的订单热力图
- 应用：闲置车辆提前调度到热点区域

**数据准备：**

```python
# 订单历史格式
order_history = [
    {"time": "09:00", "location": (x1, y1)},
    {"time": "09:05", "location": (x2, y2)},
    ...
]

# 预测结果
heatmap = np.array([[0.1, 0.3, ...],  # 15x15网格的订单概率
                     [0.2, 0.8, ...]])
```

---

## 🏗️ Phase 3: 系统架构升级（1-2 周）

### 3.1 Ray 并行化

**改造方案：**

```python
import ray

@ray.remote
class VehicleActor:
    def __init__(self, car_id):
        self.agent = CarAgent(car_id, ...)

    def step(self):
        return self.agent.step()

# 并行执行100辆车
futures = [vehicle.step.remote() for vehicle in vehicles]
results = ray.get(futures)
```

**性能提升：**

- 单进程：100 车辆 → ~5 FPS
- Ray 并行：100 车辆 → ~50 FPS

---

### 3.2 前后端通信优化

**Protobuf 序列化：**

```protobuf
message SimulationState {
  int32 step = 1;
  repeated Vehicle vehicles = 2;
  repeated Order orders = 3;
}
```

**增量更新：**

```python
# 只发送变化的车辆状态
delta = {
    "vehicles_updated": [v1, v3],  # 仅发送移动的车辆
    "orders_new": [o10],           # 新订单
    "orders_completed": [o5, o7]   # 完成的订单
}
```

---

## 🎨 Phase 4: 可视化升级（1 周）

### 4.1 Three.js 3D 场景

**效果预览：**

- 3D 校园建筑模型
- 车辆变成 3D 小车（带动画）
- 鼠标交互（旋转、缩放、点击车辆查看详情）

**技术栈：**

- `Three.js`：3D 渲染引擎
- `Vue3 + Three.js`：组件化封装

---

### 4.2 数据回放系统

**核心功能：**

1. 录制：保存每一步的状态快照
2. 回放：拖动进度条回到任意时刻
3. 分析：叠加热力图、轨迹图

**存储格式：**

```json
{
  "frames": [
    {"step": 0, "vehicles": [...], "orders": [...]},
    {"step": 1, "vehicles": [...], "orders": [...]}
  ]
}
```

---

## 📊 优先级总结

| 功能       | 优先级     | 难度       | 价值       | 耗时 |
| ---------- | ---------- | ---------- | ---------- | ---- |
| 充电桩机制 | ⭐⭐⭐⭐⭐ | ⭐⭐       | ⭐⭐⭐⭐   | 1 天 |
| 拍卖协议   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | 2 天 |
| OSM 地图   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | 2 天 |
| MARL 算法  | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | 1 周 |
| 需求预测   | ⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐⭐⭐     | 3 天 |
| Ray 并行化 | ⭐⭐       | ⭐⭐⭐     | ⭐⭐       | 2 天 |
| 3D 可视化  | ⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | 3 天 |
| 数据回放   | ⭐⭐       | ⭐⭐       | ⭐⭐⭐     | 1 天 |

---

## 🎯 下一步行动

**立即开始实现（按顺序）：**

1. ✅ 充电桩容量管理 + 智能决策
2. ✅ Web 前端可视化充电站
3. ✅ 拍卖协议核心逻辑
4. ✅ OSM 地图集成

**预计完成时间：** 5 天（每天 4-6 小时）

---

## 📝 进度追踪

- [ ] Phase 1.1: 充电桩机制（Day 1）
- [ ] Phase 1.2: 拍卖协议（Day 2-3）
- [ ] Phase 1.3: OSM 地图（Day 4-5）
- [ ] Phase 2: MARL 算法（Week 2）
- [ ] Phase 3: 架构升级（Week 3）
- [ ] Phase 4: 3D 可视化（Week 4）

**当前状态：** 🚀 准备开始 Phase 1.1
