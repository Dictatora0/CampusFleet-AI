# 使用示例

## 示例 1：快速演示

最简单的方式体验系统：

```bash
python main.py --demo
```

这将运行一个预配置的演示：

- 3 辆配送车
- 10 个随机订单
- 50 步仿真
- 贪心调度策略

## 示例 2：交互式添加订单

```bash
# 启动交互模式
python main.py

# 在命令提示符下：
👉 输入命令: add 0 0 14 14      # 从左上角到右下角
👉 输入命令: add 5 5 10 10      # 从中间到另一点
👉 输入命令: step 5             # 执行5步
👉 输入命令: status             # 查看详细状态
```

## 示例 3：自动生成订单

```bash
# 启动后开启自动模式
python main.py

👉 输入命令: auto               # 开启自动订单生成
👉 输入命令: run                # 开始持续运行
# 按 Ctrl+C 暂停
```

## 示例 4：大规模仿真

测试 5 辆车处理 20 个订单：

```bash
python main.py --mode auto --cars 5 --orders 20 --steps 200 --fps 3
```

## 示例 5：不同调度策略对比

### 贪心策略（最近优先）

```bash
python main.py --mode auto --strategy greedy --cars 4 --orders 15
```

### 负载均衡策略

```bash
python main.py --mode auto --strategy balanced --cars 4 --orders 15
```

比较两种策略的性能指标。

## 示例 6：自定义地图大小

运行 20x20 的大地图：

```bash
python main.py --size 20 --cars 6
```

## 示例 7：慢速观察

降低帧率以便仔细观察车辆行为：

```bash
python main.py --fps 1
```

## 示例 8：批量添加订单

在交互模式下：

```bash
python main.py

# 添加多个订单
👉 输入命令: random
👉 输入命令: random
👉 输入命令: random
👉 输入命令: random
👉 输入命令: random
👉 输入命令: step 50           # 执行50步看结果
👉 输入命令: status            # 查看统计
```

## 示例 9：观察避障行为

```bash
python main.py --cars 5

# 添加会产生路径冲突的订单
👉 输入命令: add 0 0 0 14
👉 输入命令: add 0 14 0 0
👉 输入命令: step              # 逐步观察避障
```

## 示例 10：性能测试

测试系统极限：

```bash
# 10辆车，50个订单
python main.py --mode auto --cars 10 --orders 50 --steps 500
```

## 常见场景

### 场景 A：早高峰配送

模拟早晨大量订单涌入：

```bash
python main.py --cars 5

👉 输入命令: random
👉 输入命令: random
👉 输入命令: random
# ... 连续添加多个订单
👉 输入命令: auto             # 开启自动模式
👉 输入命令: run              # 观察系统如何应对
```

### 场景 B：车辆不足

测试车辆不足时的调度表现：

```bash
python main.py --mode auto --cars 2 --orders 20
```

### 场景 C：长距离配送

添加跨越整个校园的订单：

```bash
python main.py

👉 输入命令: add 0 0 14 14
👉 输入命令: add 14 0 0 14
👉 输入命令: add 0 14 14 0
👉 输入命令: step 100
```

## 调试技巧

### 查看详细日志

```bash
python main.py

👉 输入命令: step              # 单步执行
👉 输入命令: status            # 查看完整状态
```

### 重置系统

```bash
👉 输入命令: reset             # 清空所有订单和状态
```

### 暂停和继续

```bash
👉 输入命令: run               # 开始运行
# 观察一段时间后按 Ctrl+C
👉 输入命令: status            # 检查当前状态
👉 输入命令: step 10           # 再执行10步
👉 输入命令: run               # 继续运行
```

## Python 脚本集成

将仿真集成到你的 Python 代码中：

```python
from core import SimulationContext, Simulation
from agents import SchedulingStrategy

# 创建仿真上下文
context = SimulationContext(
    grid_size=15,
    num_cars=3,
    scheduling_strategy=SchedulingStrategy.GREEDY_NEAREST
)

# 添加订单
context.add_order((0, 0), (14, 14))
context.add_order((5, 5), (10, 10))

# 执行仿真
for i in range(50):
    context.step()
    context.display()
    time.sleep(0.5)

# 获取统计数据
stats = context.get_statistics()
print(f"完成订单数: {stats['total_completed_orders']}")
print(f"总移动距离: {stats['total_distance']}")
```

## 高级用法

### 自定义地图

修改 `env/grid.py` 中的 `_create_default_grid` 方法来创建自定义地图布局。

### 自定义调度策略

在 `agents/scheduler_agent.py` 中添加新的调度方法。

### 集成 LLM 决策

使用预留的 `call_llm()` 函数集成大语言模型进行智能决策。
