# 🚀 快速启动指南

## 立即开始

### 1️⃣ 快速演示（推荐首次使用）

```bash
cd "CampusFleet AI"
python main.py --demo
```

这将自动运行一个完整的演示，展示 3 辆车处理 10 个订单的过程。

### 2️⃣ 交互模式

```bash
python main.py
```

启动后，尝试以下命令：

```
👉 输入命令: random          # 添加随机订单
👉 输入命令: step 5          # 执行5步仿真
👉 输入命令: auto            # 开启自动订单生成
👉 输入命令: run             # 持续运行（Ctrl+C暂停）
```

### 3️⃣ 自动运行模式

```bash
python main.py --mode auto --cars 5 --orders 15
```

## 常用命令参数

| 参数                  | 说明     | 示例                                 |
| --------------------- | -------- | ------------------------------------ |
| `--demo`              | 快速演示 | `python main.py --demo`              |
| `--mode auto`         | 自动模式 | `python main.py --mode auto`         |
| `--cars N`            | N 辆车   | `python main.py --cars 5`            |
| `--size N`            | N×N 地图 | `python main.py --size 20`           |
| `--strategy greedy`   | 贪心策略 | `python main.py --strategy greedy`   |
| `--strategy balanced` | 负载均衡 | `python main.py --strategy balanced` |

## 交互命令速查

| 命令              | 功能         |
| ----------------- | ------------ |
| `add x1 y1 x2 y2` | 添加订单     |
| `random`          | 随机订单     |
| `step [n]`        | 执行 n 步    |
| `run`             | 持续运行     |
| `pause`           | 暂停         |
| `auto`            | 切换自动模式 |
| `status`          | 详细状态     |
| `reset`           | 重置         |
| `quit`            | 退出         |

## 示例场景

### 📦 基础配送

```bash
python main.py
👉 输入命令: add 0 0 14 14
👉 输入命令: add 5 5 10 10
👉 输入命令: step 20
```

### 🚦 观察避障

```bash
python main.py --cars 5
👉 输入命令: random
👉 输入命令: random
👉 输入命令: random
👉 输入命令: run
```

### 📊 性能测试

```bash
python main.py --mode auto --cars 10 --orders 30 --steps 200
```

## 系统要求

- ✅ Python 3.7+
- ✅ 无需额外依赖
- ✅ 支持 macOS / Linux / Windows

## 显示说明

### 地图符号

- `.` = 道路
- `#` = 建筑/障碍
- `0-9` = 车辆 ID

### 车辆状态

- 🅿️ = 空闲
- 🔍 = 前往取货
- 📦 = 配送中
- ⏸️ = 等待

## 问题排查

### 程序运行但看不到动画

- ✅ 使用 `python main.py --demo` 测试
- ✅ 确保终端窗口足够大

### 车辆不移动

- ✅ 确认已添加订单：`random`
- ✅ 执行仿真步骤：`step 10`

### 订单无法完成

- ✅ 检查起点和终点是否在道路上
- ✅ 使用 `status` 命令查看详细信息

## 下一步

- 📖 阅读 [README.md](README.md) 了解完整功能
- 📝 查看 [EXAMPLES.md](EXAMPLES.md) 学习更多用法
- 🔧 修改代码实现自定义功能

## 获取帮助

```bash
python main.py --help
```

---

**享受智能配送的乐趣！** 🎉
