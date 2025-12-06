# 🚀 自动化实验脚本使用指南

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
