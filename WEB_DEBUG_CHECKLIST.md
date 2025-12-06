# Web 仿真控制台功能调试清单

## 🚀 快速启动

```bash
chmod +x debug_web.sh
./debug_web.sh
```

然后访问：http://localhost:3000

---

## ✅ 功能测试清单

### 1. **Canvas 可视化**

- [ ] 网格线显示正常
- [ ] 障碍物（灰色方块）显示
- [ ] 车辆（橙色圆圈）显示
- [ ] 订单取货点（绿色方块）显示
- [ ] 订单送货点（蓝色方块）显示
- [ ] Canvas 大小适配正常

**验证方法：**
打开 http://localhost:3000，查看左侧 Canvas 区域

---

### 2. **仿真控制按钮**

- [ ] **创建仿真**按钮工作
  - 点击后能创建新仿真
  - 配置参数生效（网格大小、车辆数等）
- [ ] **启动**按钮工作（绿色）
  - 点击后仿真开始运行
  - 车辆开始移动
- [ ] **停止**按钮工作（黄色）
  - 点击后仿真暂停
  - 车辆停止移动
- [ ] **单步**按钮工作（蓝色）
  - 点击后执行一步
  - 步数计数器+1
- [ ] **重置**按钮工作（红色）
  - 点击后仿真重置
  - 所有数据清空

**验证方法：**
依次点击各按钮，观察效果

---

### 3. **订单管理**

- [ ] **添加订单对话框**打开
  - 点击右侧"添加"按钮
  - 对话框正常弹出
- [ ] **手动添加订单**功能
  - 输入取货点坐标
  - 输入送货点坐标
  - 点击"创建"按钮
  - Canvas 出现新订单方块
  - 订单列表显示新订单
- [ ] **随机订单**功能
  - 点击"随机订单"按钮
  - Canvas 出现新订单
  - 订单列表更新
- [ ] **订单列表**显示
  - 显示待处理订单
  - 显示订单 ID 和坐标
  - 点击订单可选中

**验证方法：**

1. 先停止仿真
2. 点击"添加" -> "随机订单"
3. 观察 Canvas 和订单列表

---

### 4. **车辆状态**

- [ ] **车辆列表**显示
  - 显示所有车辆
  - 显示车辆 ID
  - 显示车辆状态（空闲/执行任务等）
  - 显示电池电量
- [ ] **车辆选中**功能
  - 点击车辆可选中
  - Canvas 高亮显示选中车辆
- [ ] **车辆路径**显示
  - 切换"显示路径"开关
  - Canvas 显示车辆计划路径

**验证方法：**
查看右侧车辆列表，点击不同车辆

---

### 5. **实时数据更新**

- [ ] **WebSocket 连接**正常
  - 右上角显示绿点（已连接）
  - 数据实时更新
- [ ] **步数计数器**实时更新
- [ ] **完成订单数**实时更新
- [ ] **车辆位置**实时更新
- [ ] **订单状态**实时更新

**验证方法：**
启动仿真，观察数据是否自动更新

---

### 6. **页面滚动**

- [ ] 页面可以上下滚动
- [ ] 所有内容都能查看
- [ ] 不会出现内容被截断

**验证方法：**
滚动页面查看所有区域

---

## 🐛 常见问题排查

### 问题 1：Canvas 是空白的

**可能原因：**

- Props 传递错误
- 数据结构不匹配
- 前端未刷新

**解决方法：**

```bash
# 刷新浏览器
Cmd + Shift + R  (macOS)
Ctrl + Shift + R  (Windows)

# 或重启前端
cd web_frontend
npm run dev
```

---

### 问题 2：订单添加没反应

**可能原因：**

- 订单立即被完成（仿真在自动运行）
- API 调用失败
- 事件监听错误

**解决方法：**

```bash
# 1. 先停止仿真
curl -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "stop"}'

# 2. 然后添加订单
curl -X POST http://localhost:8001/api/orders/random

# 3. 刷新页面查看
```

---

### 问题 3：后端崩溃

**症状：**

- API 请求失败
- 控制台出现错误

**解决方法：**

```bash
# 重启所有服务
./debug_web.sh
```

---

### 问题 4：WebSocket 连接失败

**症状：**

- 右上角显示红点
- 数据不更新

**解决方法：**

```bash
# 检查后端是否运行
curl http://localhost:8001/api/simulation/state

# 如果失败，重启服务
./debug_web.sh
```

---

## 📊 验证命令

### 检查后端状态

```bash
curl -s http://localhost:8001/api/simulation/state | python3 -m json.tool | head -30
```

### 检查订单数据

```bash
curl -s http://localhost:8001/api/simulation/state | \
  python3 -c "import sys, json; d=json.load(sys.stdin); \
  print('待处理订单:', len(d['orders']['pending'])); \
  print('车辆数:', len(d['vehicles']))"
```

### 手动添加订单

```bash
curl -X POST http://localhost:8001/api/orders/random
```

### 手动控制仿真

```bash
# 启动
curl -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "start"}'

# 停止
curl -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "stop"}'

# 单步
curl -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "step"}'
```

---

## 🎯 完整测试流程

1. **启动服务**

   ```bash
   ./debug_web.sh
   ```

2. **打开浏览器**
   访问 http://localhost:3000

3. **验证初始状态**

   - ✅ Canvas 显示 6 辆车
   - ✅ Canvas 显示 5 个订单
   - ✅ 仿真处于停止状态

4. **测试手动控制**

   - 点击"启动"按钮
   - 观察车辆移动
   - 点击"停止"按钮
   - 车辆停止移动

5. **测试订单添加**

   - 确保仿真已停止
   - 点击"添加" -> "随机订单"
   - 观察 Canvas 出现新订单
   - 订单列表更新

6. **测试自动运行**

   - 点击"启动"按钮
   - 观察订单被逐个完成
   - "完成订单"数字增加

7. **测试单步模式**
   - 点击"停止"按钮
   - 点击"单步"按钮
   - 步数+1，车辆移动一步

---

## ✅ 所有功能正常的标志

- [x] Canvas 正常显示所有元素
- [x] 所有控制按钮响应正常
- [x] 订单可以成功添加
- [x] 车辆自动执行任务
- [x] 数据实时更新
- [x] WebSocket 连接稳定
- [x] 页面可以正常滚动

---

## 🛠️ 代码修复总结

已修复的问题：

1. ✅ Canvas props 传递（orders.pending）
2. ✅ 订单创建事件监听
3. ✅ 随机订单 API 方法
4. ✅ 页面滚动 CSS
5. ✅ CSV 导出 frame_records 属性

---

**祝调试顺利！** 🎉
