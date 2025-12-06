#!/bin/bash
# 显示调度策略列表（中文正常显示）

echo "📋 CampusFleet AI - 调度策略列表"
echo "================================"
echo ""

curl -s http://localhost:8001/api/strategies | jq -r '.strategies[] | "[\(.category)] \(.name)\n  Key: \(.key)\n  说明: \(.description)\n"'

echo "================================"
echo "✅ 共 $(curl -s http://localhost:8001/api/strategies | jq '.strategies | length') 个策略"
