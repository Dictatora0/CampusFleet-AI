# 项目结构详解

## 📂 目录树

```
CampusFleet AI/
├── agents/                     # 智能体模块
│   ├── __init__.py            # 模块初始化
│   ├── car_agent.py           # 🚗 车辆智能体
│   ├── order_agent.py         # 📦 订单智能体
│   └── scheduler_agent.py     # 📋 调度智能体
│
├── env/                        # 环境模块
│   ├── __init__.py            # 模块初始化
│   ├── grid.py                # 🗺️ 网格地图环境
│   └── pathfinding.py         # 🧭 路径规划（A*算法）
│
├── core/                       # 核心模块
│   ├── __init__.py            # 模块初始化
│   ├── context.py             # 🎯 仿真上下文管理
│   └── simulation.py          # ⚙️ 仿真主循环控制
│
├── main.py                     # 🚀 主程序入口
├── requirements.txt            # 📦 依赖列表
├── .gitignore                 # Git忽略配置
│
├── README.md                   # 📖 项目说明
├── QUICKSTART.md              # 🚀 快速启动
├── EXAMPLES.md                # 📝 使用示例
└── PROJECT_STRUCTURE.md       # 📂 本文件
```

## 🧩 模块详解

### 1. agents/ - 智能体模块

#### car_agent.py - 车辆智能体

**职责：** 车辆行为控制

**关键类：**

- `CarAgent` - 车辆智能体主类
- `CarState` - 车辆状态枚举

**核心功能：**

- ✅ 任务接收与管理
- ✅ A\* 路径规划
- ✅ 移动与导航
- ✅ 避碰检测
- ✅ 状态转换（空闲 → 取货 → 配送 → 完成）
- ✅ 统计信息记录

**关键方法：**

```python
assign_task(order_id, pickup, delivery)  # 分配任务
plan_path(target, pathfinder)            # 规划路径
step(pathfinder, other_positions)        # 执行移动
handle_collision(other_car_id)           # 处理冲突
report()                                 # 报告状态
```

#### order_agent.py - 订单智能体

**职责：** 订单生命周期管理

**关键类：**

- `OrderAgent` - 订单管理器
- `Order` - 订单数据类
- `OrderStatus` - 订单状态枚举

**核心功能：**

- ✅ 订单创建
- ✅ 订单分配
- ✅ 状态跟踪（待分配 → 已分配 → 运输中 → 已完成）
- ✅ 订单查询
- ✅ 统计报告

**关键方法：**

```python
create_order(pickup, delivery)           # 创建订单
assign_order(order_id, car_id)          # 分配订单
complete_order(order_id)                # 完成订单
get_pending_orders()                    # 获取待分配订单
report()                                # 生成报告
```

#### scheduler_agent.py - 调度智能体

**职责：** 订单与车辆匹配

**关键类：**

- `SchedulerAgent` - 调度器
- `SchedulingStrategy` - 调度策略枚举

**调度策略：**

1. **贪心最近（GREEDY_NEAREST）**

   - 为每个订单选择最近的空闲车辆
   - 快速响应，适合实时调度

2. **负载均衡（BALANCED_LOAD）**

   - 优先分配给完成订单少的车辆
   - 确保工作量均衡分配

3. **匈牙利算法（HUNGARIAN）**
   - 预留接口，可扩展为最优匹配
   - 适合批量订单优化

**关键方法：**

```python
schedule(cars, orders, grid_env)         # 执行调度
_greedy_nearest_schedule()              # 贪心策略
_balanced_load_schedule()               # 负载均衡策略
set_strategy(strategy)                  # 切换策略
```

### 2. env/ - 环境模块

#### grid.py - 网格环境

**职责：** 地图管理与显示

**关键类：**

- `GridEnvironment` - 网格环境管理器

**核心功能：**

- ✅ 地图创建（障碍物、道路）
- ✅ 车辆位置追踪
- ✅ 位置有效性检查
- ✅ ASCII 动画显示
- ✅ 距离计算

**地图布局：**

```
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
0 . . . . . . . . . . . . . . .
1 . # # # . . . . . . . # # # .
2 . # # # . . . . . . . # # # .
3 . # # # . . . . . . . # # # .
4 . . . . . . . . . . . . . . .
5 . . . . . # # # # # . . . . .
6 . . . . . # # # # # . . . . .
7 . . . . . # # # # # . . . . .
8 . . . . . # # # # # . . . . .
9 . . . . . # # # # # . . . . .
0 . . . . . . . . . . . . . . .
1 . # # # . . . . . . . # # # .
2 . # # # . . . . . . . # # # .
3 . # # # . . . . . . . # # # .
4 . . . . . . . . . . . . . . .
```

**关键方法：**

```python
is_valid_position(pos)                  # 检查位置有效性
update_vehicle_position(id, pos)        # 更新车辆位置
display(orders_info, step_info)         # 显示状态
get_random_road_position()              # 获取随机道路位置
calculate_distance(pos1, pos2)          # 计算距离
```

#### pathfinding.py - 路径规划

**职责：** 路径搜索算法

**关键类：**

- `PathFinding` - 路径规划器

**核心算法：**

1. **A\* 算法**

   - 启发式搜索
   - 曼哈顿距离作为启发函数
   - 考虑动态障碍（其他车辆）

2. **BFS 算法**
   - 广度优先搜索
   - 备用算法

**关键方法：**

```python
a_star(start, goal, blocked_positions)  # A*路径规划
bfs(start, goal)                        # BFS路径规划
get_neighbors(pos)                      # 获取相邻节点
heuristic(pos1, pos2)                   # 启发函数
find_alternative_position(pos)          # 寻找替代位置
```

**A\* 算法流程：**

```
1. 初始化开放列表和关闭列表
2. 将起点加入开放列表
3. while 开放列表非空:
   a. 选择 f 值最小的节点
   b. 如果是目标点，返回路径
   c. 扩展相邻节点
   d. 计算 g 值和 h 值
   e. 更新开放列表
4. 无路径则返回 None
```

### 3. core/ - 核心模块

#### context.py - 仿真上下文

**职责：** 全局状态管理

**关键类：**

- `SimulationContext` - 仿真上下文管理器

**核心功能：**

- ✅ 环境初始化
- ✅ 智能体管理
- ✅ 订单处理
- ✅ 状态协调
- ✅ 统计收集

**协作流程：**

```
每个仿真步骤：
1. OrderAgent.step()        # 订单更新
2. SchedulerAgent.schedule() # 执行调度
3. CarAgent.step() × N       # 所有车辆移动
4. 环境更新                  # 更新显示
```

**关键方法：**

```python
add_order(pickup, delivery)             # 添加订单
add_random_order()                      # 添加随机订单
step()                                  # 执行一步仿真
display()                               # 显示当前状态
get_statistics()                        # 获取统计数据
reset()                                 # 重置仿真
```

#### simulation.py - 仿真控制

**职责：** 仿真流程控制

**关键类：**

- `Simulation` - 仿真控制器

**运行模式：**

1. **交互模式（Interactive）**

   - 用户手动输入命令
   - 逐步观察系统行为
   - 适合学习和调试

2. **自动模式（Auto）**
   - 预设订单和步数
   - 自动运行到结束
   - 适合性能测试

**关键方法：**

```python
run_interactive()                       # 交互模式
run_auto(num_steps, num_orders)        # 自动模式
set_fps(fps)                           # 设置帧率
_print_detailed_status()               # 详细状态
_print_final_statistics()              # 最终统计
```

### 4. main.py - 主程序

**职责：** 程序入口和参数解析

**功能：**

- ✅ 命令行参数解析
- ✅ 配置初始化
- ✅ 模式选择
- ✅ 错误处理

**支持的命令行参数：**

```bash
--mode {interactive|auto}   # 运行模式
--size N                    # 地图大小
--cars N                    # 车辆数量
--strategy {greedy|balanced|hungarian}  # 调度策略
--fps N                     # 帧率
--steps N                   # 仿真步数（自动模式）
--orders N                  # 订单数量（自动模式）
--demo                      # 快速演示
```

## 🔄 数据流图

```
用户输入
   ↓
main.py (参数解析)
   ↓
SimulationContext (初始化)
   ↓
┌─────────────────────────────────────┐
│        仿真主循环（每步）             │
├─────────────────────────────────────┤
│ 1. 用户/系统添加订单                 │
│    → OrderAgent.create_order()      │
│                                     │
│ 2. 调度器匹配订单与车辆              │
│    → SchedulerAgent.schedule()      │
│    → 选择策略（贪心/负载均衡）       │
│                                     │
│ 3. 车辆执行任务                      │
│    → CarAgent.step()                │
│    → PathFinding.a_star()          │
│    → 移动并避障                     │
│                                     │
│ 4. 更新环境                         │
│    → GridEnvironment.display()     │
│    → 统计数据收集                   │
└─────────────────────────────────────┘
   ↓
显示结果 / 继续下一步
```

## 🎯 关键接口

### 智能体接口

所有智能体都实现以下接口：

```python
class Agent:
    def reset(self):           # 重置状态
        pass

    def step(self):            # 执行一步
        pass

    def report(self) -> dict:  # 报告状态
        pass
```

### LLM 扩展接口

系统预留了 LLM 集成接口：

```python
# 车辆决策
def call_llm(prompt: str) -> str:
    """用于车辆的智能决策"""
    pass

# 调度优化
def call_llm_for_scheduling(context: dict) -> str:
    """用于调度策略优化"""
    pass
```

## 📊 性能指标

系统自动收集以下指标：

| 指标         | 说明                   |
| ------------ | ---------------------- |
| 已完成订单数 | 成功配送的订单总数     |
| 总移动距离   | 所有车辆的移动距离总和 |
| 平均配送距离 | 总距离 / 完成订单数    |
| 订单完成效率 | 完成订单数 / 仿真步数  |
| 车辆利用率   | 每辆车的工作时间占比   |

## 🔧 扩展指南

### 添加新的调度策略

在 `scheduler_agent.py` 中：

```python
def _my_custom_schedule(self, cars, orders, grid_env):
    # 实现你的调度逻辑
    assignments = []
    # ...
    return assignments
```

### 自定义地图

修改 `grid.py` 中的 `_create_default_grid()` 方法。

### 集成机器学习

使用预留的 `call_llm()` 接口集成 LLM 或其他 ML 模型。

## 📝 代码规范

- ✅ 类名：大驼峰（PascalCase）
- ✅ 函数名：小写下划线（snake_case）
- ✅ 常量：大写下划线（UPPER_CASE）
- ✅ 文档字符串：Google 风格
- ✅ 类型提示：使用 typing 模块

## 🧪 测试建议

```bash
# 测试基本功能
python main.py --demo

# 测试大规模场景
python main.py --mode auto --cars 10 --orders 50

# 测试不同策略
python main.py --strategy greedy
python main.py --strategy balanced

# 压力测试
python main.py --mode auto --cars 20 --orders 100 --steps 1000
```

---

**掌握项目结构，轻松定制开发！** 🎓
