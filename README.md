# 🚗 校园无人配送车多智能体系统

Campus Fleet AI - Multi-Agent Autonomous Delivery System

一个基于 Python 的校园无人配送车多智能体仿真系统，模拟多辆配送车在校园环境中的智能调度、路径规划和协作避障。

## 📋 项目概述

本项目实现了一个完整的多智能体配送系统，包含：

- **CarAgent（车辆智能体）**：负责路径规划、移动和避障
- **OrderAgent（订单智能体）**：管理订单队列和状态
- **SchedulerAgent（调度智能体）**：智能匹配订单与车辆

系统在 15×15 的二维网格地图上运行，通过 ASCII 动画实时展示车辆移动、避障、调度和订单完成的全过程。

## ✨ 核心特性

### 🎯 智能调度

- **贪心策略**：为每个订单选择最近的空闲车辆
- **负载均衡**：优先分配给完成订单少的车辆
- **匈牙利算法**：最优匹配（预留接口）

### 🗺️ 路径规划

- **A\* 算法**：高效的路径搜索
- **动态避障**：实时规避其他车辆
- **路径重规划**：遇阻时自动寻找新路径

### 🚦 避碰机制

- **位置检测**：防止多车占用同一位置
- **优先级规则**：按车辆 ID 决定通行优先级
- **智能避让**：低优先级车辆主动绕行

### 📊 实时监控

- ASCII 动画显示
- 车辆状态追踪
- 订单进度监控
- 统计数据分析

## 📁 项目结构

```
CampusFleet AI/
├── agents/                     # 智能体模块
│   ├── __init__.py
│   ├── car_agent.py           # 车辆智能体
│   ├── order_agent.py         # 订单智能体
│   └── scheduler_agent.py     # 调度智能体
├── env/                       # 环境模块
│   ├── __init__.py
│   ├── grid.py                # 网格地图
│   └── pathfinding.py         # 路径规划（A*算法）
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── context.py             # 仿真上下文
│   └── simulation.py          # 仿真主循环
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖包列表
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- 无需额外依赖包（仅使用 Python 标准库）

### 2. 安装

```bash
# 克隆或下载项目
cd "CampusFleet AI"

# （可选）创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 运行

#### 快速演示

```bash
python main.py --demo
```

#### 交互模式（推荐）

```bash
python main.py
```

#### 自动模式

```bash
python main.py --mode auto --cars 5 --orders 15 --steps 100
```

### 4. 命令行参数

```
--mode {interactive|auto}   运行模式（默认：interactive）
--size SIZE                 地图大小（默认：15）
--cars CARS                 车辆数量（默认：3）
--strategy {greedy|balanced|hungarian}  调度策略（默认：greedy）
--fps FPS                   动画帧率（默认：2）
--steps STEPS               自动模式的仿真步数（默认：100）
--orders ORDERS             自动模式的订单数量（默认：10）
--demo                      运行快速演示
```

## 🎮 使用说明

### 交互模式命令

运行交互模式后，可以使用以下命令：

```
add <x1> <y1> <x2> <y2>  - 添加订单（从(x1,y1)到(x2,y2)）
random                   - 添加随机订单
auto                     - 切换自动模式（自动生成订单）
step [n]                 - 执行n步仿真（默认1步）
run                      - 持续运行仿真
pause                    - 暂停仿真
reset                    - 重置仿真
status                   - 显示详细状态
quit                     - 退出
```

### 示例操作

```bash
# 启动交互模式
python main.py

# 在提示符下输入命令：
👉 输入命令: add 0 0 14 14         # 添加从(0,0)到(14,14)的订单
👉 输入命令: random                # 添加随机订单
👉 输入命令: step 10               # 执行10步仿真
👉 输入命令: auto                  # 开启自动订单生成
👉 输入命令: run                   # 持续运行
```

## 🧩 系统架构

### 智能体协作流程

```
1. OrderAgent 接收新订单
        ↓
2. SchedulerAgent 执行调度匹配
        ↓
3. CarAgent 接受任务并规划路径
        ↓
4. CarAgent 执行移动（考虑避障）
        ↓
5. 到达取货点 → 前往配送点
        ↓
6. 完成配送 → 更新状态 → 返回空闲
```

### 关键算法

#### A\* 路径规划

```python
def a_star(start, goal, blocked_positions):
    # 使用曼哈顿距离作为启发函数
    # 避开被占用的位置
    # 返回最优路径
```

#### 避碰策略

```python
def handle_collision(self, other_car_id):
    if self.car_id < other_car_id:
        # 优先级高，保持路径
        return True
    else:
        # 优先级低，尝试避让
        return self._try_avoid()
```

#### 贪心调度

```python
def greedy_nearest_schedule(cars, orders):
    for order in orders:
        # 选择距离订单最近的空闲车辆
        best_car = min(cars, key=lambda c: distance(c.pos, order.pickup))
        assign(best_car, order)
```

## 📊 显示说明

### 地图图例

- `.` - 道路
- `#` - 建筑/障碍
- `0-9` - 车辆（数字表示车辆 ID）

### 车辆状态

- 🅿️ - 空闲
- 🔍 - 前往取货点
- 📦 - 配送中
- ⏸️ - 等待

## 🔧 扩展接口

### LLM 集成接口

系统预留了 LLM 调用接口，可用于未来的智能决策扩展：

```python
# 在 car_agent.py 中
def call_llm(prompt: str) -> str:
    """调用LLM进行智能决策"""
    # 连接到LLM服务
    pass

# 在 scheduler_agent.py 中
def call_llm_for_scheduling(context: dict) -> str:
    """调用LLM优化调度策略"""
    # 根据历史数据和当前状态获取LLM建议
    pass
```

### 自定义调度策略

继承`SchedulerAgent`类实现自定义调度算法：

```python
class MyScheduler(SchedulerAgent):
    def _custom_schedule(self, cars, orders, grid_env):
        # 实现你的调度逻辑
        assignments = []
        # ...
        return assignments
```

## 📈 性能指标

系统会自动统计以下性能指标：

- **订单完成率**：已完成订单数 / 总订单数
- **平均配送距离**：总移动距离 / 完成订单数
- **车辆利用率**：忙碌时间 / 总运行时间
- **订单完成效率**：完成订单数 / 仿真步数

## 🛠️ 开发说明

### 添加新功能

1. **新的调度策略**：在`scheduler_agent.py`中添加新方法
2. **新的避障算法**：在`car_agent.py`中修改碰撞处理逻辑
3. **新的地图布局**：在`grid.py`中修改`_create_default_grid`方法

### 调试模式

```python
# 在 simulation.py 中启用详细日志
context.display()  # 显示当前状态
context.get_statistics()  # 获取统计数据
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证。

## 👨‍💻 作者

CampusFleet AI Team

## 🙏 致谢

- A\* 算法参考实现
- 多智能体系统设计理论
- 校园配送场景实践

## 📞 联系方式

如有问题或建议，欢迎提 Issue 或联系开发团队。

---

**Made with ❤️ for autonomous campus delivery**
