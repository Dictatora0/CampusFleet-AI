# CampusFleet AI - 调度策略简化指南

**适用场景：** 课程实验演示
**策略数量：** 3 个核心 AI 策略
**更新时间：** 2024-12-07 00:05

---

## 🎯 为什么简化？

原系统包含 10 多个调度策略，对于课程实验来说过于复杂。简化后的 3 个策略：

- ✅ 覆盖 AI 核心技术点
- ✅ 便于对比演示效果
- ✅ 降低学习和维护成本
- ✅ 适合课程汇报展示

---

## 🚀 3 个核心 AI 策略

### 1. 🎯 贪心最近算法（Greedy Nearest）

**类别：** 启发式算法（Heuristic Algorithm）

**核心思想：**

- 为每个订单选择距离最近的空闲车辆
- 局部最优策略，不考虑全局最优

**算法流程：**

```python
def _greedy_nearest_schedule(cars, orders):
    for order in orders:
        # 找到距离订单取货点最近的车辆
        best_car = min(cars, key=lambda car:
            distance(car.position, order.pickup_point))

        # 分配订单
        assign(best_car, order)
        cars.remove(best_car)
```

**优点：**

- ⚡ 计算速度快：O(n×m)
- 🎯 简单直观，易于理解
- 📊 作为基线对比方法

**缺点：**

- ❌ 可能导致某些车辆负载过重
- ❌ 不考虑电量、路径等因素
- ❌ 非全局最优解

**适用场景：**

- 订单数量少
- 对效率要求不高
- 作为基线算法对比

**预设配置：**

```javascript
{
  grid_size: 12,      // 网格大小
  num_cars: 4,        // 车辆数量
  strategy: "GREEDY_NEAREST"
}
```

---

### 2. 🎪 拍卖机制（Auction CNP）

**类别：** 多智能体系统（Multi-Agent System）

**核心思想：**

- 基于合同网协议（Contract Net Protocol）
- 订单作为"拍卖品"，车辆竞标
- 分布式决策，车辆自主计算成本

**合同网协议 4 阶段：**

```
Phase 1: 📢 Task Announcement（任务公告）
         └─ 调度器发布新订单信息

Phase 2: 💰 Bidding（竞标）
         ├─ 车辆计算竞标成本
         ├─ 考虑：距离、电量、负载
         └─ 提交竞标报价

Phase 3: 🏆 Winner Selection（中标选择）
         └─ 选择成本最低的车辆

Phase 4: ✅ Award（授予）
         └─ 将订单分配给中标车辆
```

**竞标成本计算：**

```python
def calculate_bid_cost(car, order):
    # 1. 距离成本
    pickup_dist = distance(car.position, order.pickup)
    delivery_dist = distance(order.pickup, order.delivery)
    distance_cost = pickup_dist * 2.0 + delivery_dist * 1.0

    # 2. 电量惩罚
    if car.battery < 30%:
        battery_penalty = 50  # 严重低电
    elif car.battery < 50%:
        battery_penalty = 20  # 中等电量
    else:
        battery_penalty = 0

    # 3. 负载惩罚
    load_penalty = len(car.task_queue) * 10

    # 综合成本
    return distance_cost + battery_penalty + load_penalty
```

**优点：**

- 🤖 分布式决策，符合多智能体理念
- ⚡ 考虑多维度因素（距离、电量、负载）
- 📊 实时竞标，动态调整
- 🎯 更接近真实配送场景

**缺点：**

- 📈 计算开销略高于贪心
- 🔄 需要多轮通信协商

**适用场景：**

- 车辆较多，需要负载均衡
- 订单分布不均
- 需要考虑电量管理

**预设配置：**

```javascript
{
  grid_size: 15,      // 更大网格
  num_cars: 6,        // 更多车辆
  strategy: "AUCTION_CNP"
}
```

**Web 界面特色：**

- ✅ 实时拍卖日志面板
- ✅ 显示竞标成本对比
- ✅ 追踪中标历史

---

### 3. 🤖 强化学习调度（RL Scheduler）

**类别：** 深度强化学习（Deep Reinforcement Learning）

**核心思想：**

- 通过与环境交互学习最优策略
- 智能体自主探索和优化
- 长期累积奖励最大化

**支持算法：**

- **DQN** (Deep Q-Network) - 值函数方法
- **PPO** (Proximal Policy Optimization) - 策略梯度方法

**状态空间（State）：**

```python
state = [
    # 车辆信息（每辆车）
    car.position[0], car.position[1],  # 位置
    car.battery,                        # 电量
    car.state,                          # 状态（空闲/执行等）

    # 订单信息（每个订单）
    order.pickup[0], order.pickup[1],   # 取货点
    order.delivery[0], order.delivery[1], # 送货点

    # 全局信息
    total_pending_orders,                # 待分配订单数
    average_battery,                     # 平均电量
]
```

**动作空间（Action）：**

```python
action = car_id  # 选择哪辆车执行订单
# 例如：action=2 表示将订单分配给车辆2
```

**奖励函数（Reward）：**

```python
reward = - (delivery_time + distance_penalty + battery_penalty)

# 惩罚项：
# - 配送时间长 → 负奖励
# - 距离远 → 负奖励
# - 低电量车辆 → 负奖励
```

**训练流程：**

```
1. 初始化网络参数
2. for episode in episodes:
     - 重置环境
     - for step in steps:
         - 观察状态 s
         - 选择动作 a (ε-greedy)
         - 执行动作，获得奖励 r 和新状态 s'
         - 存储经验 (s, a, r, s')
         - 从经验池采样，更新网络
     - 记录总奖励
3. 保存训练好的模型
```

**DQN vs PPO：**

| 特性         | DQN              | PPO              |
| ------------ | ---------------- | ---------------- |
| **类型**     | 值函数方法       | 策略梯度方法     |
| **学习目标** | 学习 Q 值函数    | 直接学习策略     |
| **探索策略** | ε-greedy         | 随机策略         |
| **样本效率** | 较高（经验回放） | 中等             |
| **稳定性**   | 中等             | 较好（截断更新） |
| **收敛速度** | 快               | 稳定             |

**优点：**

- 🧠 自主学习，无需人工规则
- 📈 长期优化，考虑未来影响
- 🎯 可以学习复杂策略
- 💡 适应性强，环境变化后继续学习

**缺点：**

- ⏱️ 训练时间长（需要大量交互）
- 🔧 超参数调优复杂
- 📊 需要大量数据
- ⚠️ 可能不稳定或过拟合

**适用场景：**

- 复杂动态环境
- 长期规划需求
- 有充足训练时间和数据

**预设配置：**

```javascript
{
  grid_size: 12,
  num_cars: 5,
  strategy: "RL_SCHEDULER"
}
```

**训练 vs 推理模式：**

- **训练模式** - 智能体探索学习，保存模型
- **推理模式** - 使用训练好的模型，快速决策

---

## 📊 三策略对比表

| 维度           | 贪心算法 | 拍卖机制       | 强化学习 |
| -------------- | -------- | -------------- | -------- |
| **AI 类别**    | 启发式   | 多智能体       | 深度学习 |
| **时间复杂度** | O(n×m)   | O(n×m)         | O(1)推理 |
| **决策方式**   | 中心化   | 分布式         | 智能化   |
| **考虑因素**   | 距离     | 距离+电量+负载 | 全局最优 |
| **可解释性**   | ⭐⭐⭐   | ⭐⭐           | ⭐       |
| **学习成本**   | 低       | 中             | 高       |
| **适合新手**   | ✅       | ✅             | ⚠️       |
| **课程展示**   | 基线     | 核心           | 亮点     |

---

## 🎓 课程实验建议

### 实验 1：基础对比（30 分钟）

**目标：** 理解不同策略的基本差异

**步骤：**

1. 创建相同场景（12×12，4 辆车，10 订单）
2. 依次使用 3 个策略
3. 记录指标：
   - 平均配送时间
   - 总行驶距离
   - 车辆利用率

**对比分析：**

```
贪心算法：
- 速度最快，但可能某些车很忙，某些车很闲
- 适合快速演示

拍卖机制：
- 负载更均衡
- 电量管理更好
- 适合重点讲解

强化学习：
- 需要先训练（可提前训练好）
- 展示AI学习能力
- 适合作为亮点
```

### 实验 2：拍卖机制深入（45 分钟）

**目标：** 理解合同网协议

**步骤：**

1. 使用拍卖策略创建仿真
2. 添加订单，观察拍卖日志面板
3. 分析竞标成本：
   - 为什么车辆 A 中标？
   - 车辆 B 成本为什么高？
   - 低电量如何影响竞标？

**实验场景：**

```javascript
// 场景1：距离影响
// - 订单在(10,10)
// - 车辆分布：(5,5), (15,15), (10,1)
// 预期：(10,1)中标（距离最近）

// 场景2：电量影响
// - 相同位置的两辆车
// - 电量：90% vs 25%
// 预期：高电量中标

// 场景3：负载影响
// - 一辆车已有3个任务
// - 另一辆车空闲
// 预期：空闲车辆中标
```

### 实验 3：强化学习训练（可选，2 小时）

**目标：** 了解 RL 训练过程

**步骤：**

1. 使用 DQN 训练 100 个 episode
2. 绘制奖励曲线
3. 对比训练前后性能

**关键指标：**

- Episode Reward（逐渐上升）
- Loss（逐渐下降）
- Epsilon（探索率，逐渐减小）

---

## 🛠️ 使用方法

### 启动服务

```bash
# 启动后端和前端
./debug_web.sh

# 访问
open http://localhost:3000
```

### 选择策略

**方式 1：使用预设**

```
📱 Web界面 → 选择预设：
  🎯 贪心算法（启发式）
  🎪 拍卖机制（多智能体）  ← 推荐
  🤖 强化学习（深度学习）
```

**方式 2：API 调用**

```bash
curl -X POST http://localhost:8001/api/simulation/create \
  -H "Content-Type: application/json" \
  -d '{
    "grid_size": 15,
    "num_cars": 6,
    "strategy": "AUCTION_CNP"
  }'
```

### 查看策略列表

```bash
curl http://localhost:8001/api/strategies | python -m json.tool
```

**输出：**

```json
{
  "strategies": [
    {
      "key": "GREEDY_NEAREST",
      "name": "贪心最近算法",
      "description": "启发式算法 - 为每个订单选择最近的车辆",
      "category": "启发式"
    },
    {
      "key": "AUCTION_CNP",
      "name": "拍卖机制(CNP)",
      "description": "多智能体协商 - 合同网协议车辆竞标",
      "category": "多智能体"
    },
    {
      "key": "RL_SCHEDULER",
      "name": "强化学习调度",
      "description": "深度强化学习 - DQN/PPO智能决策",
      "category": "深度学习"
    }
  ]
}
```

---

## 📁 相关文件修改清单

### 后端

```
agents/scheduler_agent.py
├─ SchedulingStrategy枚举（精简为3个）
├─ schedule()方法（简化策略分发）
└─ 保留_greedy_nearest, _auction_cnp, _rl_schedule

web_backend/main.py
└─ /api/strategies端点（返回3个策略）
```

### 前端

```
web_frontend/src/api/simulation.js
└─ presetConfigs（改为greedy/auction/rl）

web_frontend/src/views/SimulationView.vue
├─ 预设选项（改为3个）
└─ 默认预设（改为greedy）
```

---

## 🎯 课程汇报建议

### PPT 结构

**第 1 部分：问题背景**

- 校园配送场景介绍
- 调度问题的挑战

**第 2 部分：3 个 AI 策略**

- 启发式算法（贪心）
- 多智能体协商（拍卖）
- 深度强化学习（DQN/PPO）

**第 3 部分：实验演示**

- 同场景下 3 策略对比
- 拍卖日志实时可视化
- 性能指标对比

**第 4 部分：总结**

- 不同策略的适用场景
- AI 技术在物流中的应用
- 未来改进方向

### 演示脚本

```
1. 打开系统，介绍界面 (2分钟)
2. 演示贪心算法 (3分钟)
   - 快速分配
   - 指出可能的不均衡
3. 演示拍卖机制 (5分钟) ← 重点
   - 展示拍卖日志面板
   - 解释竞标成本
   - 对比负载均衡
4. 演示强化学习 (3分钟)
   - 展示训练曲线
   - 对比最终性能
5. 总结对比 (2分钟)
```

---

## ❓ 常见问题

### Q1：为什么去掉 Hungarian、VRP 等策略？

**A：** 这些是运筹学经典算法，但：

- 与 AI 课程关联不强
- 实现复杂，不便讲解
- 3 个策略已覆盖主要技术点

### Q2：强化学习训练需要多久？

**A：**

- DQN 训练 100 episodes：约 15-30 分钟
- PPO 训练 100 episodes：约 20-40 分钟
- 建议：提前训练好，演示时直接加载模型

### Q3：拍卖机制一定比贪心好吗？

**A：** 不一定。取决于场景：

- 订单少、分布均匀 → 贪心足够
- 订单多、车辆忙 → 拍卖更优
- 复杂动态环境 → 强化学习最优

### Q4：如何恢复之前的所有策略？

**A：** 查看 git 历史：

```bash
git log --oneline | grep "策略"
git checkout <commit-id> -- agents/scheduler_agent.py
```

---

## 📚 参考资料

### 启发式算法

- 《算法导论》第 15 章 - 贪心算法
- 《人工智能：一种现代方法》第 4 章

### 多智能体系统

- Smith, R. G. (1980). "The contract net protocol"
- Wooldridge, M. (2009). "An Introduction to MultiAgent Systems"

### 强化学习

- Sutton & Barto. "Reinforcement Learning: An Introduction" (2018)
- Mnih et al. (2015). "Human-level control through deep RL" (DQN 论文)
- Schulman et al. (2017). "Proximal Policy Optimization" (PPO 论文)

---

**最后更新：** 2024-12-07 00:05
**适用版本：** CampusFleet AI 课程实验简化版
**维护者：** Course Experiment Team
