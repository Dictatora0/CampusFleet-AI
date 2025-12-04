# 🧪 自动化实验脚本使用指南

## 📖 概述

`run_experiment.sh` 是一个全自动的多智能体系统功能展示实验脚本，可以一键完成从环境准备到数据分析的完整流程。

---

## 🚀 快速开始

### 基础用法

```bash
# 使用默认配置运行
./run_experiment.sh

# 自定义配置运行
./run_experiment.sh <网格大小> <车辆数> <订单数> <调度策略>
```

### 示例

```bash
# 1. 小规模测试（默认）
./run_experiment.sh
# 等同于: ./run_experiment.sh 10 4 10 GREEDY_NEAREST

# 2. 中等规模测试
./run_experiment.sh 15 6 15 BALANCED

# 3. 大规模测试
./run_experiment.sh 20 8 20 HUNGARIAN

# 4. MAPF 协调测试
./run_experiment.sh 12 5 12 MAPF_CBS

# 5. VRP 批量优化测试
./run_experiment.sh 15 6 15 VRP_BATCHING
```

---

## ⚙️ 配置参数

| 参数位置 | 参数名称 | 默认值         | 说明           | 可选值    |
| -------- | -------- | -------------- | -------------- | --------- |
| 第 1 个  | 网格大小 | 10             | 地图尺寸 (N×N) | 5-30 推荐 |
| 第 2 个  | 车辆数量 | 4              | 配送车辆数     | 2-10 推荐 |
| 第 3 个  | 订单数量 | 10             | 随机订单数     | 5-30 推荐 |
| 第 4 个  | 调度策略 | GREEDY_NEAREST | 任务分配算法   | 见下表    |

### 调度策略说明

| 策略名称         | 说明                 | 适用场景           |
| ---------------- | -------------------- | ------------------ |
| `GREEDY_NEAREST` | 贪心最近车辆         | 快速响应，小规模   |
| `BALANCED`       | 负载均衡             | 均衡利用，中规模   |
| `HUNGARIAN`      | 匈牙利算法           | 全局最优，中等规模 |
| `VRP_BATCHING`   | 车辆路径问题批量优化 | 多订单拼单         |
| `MAPF_CBS`       | 多智能体路径规划     | 路径冲突避免       |

---

## 📊 实验流程

脚本自动执行以下 7 个步骤：

### 1️⃣ 环境准备 (步骤 1/7)

- ✅ 检查必要依赖 (curl, python3, npm)
- ✅ 检查虚拟环境
- ✅ 创建数据目录结构

### 2️⃣ 启动后端 (步骤 2/7)

- ✅ 启动 FastAPI 后端服务
- ✅ 自动重试检测 (最多 10 次)
- ✅ 错误时显示日志尾部

### 3️⃣ 启动前端 (步骤 3/7)

- ✅ 检查并安装 npm 依赖
- ✅ 启动 Vite 开发服务器
- ✅ 自动检测服务就绪 (最多 20 次)

### 4️⃣ 创建仿真 (步骤 4/7)

- ✅ 使用自定义参数创建仿真
- ✅ 添加指定数量随机订单
- ✅ 启动自动步进模式

### 5️⃣ 数据采集 (步骤 5/7)

采集 3 个时间点的数据：

- 📸 **时刻 1** (步骤 ~20): 初期数据
- 📸 **时刻 2** (步骤 ~60): 中期数据
- 📸 **时刻 3** (步骤 ~100): 后期数据

每个时刻采集：

- `agents_stepX.json` - 智能体状态
- `comm_stepX.json` - 通信日志
- `collab_stepX.json` - 协作决策
- `perf_stepX.json` - 性能指标

### 6️⃣ 停止仿真 (步骤 6/7)

- ✅ 发送停止命令
- ✅ 导出完整 CSV 运行日志

### 7️⃣ 生成图表 (步骤 7/7)

自动生成 4 张高质量图表：

- 📈 `completion_rate_trend.png` - 完成率趋势
- 📊 `vehicle_utilization.png` - 车辆利用率
- 🥧 `order_status_distribution.png` - 订单状态分布
- 🎯 `performance_radar.png` - 性能雷达图

---

## 📂 输出文件结构

```
assignment_data/
├── screenshots/              # 手动截图保存目录
├── json_data/               # 原始JSON数据
│   ├── agents_step20.json
│   ├── agents_step60.json
│   ├── agents_step100.json
│   ├── comm_step20.json
│   ├── comm_step60.json
│   ├── comm_step100.json
│   ├── collab_step20.json
│   ├── collab_step60.json
│   ├── collab_step100.json
│   ├── perf_step20.json
│   ├── perf_step60.json
│   └── perf_step100.json
├── csv_exports/             # CSV格式数据
│   └── simulation_frames.csv
├── plots/                   # 可视化图表
│   ├── completion_rate_trend.png
│   ├── vehicle_utilization.png
│   ├── order_status_distribution.png
│   └── performance_radar.png
├── backend.log              # 后端服务日志
├── frontend.log             # 前端服务日志
├── experiment_summary.txt   # 实验摘要报告
└── generate_plots.py        # 绘图脚本
```

---

## 🛠️ 依赖检查

脚本会自动检查以下依赖：

| 依赖      | 用途     | 安装方法               |
| --------- | -------- | ---------------------- |
| `curl`    | API 请求 | macOS 已内置           |
| `python3` | 后端服务 | `brew install python3` |
| `npm`     | 前端构建 | `brew install node`    |

如果缺少依赖，脚本会提示并退出。

---

## 🔒 错误处理

### 自动清理机制

脚本设置了错误陷阱 (`trap cleanup ERR INT TERM`)：

- ✅ 遇到错误自动停止所有服务
- ✅ 清理后台进程
- ✅ Ctrl+C 中断也会触发清理

### 重试机制

**后端启动检测** (最多 10 次):

```bash
# 每秒检查一次，最多10秒
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    # 成功
fi
```

**前端启动检测** (最多 20 次):

```bash
# 每秒检查一次，最多20秒
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    # 成功
fi
```

### 常见错误

| 错误信息              | 原因                  | 解决方法               |
| --------------------- | --------------------- | ---------------------- |
| `❌ 缺少必要依赖`     | 缺少 curl/python3/npm | 安装缺失依赖           |
| `❌ 虚拟环境不存在`   | 未创建 venv           | 运行安装命令           |
| `❌ 后端服务启动失败` | 端口占用或代码错误    | 检查日志 `backend.log` |
| `❌ 仿真创建失败`     | API 错误              | 检查后端日志           |
| `找不到数据文件`      | 采集时间不足          | 延长运行时间           |

---

## 🎯 使用技巧

### 1. 快速测试

```bash
# 最小配置，快速验证
./run_experiment.sh 5 2 5 GREEDY_NEAREST
```

### 2. 性能对比实验

```bash
# 测试不同策略
./run_experiment.sh 15 5 15 GREEDY_NEAREST
./run_experiment.sh 15 5 15 BALANCED
./run_experiment.sh 15 5 15 HUNGARIAN
```

### 3. 扩展性测试

```bash
# 测试不同规模
./run_experiment.sh 10 4 10
./run_experiment.sh 15 6 15
./run_experiment.sh 20 8 20
```

### 4. 查看实时日志

```bash
# 终端1: 运行实验
./run_experiment.sh

# 终端2: 实时查看后端日志
tail -f assignment_data/backend.log

# 终端3: 实时查看前端日志
tail -f assignment_data/frontend.log
```

### 5. 自定义时间配置

编辑脚本中的时间参数：

```bash
COLLECT_INTERVAL_1=20  # 第一次采集等待时间（秒）
COLLECT_INTERVAL_2=40  # 第二次采集间隔
COLLECT_INTERVAL_3=40  # 第三次采集间隔
```

---

## 🔄 停止服务

### 方法 1: 使用停止脚本（推荐）

```bash
./stop_experiment.sh
```

### 方法 2: 手动停止

```bash
# 停止后端
kill $(cat assignment_data/backend.pid)

# 停止前端
kill $(cat assignment_data/frontend.pid)

# 清理所有相关进程
pkill -f "web_backend/main.py"
pkill -f "vite"
```

---

## 📸 手动操作清单

实验运行期间，请完成以下手动操作：

### 1. Web 界面截图

**访问地址**: http://localhost:3000/multi-agent

**建议截图**:

- ✅ 完整监控面板全景
- ✅ 智能体状态面板（车辆/调度/环境）
- ✅ 通信日志窗口（消息流）
- ✅ 协作决策可视化（分配关系）

**保存位置**: `assignment_data/screenshots/web_*.png`

### 2. GUI 测试（可选）

```bash
# 场景 1: 小规模基础功能
python run_with_gui.py --strategy greedy --cars 4 --size 10 --fps 3

# 场景 2: 中等规模扩展性
python run_with_gui.py --strategy balanced --cars 6 --size 15 --fps 4

# 场景 3: AI 智能调度
python run_with_gui.py --strategy dqn_inference --cars 5 --size 12 --fps 3
```

**保存截图**: `assignment_data/screenshots/gui_*.png`

---

## 📊 数据分析

### 查看实验摘要

```bash
cat assignment_data/experiment_summary.txt
```

### 分析 CSV 数据

```python
import pandas as pd

# 读取运行日志
df = pd.read_csv('assignment_data/csv_exports/simulation_frames.csv')

# 查看统计
print(df.describe())

# 分析完成率变化
df['completion_rate'] = df['completed_orders'] / df['total_orders'] * 100
df[['step', 'completion_rate']].plot()
```

### 分析 JSON 数据

```python
import json

# 读取性能指标
with open('assignment_data/json_data/perf_step100.json') as f:
    perf = json.load(f)

print(f"完成率: {perf['metrics']['completion_rate']:.1f}%")
print(f"车辆利用率: {perf['metrics']['vehicle_utilization']:.1f}%")
print(f"性能等级: {perf['performance_grade']}")
```

---

## 🐛 故障排查

### 问题 1: 端口被占用

**症状**: 后端或前端启动失败

**解决**:

```bash
# 检查端口占用
lsof -i :8001  # 后端端口
lsof -i :3000  # 前端端口

# 杀死占用进程
kill -9 <PID>
```

### 问题 2: 虚拟环境问题

**症状**: 找不到 Python 模块

**解决**:

```bash
# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 3: npm 依赖问题

**症状**: 前端启动失败

**解决**:

```bash
cd web_frontend
rm -rf node_modules package-lock.json
npm install
```

### 问题 4: 绘图失败

**症状**: 找不到中文字体

**解决**:

```bash
# macOS: 使用系统字体
# 脚本已配置 Arial Unicode MS

# Linux: 安装字体
sudo apt-get install fonts-wqy-microhei
```

---

## 📝 最佳实践

### 1. 实验前检查

- ✅ 确保虚拟环境已激活
- ✅ 确保端口 8001 和 3000 未被占用
- ✅ 确保有足够磁盘空间 (建议 > 500MB)

### 2. 实验中注意

- ✅ 不要关闭终端窗口
- ✅ 在采集期间访问 Web 界面
- ✅ 及时截图保存

### 3. 实验后整理

- ✅ 查看实验摘要
- ✅ 检查所有图表生成
- ✅ 整理截图到 screenshots 目录
- ✅ 停止服务释放资源

---

## 🔗 相关文档

- **详细实验步骤**: `assignment_submission/实验步骤.md`
- **系统使用指南**: `assignment_submission/使用指南.md`
- **技术方案**: `assignment_submission/技术方案.md`
- **API 文档**: http://localhost:8001/docs (运行后访问)

---

## ⚡ 性能调优

### 加快实验速度

```bash
# 编辑脚本，缩短采集间隔
COLLECT_INTERVAL_1=10  # 原20秒 → 10秒
COLLECT_INTERVAL_2=20  # 原40秒 → 20秒
COLLECT_INTERVAL_3=20  # 原40秒 → 20秒
```

### 提高图表质量

```python
# 在 generate_plots.py 中修改
plt.savefig(..., dpi=600)  # 原300 → 600 (更高分辨率)
```

---

## 💡 高级用法

### 批量实验

```bash
#!/bin/bash
# 批量运行不同配置

for strategy in GREEDY_NEAREST BALANCED HUNGARIAN; do
    echo "Testing strategy: $strategy"
    ./run_experiment.sh 15 5 15 $strategy
    mv assignment_data assignment_data_$strategy
done
```

### 自动化报告生成

```bash
# 运行实验并生成 PDF 报告
./run_experiment.sh
python generate_report.py  # 需要自己实现
```

---

**最后更新**: 2025-12-04  
**维护人员**: Cascade AI  
**版本**: 2.0
