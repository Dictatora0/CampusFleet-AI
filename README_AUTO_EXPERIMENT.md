# 🚀 自动化实验脚本使用指南

---

## 📋 完整待办清单（用于撰写报告）

### ✅ 阶段 1：实验数据采集（15-20 分钟）

#### 必做实验（对比两种核心策略）

- [ ] **实验 1：贪心最近策略（基线）**

  ```bash
  ./run_experiment.sh 15 6 20 GREEDY_NEAREST
  ```

  - ⏱️ 等待约 2 分钟自动完成
  - 📂 数据保存在 `assignment_data/`（会自动创建）
  - ✅ 检查生成的 4-5 张图表

- [ ] **实验 2：拍卖机制（多智能体协商亮点）**
  ```bash
  ./stop_experiment.sh  # 先停止上一个实验的服务
  ./run_experiment.sh 15 6 20 AUCTION_CNP
  ```
  - ⏱️ 等待约 2 分钟自动完成
  - 📂 需要手动重命名数据目录以保留：
    ```bash
    mv assignment_data assignment_data_AUCTION_CNP
    ```
  - ✅ 检查是否生成了拍卖成本分布图（第 6 张图）

#### 可选实验（如果报告需要三种策略对比）

- [ ] **实验 3：强化学习调度（可选）**

  ```bash
  ./stop_experiment.sh
  ./run_experiment.sh 15 6 20 RL_SCHEDULER
  ```

  - 📂 完成后重命名：`mv assignment_data assignment_data_RL_SCHEDULER`

- [ ] **停止所有服务**
  ```bash
  ./stop_experiment.sh
  ```

---

### 📸 阶段 2：Web 界面截图（10-15 分钟）

**重要提示**：每次运行实验时在浏览器中截图，建议在"实验 2（AUCTION_CNP）"时完成所有截图。

#### 2.1 多智能体监控面板（4 张）

在实验运行时访问：http://localhost:3000/multi-agent

- [ ] 截图 1：完整监控面板（整体布局，显示所有模块）
- [ ] 截图 2：智能体状态详情（展开车辆/调度器/环境的详细信息）
- [ ] 截图 3：通信日志窗口（显示消息交互流，如任务分配消息）
- [ ] 截图 4：协作决策可视化（任务分配图表或车辆利用率）

保存命名建议：`monitor_panel_full.png`, `agent_details.png`, `comm_logs.png`, `collab_viz.png`

#### 2.2 拍卖日志面板（2-3 张，AUCTION_CNP 专属）

访问：http://localhost:3000/

- [ ] 截图 5：拍卖日志面板全貌（显示多轮拍卖记录）
- [ ] 截图 6：单条拍卖详情（展示竞标车辆、成本、中标结果）
- [ ] 截图 7（可选）：拍卖统计信息（总拍卖次数、成功率等）

保存命名建议：`auction_panel.png`, `auction_detail.png`, `auction_stats.png`

#### 2.3 充电系统可视化（2-3 张）

访问：http://localhost:3000/

- [ ] 截图 8：Canvas 充电站整体视图（显示充电站位置和车辆分布）
- [ ] 截图 9：充电站详情（鼠标悬停 Tooltip，显示使用率、排队情况）
- [ ] 截图 10：车辆电量颜色编码（截取显示不同电量车辆的区域）
  - 绿色 = 高电量，黄色 = 中等，橙色 = 低电量，红色 = 严重低电

保存命名建议：`canvas_charging_stations.png`, `charging_tooltip.png`, `battery_colors.png`

**所有截图保存位置**：`assignment_data_AUCTION_CNP/screenshots/`

---

### 🎮 阶段 3：GUI 仿真截图（5-10 分钟）

运行本地 GUI 并截取不同策略的仿真画面。

#### 3.1 贪心策略演示

```bash
python run_with_gui.py
# 在菜单中选择：GREEDY_NEAREST
```

- [ ] 截图 11：GUI 初始状态（显示地图、车辆、订单）
- [ ] 截图 12：GUI 运行中（车辆正在执行任务，显示路径）
- [ ] 截图 13（可选）：GUI 充电场景（车辆前往充电站）

保存命名建议：`gui_greedy_init.png`, `gui_greedy_running.png`, `gui_greedy_charging.png`

#### 3.2 拍卖机制演示

```bash
python run_with_gui.py
# 在菜单中选择：AUCTION_CNP
```

- [ ] 截图 14：GUI 拍卖策略初始状态
- [ ] 截图 15：GUI 拍卖策略运行中

保存命名建议：`gui_auction_init.png`, `gui_auction_running.png`

#### 3.3 强化学习演示（可选）

```bash
python run_with_gui.py
# 在菜单中选择：RL_SCHEDULER
```

- [ ] 截图 16（可选）：GUI 强化学习策略运行

**所有 GUI 截图保存位置**：`assignment_data_AUCTION_CNP/screenshots/gui/`

---

### 📊 阶段 4：整理报告素材（10 分钟）

#### 4.1 检查自动生成的图表

**贪心策略目录**（`assignment_data_GREEDY_NEAREST/plots/`）：

- [ ] ✅ completion_rate_trend.png（完成率趋势）
- [ ] ✅ vehicle_utilization.png（车辆利用率）
- [ ] ✅ order_status_distribution.png（订单状态分布）
- [ ] ✅ performance_radar.png（性能雷达图）
- [ ] ✅ charging_station_utilization.png（充电站利用率）

**拍卖策略目录**（`assignment_data_AUCTION_CNP/plots/`）：

- [ ] ✅ 以上 5 张基础图表
- [ ] ✅ auction_cost_distribution.png（拍卖成本分布，专属）

#### 4.2 整理 JSON 数据文件

检查每个策略目录的 `json_data/` 文件夹是否包含：

- [ ] agents_step20/60/100.json（智能体状态）
- [ ] comm_step20/60/100.json（通信日志）
- [ ] collab_step20/60/100.json（协作决策）
- [ ] perf_step20/60/100.json（性能指标）
- [ ] charging_step20/60/100.json（充电站状态）
- [ ] auction_step20/60/100.json（拍卖日志，仅 AUCTION_CNP）

#### 4.3 阅读实验摘要

- [ ] 打开并阅读：`assignment_data/experiment_summary.txt`
- [ ] 记录关键数值（完成率、车辆利用率等）用于报告

#### 4.4 创建报告素材目录结构

```bash
mkdir -p report_materials
cp -r assignment_data_GREEDY_NEAREST/plots report_materials/plots_greedy
cp -r assignment_data_AUCTION_CNP/plots report_materials/plots_auction
cp -r assignment_data_AUCTION_CNP/screenshots report_materials/screenshots
```

- [ ] 整理完成，确认所有素材齐全

---

### ✍️ 阶段 5：撰写报告（参考模板）

使用生成的图表和截图，按以下结构撰写报告第 6 章。

#### 6.1 实验设置（1 段）

- [ ] 描述实验配置（15×15 网格，6 车，20 订单）
- [ ] 说明运行了哪些策略（GREEDY_NEAREST、AUCTION_CNP）
- [ ] 提到数据采集方式（自动化脚本，3 个时间点）

#### 6.2 调度策略定量对比（3-4 段 + 3 张图）

- [ ] **完成率对比**（插入 `completion_rate_trend.png`）
  - 描述两种策略的完成率曲线差异
  - 分析哪种策略在不同阶段表现更好
- [ ] **车辆利用率对比**（插入 `vehicle_utilization.png`）
  - 对比两种策略的资源使用效率
  - 说明拍卖机制如何均衡负载
- [ ] **综合性能对比**（插入 `performance_radar.png`）
  - 多维度对比（完成率、利用率、效率）
  - 总结各策略优劣

#### 6.3 拍卖机制深入分析（2-3 段 + 2 张图/截图）

- [ ] **拍卖成本分布分析**（插入 `auction_cost_distribution.png`）
  - 描述拍卖成本的分布特点
  - 说明平均成本的意义（距离、电量、负载的折中）
- [ ] **拍卖过程可视化**（插入拍卖日志面板截图）
  - 展示实时竞标过程
  - 说明合同网协议（CNP）的工作原理

#### 6.4 充电系统分析（2 段 + 2 张图/截图）

- [ ] **充电站利用率**（插入 `charging_station_utilization.png`）
  - 描述充电站使用情况随时间的变化
  - 分析与任务负载的关系
- [ ] **充电系统可视化**（插入 Canvas 充电站截图）
  - 展示充电站位置分布
  - 说明车辆电量管理（四级颜色编码）
  - 提及排队管理和容量控制

#### 6.5 多智能体监控与可视化（1-2 段 + 3-4 张截图）

- [ ] **监控面板功能**（插入监控面板截图）
  - 智能体状态监控
  - 通信日志可视化
  - 协作决策展示
- [ ] **GUI 仿真对比**（插入 GUI 截图）
  - 对比不同策略下的车辆行为
  - 展示路径规划和充电决策

#### 6.6 结论（1 段）

- [ ] 总结三种策略的特点和适用场景
- [ ] 强调系统的多智能体协作、拍卖机制、充电管理等亮点
- [ ] 说明可视化工具对系统分析的价值

---

### 🎯 最终检查清单

#### 数据完整性

- [ ] 至少有 2 个策略的完整实验数据
- [ ] 每个策略有 4-6 张自动生成的图表
- [ ] 有充足的 Web 界面截图（8-10 张）
- [ ] 有 GUI 仿真截图（3-5 张）

#### 报告内容

- [ ] 报告第 6 章已完成初稿
- [ ] 所有图表都已插入并标注图号
- [ ] 所有数值引用准确（来自 experiment_summary.txt）
- [ ] 文字描述与图表内容匹配

#### 演示准备（如需要）

- [ ] 能够运行 `./debug_web.sh` 快速启动演示
- [ ] 准备好解释拍卖机制的工作原理
- [ ] 准备好展示充电系统的可视化效果

---

## 快速开始

一键执行完整实验流程（默认 10×10 网格，4 车，10 订单，GREEDY_NEAREST）：

```bash
cd "/Users/lifulin/Desktop/CampusFleet AI"
./run_experiment.sh
```

也可以通过参数控制规模与调度策略，推荐依次对比三种核心策略：

```bash
# 1️⃣ 启发式基线：贪心最近车辆
./run_experiment.sh 15 6 20 GREEDY_NEAREST

# 2️⃣ 多智能体协商：拍卖机制（合同网协议 CNP）
./run_experiment.sh 15 6 20 AUCTION_CNP

# 3️⃣ AI 智能调度：强化学习调度（RL_SCHEDULER）
./run_experiment.sh 15 6 20 RL_SCHEDULER
```

## 脚本功能

`run_experiment.sh` 会自动完成以下任务：

### ✅ 自动执行的部分

1. **环境准备** - 创建数据保存目录
2. **启动服务** - 自动启动 Web 后端和前端
3. **创建仿真** - 配置并启动仿真实例（默认 4 车 10 订单，可通过命令行参数调整网格/车辆/订单/调度策略）
4. **数据采集** - 在 3 个时间点采集运行数据
   - 智能体状态、通信日志、协作决策、性能指标
   - **充电站状态**（充电位使用率、排队情况）
   - **拍卖日志**（AUCTION_CNP 策略专属，记录竞标过程）
5. **数据导出** - 导出完整 CSV 运行日志
6. **生成图表** - 自动生成 4-6 张性能分析图表
   - 基础图表（4 张）：完成率趋势、车辆利用率、订单分布、性能雷达
   - **充电站利用率图**（展示充电系统亮点）
   - **拍卖成本分布图**（AUCTION_CNP 策略专属，展示拍卖机制）
7. **生成摘要** - 创建实验数据摘要文档

### ⚠️ 需要手动完成的部分

1. **Web 界面截图**

   - **多智能体监控面板**：http://localhost:3000/multi-agent

     - 截取：完整面板、智能体状态、通信日志、协作决策

   - **拍卖日志面板**（AUCTION_CNP 策略专属）：http://localhost:3000/

     - 截取：拍卖日志面板（Auction Log Panel）
     - 截取：竞标成本与中标车辆信息

   - **充电系统可视化**：http://localhost:3000/
     - 截取：Canvas 充电站状态（鼠标悬停查看详情）
     - 截取：车辆电量颜色编码（绿/黄/橙/红）

2. **GUI 仿真截图**

   - 运行以下场景并截图（启动后在菜单中选择对应策略）：

   ```bash
   # 场景 1：贪心基线（GREEDY_NEAREST）
   python run_with_gui.py    # 在菜单中选择 GREEDY_NEAREST

   # 场景 2：拍卖机制展示（AUCTION_CNP）
   python run_with_gui.py    # 在菜单中选择 AUCTION_CNP

   # 场景 3：强化学习调度展示（RL_SCHEDULER）
   python run_with_gui.py    # 在菜单中选择 RL_SCHEDULER
   ```

## 生成的数据文件

执行完毕后，所有数据保存在 `assignment_data/` 目录：

```
assignment_data/
├── plots/                          # 📊 可视化图表
│   ├── completion_rate_trend.png   #   完成率趋势图
│   ├── vehicle_utilization.png     #   车辆利用率图
│   ├── order_status_distribution.png # 订单状态分布图
│   ├── performance_radar.png       #   性能雷达图
│   ├── charging_station_utilization.png # 充电站利用率图 [NEW]
│   └── auction_cost_distribution.png    # 拍卖成本分布（AUCTION_CNP专属）[NEW]
│
├── json_data/                      # 📁 JSON 快照数据
│   ├── agents_step20.json          #   时刻 1 智能体状态
│   ├── agents_step60.json          #   时刻 2 智能体状态
│   ├── agents_step100.json         #   时刻 3 智能体状态
│   ├── comm_stepX.json × 3         #   通信日志快照
│   ├── collab_stepX.json × 3       #   协作决策快照
│   ├── perf_stepX.json × 3         #   性能指标快照
│   ├── charging_stepX.json × 3     #   充电站状态快照 [NEW]
│   └── auction_stepX.json × 3      #   拍卖日志快照（AUCTION_CNP专属）[NEW]
│
├── csv_exports/                    # 📄 CSV 导出数据
│   └── simulation_frames.csv       #   完整运行日志
│
├── screenshots/                    # 📸 截图保存位置（手动）
│   └── (请将截图保存到这里)
│
├── experiment_summary.txt          # 📝 实验数据摘要
├── backend.log                     # 后端日志
└── frontend.log                    # 前端日志
```

## 停止服务

实验完成后停止 Web 服务：

```bash
./stop_experiment.sh
```

或手动停止：

```bash
pkill -f "web_backend/main.py"
pkill -f "vite"
```

## 常见问题

### Q: 脚本执行失败？

**A**: 检查以下几点：

1. 是否在项目根目录执行
2. 是否已安装所有 Python 依赖 (`pip install -r requirements.txt`)
3. 是否已安装前端依赖 (`cd web_frontend && npm install`)
4. 端口 8001 和 3000 是否被占用

### Q: 图表生成失败？

**A**:

- 确保安装了 matplotlib: `pip install matplotlib`
- 检查是否有中文字体问题（可能需要调整字体设置）

### Q: 如何查看生成的图表？

**A**:

```bash
open assignment_data/plots/
```

### Q: 如何重新运行实验？

**A**:

1. 先停止服务：`./stop_experiment.sh`
2. 删除旧数据：`rm -rf assignment_data`
3. 重新运行：`./run_experiment.sh`

## 实验流程时间

- 总耗时：约 **3-5 分钟**
  - 环境准备：10 秒
  - 服务启动：15 秒
  - 仿真运行：100 秒（采集 3 个时间点数据）
  - 图表生成：10 秒

## 下一步

1. 查看生成的实验摘要：

   ```bash
   cat assignment_data/experiment_summary.txt
   ```

2. 浏览生成的图表：

   ```bash
   open assignment_data/plots/
   ```

3. 在浏览器中查看 Web 监控界面并截图：

   ```
   http://localhost:3000/multi-agent
   ```

4. 运行 GUI 场景测试并截图（见上方命令）

5. 将所有材料整理到实验报告中

## 报告素材清单

执行完所有步骤后，你将拥有：

- ✅ **4-6 张自动生成的性能分析图表**（可直接用于报告中的结果分析）
  - 基础图表（4 张）：完成率趋势、车辆利用率、订单状态分布、性能雷达图
  - 充电系统图表（1 张）：充电站利用率变化
  - 拍卖机制图表（1 张，AUCTION_CNP 专属）：拍卖成本分布
- ✅ 完整的 CSV 运行日志（可用于进一步分析）
- ✅ 3 个时间点的详细 JSON 快照数据（包括充电站状态和拍卖日志）
- ✅ 实验数据摘要文档
- 📸 **6-10 张 Web 界面截图**（需手动，包含拍卖日志和充电系统）
- 📸 **3 张 GUI 仿真截图**（需手动）

💡 **报告撰写建议**：

- **调度策略对比**：使用基础图表对比三种策略（GREEDY_NEAREST / AUCTION_CNP / RL_SCHEDULER）：
  - 完成率趋势图：展示不同策略的订单完成效率差异
  - 车辆利用率图：对比车辆资源使用情况
  - 性能雷达图：多维度综合性能对比
- **多智能体协商亮点**：使用 AUCTION_CNP 专属图表和截图：
  - 拍卖成本分布图：展示拍卖机制的成本优化效果
  - 拍卖日志面板截图：展示实时竞标过程和中标车辆
  - 说明合同网协议（CNP）如何实现分布式任务分配
- **充电系统亮点**：使用充电系统图表和截图：
  - 充电站利用率图：展示充电站资源管理效果
  - Canvas 充电站截图：展示充电位使用、排队情况（鼠标悬停 Tooltip）
  - 车辆电量颜色编码截图：展示智能电量管理（绿/黄/橙/红四级预警）
- **多智能体监控**：结合监控界面截图，说明系统具备：
  - 智能体状态监控（车辆、调度、环境）
  - 通信日志可视化（消息交互过程）
  - 协作决策可视化（任务分配、车辆利用率）
- **GUI 可视化**：结合 GUI 截图，展示：
  - 订单取/送货点路径规划
  - 车辆实时状态与电量变化
  - 充电站位置与使用情况

---

**祝实验顺利！** 🎉
