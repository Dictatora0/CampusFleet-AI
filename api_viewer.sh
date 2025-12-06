#!/bin/bash
# CampusFleet AI - API查看工具（中文友好）

BASE_URL="http://localhost:8001"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

# 1. 显示调度策略
show_strategies() {
    show_header "📋 调度策略列表"
    curl -s $BASE_URL/api/strategies | jq -r '.strategies[] | "[\(.category)] \(.name)\n  Key: \(.key)\n  说明: \(.description)\n"'
    echo ""
}

# 2. 显示仿真状态
show_state() {
    show_header "🎮 仿真状态"
    STATE=$(curl -s $BASE_URL/api/simulation/state)

    echo "运行状态: $(echo $STATE | jq -r '.is_running')"
    echo "当前步数: $(echo $STATE | jq -r '.step')"
    echo "调度策略: $(echo $STATE | jq -r '.strategy')"
    echo "车辆数量: $(echo $STATE | jq -r '.vehicles | length')"
    echo "待分配订单: $(echo $STATE | jq -r '.orders.pending | length')"
    echo ""
}

# 3. 显示拍卖日志
show_auction_logs() {
    show_header "🎪 拍卖日志"
    LOGS=$(curl -s $BASE_URL/api/auction/logs)

    if [ "$(echo $LOGS | jq -r '.total_records')" -eq 0 ]; then
        echo "暂无拍卖日志"
    else
        echo $LOGS | jq -r '.auction_history[] | "时间: \(.timestamp)\n策略: \(.strategy)\n总拍卖: \(.total_auctions)\n成功: \(.successful_auctions)\n"'
    fi
    echo ""
}

# 4. 显示车辆状态
show_vehicles() {
    show_header "🚗 车辆状态"
    curl -s $BASE_URL/api/simulation/state | jq -r '.vehicles[] | "车辆#\(.id) - 位置:(\(.position[0]),\(.position[1])) 电量:\(.battery)% 状态:\(.state)"'
    echo ""
}

# 主菜单
case "$1" in
    strategies)
        show_strategies
        ;;
    state)
        show_state
        ;;
    auction)
        show_auction_logs
        ;;
    vehicles)
        show_vehicles
        ;;
    all)
        show_strategies
        show_state
        show_auction_logs
        show_vehicles
        ;;
    *)
        echo -e "${YELLOW}使用方法:${NC}"
        echo "  ./api_viewer.sh strategies   # 查看调度策略"
        echo "  ./api_viewer.sh state        # 查看仿真状态"
        echo "  ./api_viewer.sh auction      # 查看拍卖日志"
        echo "  ./api_viewer.sh vehicles     # 查看车辆状态"
        echo "  ./api_viewer.sh all          # 查看所有信息"
        echo ""
        echo -e "${YELLOW}示例:${NC}"
        echo "  ./api_viewer.sh strategies"
        ;;
esac
