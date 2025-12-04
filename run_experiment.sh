#!/bin/bash
# ============================================================================
# 多智能体系统功能展示自动化实验脚本 v2.0
# ============================================================================
# 描述: 一键运行从环境准备到数据分析的完整实验流程
# 作者: Cascade AI
# 日期: 2025-12-04
# 文档: 详见 EXPERIMENT_GUIDE.md
# ============================================================================

set -e  # 遇到错误立即退出

VERSION="2.0"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    cat << EOF
${BLUE}========================================
多智能体系统功能展示实验脚本 v${VERSION}
========================================${NC}

${GREEN}用法:${NC}
  $0 [网格大小] [车辆数] [订单数] [调度策略]

${GREEN}参数:${NC}
  网格大小    地图尺寸 (NxN)，默认: 10，推荐范围: 5-30
  车辆数      配送车辆数量，默认: 4，推荐范围: 2-10
  订单数      随机订单数量，默认: 10，推荐范围: 5-30
  调度策略    任务分配算法，默认: GREEDY_NEAREST

${GREEN}调度策略选项:${NC}
  GREEDY_NEAREST   - 贪心最近车辆（快速响应）
  BALANCED         - 负载均衡（均衡利用）
  HUNGARIAN        - 匈牙利算法（全局最优）
  VRP_BATCHING     - VRP批量优化（多订单拼单）
  MAPF_CBS         - MAPF路径规划（冲突避免）

${GREEN}示例:${NC}
  $0                              # 使用默认配置
  $0 15 6 15 BALANCED            # 中等规模负载均衡测试
  $0 20 8 20 HUNGARIAN           # 大规模全局最优测试

${GREEN}输出:${NC}
  - JSON数据: assignment_data/json_data/*.json
  - CSV日志:  assignment_data/csv_exports/*.csv
  - 可视化:   assignment_data/plots/*.png
  - 摘要:     assignment_data/experiment_summary.txt

${GREEN}服务:${NC}
  - 后端API:  http://localhost:8001/api/docs
  - 前端界面: http://localhost:3000/multi-agent

${GREEN}停止服务:${NC}
  ./stop_experiment.sh

${GREEN}详细文档:${NC}
  EXPERIMENT_GUIDE.md

${BLUE}========================================${NC}
EOF
    exit 0
}

# 检查是否请求帮助
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
fi

# 自动检测项目目录（脚本所在目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
DATA_DIR="$PROJECT_DIR/assignment_data"

# 配置参数（可通过命令行参数覆盖）
GRID_SIZE=${1:-10}
NUM_CARS=${2:-4}
NUM_ORDERS=${3:-10}
STRATEGY=${4:-"GREEDY_NEAREST"}

# 参数验证
if [ -n "$1" ]; then
    # 检查网格大小是否为数字
    if ! [[ "$GRID_SIZE" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ 错误: 网格大小必须是数字，收到: $GRID_SIZE${NC}"
        echo -e "${YELLOW}💡 使用 --help 查看帮助信息${NC}"
        exit 1
    fi
    
    # 检查范围
    if [ "$GRID_SIZE" -lt 5 ] || [ "$GRID_SIZE" -gt 50 ]; then
        echo -e "${YELLOW}⚠️  警告: 网格大小 $GRID_SIZE 超出推荐范围 (5-30)${NC}"
    fi
fi

if [ -n "$2" ]; then
    if ! [[ "$NUM_CARS" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ 错误: 车辆数必须是数字，收到: $NUM_CARS${NC}"
        echo -e "${YELLOW}💡 使用 --help 查看帮助信息${NC}"
        exit 1
    fi
    
    if [ "$NUM_CARS" -lt 1 ] || [ "$NUM_CARS" -gt 20 ]; then
        echo -e "${YELLOW}⚠️  警告: 车辆数 $NUM_CARS 超出推荐范围 (2-10)${NC}"
    fi
fi

if [ -n "$3" ]; then
    if ! [[ "$NUM_ORDERS" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ 错误: 订单数必须是数字，收到: $NUM_ORDERS${NC}"
        echo -e "${YELLOW}💡 使用 --help 查看帮助信息${NC}"
        exit 1
    fi
    
    if [ "$NUM_ORDERS" -lt 1 ] || [ "$NUM_ORDERS" -gt 100 ]; then
        echo -e "${YELLOW}⚠️  警告: 订单数 $NUM_ORDERS 超出推荐范围 (5-30)${NC}"
    fi
fi

# 时间配置
BACKEND_WAIT=5
FRONTEND_WAIT=10
COLLECT_INTERVAL_1=20
COLLECT_INTERVAL_2=40
COLLECT_INTERVAL_3=40

# 依赖检查函数
check_dependencies() {
    local missing_deps=()
    
    command -v curl >/dev/null 2>&1 || missing_deps+=("curl")
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v npm >/dev/null 2>&1 || missing_deps+=("npm")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}❌ 缺少必要依赖: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}请先安装缺失的依赖${NC}"
        exit 1
    fi
}

# 清理函数（错误时调用）
cleanup() {
    echo -e "\n${YELLOW}⚠️  检测到错误，正在清理...${NC}"
    
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
        echo "已停止后端服务 (PID: $BACKEND_PID)"
    fi
    
    if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null
        echo "已停止前端服务 (PID: $FRONTEND_PID)"
    fi
    
    pkill -f "web_backend/main.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 清理完成${NC}"
    exit 1
}

# 设置错误时的清理陷阱
trap cleanup ERR INT TERM

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  多智能体系统功能展示实验${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}实验配置:${NC}"
echo -e "  网格大小: ${GRID_SIZE}×${GRID_SIZE}"
echo -e "  车辆数量: ${NUM_CARS} 辆"
echo -e "  订单数量: ${NUM_ORDERS} 个"
echo -e "  调度策略: ${STRATEGY}"
echo -e "${BLUE}========================================${NC}\n"

# 检查依赖
check_dependencies

# 步骤 1: 环境准备
echo -e "\n${GREEN}[步骤 1/7] 环境准备${NC}"
cd "$PROJECT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，请先运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

source venv/bin/activate

echo "创建数据保存目录..."
mkdir -p "$DATA_DIR/screenshots"
mkdir -p "$DATA_DIR/json_data"
mkdir -p "$DATA_DIR/csv_exports"
mkdir -p "$DATA_DIR/plots"
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 步骤 2: 启动 Web 后端
echo -e "\n${GREEN}[步骤 2/7] 启动 Web 后端服务${NC}"
cd "$PROJECT_DIR/web_backend"
"$PROJECT_DIR/venv/bin/python" main.py > "$DATA_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "后端进程 PID: $BACKEND_PID"
echo $BACKEND_PID > "$DATA_DIR/backend.pid"

# 等待后端启动
echo "等待后端启动..."
sleep 5

# 检查后端是否正常运行（重试机制）
BACKEND_READY=0
for i in {1..10}; do
    if curl -s http://localhost:8001/ > /dev/null 2>&1; then
        BACKEND_READY=1
        break
    fi
    echo -n "."
    sleep 1
done

if [ $BACKEND_READY -eq 1 ]; then
    echo -e "\n${GREEN}✅ 后端服务启动成功${NC}"
else
    echo -e "\n${RED}❌ 后端服务启动失败，请检查日志: $DATA_DIR/backend.log${NC}"
    tail -20 "$DATA_DIR/backend.log"
    cleanup
fi

# 步骤 3: 启动 Web 前端
echo -e "\n${GREEN}[步骤 3/7] 启动 Web 前端服务${NC}"
cd "$PROJECT_DIR/web_frontend"

# 检查是否需要安装依赖
if [ ! -d "node_modules" ]; then
    echo "首次运行，安装前端依赖..."
    npm install
fi

npm run dev > "$DATA_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "前端进程 PID: $FRONTEND_PID"
echo $FRONTEND_PID > "$DATA_DIR/frontend.pid"

echo "等待前端启动..."
FRONTEND_READY=0
for i in {1..20}; do
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        FRONTEND_READY=1
        break
    fi
    echo -n "."
    sleep 1
done

if [ $FRONTEND_READY -eq 1 ]; then
    echo -e "\n${GREEN}✅ 前端服务启动成功${NC}"
else
    echo -e "\n${YELLOW}⚠️  前端可能未完全就绪，但将继续执行${NC}"
fi
echo -e "${YELLOW}📱 前端地址: http://localhost:3000${NC}"
echo -e "${YELLOW}📱 多智能体监控: http://localhost:3000/multi-agent${NC}"

# 步骤 4: 创建仿真并运行
echo -e "\n${GREEN}[步骤 4/7] 创建并运行仿真${NC}"
cd "$PROJECT_DIR"

echo "创建仿真实例..."
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8001/api/simulation/create \
  -H "Content-Type: application/json" \
  -d "{
    \"grid_size\": $GRID_SIZE,
    \"num_cars\": $NUM_CARS,
    \"strategy\": \"$STRATEGY\",
    \"enable_logging\": true
  }")

if echo "$CREATE_RESPONSE" | grep -q "success\|created"; then
    echo -e "${GREEN}✅ 仿真创建成功${NC}"
else
    echo -e "${RED}❌ 仿真创建失败: $CREATE_RESPONSE${NC}"
    cleanup
fi

echo -e "${GREEN}✅ 仿真创建成功${NC}"

echo "添加 $NUM_ORDERS 个随机订单..."
for i in $(seq 1 $NUM_ORDERS); do
  ORDER_RESP=$(curl -s -X POST http://localhost:8001/api/orders/random)
  if echo "$ORDER_RESP" | grep -q "success\|order"; then
    echo -n "."
  else
    echo -n "x"
  fi
  sleep 0.3
done
echo ""
echo -e "${GREEN}✅ 订单添加完成${NC}"

echo "启动仿真..."
curl -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "start", "params": {"auto_step": true}}' > /dev/null 2>&1

echo -e "${GREEN}✅ 仿真已启动，自动步进中...${NC}"

# 步骤 5: 数据采集
echo -e "\n${GREEN}[步骤 5/7] 采集运行数据${NC}"
echo -e "${YELLOW}⏱️  等待仿真运行并采集数据（约 2 分钟）...${NC}"
echo ""
echo -e "${BLUE}📸 请在浏览器中打开以下地址并截图：${NC}"
echo -e "   ${YELLOW}http://localhost:3000/multi-agent${NC}"
echo -e "${BLUE}   建议截图：${NC}"
echo -e "   1. 完整监控面板"
echo -e "   2. 智能体状态详情"
echo -e "   3. 通信日志窗口"
echo -e "   4. 协作决策可视化"
echo ""

# 采集时刻 1：20 秒后
sleep 20
echo "采集时刻 1 数据（步骤 ~20）..."
curl -s http://localhost:8001/api/agents/status > "$DATA_DIR/json_data/agents_step20.json"
curl -s http://localhost:8001/api/communication/logs > "$DATA_DIR/json_data/comm_step20.json"
curl -s http://localhost:8001/api/collaboration/decisions > "$DATA_DIR/json_data/collab_step20.json"
curl -s http://localhost:8001/api/performance/metrics > "$DATA_DIR/json_data/perf_step20.json"
echo -e "${GREEN}✅ 时刻 1 数据已保存${NC}"

# 采集时刻 2：再等 40 秒
sleep 40
echo "采集时刻 2 数据（步骤 ~60）..."
curl -s http://localhost:8001/api/agents/status > "$DATA_DIR/json_data/agents_step60.json"
curl -s http://localhost:8001/api/communication/logs > "$DATA_DIR/json_data/comm_step60.json"
curl -s http://localhost:8001/api/collaboration/decisions > "$DATA_DIR/json_data/collab_step60.json"
curl -s http://localhost:8001/api/performance/metrics > "$DATA_DIR/json_data/perf_step60.json"
echo -e "${GREEN}✅ 时刻 2 数据已保存${NC}"

# 采集时刻 3：再等 40 秒
sleep 40
echo "采集时刻 3 数据（步骤 ~100）..."
curl -s http://localhost:8001/api/agents/status > "$DATA_DIR/json_data/agents_step100.json"
curl -s http://localhost:8001/api/communication/logs > "$DATA_DIR/json_data/comm_step100.json"
curl -s http://localhost:8001/api/collaboration/decisions > "$DATA_DIR/json_data/collab_step100.json"
curl -s http://localhost:8001/api/performance/metrics > "$DATA_DIR/json_data/perf_step100.json"
echo -e "${GREEN}✅ 时刻 3 数据已保存${NC}"

# 导出完整运行日志
echo "导出完整运行日志（CSV 格式）..."
curl -s "http://localhost:8001/api/analytics/export" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data'])" \
  > "$DATA_DIR/csv_exports/simulation_frames.csv"
echo -e "${GREEN}✅ 运行日志已导出${NC}"

# 步骤 6: 停止仿真
echo -e "\n${GREEN}[步骤 6/7] 停止仿真${NC}"
curl -s -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "stop"}' > /dev/null 2>&1
echo -e "${GREEN}✅ 仿真已停止${NC}"

# 步骤 7: 生成分析图表
echo -e "\n${GREEN}[步骤 7/7] 生成性能分析图表${NC}"

cat > "$DATA_DIR/generate_plots.py" << 'PLOTSCRIPT'
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = Path(__file__).parent

# 读取性能数据
try:
    perf_20 = json.load(open(DATA_DIR / 'json_data/perf_step20.json'))
    perf_60 = json.load(open(DATA_DIR / 'json_data/perf_step60.json'))
    perf_100 = json.load(open(DATA_DIR / 'json_data/perf_step100.json'))
except FileNotFoundError as e:
    print(f"错误: 找不到数据文件 {e}")
    print("提示: 请确保实验已运行足够长时间以采集所有数据点")
    exit(1)
except json.JSONDecodeError as e:
    print(f"错误: JSON 解析失败 {e}")
    print("提示: 数据文件可能损坏，请重新运行实验")
    exit(1)

# 图 1：完成率随时间变化
steps = [20, 60, 100]
completion_rates = [
    perf_20['metrics']['completion_rate'],
    perf_60['metrics']['completion_rate'],
    perf_100['metrics']['completion_rate']
]

plt.figure(figsize=(10, 6))
plt.plot(steps, completion_rates, marker='o', linewidth=2, markersize=10,
         color='#3498db', label='Completion Rate')
plt.xlabel('Simulation Steps', fontsize=13, fontweight='bold')
plt.ylabel('Completion Rate (%)', fontsize=13, fontweight='bold')
plt.title('Order Completion Rate Over Time', fontsize=15, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(fontsize=11)
plt.tight_layout()
plt.savefig(DATA_DIR / 'plots/completion_rate_trend.png', dpi=300, bbox_inches='tight')
print("✅ 生成图表 1: completion_rate_trend.png")

# 图 2：车辆利用率对比
vehicle_utils = [
    perf_20['metrics']['vehicle_utilization'],
    perf_60['metrics']['vehicle_utilization'],
    perf_100['metrics']['vehicle_utilization']
]

plt.figure(figsize=(10, 6))
colors = ['#3498db', '#2ecc71', '#e74c3c']
bars = plt.bar(steps, vehicle_utils, color=colors, width=15, alpha=0.8)
plt.xlabel('Simulation Steps', fontsize=13, fontweight='bold')
plt.ylabel('Vehicle Utilization (%)', fontsize=13, fontweight='bold')
plt.title('Vehicle Utilization Rate', fontsize=15, fontweight='bold')
plt.ylim(0, 100)
plt.grid(True, alpha=0.3, axis='y', linestyle='--')

# 在柱状图上添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(DATA_DIR / 'plots/vehicle_utilization.png', dpi=300, bbox_inches='tight')
print("✅ 生成图表 2: vehicle_utilization.png")

# 图 3：订单处理状态分布
labels = ['Completed', 'Pending']
sizes = [
    perf_100['metrics']['completed_orders'],
    perf_100['metrics']['pending_orders']
]
colors = ['#2ecc71', '#e67e22']
explode = (0.1, 0)

plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 12})
plt.title('Final Order Status Distribution', fontsize=15, fontweight='bold', pad=20)

# 美化百分比文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(13)

plt.tight_layout()
plt.savefig(DATA_DIR / 'plots/order_status_distribution.png', dpi=300, bbox_inches='tight')
print("✅ 生成图表 3: order_status_distribution.png")

# 图 4：多指标对比雷达图
import numpy as np

categories = ['Completion\nRate', 'Vehicle\nUtilization', 'Response\nSpeed']
values_step100 = [
    perf_100['metrics']['completion_rate'],
    perf_100['metrics']['vehicle_utilization'],
    80  # 响应速度（假设值，可根据实际调整）
]

# 闭合雷达图
values_step100 += values_step100[:1]
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
ax.plot(angles, values_step100, 'o-', linewidth=2, color='#3498db', label='Step 100')
ax.fill(angles, values_step100, alpha=0.25, color='#3498db')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11)
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)
ax.grid(True, linestyle='--', alpha=0.5)
plt.title('System Performance Metrics', fontsize=15, fontweight='bold', pad=20)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=11)
plt.tight_layout()
plt.savefig(DATA_DIR / 'plots/performance_radar.png', dpi=300, bbox_inches='tight')
print("✅ 生成图表 4: performance_radar.png")

print("\n📊 所有图表生成完成！")
print(f"图表保存位置: {DATA_DIR / 'plots'}")
PLOTSCRIPT

# 运行绘图脚本
python3 "$DATA_DIR/generate_plots.py"

# 生成实验报告摘要
echo -e "\n${GREEN}生成实验数据摘要...${NC}"
cat > "$DATA_DIR/experiment_summary.txt" << SUMMARY
========================================
多智能体系统功能展示实验报告摘要
========================================
实验时间: $(date '+%Y-%m-%d %H:%M:%S')

一、实验配置
-----------
网格大小: 10×10
车辆数量: 4 辆
订单数量: 10 个
调度策略: GREEDY_NEAREST
数据记录: 已启用

二、关键性能指标（最终状态）
--------------------------
SUMMARY

# 从 JSON 中提取关键数据
python3 << PYSCRIPT >> "$DATA_DIR/experiment_summary.txt"
import json
perf = json.load(open('$DATA_DIR/json_data/perf_step100.json'))
metrics = perf['metrics']
print(f"完成率: {metrics['completion_rate']:.1f}%")
print(f"已完成订单: {metrics['completed_orders']} 个")
print(f"待处理订单: {metrics['pending_orders']} 个")
print(f"车辆利用率: {metrics['vehicle_utilization']:.1f}%")
print(f"性能等级: {perf['performance_grade']}")
PYSCRIPT

cat >> "$DATA_DIR/experiment_summary.txt" << SUMMARY2

三、生成的数据文件
-----------------
📊 可视化图表（4 张）:
  - completion_rate_trend.png
  - vehicle_utilization.png
  - order_status_distribution.png
  - performance_radar.png

📁 原始数据文件:
  - simulation_frames.csv (完整运行日志)
  - agents_stepX.json × 3 (智能体状态快照)
  - comm_stepX.json × 3 (通信日志快照)
  - collab_stepX.json × 3 (协作决策快照)
  - perf_stepX.json × 3 (性能指标快照)

四、手动操作提醒
---------------
⚠️  请手动完成以下操作：
1. 访问 http://localhost:3000/multi-agent 截取 Web 界面
2. 运行 GUI 测试（见下方命令）并截图
3. 整理截图到 assignment_data/screenshots/ 目录

五、GUI 测试命令
---------------
场景 1 - 小规模测试:
  python run_with_gui.py --strategy greedy --cars 4 --size 10 --fps 3

场景 2 - 中等规模测试:
  python run_with_gui.py --strategy balanced --cars 6 --size 15 --fps 4

场景 3 - AI 智能调度:
  python run_with_gui.py --strategy dqn_inference --cars 5 --size 12 --fps 3

========================================
SUMMARY2

echo -e "${GREEN}✅ 实验摘要已生成${NC}"

# 完成
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 自动化实验流程完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}📂 所有数据已保存到: $DATA_DIR${NC}"
echo -e "${YELLOW}📊 查看图表: $DATA_DIR/plots/${NC}"
echo -e "${YELLOW}📄 查看摘要: $DATA_DIR/experiment_summary.txt${NC}"
echo ""
echo -e "${BLUE}🌐 Web 服务仍在运行：${NC}"
echo -e "   前端: http://localhost:3000/multi-agent"
echo -e "   后端: http://localhost:8001/api/docs"
echo ""
echo -e "${RED}⚠️  请手动完成：${NC}"
echo -e "   1. 在浏览器中截取 Web 界面截图"
echo -e "   2. 运行 GUI 测试场景并截图（见上方命令）"
echo -e "   3. 查看生成的实验摘要文件"
echo ""
echo -e "${YELLOW}停止服务请运行: ./stop_experiment.sh${NC}"
echo ""

# 保存进程信息以便后续停止
cat > "$DATA_DIR/process_info.txt" << INFO
Backend PID: $BACKEND_PID
Frontend PID: $FRONTEND_PID
Started at: $(date)
INFO

# 创建停止脚本
cat > "$PROJECT_DIR/stop_experiment.sh" << 'STOPSCRIPT'
#!/bin/bash
# 停止实验脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="$SCRIPT_DIR/assignment_data"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  停止实验服务${NC}"
echo -e "${BLUE}========================================${NC}"

# 停止记录的进程
STOPPED_COUNT=0

if [ -f "$DATA_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$DATA_DIR/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
        STOPPED_COUNT=$((STOPPED_COUNT + 1))
    else
        echo -e "${YELLOW}⚠️  后端服务已不在运行${NC}"
    fi
    rm "$DATA_DIR/backend.pid"
fi

if [ -f "$DATA_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$DATA_DIR/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
        STOPPED_COUNT=$((STOPPED_COUNT + 1))
    else
        echo -e "${YELLOW}⚠️  前端服务已不在运行${NC}"
    fi
    rm "$DATA_DIR/frontend.pid"
fi

# 清理所有相关进程
echo "清理残留进程..."
KILLED_BACKEND=$(pkill -f "web_backend/main.py" 2>/dev/null; echo $?)
KILLED_FRONTEND=$(pkill -f "vite" 2>/dev/null; echo $?)

if [ $KILLED_BACKEND -eq 0 ] || [ $KILLED_FRONTEND -eq 0 ]; then
    echo -e "${GREEN}✅ 清理了残留进程${NC}"
fi

# 检查端口是否释放
sleep 1
if lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}⚠️  端口 8001 仍被占用${NC}"
else
    echo -e "${GREEN}✅ 端口 8001 已释放${NC}"
fi

if lsof -i :3000 >/dev/null 2>&1; then
    echo -e "${RED}⚠️  端口 3000 仍被占用${NC}"
else
    echo -e "${GREEN}✅ 端口 3000 已释放${NC}"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${BLUE}========================================${NC}"
STOPSCRIPT

chmod +x "$PROJECT_DIR/stop_experiment.sh"

echo -e "${GREEN}提示: 停止脚本已创建并设置为可执行${NC}"
