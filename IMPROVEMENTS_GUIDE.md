# 系统改进指南

本文档详细说明了针对校园无人配送车多智能体系统的所有改进措施。

## 📋 改进概览

本次改进主要集中在以下四个方面：

1. **Priority High: 数据导出和分析功能** ✅
2. **Priority High: 死锁/活锁处理机制** ✅
3. **Priority Medium: 电量系统和充电站** ✅
4. **Priority Low: Pygame 可视化界面** ✅

---

## 1️⃣ 数据导出和分析功能

### 核心功能

#### 数据记录 (`analytics/data_logger.py`)

- **帧数据记录**: 每一步记录系统整体状态
- **车辆位置追踪**: 记录每辆车的实时位置和状态
- **订单事件日志**: 记录订单创建、分配、完成等事件
- **调度事件日志**: 记录每次调度决策

#### CSV 导出

自动导出以下文件：

- `simulation_frames_*.csv`: 系统每帧的整体统计
- `simulation_cars_*.csv`: 车辆位置和状态历史
- `simulation_orders_*.csv`: 订单事件日志
- `simulation_scheduler_*.csv`: 调度事件记录
- `simulation_metadata_*.json`: 仿真元数据

#### 数据可视化 (`analytics/visualization.py`)

自动生成以下图表：

1. **订单完成率曲线图**

   - 显示待分配、已分配、已完成订单随时间的变化

2. **效率指标图**

   - 订单完成效率 (订单数/步数)
   - 车辆利用率 (活跃车辆/总车辆)

3. **距离统计图**

   - 每辆车的总行驶距离柱状图
   - 距离累积曲线

4. **交通热力图**

   - 显示地图上哪些位置被访问最频繁
   - 帮助识别拥堵点

5. **订单等待时间分布**
   - 直方图显示等待时间分布
   - 箱型图展示统计特征

### 使用方法

```python
from core import SimulationContext

# 初始化时启用数据记录
context = SimulationContext(enable_data_logging=True)

# 运行仿真...
# 仿真结束后导出数据
exported_files = context.export_data()

# 生成可视化图表
from analytics import DataVisualizer
visualizer = DataVisualizer()
visualizer.generate_all_plots(frames_csv, cars_csv, orders_csv, grid_size)
```

### 实验价值

- **性能对比**: 比较不同调度策略的效率
- **瓶颈分析**: 通过热力图识别系统瓶颈
- **优化依据**: 基于数据做出系统优化决策

---

## 2️⃣ 死锁/活锁处理机制

### 问题分析

**原有问题**:

- 车辆仅通过 ID 优先级决定让路
- 狭窄路段迎面相遇会陷入僵局
- 三辆车循环等待造成死锁
- 反复重规划路径导致活锁

### 改进措施

#### 死锁检测 (`agents/car_agent.py`)

```python
# 新增属性
self.stuck_counter = 0  # 被卡住计数器
self.max_stuck_time = 10  # 死锁阈值
self.last_position = initial_position  # 位置追踪
```

**检测机制**:

- 每步比较当前位置与上一步位置
- 如果位置未变化，`stuck_counter++`
- 超过阈值触发死锁恢复模式

#### 死锁恢复策略

实现了三层恢复策略：

**策略 1: 随机移动破坏循环**

```python
# 随机选择一个可用相邻位置移动
available_neighbors = [pos for pos in neighbors if pos not in other_car_positions]
if available_neighbors:
    random_pos = random.choice(available_neighbors)
    # 移动到随机位置，打破死锁循环
```

**策略 2: 随机等待避免同步**

```python
# 30%概率主动等待，避免所有车同步移动
if random.random() < 0.3:
    self.stuck_counter = max(0, self.stuck_counter - 2)
```

**策略 3: 完全重置路径规划**

```python
# 忽略其他车辆，尝试找到任何可行路径
self.plan_path(target, pathfinder, set())
```

#### 状态可视化

- 死锁恢复模式下显示 ⚠️ 图标
- 便于观察和调试死锁情况

### 实验价值

- 对比"反应式避障"与"死锁恢复"的效率差异
- 测试系统在高密度场景下的鲁棒性
- 验证随机策略打破确定性死锁的有效性

---

## 3️⃣ 电量系统和充电站机制

### 系统设计

#### 电量模型 (`agents/car_agent.py`)

```python
# 电量系统参数
self.max_battery = 100.0  # 最大电量
self.battery = max_battery  # 当前电量
self.battery_consumption_rate = 1.0  # 每格消耗
self.low_battery_threshold = 20.0  # 低电量阈值
self.critical_battery_threshold = 10.0  # 严重低电
self.charging_rate = 5.0  # 充电速度
```

**电量消耗**:

- 每移动一格消耗 `battery_consumption_rate` 电量
- 空闲和等待不消耗电量
- 充电状态每步恢复 `charging_rate` 电量

#### 充电站管理 (`env/grid.py`)

```python
# 在地图边缘初始化充电站
self.charging_stations: List[Tuple[int, int]] = []
self._initialize_charging_stations(num_charging_stations)
```

**充电站选择**:

- 优先在地图边缘放置（模拟停车场）
- 可配置数量
- 自动计算最近充电站

#### 充电策略 (`core/context.py`)

**严重低电强制充电**:

```python
if car.is_critical_battery() and car.state.name not in ['MOVING_TO_CHARGE', 'CHARGING']:
    nearest_station = self.grid_env.get_nearest_charging_station(car.position)
    if nearest_station:
        # 取消当前任务
        if car.current_order_id:
            self.order_agent.cancel_order(car.current_order_id)
        car.start_charging(nearest_station)
```

**调度时考虑电量**:

```python
# 只分配任务给电量充足的车辆
idle_cars = [car for car in cars if car.is_available_for_task()]
```

### 新增状态

- `CHARGING`: 充电中
- `MOVING_TO_CHARGE`: 前往充电站

### 可视化增强

- 电量条显示（绿色>50%，黄色 20-50%，红色<20%）
- 充电站标记为 'C'
- 充电中车辆显示 🔋 图标

### 实验价值

- **复杂度提升**: 调度器需要权衡任务分配和充电需求
- **真实性增强**: 更接近实际无人配送场景
- **优化空间**: 可以研究最优充电站布局和充电策略

---

## 4️⃣ Pygame 可视化界面

### 功能特性

#### 图形化显示 (`visualization/pygame_viewer.py`)

**地图渲染**:

- 道路：白色
- 建筑：灰色
- 充电站：金色圆圈标记 'C'
- 网格线：浅灰色

**车辆显示**:

- 根据状态显示不同颜色：
  - 空闲：绿色
  - 前往取货：蓝色
  - 配送中：橙色
  - 充电：黄色
  - 低电量：红色
- 底部显示电量条（颜色编码）
- 车辆 ID 标注在中心

**订单标记**:

- 取货点：浅蓝色圆点
- 配送点：粉色圆点

**信息面板**:

- 系统状态摘要
- 车辆状态列表
- 实时电量显示

**顶部栏**:

- 系统标题
- 调度策略
- 充电站数量

### 使用方法

#### 方式 1: 使用 GUI 脚本

```bash
python run_with_gui.py
```

#### 方式 2: 集成到代码

```python
from core import SimulationContext
from visualization import PygameViewer

context = SimulationContext(grid_size=15, num_cars=3)
viewer = PygameViewer(grid_size=15, cell_size=40, fps=10)

while running:
    if not viewer.handle_events():
        break
    context.step()
    viewer.render(context)

viewer.close()
```

### 控制说明

- **ESC**: 退出仿真
- **关闭窗口**: 退出仿真

### 优势

- **直观性**: 一目了然观察车辆移动和订单状态
- **调试便利**: 快速发现死锁和路径问题
- **演示效果**: 适合演示和汇报

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

必需依赖：

- `scipy`: 匈牙利算法
- `numpy`: 数据处理
- `pandas`: 数据分析
- `matplotlib`: 图表生成
- `pygame`: 图形界面（可选）

### 2. 运行仿真

#### ASCII 界面模式（原有）

```bash
python main.py
```

#### 图形界面模式（新增）

```bash
python run_with_gui.py
```

### 3. 查看结果

仿真结束后：

- CSV 文件保存在 `simulation_logs/` 目录
- 图表保存在 `simulation_logs/` 目录
- 包含 PNG 格式的各类统计图表

---

## 📊 实验建议

### 对比实验 1: 调度策略对比

```python
strategies = [
    SchedulingStrategy.GREEDY_NEAREST,
    SchedulingStrategy.BALANCED_LOAD,
    SchedulingStrategy.HUNGARIAN
]

for strategy in strategies:
    context = SimulationContext(strategy=strategy)
    # 运行仿真并记录数据
    # 对比完成订单数、总距离、等待时间
```

### 对比实验 2: 电量影响

```python
# 不同电池容量
for max_battery in [50, 100, 200]:
    car = CarAgent(car_id=0, position=(0,0), max_battery=max_battery)
    # 测试充电频率和效率影响
```

### 对比实验 3: 充电站布局

```python
# 不同充电站数量
for num_stations in [1, 2, 4]:
    context = SimulationContext(num_charging_stations=num_stations)
    # 分析充电等待时间和系统效率
```

---

## 🔬 代码架构

```
CampusFleet AI/
├── analytics/              # 新增：数据分析模块
│   ├── data_logger.py     # 数据记录器
│   └── visualization.py   # 可视化生成器
├── visualization/          # 新增：图形界面模块
│   └── pygame_viewer.py   # Pygame渲染器
├── agents/
│   ├── car_agent.py       # 改进：电量+死锁处理
│   ├── order_agent.py     # 改进：取消订单
│   └── scheduler_agent.py # 改进：考虑电量
├── core/
│   ├── context.py         # 改进：充电管理
│   └── simulation.py      # 改进：数据导出
├── env/
│   └── grid.py           # 改进：充电站
├── run_with_gui.py       # 新增：GUI启动脚本
└── simulation_logs/      # 新增：数据导出目录
```

---

## ⚠️ 注意事项

1. **依赖安装**: 确保所有依赖已正确安装

   ```bash
   pip install scipy numpy pandas matplotlib pygame
   ```

2. **Pygame 可选**: 如果不需要图形界面，可以不安装 pygame

3. **性能**:

   - 数据记录会略微降低性能
   - 可通过 `enable_data_logging=False` 禁用

4. **文件管理**:
   - CSV 文件会自动带时间戳
   - 定期清理 `simulation_logs/` 目录

---

## 📈 后续扩展建议

### 算法改进

- 实现 Time-space A\*路径规划
- 引入 CBS (Conflict-Based Search)
- 多订单拼单逻辑（VRP 问题）

### 功能扩展

- 不同地形移动代价（加权图）
- 载重限制和容量约束
- 动态订单生成（泊松过程）

### 可视化增强

- 实时路径显示
- 3D 可视化
- Web 界面（使用 Flask/FastAPI）

### LLM 集成

- 自然语言订单生成
- 智能异常处理决策
- 动态策略调整

---

## 📝 总结

本次改进显著提升了系统的：

1. **实验价值**: 通过数据分析支持科学实验
2. **鲁棒性**: 死锁处理机制大幅提升系统稳定性
3. **真实性**: 电量系统使仿真更接近实际场景
4. **易用性**: 图形界面降低使用门槛

所有改进均已集成到主系统，保持向后兼容，可以作为高质量的实验作业提交。
