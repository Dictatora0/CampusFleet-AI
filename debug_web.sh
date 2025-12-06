#!/bin/bash

# Web页面调试脚本

echo "========================================="
echo "  Web仿真控制台调试工具"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 停止现有服务
echo -e "${BLUE}[1/5] 停止现有服务...${NC}"
pkill -9 -f "web_backend/main.py" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null

# 确保端口 8001/3000 已释放
for port in 8001 3000; do
  PIDS=$(lsof -ti :$port 2>/dev/null)
  if [ -n "$PIDS" ]; then
    echo -e "${YELLOW}⚠️  端口 $port 被占用，正在释放...${NC}"
    echo "$PIDS" | xargs kill -9 2>/dev/null
  fi
done

sleep 2
echo -e "${GREEN}✅ 清理完成${NC}"
echo ""

# 2. 启动后端
echo -e "${BLUE}[2/5] 启动后端服务...${NC}"
cd web_backend
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 3

# 检查后端
if curl -s http://localhost:8001/api/simulation/state > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端启动成功 (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ 后端启动失败${NC}"
    echo "查看日志: tail backend.log"
    exit 1
fi
echo ""

# 3. 启动前端
echo -e "${BLUE}[3/5] 启动前端服务...${NC}"
cd web_frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 5

# 检查前端
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端启动成功 (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ 前端启动失败${NC}"
    echo "查看日志: tail frontend.log"
    exit 1
fi
echo ""

# 4. 创建测试仿真（拍卖策略）
echo -e "${BLUE}[4/5] 创建测试仿真...${NC}"
curl -s -X POST http://localhost:8001/api/simulation/create \
  -H "Content-Type: application/json" \
  -d '{
    "grid_size": 15,
    "num_cars": 6,
    "strategy": "AUCTION_CNP",
    "enable_logging": true
  }' > /dev/null

echo -e "${GREEN}✅ 仿真已创建（拍卖机制）${NC}"
echo ""

# 5. 停止自动步进
echo -e "${BLUE}[5/5] 设置手动控制模式...${NC}"

# 先停止自动步进
curl -s -X POST http://localhost:8001/api/simulation/control \
  -H "Content-Type: application/json" \
  -d '{"command": "stop"}' > /dev/null

echo -e "${GREEN}✅ 已设置为手动控制模式${NC}"
echo -e "${YELLOW}💡 提示：Web页面创建仿真时会自动添加订单${NC}"

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}✅ 调试环境准备完成！${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${YELLOW}📱 访问地址：${NC}"
echo -e "   仿真控制台: ${BLUE}http://localhost:3000${NC}"
echo -e "   多智能体监控: ${BLUE}http://localhost:3000/multi-agent${NC}"
echo -e "   后端API文档: ${BLUE}http://localhost:8001/api/docs${NC}"
echo ""
echo -e "${YELLOW}🔍 当前状态：${NC}"
echo -e "   • 仿真已创建（15×15，6车辆）"
echo -e "   • ${YELLOW}未添加订单${NC}（需在Web页面操作）"
echo -e "   • 仿真处于${RED}停止${NC}状态（手动控制）"
echo ""
echo -e "${YELLOW}💡 测试步骤：${NC}"
echo -e "   1. 打开浏览器访问: http://localhost:3000"
echo -e "   2. ${GREEN}点击「创建仿真」${NC}按钮"
echo -e "      - 可设置初始订单数（0-20个）"
echo -e "      - 默认自动创建5个订单"
echo -e "   3. 查看Canvas显示："
echo -e "      - 灰色方块（障碍物）"
echo -e "      - 橙色圆圈（车辆）"
echo -e "      - ${GREEN}绿色方块（取货点）${NC}"
echo -e "      - ${BLUE}蓝色方块（送货点）${NC}"
echo -e "   4. 点击${GREEN}启动${NC}按钮，观察车辆配送"
echo -e "   5. 点击${YELLOW}单步${NC}按钮，逐步执行"
echo -e "   6. 点击${BLUE}添加${NC}按钮，手动添加更多订单"
echo ""
echo -e "${YELLOW}📊 查看状态（中文友好）：${NC}"
echo -e "   ./api_viewer.sh all          # 查看所有信息"
echo -e "   ./api_viewer.sh strategies   # 查看调度策略"
echo -e "   ./api_viewer.sh state        # 查看仿真状态"
echo ""
echo -e "${YELLOW}🛑 停止服务：${NC}"
echo -e "   pkill -9 -f 'web_backend/main.py'"
echo -e "   pkill -9 -f 'vite'"
echo ""
echo -e "${BLUE}=========================================${NC}"
