# 🚀 自动化实验脚本使用指南

## 快速开始

一键执行完整实验流程：

```bash
cd "/Users/lifulin/Desktop/CampusFleet AI"
./run_experiment.sh
```

## 脚本功能

`run_experiment.sh` 会自动完成以下任务：

### ✅ 自动执行的部分

1. **环境准备** - 创建数据保存目录
2. **启动服务** - 自动启动 Web 后端和前端
3. **创建仿真** - 配置并启动 4 车 10 订单仿真
4. **数据采集** - 在 3 个时间点采集运行数据
5. **数据导出** - 导出完整 CSV 运行日志
6. **生成图表** - 自动生成 4 张性能分析图表
7. **生成摘要** - 创建实验数据摘要文档

### ⚠️ 需要手动完成的部分

1. **Web 界面截图**

   - 访问：http://localhost:3000/multi-agent
   - 截取：完整面板、智能体状态、通信日志、协作决策

2. **GUI 仿真截图**

   - 运行以下命令并截图：

   ```bash
   # 场景 1：小规模测试
   python run_with_gui.py --strategy greedy --cars 4 --size 10 --fps 3

   # 场景 2：中等规模测试
   python run_with_gui.py --strategy balanced --cars 6 --size 15 --fps 4

   # 场景 3：AI 智能调度
   python run_with_gui.py --strategy dqn_inference --cars 5 --size 12 --fps 3
   ```

## 生成的数据文件

执行完毕后，所有数据保存在 `assignment_data/` 目录：

```
assignment_data/
├── plots/                          # 📊 可视化图表
│   ├── completion_rate_trend.png   #   完成率趋势图
│   ├── vehicle_utilization.png     #   车辆利用率图
│   ├── order_status_distribution.png # 订单状态分布图
│   └── performance_radar.png       #   性能雷达图
│
├── json_data/                      # 📁 JSON 快照数据
│   ├── agents_step20.json          #   时刻 1 智能体状态
│   ├── agents_step60.json          #   时刻 2 智能体状态
│   ├── agents_step100.json         #   时刻 3 智能体状态
│   ├── comm_stepX.json × 3         #   通信日志快照
│   ├── collab_stepX.json × 3       #   协作决策快照
│   └── perf_stepX.json × 3         #   性能指标快照
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

- ✅ 4 张自动生成的性能分析图表
- ✅ 完整的 CSV 运行日志（可用于进一步分析）
- ✅ 3 个时间点的详细 JSON 快照数据
- ✅ 实验数据摘要文档
- 📸 4-7 张 Web 界面截图（需手动）
- 📸 3 张 GUI 仿真截图（需手动）

---

**祝实验顺利！** 🎉
