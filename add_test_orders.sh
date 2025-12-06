#!/bin/bash

echo "🔄 添加测试订单..."

# 添加10个随机订单
for i in {1..10}; do
  result=$(curl -s -X POST http://localhost:8001/api/orders/random)
  echo "订单 $i: $result"
  sleep 0.1
done

echo ""
echo "✅ 已添加10个订单"
echo ""
echo "📊 当前状态："
curl -s http://localhost:8001/api/simulation/state | python -c "import sys, json; d=json.load(sys.stdin); print(f'步数: {d[\"step\"]}'); print(f'运行中: {d[\"is_running\"]}'); print(f'车辆数: {len(d[\"vehicles\"])}'); print(f'待处理订单: {len(d[\"orders\"][\"pending\"])}')"

echo ""
echo "💡 现在刷新浏览器页面查看效果"
echo "   http://localhost:3000"
