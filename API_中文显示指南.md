# API 中文显示指南

**问题：** curl 查看 API 返回的 JSON 中文显示为 `\u5b66\u4e60` 等 Unicode 转义序列
**原因：** Python 的`json.tool`默认会转义非 ASCII 字符
**解决：** 使用`jq`工具或专用脚本

---

## ✅ 解决方案

### 方案 1：使用 jq 工具（推荐）

```bash
# 安装jq（如果没有）
brew install jq  # macOS

# 使用jq查看API
curl -s http://localhost:8001/api/strategies | jq -r .
```

**输出：**

```json
{
  "strategies": [
    {
      "key": "GREEDY_NEAREST",
      "name": "贪心最近算法",        ← 中文正常显示
      "description": "启发式算法 - 为每个订单选择最近的车辆",
      "category": "启发式"
    },
    ...
  ]
}
```

---

### 方案 2：使用 api_viewer.sh 脚本（最方便）

我们提供了专门的查看工具：

```bash
# 查看所有信息
./api_viewer.sh all

# 只查看调度策略
./api_viewer.sh strategies

# 只查看仿真状态
./api_viewer.sh state

# 只查看拍卖日志
./api_viewer.sh auction

# 只查看车辆状态
./api_viewer.sh vehicles
```

**输出示例：**

```
================================
📋 调度策略列表
================================

[启发式] 贪心最近算法
  Key: GREEDY_NEAREST
  说明: 启发式算法 - 为每个订单选择最近的车辆

[多智能体] 拍卖机制(CNP)
  Key: AUCTION_CNP
  说明: 多智能体协商 - 合同网协议车辆竞标

[深度学习] 强化学习调度
  Key: RL_SCHEDULER
  说明: 深度强化学习 - DQN/PPO智能决策
```

---

### 方案 3：直接在浏览器查看（最简单）

```bash
# 打开浏览器访问API文档
open http://localhost:8001/docs

# 或者直接访问API端点
open http://localhost:8001/api/strategies
```

浏览器会自动正确显示中文。

---

## 📋 常用命令对照表

| 功能         | 旧命令（乱码）                     | 新命令（正常）               |
| ------------ | ---------------------------------- | ---------------------------- |
| **查看策略** | `curl ... \| python3 -m json.tool` | `./api_viewer.sh strategies` |
| **查看状态** | `curl ... \| python3 -m json.tool` | `./api_viewer.sh state`      |
| **查看拍卖** | `curl ... \| python3 -m json.tool` | `./api_viewer.sh auction`    |
| **查看车辆** | `curl ... \| python3 -m json.tool` | `./api_viewer.sh vehicles`   |
| **查看全部** | 无                                 | `./api_viewer.sh all`        |

---

## 🎯 快速测试

### 1. 查看调度策略（3 个核心 AI 策略）

```bash
./api_viewer.sh strategies
```

**预期输出：**

- ✅ 贪心最近算法（启发式）
- ✅ 拍卖机制(CNP)（多智能体）
- ✅ 强化学习调度（深度学习）

### 2. 查看当前仿真状态

```bash
./api_viewer.sh state
```

**输出信息：**

- 运行状态（true/false）
- 当前步数
- 调度策略
- 车辆数量
- 待分配订单数

### 3. 查看拍卖日志（仅拍卖策略时有数据）

```bash
./api_viewer.sh auction
```

**输出信息：**

- 拍卖时间戳
- 总拍卖次数
- 成功分配数
- 详细日志

### 4. 查看所有车辆状态

```bash
./api_viewer.sh vehicles
```

**输出信息：**

- 车辆 ID
- 当前位置
- 电量百分比
- 状态（Idle/MovingToPickup/等）

---

## 🔧 原理说明

### Unicode 转义序列

```
\u5b66\u4e60 = 学习
\u8d2a\u5fc3 = 贪心
\u62cd\u5356 = 拍卖
```

这是 JSON 标准的一部分，用于表示非 ASCII 字符。

### 为什么会出现？

```bash
# Python的json.tool默认行为
python3 -m json.tool --help
# 输出: 没有 --ensure-ascii=False 选项

# 因此中文会被转义
echo '{"name": "学习"}' | python3 -m json.tool
# 输出: {"name": "\u5b66\u4e60"}
```

### jq 如何解决？

```bash
# jq默认保留UTF-8字符
echo '{"name": "学习"}' | jq .
# 输出: {"name": "学习"}

# jq的-r选项（raw output）进一步美化
echo '{"name": "学习"}' | jq -r .
# 输出: {"name": "学习"}
```

---

## 💡 脚本说明

### show_strategies.sh

**功能：** 快速查看调度策略列表
**使用：** `./show_strategies.sh`

```bash
#!/bin/bash
curl -s http://localhost:8001/api/strategies | \
  jq -r '.strategies[] | "[\(.category)] \(.name)\n  Key: \(.key)\n  说明: \(.description)\n"'
```

### api_viewer.sh

**功能：** 全功能 API 查看工具
**使用：** `./api_viewer.sh [strategies|state|auction|vehicles|all]`

**特点：**

- ✅ 带颜色高亮
- ✅ 格式化输出
- ✅ 支持分模块查看
- ✅ 中文完美显示

---

## 🐛 故障排查

### 问题 1：jq 命令不存在

**错误：**

```
bash: jq: command not found
```

**解决：**

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

### 问题 2：api_viewer.sh 没有执行权限

**错误：**

```
Permission denied: ./api_viewer.sh
```

**解决：**

```bash
chmod +x api_viewer.sh
chmod +x show_strategies.sh
```

### 问题 3：curl 连接失败

**错误：**

```
curl: (7) Failed to connect to localhost port 8001
```

**解决：**

```bash
# 检查后端是否运行
ps aux | grep 'web_backend/main.py'

# 重启服务
./debug_web.sh
```

---

## 📱 Web 界面查看（零配置）

最简单的方法是直接在浏览器中查看：

### 1. API 文档界面

```bash
open http://localhost:8001/docs
```

**功能：**

- ✅ Swagger UI 自动文档
- ✅ 可视化 API 测试
- ✅ 中文完美显示
- ✅ 交互式测试

### 2. 直接访问 API

```bash
# 浏览器访问
open http://localhost:8001/api/strategies
```

浏览器会自动渲染 JSON，中文正常显示。

### 3. 主控制台

```bash
open http://localhost:3000
```

**功能：**

- 选择策略下拉框 → 中文显示
- 拍卖日志面板 → 中文显示
- 车辆状态列表 → 中文显示

---

## 🎓 课程演示建议

### 对比演示效果

**不推荐（显示乱码）：**

```bash
curl http://localhost:8001/api/strategies | python3 -m json.tool
# 输出: "\u8d2a\u5fc3\u6700\u8fd1\u7b97\u6cd5"
# 学生：？？？这是什么？
```

**推荐（清晰易读）：**

```bash
./api_viewer.sh strategies
# 输出: [启发式] 贪心最近算法
#       Key: GREEDY_NEAREST
#       说明: 启发式算法 - 为每个订单选择最近的车辆
# 学生：清楚！
```

### 演示脚本

```bash
# 1. 启动服务
./debug_web.sh

# 2. 查看3个核心策略
./api_viewer.sh strategies

# 3. 打开Web界面
open http://localhost:3000

# 4. 选择拍卖策略，创建仿真

# 5. 查看拍卖日志（实时更新）
watch -n 2 ./api_viewer.sh auction
```

---

## 📚 参考资料

### jq 官方文档

- 官网: https://stedolan.github.io/jq/
- 教程: https://stedolan.github.io/jq/tutorial/

### JSON 与 Unicode

- RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format
- Unicode 编码: https://www.unicode.org/

### Swagger UI

- FastAPI 文档: https://fastapi.tiangolo.com/
- Swagger UI: https://swagger.io/tools/swagger-ui/

---

**总结：** 使用 `./api_viewer.sh` 脚本是最方便的方式！

**最后更新：** 2024-12-07 00:10
