# CampusFleet AI - 多智能体校园配送仿真系统

基于多智能体架构的校园无人配送仿真平台，集成传统调度算法、优化算法与强化学习决策，并提供 GUI 与 Web 多智能体监控界面，可用于课程作业、教学演示和算法验证。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-4FC08D.svg)](https://vuejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 目录

- [CampusFleet AI - 多智能体校园配送仿真系统](#campusfleet-ai---多智能体校园配送仿真系统)
  - [目录](#目录)
  - [1. 项目简介](#1-项目简介)
  - [2. 目录结构](#2-目录结构)
  - [3. 环境与安装](#3-环境与安装)
    - [3.1 环境要求](#31-环境要求)
    - [3.2 安装步骤](#32-安装步骤)
  - [4. 快速开始](#4-快速开始)
    - [4.1 GUI 仿真](#41-gui-仿真)
    - [4.2 Web 多智能体监控](#42-web-多智能体监控)
      - [启动后端](#启动后端)
      - [启动前端](#启动前端)
      - [创建并运行仿真（通过 API）](#创建并运行仿真通过-api)
      - [打开多智能体监控面板](#打开多智能体监控面板)
    - [4.3 自动化实验脚本](#43-自动化实验脚本)
      - [一键运行](#一键运行)
  - [5. 功能概览](#5-功能概览)
    - [5.1 多智能体架构](#51-多智能体架构)
    - [5.2 调度与路径规划](#52-调度与路径规划)
    - [5.3 Web 监控面板](#53-web-监控面板)
  - [6. 实验与评估](#6-实验与评估)
    - [6.1 多智能体系统功能展示实验（推荐）](#61-多智能体系统功能展示实验推荐)
      - [6.1.1 多场景 GUI 功能演示](#611-多场景-gui-功能演示)
      - [6.1.2 Web 多智能体监控与协作可视化](#612-web-多智能体监控与协作可视化)
      - [6.1.3 自动化数据采集与图表生成](#613-自动化数据采集与图表生成)
    - [6.2 强化学习对比实验（可选，高级）](#62-强化学习对比实验可选高级)
  - [7. 文档索引](#7-文档索引)
  - [8. 测试与开发](#8-测试与开发)
    - [8.1 单元测试与集成测试](#81-单元测试与集成测试)
    - [8.2 代码风格与格式化](#82-代码风格与格式化)
  - [9. 许可证](#9-许可证)

---

## 1. 项目简介

- 应用场景：校园无人车/机器人配送，多车协同完成取货与送货任务。
- 系统类型：多智能体系统，包含环境、车辆、订单、调度等智能体。
- 主要能力：
  - 多策略调度：贪心、负载均衡、匈牙利、VRP 拼单、MAPF CBS 协调、DQN/PPO 等。
  - 实时路径规划：A*、时空 A*、多智能体路径规划（MAPF）。
  - 可视化：本地 GUI 仿真 + 基于 FastAPI + Vue3 的 Web 监控面板。
  - 数据记录：支持 CSV 导出、JSON 快照和性能图表生成。

适用用途：

- 多智能体系统 / 强化学习 / 调度与路径规划 课程作业
- 教学演示与答辩展示
- 算法原型验证与对比实验

---

## 2. 目录结构

```text
CampusFleet-AI/
├── agents/                 # 智能体实现（车辆、订单、调度等）
├── analytics/              # 数据记录与导出
├── core/                   # 仿真上下文与核心逻辑
├── env/                    # 网格环境与路径规划
├── rl_agents/              # 强化学习智能体与训练管理
├── web_backend/            # FastAPI Web 后端
├── web_frontend/           # Vue3 Web 前端
├── experiments/            # 强化学习对比与严谨实验脚本
├── assignment_submission/  # 课程作业文档（技术方案、实验步骤等）
├── demos/                  # 各类功能演示脚本
├── tests/                  # 单元测试
├── tests_integration/      # 集成测试
├── run_with_gui.py         # GUI 仿真入口
├── run_experiment.sh       # 自动化实验脚本
├── requirements*.txt       # 依赖列表
└── README.md               # 主文档（本文件）
```

---

## 3. 环境与安装

### 3.1 环境要求

- Python 3.8+
- 操作系统：Windows / macOS / Linux
- 可选：NVIDIA GPU（RL 训练加速）
- Node.js 16+（用于 Web 前端）

### 3.2 安装步骤

```bash
# 克隆项目
git clone https://github.com/Dictatora0/CampusFleet-AI.git
cd CampusFleet-AI

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装基础依赖
pip install -r requirements.txt

# 如需 Web 平台
pip install -r requirements-web.txt

# 如需强化学习训练
pip install -r requirements-rl.txt
```

---

## 4. 快速开始

### 4.1 GUI 仿真

基础 GUI 仿真（默认贪心策略）：

```bash
source venv/bin/activate
python run_with_gui.py
```

常用参数：

```bash
python run_with_gui.py \
  --strategy dqn_inference \  # 调度策略：greedy / balanced / hungarian / vrp_batching / mapf_cbs / dqn_inference / ...
  --cars 4 \                 # 车辆数量（推荐 3–6）
  --size 10 \               # 网格大小（推荐 10–15）
  --fps 3                   # 刷新帧率（2–5）
```

示例：

```bash
# VRP 拼单策略
python run_with_gui.py --strategy vrp_batching --cars 4

# MAPF CBS 协调（多车无死锁）
python run_with_gui.py --strategy mapf_cbs --cars 5

# 已训练 DQN 调度策略推理
python run_with_gui.py --strategy dqn_inference --cars 4
```

---

### 4.2 Web 多智能体监控

Web 前后端提供多智能体状态、通信、协作决策与性能的实时监控界面。

#### 启动后端

```bash
cd web_backend
python main.py
# API 文档: http://localhost:8001/api/docs
# WebSocket: ws://localhost:8001/ws/simulation
```

#### 启动前端

```bash
cd web_frontend
npm install        # 首次运行需要
npm run dev
# 前端地址: http://localhost:3000
```

#### 创建并运行仿真（通过 API）

```bash
# 在项目根目录，确保虚拟环境已激活
cd CampusFleet-AI

# 创建仿真实例
curl -X POST http://localhost:8001/api/simulation/create \
  -H "Content-Type: application/json" \
  -d '{
    "grid_size": 10,
    "num_cars": 4,
    "strategy": "GREEDY_NEAREST",
    "enable_logging": true
  }'

# 添加若干随机订单
for i in {1..8}; do
  curl -X POST http://localhost:8001/api/orders/random
  sleep 0.3
done

# 启动仿真（自动步进）
curl -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "start", "params": {"auto_step": true}}'
```

#### 打开多智能体监控面板

浏览器访问：

- 仿真控制台：`http://localhost:3000/`
- 多智能体监控：`http://localhost:3000/multi-agent`

多智能体监控页面提供：

- 顶部统计卡片：车辆数、订单数、通信消息数、完成率等。
- 左侧智能体状态面板：车辆 / 调度 / 环境智能体详细状态。
- 中间通信日志窗口：状态报告、任务分配、完成通知等消息流。
- 右侧协作决策可视化：车辆 → 订单分配、车辆利用率、并行执行数。
- 底部性能指标：完成率、完成/待处理订单、车辆利用率、性能等级。

---

### 4.3 自动化实验脚本

项目提供一键自动化实验脚本，便于生成报告所需数据与图表：

- 脚本：`run_experiment.sh`
- 说明：`README_AUTO_EXPERIMENT.md`

#### 一键运行

```bash
cd CampusFleet-AI
source venv/bin/activate
./run_experiment.sh
```

脚本会自动完成：

- 创建数据目录 `assignment_data/`
- 启动 Web 后端与前端
- 创建仿真并添加订单
- 运行仿真并在 3 个时间点采集数据
- 导出 CSV 运行日志
- 生成 4 张性能分析图表
- 生成实验摘要 `assignment_data/experiment_summary.txt`

执行完成后，可在 `assignment_data/` 中找到：

- `plots/`：完成率趋势、车辆利用率、订单状态分布、性能雷达图
- `csv_exports/simulation_frames.csv`：完整运行日志
- `json_data/*.json`：多时刻性能与协作数据快照
- `screenshots/`：建议保存 GUI 与 Web 界面截图

停止服务：

```bash
./stop_experiment.sh
```

详细说明见 `README_AUTO_EXPERIMENT.md`。

---

## 5. 功能概览

### 5.1 多智能体架构

系统中主要智能体：

- 环境智能体（Environment）：网格地图、障碍物、位置查询。
- 车辆智能体（Vehicle）：执行配送任务，具备感知、决策、行动能力。
- 订单智能体（Order）：管理订单生命周期与统计信息。
- 调度智能体（Scheduler）：集中式任务分配与协作决策。

### 5.2 调度与路径规划

- 传统调度策略：
  - `greedy`：贪心最近车辆
  - `balanced`：负载均衡
  - `hungarian`：匈牙利算法，全局最优匹配
- 优化算法：
  - `vrp_batching`：车辆路径问题（VRP）拼单优化
  - `mapf_cbs`：多智能体路径规划（MAPF），冲突感知搜索（CBS）
- 强化学习策略：
  - DQN / Double DQN 调度智能体
  - PPO 调度智能体

路径规划：

- A\* 最短路径搜索
- 时空 A\* 与 MAPF 协调无碰撞路径
- 避碰策略与死锁避免

### 5.3 Web 监控面板

多智能体监控面板的核心功能（详情见 `web_frontend/README_MULTIAGENT.md`）：

- 智能体状态面板：车辆、调度、环境智能体状态一览。
- 通信日志窗口：最近消息流与各类型消息统计。
- 协作决策可视化：车辆 → 订单分配、车辆利用率、并行执行数。
- 实时性能图表：完成率、订单统计、车辆利用率、性能等级。
- 自动刷新：默认每 2 秒刷新一次，可手动刷新。

### 5.4 Web 界面详细使用说明

Web 界面提供两个主要页面：**仿真控制台**和**多智能体监控面板**。以下详细说明每个页面的数据来源、含义和操作方式。

#### 5.4.1 仿真控制台 (`/`)

**访问地址**: `http://localhost:3000/`

##### 控制面板区域

**预设配置下拉框**

- **功能**: 快速选择预定义的仿真场景
- **选项说明**:
  - `小规模测试`: 10×10 网格，4 辆车，适合快速验证
  - `中等规模演示`: 15×15 网格，5 辆车，适合教学演示
  - `大规模仿真`: 20×20 网格，8 辆车，展示系统扩展性
  - `MAPF协调演示`: 启用 MAPF CBS 路径协调
  - `VRP拼单演示`: 启用 VRP 批量配送优化
- **数据来源**: 前端预定义配置 (`presetConfigs`)

**创建仿真按钮** (蓝色)

- **功能**: 根据当前选择的预设创建新的仿真实例
- **操作**: 点击后向后端发送 `POST /api/simulation/create` 请求
- **响应**: 创建成功后激活其他控制按钮
- **提示**: 每次创建会重置所有状态，清空之前的订单和车辆

**重置按钮** (红色)

- **功能**: 停止当前仿真并清除所有数据
- **触发条件**: 仅在已创建仿真后可用
- **效果**: 需要重新创建仿真才能继续

**启动按钮** (绿色)

- **功能**: 开始自动步进仿真
- **参数**: `auto_step: true`，仿真会按 1 秒间隔自动执行每一步
- **禁用条件**: 未创建仿真或已在运行中
- **API 调用**: `POST /api/simulation/control {"command": "start"}`

**停止按钮** (黄色)

- **功能**: 暂停自动步进
- **效果**: 仿真状态保持，可以再次启动继续
- **禁用条件**: 未运行或未创建仿真

**单步按钮** (灰色)

- **功能**: 手动执行单个仿真步骤
- **用途**: 用于逐步观察系统行为，便于调试
- **禁用条件**: 仿真正在自动运行时不可用
- **API 调用**: `POST /api/simulation/step?steps=1`

##### 统计信息展示

**步数** (Steps)

- **含义**: 当前仿真已执行的时间步数
- **来源**: 后端 `simulation.step`
- **更新频率**: 每步更新一次

**完成订单** (Completed Orders)

- **含义**: 已成功送达的订单总数
- **来源**: 后端 `simulation.statistics.total_completed_orders`
- **计算方式**: 所有车辆完成的订单累加

**活跃车辆** (Active Vehicles)

- **含义**: 当前正在执行任务的车辆数量
- **来源**: 前端计算，统计状态不为 `Idle` 的车辆
- **意义**: 反映系统负载和车辆利用率

**待处理订单** (Pending Orders)

- **含义**: 已创建但尚未分配或完成的订单数
- **来源**: 前端计算，统计状态为 `PENDING` 的订单
- **意义**: 反映系统积压情况

##### 可视化面板

**显示路径按钮** (路径图标)

- **功能**: 切换车辆行驶路径的可视化显示
- **效果**: 显示车辆计划的移动轨迹
- **状态**: 蓝色=已启用，灰色=未启用

**显示网格按钮** (网格图标)

- **功能**: 切换网格线的显示
- **效果**: 显示/隐藏地图背景网格
- **用途**: 便于精确定位坐标

**Canvas 画布**

- **显示内容**:
  - 灰色方块: 障碍物 (不可通行)
  - 橙色圆圈: 车辆当前位置
  - 绿色方块: 订单取货点
  - 蓝色方块: 订单送货点
  - 彩色线条: 车辆规划路径
- **交互**: 点击画布可选中车辆或查看详情

##### 详情面板

**车辆列表**

- 显示所有车辆的实时状态
- **ID**: 车辆编号
- **状态**: 空闲/前往取货/取货中/配送中/送达中
- **位置**: 当前坐标 (x, y)
- **电量**: 剩余电量百分比（颜色：绿>60%，黄 30-60%，红<30%）
- **任务**: 当前执行的订单 ID

**订单列表**

- 显示所有订单的状态
- **订单 ID**: 唯一标识符
- **状态**: 待分配/已分配/已取货/已送达/已取消
- **取货点**: 坐标位置
- **送货点**: 目标位置
- **分配车辆**: 负责配送的车辆 ID
- **优先级**: 1-3 星评级（目前均为 1）

**添加订单区域**

- **手动添加**: 指定取货点和送货点坐标
- **随机订单**: 系统自动生成随机位置的订单
- **优先级选择**: 设置订单优先级（1-3）

---

#### 5.4.2 多智能体监控面板 (`/multi-agent`)

**访问地址**: `http://localhost:3000/multi-agent`

##### 顶部统计卡片（4 个）

**车辆智能体卡片** (🚗 图标)

- **主数值**: 车辆智能体总数
- **来源**: 后端 `GET /api/agents/status` 返回的 `agents.vehicles` 数组长度
- **活跃数**: 状态为 `busy` 的车辆数量
- **含义**: 展示系统中车辆的总体配置和当前工作状态

**订单智能体卡片** (📦 图标)

- **主数值**: 订单智能体总数
- **来源**: 后端 `agents.orders` 数组长度
- **待处理数**: 状态为 `PENDING` 的订单数
- **含义**: 反映订单总量和待分配情况

**通信消息卡片** (📡 图标)

- **主数值**: 累计通信消息总数
- **来源**: 后端 `GET /api/communication/logs` 的 `total_messages`
- **本轮消息**: 当前步骤的消息数
- **含义**: 展示智能体间通信活跃度

**完成率卡片** (📊 图标)

- **主数值**: 订单完成百分比
- **计算**: (已完成订单数 / 总订单数) × 100%
- **来源**: 后端 `GET /api/performance/metrics` 的 `completion_rate`
- **性能等级**: A-F 等级评价
  - A: ≥90%, B: ≥80%, C: ≥70%, D: ≥60%, F: <60%
- **含义**: 系统整体配送效率指标

##### 左侧：智能体状态面板

**刷新按钮** (蓝色)

- **功能**: 手动刷新智能体状态数据
- **API 调用**: `GET /api/agents/status`
- **自动刷新**: 默认每 2 秒自动刷新一次

**车辆智能体标签页**

每个车辆卡片显示：

- **车辆 ID**: 唯一标识符 (例如: 车辆 #0)
- **状态标签**: 空闲(灰色) / 忙碌(绿色)
- **位置**: 当前网格坐标 (x, y)
  - **来源**: `vehicle.position`
  - **含义**: 车辆在地图上的精确位置
- **感知**: 感知范围（格数）
  - **来源**: `vehicle.perception.range`
  - **含义**: 车辆可探测订单的范围，固定为 5 格
- **决策**: 决策方法
  - **来源**: `vehicle.decision.method`
  - **显示**: "A\* pathfinding"（A 星路径规划算法）
  - **含义**: 车辆使用的路径规划算法
- **行动**: 当前行为
  - **来源**: `vehicle.action.current`
  - **状态**: moving(移动中) / idle(空闲)
  - **含义**: 车辆的当前动作状态
- **已完成**: 完成订单数
  - **来源**: `vehicle.completed_orders`
  - **含义**: 该车辆累计完成的订单总数

**调度智能体标签页**

- **策略**: 当前使用的调度算法
  - **来源**: `agents.scheduler.strategy`
  - **可能值**: GREEDY_NEAREST / HUNGARIAN / VRP_BATCHING / MAPF_CBS
- **总分配**: 累计任务分配次数
  - **来源**: `agents.scheduler.total_assignments`
  - **含义**: 调度器执行过的分配决策总数
- **活跃车辆**: 正在工作的车辆数
  - **来源**: `agents.scheduler.active_vehicles`
- **待分配订单**: 等待分配的订单数
  - **来源**: `agents.scheduler.pending_orders`

**环境智能体标签页**

- **网格大小**: 地图尺寸
  - **来源**: `agents.environment.grid_size`
  - **显示**: N×N（例如 15×15）
- **当前步骤**: 仿真执行的步数
  - **来源**: `agents.environment.current_step`
- **总订单数**: 系统创建的订单总数
  - **来源**: `agents.environment.total_orders`
- **已完成**: 成功配送的订单数
  - **来源**: `agents.environment.completed_orders`

##### 中间：通信日志窗口

**刷新按钮** (蓝色)

- **功能**: 手动刷新通信日志
- **API 调用**: `GET /api/communication/logs`

**通信统计条**

- **状态报告**: 车辆定期向调度器汇报位置和状态
- **任务分配**: 调度器向车辆分配新订单

**日志列表**

每条日志包含：

- **时间戳**: 消息产生的精确时间
- **发送者**: 消息来源智能体（例如: Vehicle-0, Scheduler）
- **箭头**: → 表示消息传递方向
- **接收者**: 消息目标智能体
- **消息内容**: 具体通信内容
  - **位置报告**: "Position: (x, y), Status: idle/busy"
  - **任务分配**: "Assigned Order-{订单 ID}"
- **消息类型**:
  - **状态报告** (灰色边框): 车辆 → 调度器的周期性状态更新
  - **任务分配** (绿色边框): 调度器 → 车辆的订单分配通知
- **数据来源**: 后端 `communication_logs` API
- **更新方式**: 实时追加新消息，显示最近 20 条

##### 右侧：协作决策可视化

**刷新按钮** (蓝色)

- **功能**: 手动刷新协作数据
- **API 调用**: `GET /api/collaboration/decisions`

**协作指标**

**车辆利用率进度条**

- **计算**: (活跃车辆数 / 总车辆数) × 100%
- **来源**: `collaboration_metrics.vehicle_utilization`
- **颜色规则**:
  - 绿色: ≥70%（高利用率）
  - 黄色: 40-70%（中等）
  - 红色: <40%（利用率低）
- **含义**: 反映车队整体工作饱和度

**并行执行数**

- **数值**: 同时执行任务的车辆数量
- **来源**: `collaboration_metrics.parallel_execution`
- **含义**: 系统并发处理能力的实时指标

**当前分配列表**

每个分配项显示：

- **车辆 ID → 订单 ID**: 分配关系
- **距离取货点**: 曼哈顿距离（格数）
  - **计算**: |车辆 x - 取货点 x| + |车辆 y - 取货点 y|
  - **来源**: 后端实时计算
- **预计步数**: 车辆到达取货点所需步数
  - **来源**: `eta_steps`（车辆当前路径长度）
- **决策理由**: "Optimal assignment"（最优分配）
- **数据来源**: 后端 `assignments` 数组
- **空状态**: 显示"暂无活跃分配"当所有车辆空闲时

##### 底部：性能指标面板

**刷新按钮** (蓝色)

- **功能**: 手动刷新性能数据
- **API 调用**: `GET /api/performance/metrics`

**核心指标**

**完成率**

- **显示**: 百分比进度条 + 数值
- **计算**: (已完成订单 / 总订单) × 100%
- **来源**: `metrics.completion_rate`
- **颜色**: 根据完成率显示不同颜色

**已完成订单**

- **数值**: 成功配送的订单绝对数量
- **来源**: `metrics.completed_orders`

**总订单数**

- **数值**: 系统创建的所有订单总数
- **来源**: `metrics.total_orders`

**待处理订单**

- **数值**: 未完成（待分配+进行中）的订单数
- **来源**: `metrics.pending_orders`

**车辆利用率**

- **显示**: 百分比
- **来源**: `metrics.vehicle_utilization`

**性能等级**

- **显示**: A / B / C / D / F 大字母评级
- **颜色**:
  - A/B: 绿色（优秀/良好）
  - C: 黄色（中等）
  - D/F: 红色（较差/不及格）
- **来源**: 后端 `performance_grade` 综合评估

---

#### 5.4.3 数据更新机制

**自动刷新**

- 多智能体监控面板默认每 2 秒自动调用 API 更新数据
- 使用 `setInterval` 定时器实现
- 可通过各面板的"刷新"按钮手动立即更新

**WebSocket 实时推送**

- 建立 `ws://localhost:8001/ws/simulation` 连接
- 服务端主动推送仿真状态变化
- 前端收到推送后更新可视化显示
- 连接状态在顶部导航栏显示（绿点=已连接，红点=断开）

**数据流向**

```
后端API ──→ HTTP请求 ──→ 前端Store ──→ Vue组件 ──→ 用户界面
   ↓
WebSocket ──→ 实时推送 ──→ 前端监听 ──→ 状态更新 ──→ 界面刷新
```

---

#### 5.4.4 常见操作流程

**标准实验流程**:

1. 访问仿真控制台 (`/`)
2. 选择预设配置（如"中等规模演示"）
3. 点击"创建仿真"
4. 添加 3-5 个随机订单
5. 点击"启动"开始自动仿真
6. 切换到多智能体监控页面 (`/multi-agent`)
7. 观察各指标变化，截取关键截图
8. 仿真稳定运行后点击"停止"
9. 导出数据用于分析

**调试观察流程**:

1. 创建小规模仿真（10×10, 4 车）
2. 添加 1-2 个订单
3. 使用"单步"按钮逐步执行
4. 在智能体状态面板观察每步变化
5. 在通信日志查看消息交互
6. 在 Canvas 上查看路径规划

**性能测试流程**:

1. 使用"大规模仿真"预设
2. 添加 10 个以上订单
3. 启动仿真并运行至少 50 步
4. 在性能指标面板记录完成率
5. 观察车辆利用率变化趋势
6. 导出 CSV 数据进行详细分析

---

## 6. 实验与评估

### 6.1 多智能体系统功能展示实验（推荐）

本实验面向课程作业与系统展示，重点是**系统功能、协作机制、Web 可视化和自动化数据采集**，不强调算法对比。

完整步骤整理在：`assignment_submission/实验步骤.md`，这里给出概要版流程：

#### 6.1.1 多场景 GUI 功能演示

通过 `run_with_gui.py` 在不同规模与策略下运行仿真，展示：

- 小规模基础场景：4 车 + 少量订单，展示基本协作与路径规划。
- 中等规模场景：6 车 + 更多订单，展示系统扩展性与车辆利用率。
- AI 调度场景：使用 `dqn_inference` 策略，展示强化学习调度在系统中的实际效果（作为一种策略，而非算法对比实验）。

典型命令示例：

```bash
# 场景 1：小规模基础功能
python run_with_gui.py --strategy greedy --cars 4 --size 10 --fps 3

# 场景 2：中等规模扩展性
python run_with_gui.py --strategy balanced --cars 6 --size 15 --fps 4

# 场景 3：AI 智能调度
python run_with_gui.py --strategy dqn_inference --cars 5 --size 12 --fps 3
```

建议在每个场景中手动截取 GUI 截图，保存到 `assignment_data/screenshots/` 用于报告与展示。

#### 6.1.2 Web 多智能体监控与协作可视化

结合第 4.2 节的步骤，通过 Web 多智能体监控页面展示：

- 顶部统计卡片：整体负载与完成率。
- 智能体状态面板：车辆 / 调度 / 环境三类智能体的实时状态。
- 通信日志窗口：任务分配与状态报告的消息流。
- 协作决策可视化：任务分配关系、车辆利用率、并行执行情况。

建议在仿真运行稳定后，截取以下 3–4 张关键截图：

- 完整监控面板
- 某辆车的状态详情
- 通信日志高峰时刻
- 协作决策与车辆利用率面板

#### 6.1.3 自动化数据采集与图表生成

为避免手工操作出错，推荐使用自动化脚本 `run_experiment.sh` 完成数据采集与图表生成（详见 `README_AUTO_EXPERIMENT.md`）：

```bash
source venv/bin/activate
./run_experiment.sh
```

脚本会：

- 在 `assignment_data/` 下创建统一的数据与图表目录结构。
- 自动启动 Web 后端与前端，并创建仿真、添加订单、运行一段时间。
- 在多个时间点调用 Web API 采集性能指标与协作数据（JSON）。
- 通过内置 Python 脚本生成 4 张高分辨率图表：
  - 完成率随时间变化
  - 车辆利用率变化
  - 最终订单状态分布
  - 综合性能雷达图
- 生成一份 `experiment_summary.txt`，汇总关键指标与文件列表。

最终，你可以直接从以下位置整理报告素材：

- `assignment_data/plots/`：性能分析图表（可直接插入报告）。
- `assignment_data/csv_exports/simulation_frames.csv`：完整运行日志，可做进一步统计分析。
- `assignment_data/json_data/*.json`：多时刻性能、智能体状态、协作决策与通信日志快照。
- `assignment_data/screenshots/`：GUI + Web 截图（需要手动保存）。

> 推荐写作方式：以“系统功能演示 + Web 可视化 + 自动化数据采集”为主线，只在需要时简要提及使用了强化学习调度策略，而不展开算法对比。

### 6.2 强化学习对比实验（可选，高级）

如果需要从科研或算法验证角度，对比不同 RL 调度策略（如 Standard DQN 与 Double DQN），可以使用 `experiments/` 目录中的脚本：

- 快速对比（单次运行）：`experiments/rl_comparison.py`
- 严谨多次实验：`experiments/rl_comparison_rigorous.py`

该部分会运行较长时间，仅在需要撰写强化学习相关论文或深入算法分析时使用。详细实验设计、输出文件结构与图表说明参见：

- `experiments/README_RIGOROUS_EXPERIMENT.md`

---

## 7. 文档索引

| 文档                      | 位置                                        | 说明                           |
| ------------------------- | ------------------------------------------- | ------------------------------ |
| 课程作业技术方案          | `assignment_submission/技术方案.md`         | 系统架构、智能体设计、实验结果 |
| 实验步骤方案              | `assignment_submission/实验步骤.md`         | 完整功能展示与数据采集步骤     |
| 作业提交说明              | `assignment_submission/README.md`           | 作业材料列表与快速指引         |
| 系统使用指南              | `assignment_submission/使用指南.md`         | 环境安装、运行方式、参数调优   |
| Web 快速使用指南          | `QUICK_START_WEB.md`                        | Web 后端/前端启动与面板说明    |
| 多智能体 Web 界面使用指南 | `web_frontend/README_MULTIAGENT.md`         | 多智能体监控面板详细说明       |
| 自动化实验脚本使用指南    | `README_AUTO_EXPERIMENT.md`                 | `run_experiment.sh` 说明       |
| 严谨 RL 实验文档          | `experiments/README_RIGOROUS_EXPERIMENT.md` | 论文级对比实验设计与结果       |
| 强化学习报告模版          | `experiments/REPORT_TEMPLATE.md`            | 报告写作结构模版               |

---

## 8. 测试与开发

### 8.1 单元测试与集成测试

单元测试：

```bash
# 运行所有单元测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

集成测试：

```bash
# 基础系统集成测试
python tests_integration/test_system.py

# 强化学习系统集成测试
python tests_integration/test_rl_system.py

# 运行全部集成测试
pytest tests_integration/
```

### 8.2 代码风格与格式化

```bash
# 格式化代码
black . --line-length 100
isort . --profile black

# 代码检查
flake8 . --max-line-length=100
```

---

## 9. 许可证

本项目采用 MIT License 开源许可协议，详情见 `LICENSE` 文件。
