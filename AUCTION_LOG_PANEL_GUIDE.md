# Web 前端拍卖日志面板使用指南

**功能：** 实时显示拍卖机制（CNP）的订单分配过程
**状态：** ✅ 已完成
**更新时间：** 2024-12-06 22:55

---

## 📋 功能概述

拍卖日志面板是一个实时可视化组件，用于展示基于**合同网协议（CNP）**的订单分配过程。面板会显示：

1. **拍卖统计** - 总拍卖数、成功数、流拍数
2. **拍卖时间线** - 4 个阶段的详细日志
3. **竞标详情** - 中标成本、竞标者数量、第二名成本

---

## 🚀 使用步骤

### Step 1: 启动服务

```bash
# 在项目根目录执行
./debug_web.sh
```

**预期输出：**

```
✅ 后端启动成功 (PID: xxxxx)
✅ 前端启动成功 (PID: xxxxx)
✅ 仿真已创建
📱 访问地址：http://localhost:3000
```

### Step 2: 创建使用拍卖策略的仿真

1. **打开浏览器**

   ```bash
   open http://localhost:3000
   ```

2. **选择预设** - 在"选择预设"下拉框中选择任意预设

3. **选择拍卖策略** - 这是关键步骤！

   - 在创建仿真时，需要选择 **"拍卖机制(CNP)"** 策略
   - 如果默认配置中没有该策略，需要修改配置：

   ```javascript
   // 修改 web_frontend/src/api/simulation.js
   // 或者通过API直接创建
   curl -X POST http://localhost:8001/api/simulation/create \
     -H "Content-Type: application/json" \
     -d '{
       "grid_size": 15,
       "num_cars": 6,
       "strategy": "AUCTION_CNP"  // ← 关键：使用拍卖策略
     }'
   ```

4. **设置初始订单数** - 建议设置 5-10 个订单

5. **点击"创建仿真"**

### Step 3: 查看拍卖日志面板

创建仿真后，在右侧信息面板中会出现：

```
┌────────────────────────┐
│ 📖 图例说明             │
├────────────────────────┤
│ 🚗 车辆状态             │
├────────────────────────┤
│ 📋 订单管理             │
├────────────────────────┤
│ 🎪 拍卖日志   ← 新增！  │
│ ├─ 总拍卖: 5           │
│ ├─ 成功: 5             │
│ └─ 流拍: 0             │
└────────────────────────┘
```

### Step 4: 添加订单触发拍卖

1. **点击"添加"按钮** 添加新订单
2. **或点击"随机订单"** 快速添加

每次添加订单时，拍卖日志会实时更新，显示：

```
📢 发布 - 订单 #1 发布拍卖 (5,5) → (10,10)
         共 3 个竞标者

🏆 中标 - 车辆 #2 中标
         中标成本: 18.00
         第二名: 30.00
         共 3 个竞标

✅ 授予 - 订单 #1 已授予车辆 #2
```

### Step 5: 启动仿真观察

点击"启动"按钮，观察：

- 车辆移动到取货点
- 电量变化
- 新订单触发新拍卖
- 拍卖日志实时滚动

---

## 🎨 界面说明

### 拍卖统计卡片

```
┌─────────────────────────────┐
│ 总拍卖   成功    流拍       │
│   10    ✓ 9    ⚠️ 1       │
└─────────────────────────────┘
```

- **总拍卖** - 发布的订单总数
- **成功** (绿色) - 成功分配的订单数
- **流拍** (黄色) - 无车辆竞标的订单数

### 拍卖时间线

#### 📢 发布阶段 (Announcement)

```
订单 #5  |  发布拍卖 (7,7) → (12,12)  |  6 个竞标者
```

#### 🏆 中标阶段 (Winner Selection)

```
🏆 车辆 #3 中标
   ├─ 中标成本: 24.50
   ├─ 第二名: 38.20
   └─ 共 6 个竞标
```

- **中标成本** - 获胜车辆的综合成本
- **第二名** - 第二低的成本（显示竞争激烈程度）
- **总竞标数** - 参与竞标的车辆数

#### ✅ 授予阶段 (Award)

```
✓  订单 #5 已授予车辆 #3
```

#### ❌ 流拍阶段 (No Bids)

```
✗  订单 #8 流拍  |  无有效竞标
```

**流拍原因：**

- 所有车辆电量不足
- 所有车辆距离过远，成本超过上限
- 所有车辆都在执行任务

---

## 🔧 API 接口

### 获取拍卖日志

```bash
GET http://localhost:8001/api/auction/logs
```

**响应示例：**

```json
{
  "status": "success",
  "auction_history": [
    {
      "timestamp": 1701878400.123,
      "strategy": "Auction CNP",
      "total_auctions": 5,
      "successful_auctions": 5,
      "logs": [
        {
          "phase": "announcement",
          "order_id": 1,
          "pickup": [5, 5],
          "delivery": [10, 10],
          "bidders_count": 3
        },
        {
          "phase": "winner_selection",
          "order_id": 1,
          "winner_car_id": 2,
          "winner_cost": 18.0,
          "total_bids": 3,
          "runner_up_cost": 30.0
        },
        {
          "phase": "award",
          "order_id": 1,
          "car_id": 2,
          "status": "success"
        }
      ]
    }
  ],
  "total_records": 1
}
```

---

## 💡 使用技巧

### 1. 对比不同策略

创建两个仿真分别使用：

- **贪心策略** (GREEDY_NEAREST) - 无拍卖日志
- **拍卖策略** (AUCTION_CNP) - 有拍卖日志

观察分配效率差异。

### 2. 观察电量影响

添加订单后，观察：

- 高电量车辆是否更容易中标
- 低电量车辆成本是否明显增高

### 3. 分析竞争激烈程度

查看"第二名成本"：

- 差距大 → 中标车辆明显优势
- 差距小 → 多个车辆竞争激烈

### 4. 识别流拍模式

如果频繁流拍，可能：

- 充电站太少 → 车辆电量普遍不足
- 订单距离过远 → 所有车辆成本都太高
- 车辆数量太少 → 都在执行任务

---

## 🐛 故障排查

### 问题 1：拍卖日志面板显示"非拍卖模式"

**原因：** 未使用拍卖策略

**解决：**

1. 检查仿真创建时的策略选择
2. 确认后端 API 返回的 strategy 字段为 `"Auction CNP"`

```bash
# 检查当前策略
curl http://localhost:8001/api/simulation/state | grep strategy
```

### 问题 2：拍卖日志为空

**原因：** 没有触发拍卖

**解决：**

1. 添加新订单（点击"添加"按钮）
2. 等待 2 秒（面板自动刷新周期）
3. 检查后端日志是否有拍卖记录

```bash
# 检查拍卖日志API
curl http://localhost:8001/api/auction/logs
```

### 问题 3：组件报错

**原因：** 前端组件未正确导入

**解决：**

```bash
# 重启前端服务
pkill -9 -f vite
cd web_frontend
npm run dev
```

### 问题 4：策略列表中没有"拍卖机制(CNP)"

**原因：** 后端 strategies 接口未更新

**解决：**

```bash
# 检查strategies接口
curl http://localhost:8001/api/strategies

# 应该包含：
# {
#   "key": "AUCTION_CNP",
#   "name": "拍卖机制(CNP)",
#   "description": "合同网协议，车辆竞标订单"
# }
```

---

## 📁 相关文件

### 后端

- `web_backend/main.py` - API 端点 `/api/auction/logs`
- `agents/scheduler_agent.py` - 拍卖逻辑和日志记录

### 前端

- `web_frontend/src/components/AuctionLogPanel.vue` - 拍卖日志组件
- `web_frontend/src/views/SimulationView.vue` - 集成到主页面
- `web_frontend/src/main.js` - Vuex state 添加 strategy 字段

---

## 🎯 下一步优化

### Phase 1: 增强功能

- [ ] 添加成本分布图表（柱状图）
- [ ] 拍卖历史导出（CSV）
- [ ] 竞标成本趋势曲线

### Phase 2: 分析工具

- [ ] 平均中标成本统计
- [ ] 流拍率分析
- [ ] 车辆中标率排行榜

### Phase 3: 交互优化

- [ ] 点击日志高亮对应车辆
- [ ] 拍卖过程动画效果
- [ ] 成本对比雷达图

---

## 📖 参考文档

- [AUCTION_CNP_COMPLETION_SUMMARY.md](./AUCTION_CNP_COMPLETION_SUMMARY.md) - 拍卖机制详细文档
- [test_auction_mechanism.py](./test_auction_mechanism.py) - 后端测试脚本
- [Element Plus Timeline](https://element-plus.org/zh-CN/component/timeline.html) - 时间线组件文档

---

**完成标记：** ✅ Web 前端拍卖日志面板已实现并集成
**测试状态：** 待用户浏览器测试
**更新时间：** 2024-12-06 22:55
