#!/bin/bash

echo "🧹 清理Python缓存..."
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "🛑 停止所有服务..."
pkill -9 -f "web_backend/main.py" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null

sleep 2

echo "✅ 清理完成，现在可以运行实验了"
echo ""
echo "运行命令："
echo "./run_experiment.sh 15 6 20 BALANCED_LOAD"
