# GUI 实验使用指南

## 📋 保存策略说明

### ✅ 新的保存机制

**每个策略只保留最新一次运行的结果**

- 每次运行时会**自动删除**该策略的旧数据
- 确保目录整洁，不会积累历史数据
- 每个策略独立管理，互不影响

### 📁 目录结构

```
CampusFleet AI/
├── gui_logs_GREEDY_NEAREST/    # 贪心策略（最新结果）
│   ├── gui_GREEDY_NEAREST_frames_*.csv
│   ├── gui_GREEDY_NEAREST_cars_*.csv
│   ├── gui_GREEDY_NEAREST_orders_*.csv
│   ├── gui_GREEDY_NEAREST_scheduler_*.csv
│   ├── gui_GREEDY_NEAREST_metadata_*.json
│   └── *.png (5个图表)
│
├── gui_logs_AUCTION_CNP/       # 拍卖机制（最新结果）
│   ├── gui_AUCTION_CNP_frames_*.csv
│   ├── gui_AUCTION_CNP_cars_*.csv
│   ├── gui_AUCTION_CNP_orders_*.csv
│   ├── gui_AUCTION_CNP_scheduler_*.csv
│   ├── gui_AUCTION_CNP_metadata_*.json
│   └── *.png (5个图表)
│
└── gui_logs_RL_SCHEDULER/      # RL调度（最新结果）
    ├── gui_RL_SCHEDULER_frames_*.csv
    ├── gui_RL_SCHEDULER_cars_*.csv
    ├── gui_RL_SCHEDULER_orders_*.csv
    ├── gui_RL_SCHEDULER_scheduler_*.csv
    ├── gui_RL_SCHEDULER_metadata_*.json
    └── *.png (5个图表)
```

---

## 🚀 运行实验

### 方法 1：逐个运行策略

```bash
# 运行贪心策略
python run_with_gui.py
# 输入: 1

# 运行拍卖机制
python run_with_gui.py
# 输入: 2

# 运行 RL 调度
python run_with_gui.py
# 输入: 3
```

### 方法 2：自动运行所有策略

```bash
# 创建自动化脚本
cat > run_all_strategies.sh << 'EOF'
#!/bin/bash
echo "=== 运行所有三种策略 ==="

echo -e "\n1️⃣  运行贪心策略..."
echo "1" | python run_with_gui.py

echo -e "\n2️⃣  运行拍卖机制..."
echo "2" | python run_with_gui.py

echo -e "\n3️⃣  运行 RL 调度..."
echo "3" | python run_with_gui.py

echo -e "\n✅ 所有策略运行完成！"
EOF

chmod +x run_all_strategies.sh
./run_all_strategies.sh
```

---

## 📊 生成的数据

### CSV 数据文件

1. **frames\_\*.csv** - 每一帧的仿真状态

   - 时间步、车辆数、订单数、系统状态

2. **cars\_\*.csv** - 车辆轨迹数据

   - 车辆 ID、位置、状态、电量、载货量

3. **orders\_\*.csv** - 订单处理数据

   - 订单 ID、事件类型（创建/分配/完成）、时间戳

4. **scheduler\_\*.csv** - 调度事件记录

   - 调度决策、车辆分配、时间戳

5. **metadata\_\*.json** - 实验元数据
   - 配置参数、总体统计、性能指标

### 可视化图表

1. **order_completion_over_time.png**

   - 订单完成趋势曲线
   - 显示随时间的订单完成情况

2. **efficiency_metrics.png**

   - 效率指标对比
   - 包括完成率、平均距离等

3. **distance_statistics.png**

   - 距离统计分布
   - 车辆行驶距离分析

4. **traffic_heatmap.png**

   - 交通热力图
   - 显示网格中的活动密度

5. **waiting_time_distribution.png**
   - 等待时间分布
   - 订单等待时间统计

---

## 🔄 重新生成图表

如果需要从现有 CSV 数据重新生成图表：

```bash
python regenerate_plots.py
```

这将自动：

- 查找所有策略目录
- 读取最新的 CSV 文件
- 重新生成所有 5 个图表

---

## ⚠️ 注意事项

### 数据保存规则

1. **自动清理**: 每次运行会删除该策略的旧数据
2. **独立管理**: 三个策略互不影响
3. **时间戳**: 文件名包含时间戳便于识别

### 如果需要保留历史数据

**方法 1：手动备份**

```bash
# 备份当前结果
cp -r gui_logs_RL_SCHEDULER gui_logs_RL_SCHEDULER_backup_$(date +%Y%m%d_%H%M%S)
```

**方法 2：移动到归档目录**

```bash
# 创建归档目录
mkdir -p archived_results

# 移动旧结果
mv gui_logs_* archived_results/
```

---

## 📈 对比分析

运行完三个策略后，可以对比：

| 指标         | GREEDY        | AUCTION       | RL            |
| ------------ | ------------- | ------------- | ------------- |
| 平均完成时间 | 查看 CSV      | 查看 CSV      | 查看 CSV      |
| 平均距离     | 查看 metadata | 查看 metadata | 查看 metadata |
| 完成订单数   | 查看 metadata | 查看 metadata | 查看 metadata |
| 车辆利用率   | 查看图表      | 查看图表      | 查看图表      |

### 快速查看元数据

```bash
# 查看贪心策略结果
cat gui_logs_GREEDY_NEAREST/gui_GREEDY_NEAREST_metadata_*.json | jq

# 查看拍卖机制结果
cat gui_logs_AUCTION_CNP/gui_AUCTION_CNP_metadata_*.json | jq

# 查看 RL 调度结果
cat gui_logs_RL_SCHEDULER/gui_RL_SCHEDULER_metadata_*.json | jq
```

---

## 🎯 报告建议

### 报告中应包含的图表

1. **订单完成趋势对比** (3 个策略并排)
2. **效率指标对比表**
3. **交通热力图对比** (显示不同策略的路径分布)
4. **等待时间箱型图对比**
5. **关键性能指标汇总表**

### 报告数据提取

```python
# 读取并对比三个策略的元数据
import json
import pandas as pd

strategies = ['GREEDY_NEAREST', 'AUCTION_CNP', 'RL_SCHEDULER']
results = []

for strategy in strategies:
    with open(f'gui_logs_{strategy}/gui_{strategy}_metadata_*.json') as f:
        data = json.load(f)
        results.append({
            'Strategy': strategy,
            'Total Frames': data['total_frames'],
            # 添加其他指标...
        })

df = pd.DataFrame(results)
print(df.to_markdown())
```

---

## ✨ 快速开始

```bash
# 1. 运行所有策略
echo "1" | python run_with_gui.py
echo "2" | python run_with_gui.py
echo "3" | python run_with_gui.py

# 2. 检查结果
ls -lh gui_logs_*/

# 3. 查看图表
open gui_logs_*/*.png

# 4. 对比元数据
for dir in gui_logs_*; do
    echo "=== $dir ==="
    cat $dir/*.json | jq '.total_frames, .end_time'
done
```

---

## 🎓 实验完成清单

- [ ] 运行贪心策略 (GREEDY_NEAREST)
- [ ] 运行拍卖机制 (AUCTION_CNP)
- [ ] 运行 RL 调度 (RL_SCHEDULER)
- [ ] 检查所有 CSV 数据已生成
- [ ] 检查所有图表已生成
- [ ] 备份重要结果（如需要）
- [ ] 提取关键指标到报告
- [ ] 创建对比图表
- [ ] 撰写分析总结

---

**最后更新**: 2025-12-07
**版本**: 2.0 - 自动清理旧数据
