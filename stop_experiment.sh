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
