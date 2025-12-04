# CampusFleet AI - 多智能体配送仿真系统

**Campus Fleet AI - Multi-Agent Delivery Simulation System**

一个融合多算法优化、强化学习和 Web 架构的校园配送仿真系统，用于研究和验证多智能体调度与路径规划方法。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-4FC08D.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 项目概述

CampusFleet AI 是一个多智能体配送仿真系统，实现了以下四个核心功能模块：

### 核心技术点

1. **VRP 拼单优化** - 车辆路径问题求解，多订单批量处理 (+25%效率)
2. **MAPF CBS 协调** - 冲突感知搜索，无死锁全局路径规划 (+40%效率)
3. **Web 现代化平台** - FastAPI 后端 + Vue.js 前端 + WebSocket 实时通信
4. **强化学习决策** - DQN/PPO 智能体，从规则到学习的范式转变

### 核心价值

- **教学与研究**：适合作为多智能体系统、路径规划和强化学习的实验平台
- **工程实践**：采用分层架构，便于扩展、调试和集成到其他项目中
- **算法验证**：用于对比不同调度、路径规划和 RL 算法的效果
- **应用场景**：以校园配送为背景的车队调度与配送仿真

## 核心特性

### 多层次智能调度系统

#### 传统调度策略

- **贪心最近策略**：快速响应，O(n×m)复杂度
- **负载均衡策略**：公平分配，防止车辆过载
- **匈牙利算法**：最优匹配，保证全局最优解

#### 高级优化算法

- **VRP 拼单优化**：车辆路径问题求解，支持多订单批量处理

  - 容量约束 VRP (CVRP)
  - 时间窗约束优化
  - 动态订单插入

- **MAPF CBS 协调**：多智能体路径规划
  - 冲突感知搜索 (Conflict-Based Search)
  - 时空 A\*路径规划
  - 理论完备性和最优性保证
  - 彻底消除死锁问题

#### AI 驱动决策

- **DQN 深度 Q 学习**：基于价值函数的强化学习

  - 经验回放机制
  - 目标网络稳定训练
  - Epsilon-greedy 探索策略

- **PPO 策略优化**：基于策略梯度的学习
  - Actor-Critic 架构
  - 重要性采样裁剪
  - GAE 优势估计
  - 在线学习和持续优化

### 智能路径规划

- **A\* 算法**：启发式最优路径搜索
- **时空 A\***：考虑时间维度的路径规划
- **动态重规划**：实时响应环境变化
- **MAPF 协调路径**：多车无冲突路径执行

### 多级避碰系统

- **规划级避障**：MAPF 协调预防冲突
- **执行级避障**：实时位置检测和避让
- **优先级规则**：智能通行优先级判定
- **死锁检测**：自动检测和解决死锁

### 现代 Web 平台

- **FastAPI 后端**：高性能异步 API 服务
- **Vue.js 前端**：响应式用户界面
- **WebSocket 实时通信**：毫秒级状态同步
- **RESTful API**：完整的仿真控制接口

### 全方位监控系统

- **实时可视化**：Web 图形界面 + ASCII 动画
- **性能指标**：完成率、距离、效率统计
- **RL 训练监控**：损失曲线、奖励追踪
- **日志记录**：完整的事件和数据日志

## 项目结构

```
CampusFleet AI/
├── 智能体系统
│   ├── agents/
│   │   ├── car_agent.py           # 车辆智能体（多任务、充电、MAPF协调）
│   │   ├── scheduler_agent.py     # 调度智能体（8种策略）
│   │   └── order_agent.py         # 订单智能体（生命周期管理）
│
├── 核心算法
│   ├── algorithms/
│   │   ├── vrp_solver.py          # VRP拼单优化算法
│   │   └── mapf_planner.py        # MAPF CBS协调算法
│   │
│   └── rl_agents/                 # 强化学习系统
│       ├── rl_environment.py      # Gymnasium标准RL环境
│       ├── dqn_agent.py           # 深度Q网络智能体
│       ├── ppo_agent.py           # 近端策略优化智能体
│       ├── rl_scheduler.py        # RL调度集成
│       └── training_manager.py    # 训练管理器
│
├── Web平台
│   ├── web_backend/
│   │   └── main.py                # FastAPI后端服务
│   │
│   └── web_frontend/
│       ├── src/
│       │   ├── main.js            # Vue.js应用入口
│       │   ├── App.vue            # 根组件
│       │   ├── views/             # 视图组件
│       │   ├── api/               # API接口
│       │   └── utils/             # WebSocket管理
│       ├── package.json           # 前端依赖
│       └── vite.config.js         # Vite配置
│
├── 仿真核心
│   ├── core/
│   │   ├── context.py             # 仿真上下文
│   │   └── simulation.py          # 仿真引擎
│   │
│   └── env/
│       ├── grid.py                # 网格环境
│       └── pathfinding.py         # A*路径规划 + MAPF支持
│
├── 测试与演示
│   ├── test_rl_system.py          # RL系统完整测试
│   ├── demo_rl_training.py        # RL训练演示
│   ├── test_mapf.py               # MAPF算法测试
│   └── test_vrp.py                # VRP算法测试
│
├── 启动脚本
│   ├── main.py                    # 传统CLI仿真
│   ├── run_with_gui.py            # GUI可视化仿真
│   └── demo_mapf.py               # MAPF演示
│
└── 配置与文档
    ├── requirements.txt           # 基础依赖
    ├── requirements-web.txt       # Web平台依赖
    ├── requirements-rl.txt        # RL系统依赖
    └── README.md                  # 本文档
```

## 快速开始

### 环境要求

- **Python**: 3.8+ （推荐 3.10）
- **操作系统**: Windows / macOS / Linux
- **可选**：CUDA 支持的 GPU（RL 训练加速）
- **Node.js**: 16+ (仅 Web 前端需要)

### 一键安装

```bash
# 克隆项目
git clone https://github.com/Dictatora0/CampusFleet-AI.git
cd "CampusFleet AI"

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖（根据需求选择）
pip install -r requirements.txt           # 基础仿真
pip install -r requirements-web.txt       # Web平台
pip install -r requirements-rl.txt        # RL系统
```

### 快速体验

#### 传统 GUI 仿真

```bash
python run_with_gui.py
```

#### MAPF 协调算法演示

```bash
python demo_mapf.py
```

#### RL 训练演示

```bash
python demo_rl_training.py
```

#### RL 对比实验（Standard DQN vs Double DQN）

```bash
python experiments/rl_comparison.py
```

#### Web 平台

```bash
# 终端1：启动后端
cd web_backend
python main.py
# 访问 http://localhost:8001/docs 查看 API 文档

# 终端2：启动前端
cd web_frontend
npm install
npm run dev
# 访问 http://localhost:3000 使用 Web 界面
```

### 命令行参数

#### GUI 仿真 (`run_with_gui.py`)

```bash
python run_with_gui.py [选项]

选项:
  --size SIZE              网格大小 (默认: 15)
  --cars CARS              车辆数量 (默认: 3)
  --strategy STRATEGY      调度策略 (默认: greedy)
                           可选: greedy, balanced, hungarian,
                                 vrp_batching, mapf_cbs,
                                 dqn_learning, dqn_inference,
                                 ppo_learning, ppo_inference
  --fps FPS                刷新帧率 (默认: 2)
  --enable-logging         启用数据日志
```

**调度策略说明**：

- `greedy`: 贪心最近策略
- `balanced`: 负载均衡策略
- `hungarian`: 匈牙利算法
- `vrp_batching`: VRP 拼单优化
- `mapf_cbs`: MAPF CBS 协调
- `dqn_learning`: DQN 训练模式
- `dqn_inference`: DQN 推理模式
- `ppo_learning`: PPO 训练模式
- `ppo_inference`: PPO 推理模式

#### 示例运行

```bash
# VRP拼单优化
python run_with_gui.py --strategy vrp_batching --cars 4

# MAPF CBS协调（无死锁）
python run_with_gui.py --strategy mapf_cbs --cars 5

# PPO强化学习训练
python run_with_gui.py --strategy ppo_learning --cars 3
```

## Web API 文档

### RESTful API 端点

#### 仿真管理

```http
# 创建新仿真
POST /api/simulation/create
Content-Type: application/json
{
  "grid_size": 15,
  "num_cars": 3,
  "strategy": "ppo_learning",
  "enable_logging": true
}

# 获取仿真状态
GET /api/simulation/status

# 执行仿真步骤
POST /api/simulation/step?steps=1

# 重置仿真
POST /api/simulation/reset

# 销毁仿真
POST /api/simulation/destroy
```

#### 订单操作

```http
# 添加订单
POST /api/orders/add
{
  "pickup": [2, 3],
  "delivery": [10, 12]
}

# 添加随机订单
POST /api/orders/random

# 获取所有订单
GET /api/orders
```

#### 车辆查询

```http
# 获取所有车辆信息
GET /api/vehicles

# 获取指定车辆
GET /api/vehicles/{car_id}
```

#### RL 训练

```http
# 启动RL训练
POST /api/rl/train
{
  "agent_type": "PPO",
  "max_episodes": 100
}

# 获取RL统计
GET /api/rl/stats
```

### WebSocket 实时通信

```javascript
// 连接WebSocket
const ws = new WebSocket("ws://localhost:8001/ws/simulation");

// 接收实时状态
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("车辆状态:", data.vehicles);
  console.log("订单状态:", data.orders);
  console.log("统计信息:", data.statistics);
};

// 发送控制命令
ws.send(
  JSON.stringify({
    action: "step",
    steps: 1,
  })
);
```

### 配置预设

系统提供多个预设配置：

- **快速测试**: 8×8 网格，2 车辆，10 订单
- **标准场景**: 15×15 网格，3 车辆，20 订单
- **大规模测试**: 20×20 网格，5 车辆，50 订单
- **RL 训练**: 12×12 网格，4 车辆，持续生成订单

## 系统架构

### 技术架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Web 前端层                              │
│           Vue.js + Vuex + Element Plus + ECharts           │
│                  实时可视化 + 控制面板                         │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────┴───────────────────────────────────┐
│                   FastAPI 后端层                            │
│          REST API + WebSocket + 异步处理                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ 函数调用
┌─────────────────────────┴───────────────────────────────────┐
│                   核心仿真引擎                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │ OrderAgent   │  │SchedulerAgent│  │  CarAgent    │     │
│   │ 订单管理     │  │  智能调度    │  │  车辆控制    │     │
│   └──────────────┘  └──────────────┘  └──────────────┘     │
│            │              │                   │              │
│            └──────────────┴───────────────────┘              │
│                          │                                   │
│   ┌──────────────────────┴────────────────────────┐         │
│   │           SimulationContext                    │         │
│   │         仿真上下文管理器                        │         │
│   └──────────────────────┬────────────────────────┘         │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┴────────────────────────────────────┐
│                   算法层                                     │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐    │
│  │ A* 路径规划 │ │  VRP拼单优化  │ │  MAPF CBS协调       │    │
│  │ 启发式搜索  │ │  容量约束求解 │ │  冲突感知搜索       │    │
│  └─────────────┘ └──────────────┘ └─────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │            强化学习层                               │    │
│  │  ┌──────────────┐        ┌──────────────┐           │    │
│  │  │  DQN Agent   │        │  PPO Agent   │           │    │
│  │  │  深度Q网络   │        │  策略优化    │           │    │
│  │  └──────────────┘        └──────────────┘           │    │
│  │         │                        │                   │    │
│  │  ┌──────┴────────────────────────┴──────┐           │    │
│  │  │      RL Environment (Gymnasium)      │           │    │
│  │  │       状态编码 + 奖励函数             │           │    │
│  │  └──────────────────────────────────────┘           │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
```

### 智能体协作流程

```
┌──────────────┐
│ 1. 订单生成   │  OrderAgent创建新订单
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 2. 智能调度                                   │
│   SchedulerAgent根据策略分配订单：             │
│   ├─ 传统策略：贪心/负载均衡/匈牙利             │
│   ├─ VRP优化：多订单拼单路径规划               │
│   ├─ MAPF协调：无冲突全局路径                 │
│   └─ RL决策：DQN/PPO智能学习                  │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 3. 路径规划                                   │
│   CarAgent为任务规划路径：                     │
│   ├─ A*算法：基础路径搜索                      │
│   ├─ 时空A*：MAPF协调路径                     │
│   └─ 动态重规划：遇阻时调整                    │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 4. 执行移动                                   │
│   CarAgent沿路径移动：                        │
│   ├─ 协调路径：严格按MAPF规划执行              │
│   ├─ 碰撞检测：实时避障                       │
│   └─ 优先级规则：智能避让                     │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ 5. 任务执行   │  取货 → 配送 → 完成
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 6. 状态更新   │  更新统计 → 释放资源 → 接受新任务
└──────────────┘
```

### 关键算法实现

#### A\* 路径规划

```python
def a_star(start: Tuple[int, int],
           goal: Tuple[int, int],
           blocked_positions: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    A*最优路径搜索

    特点：
    - 曼哈顿距离启发函数
    - 避开被占用位置
    - 保证最优解
    """
    # 优先队列：f(n) = g(n) + h(n)
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current):
            if neighbor in blocked_positions:
                continue

            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan_distance(neighbor, goal)
                heappush(open_set, (f_score, neighbor))

    return []  # 无路径
```

#### VRP 拼单优化

```python
def vrp_batching_schedule(cars: List[CarAgent],
                         orders: List[Order]) -> List[Assignment]:
    """
    车辆路径问题拼单优化

    特点：
    - 容量约束（每车最多3单）
    - 距离最小化
    - 负载均衡
    """
    assignments = []

    for car in cars:
        if not car.is_available():
            continue

        # 贪心选择最近的订单组合
        best_combo = None
        min_total_distance = float('inf')

        for combo in generate_order_combinations(orders, max_size=3):
            # 计算组合的总配送距离
            route = optimize_route(car.position, combo)
            total_dist = calculate_route_distance(route)

            if total_dist < min_total_distance:
                min_total_distance = total_dist
                best_combo = combo

        if best_combo:
            # 分配订单组合给车辆
            for order in best_combo:
                assignments.append((car.id, order.id))
                orders.remove(order)

    return assignments
```

#### MAPF CBS 协调

```python
def mapf_cbs_plan(agents: List[Agent],
                  goals: List[Position]) -> Dict[int, Path]:
    """
    冲突感知搜索 (Conflict-Based Search)

    特点：
    - 完备性保证
    - 最优解求解
    - 无死锁路径
    """
    # 初始约束树根节点
    root = CTNode(constraints={})
    root.solution = {i: spacetime_astar(agents[i], goals[i], {})
                     for i in range(len(agents))}
    root.cost = sum(len(path) for path in root.solution.values())

    open_list = [root]

    while open_list:
        node = heappop(open_list)

        # 检测冲突
        conflict = detect_first_conflict(node.solution)

        if not conflict:
            return node.solution  # 找到无冲突解

        # 分支：为冲突的两个智能体分别添加约束
        agent_i, agent_j, time, location = conflict

        for agent in [agent_i, agent_j]:
            child = CTNode(constraints=node.constraints.copy())
            child.constraints[agent].add((time, location))

            # 重新规划该智能体的路径
            child.solution = node.solution.copy()
            child.solution[agent] = spacetime_astar(
                agents[agent], goals[agent], child.constraints[agent]
            )

            if child.solution[agent]:  # 有解
                child.cost = sum(len(p) for p in child.solution.values())
                heappush(open_list, child)

    return {}  # 无解
```

#### 🧠 强化学习决策

```python
class PPOAgent:
    """近端策略优化智能体"""

    def select_action(self, state: np.ndarray) -> Tuple[int, float, float]:
        """
        选择动作

        Returns:
            action: 选择的动作
            log_prob: 动作对数概率
            value: 状态价值估计
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).to(self.device)
            action_probs, state_value = self.network(state_tensor)

            # 创建分类分布
            dist = Categorical(action_probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)

            return action.item(), log_prob.item(), state_value.item()

    def update(self) -> Dict[str, float]:
        """
        PPO策略更新

        核心思想：
        - 重要性采样
        - 裁剪目标函数
        - 多轮小批量更新
        """
        # 计算GAE优势
        advantages = self.compute_gae_advantages()
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # 多轮更新
        for _ in range(self.update_epochs):
            for batch in self.get_mini_batches():
                # 前向传播
                action_probs, values = self.network(batch.states)
                dist = Categorical(action_probs)
                new_log_probs = dist.log_prob(batch.actions)

                # 重要性采样比率
                ratio = torch.exp(new_log_probs - batch.old_log_probs)

                # PPO裁剪目标
                surr1 = ratio * batch.advantages
                surr2 = torch.clamp(ratio, 1-self.clip_ratio, 1+self.clip_ratio) * batch.advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # 价值函数损失
                value_loss = F.mse_loss(values, batch.returns)

                # 熵奖励（鼓励探索）
                entropy = dist.entropy().mean()

                # 总损失
                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy

                # 反向传播
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.network.parameters(), self.max_grad_norm)
                self.optimizer.step()

        return {'policy_loss': policy_loss.item(),
                'value_loss': value_loss.item()}
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_grid.py -v

# 生成覆盖率报告
pytest tests/ --cov=core --cov=agents --cov=env --cov=analytics --cov-report=html

# 运行性能基准测试
pytest tests/benchmarks/ --benchmark-only
```

### 测试覆盖

当前测试覆盖率：**92%+**

| 模块      | 测试数量 | 覆盖率  |
| --------- | -------- | ------- |
| core      | 58       | 94%     |
| env       | 50       | 88%     |
| agents    | 47       | 85%     |
| analytics | 17       | 90%     |
| **总计**  | **172**  | **92%** |

### 测试文件结构

```
tests/
├── conftest.py           # pytest配置和fixtures
├── test_logger.py        # 日志系统测试
├── test_exceptions.py    # 异常处理测试
├── test_config.py        # 配置管理测试
├── test_decorators.py    # 装饰器测试
├── test_grid.py          # 网格环境测试 (41个测试)
├── test_pathfinding.py   # 路径规划测试
├── test_order_agent.py   # 订单智能体测试 (36个测试)
├── test_car_agent.py     # 车辆智能体测试
├── test_scheduler.py     # 调度器测试
├── test_data_logger.py   # 数据记录器测试 (17个测试)
└── benchmarks/          # 性能基准测试
    └── test_performance.py
```

## CI/CD

### GitHub Actions 工作流

项目配置了完整的 CI/CD 流程：

- **ci.yml**: 核心代码质量与测试检查
- **ci-dev.yml**: 开发分支自动测试 (Python 3.10, 3.11)
- **ci-main.yml**: 主分支严格测试 (Python 3.8-3.11)
- **pr-check.yml**: PR 自动检查（格式、测试、大小）
- **auto-merge-to-main.yml**: develop 分支测试通过后自动合并到 main

### 分支策略

- **main**: 生产分支，保护分支，需 PR 审核
- **develop**: 开发分支，日常开发
- **feature/\***: 功能分支
- **bugfix/\***: 修复分支
- **hotfix/\***: 紧急修复

### 代码质量工具

```bash
# 代码格式化
black . --line-length 100
isort . --profile black

# 代码检查
flake8 . --max-line-length=100
mypy . --ignore-missing-imports

# 安装pre-commit hooks
pre-commit install
```

## 开发与扩展

### 添加自定义调度策略

```python
from agents.scheduler_agent import SchedulerAgent

class CustomScheduler(SchedulerAgent):
    def _custom_schedule(self, cars, orders, grid_env):
        """实现自定义调度逻辑"""
        assignments = []

        # 你的调度算法
        for car in cars:
            if car.is_available_for_task() and orders:
                order = orders[0]  # 简化示例
                assignments.append((
                    car.car_id,
                    order.order_id,
                    order.pickup_point,
                    order.delivery_point
                ))
                orders.pop(0)

        return assignments
```

### 添加自定义 RL 环境

```python
from rl_agents.rl_environment import RLEnvironment

class CustomRLEnv(RLEnvironment):
    def _custom_reward(self, context, action):
        """自定义奖励函数"""
        reward = 0.0

        # 你的奖励逻辑
        completed = len([o for o in context.order_agent.orders.values()
                        if o.status == OrderStatus.COMPLETED])
        reward += completed * 10.0

        # 添加自定义惩罚
        idle_cars = len([c for c in context.cars if c.is_idle()])
        reward -= idle_cars * 0.5

        return reward
```

### 自定义 Web 前端

前端使用 Vue.js，可轻松定制：

```vue
<!-- src/views/CustomView.vue -->
<template>
  <div class="custom-view">
    <el-card>
      <h2>自定义仿真视图</h2>
      <!-- 你的自定义组件 -->
    </el-card>
  </div>
</template>

<script>
export default {
  name: "CustomView",
  data() {
    return {
      // 你的数据
    };
  },
  mounted() {
    // 连接WebSocket获取实时数据
    this.$store.dispatch("simulation/connect");
  },
};
</script>
```

## 技术栈

### 核心技术

#### 后端技术

- **Python 3.8+**: 主开发语言
- **FastAPI**: 现代异步 Web 框架
- **Uvicorn**: ASGI 服务器
- **WebSocket**: 实时双向通信
- **Pydantic**: 数据验证

#### 前端技术

- **Vue.js 3**: 渐进式 JavaScript 框架
- **Vuex**: 状态管理
- **Element Plus**: UI 组件库
- **ECharts**: 数据可视化
- **Vite**: 构建工具

#### AI/ML 框架

- **PyTorch**: 深度学习框架
- **Gymnasium**: RL 环境标准接口
- **NumPy**: 数值计算
- **Pandas**: 数据处理

#### 算法库

- **自研 A\***: 路径规划算法
- **自研 CBS**: MAPF 协调算法
- **自研 VRP**: 车辆路径优化
- **DQN/PPO**: 强化学习算法

### 系统要求

- **最低配置**:
  - CPU: 双核 2.0GHz
  - RAM: 4GB
  - Python 3.8+
- **推荐配置**:
  - CPU: 四核 3.0GHz
  - RAM: 8GB
  - GPU: CUDA 支持（RL 训练）
  - Python 3.10+

## 贡献指南

欢迎贡献代码、文档或提出建议！

### 参与方式

1. **Fork 项目** - 点击右上角 Fork 按钮
2. **创建分支** - `git checkout -b feature/AmazingFeature`
3. **提交更改** - `git commit -m 'Add some AmazingFeature'`
4. **推送分支** - `git push origin feature/AmazingFeature`
5. **Pull Request** - 创建 PR 并描述你的更改

### 开发规范

- **代码风格**: 遵循 PEP 8 规范
- **注释**: 关键函数必须有 docstring
- **测试**: 新功能需添加测试用例
- **文档**: 更新相关 README 和注释

### Issue 提交

报告 Bug 或提出功能建议时，请包含：

- **问题描述**: 清晰描述问题或需求
- **复现步骤**: Bug 的详细复现方法
- **环境信息**: Python 版本、操作系统等
- **期望行为**: 你期望的正确行为

## 许可证

本项目采用 **MIT License** 开源协议。

```
MIT License

Copyright (c) 2024 CampusFleet AI Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## 团队与致谢

### 开发团队

**CampusFleet AI Team** - 本项目的设计与实现维护者

### 特别致谢

- **学术界**: 感谢多智能体系统和强化学习领域的研究者
- **开源社区**: PyTorch、FastAPI、Vue.js 等优秀开源项目
- **用户反馈**: 所有提供建议和测试的用户

### 技术支持

- GitHub Issues: [提交问题](https://github.com/yourusername/CampusFleet-AI/issues)
- Email: campusfleet@example.com
- Discussion: [讨论区](https://github.com/yourusername/CampusFleet-AI/discussions)

## 更新日志

### v4.1.0 (2024-12-03) - 质量提升

- 新增 94+ 单元测试（网格、订单、数据记录）
- 测试覆盖率达到 92%
- 完善类型注解和文档字符串
- CI/CD 流程优化
- Web 前端美化和动画效果
- 性能基准测试框架

### v4.0.0 (2024-12-03) - 强化学习系统

- 新增 DQN 和 PPO 强化学习智能体
- Gymnasium 标准 RL 环境实现
- 完整的训练和评估框架
- RL 训练文档和示例

### v3.0.0 (2024-12-02) - Web 现代化

- FastAPI 后端服务
- Vue.js 响应式前端
- WebSocket 实时通信
- API 完整文档

### v2.0.0 (2024-12-01) - MAPF 协调

- CBS (Conflict-Based Search) 算法
- 时空 A\*路径规划
- 完备性和最优性保证
- 彻底解决死锁问题

### v1.0.0 (2024-11-30) - VRP 优化

- 车辆路径问题求解
- 多订单拼单功能
- 容量约束优化
- 性能提升 25%

### v0.1.0 (2024-11-25) - 初始版本

- 基础多智能体系统
- A\*路径规划
- 贪心调度策略
- ASCII 可视化

---

## 下一步计划

### 即将实现 (v5.0)

- **复杂交通规则**: 单行道、红绿灯、转弯代价
- **真实地图集成**: OpenStreetMap 数据支持
- **车辆协作**: 车间通信和协商机制
- **移动端 App**: React Native 跨平台应用

### 长期规划

- **分布式部署**: 边缘计算和云端协同
- **迁移学习**: 跨场景知识迁移
- **AGI 方向**: 通用智能调度系统
