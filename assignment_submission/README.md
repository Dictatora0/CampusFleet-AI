# 课程作业提交材料

**项目**: 多智能体校园配送系统  
**日期**: 2025-12-04  

## 📁 文件说明

本目录包含所有作业提交材料：

### 1. 技术方案.md
完整的技术方案文档，包括：
- 系统概述
- 智能体架构（4类智能体）
- 决策方法（Double DQN详解）
- 协作机制（任务分配、通信、冲突避免）
- 实验结果和分析
- 代码实现细节

### 2. 演示脚本.md
课堂演示用脚本（5-8分钟），包括：
- 完整演示流程
- 每分钟说什么
- 常见问题回答
- 技术细节准备
- 备用方案

### 3. 使用指南.md
系统使用说明，包括：
- 快速开始
- 实验运行
- 参数调优
- 常见问题
- 高级功能

## 🚀 快速开始

### 运行GUI演示
```bash
cd "/Users/lifulin/Desktop/CampusFleet AI"
source venv/bin/activate
python run_with_gui.py --strategy dqn_inference --cars 4
```

### 查看实验结果
```bash
open experiments/results/dqn_comparison.png
```

### 启动Web界面
```bash
# 终端1
cd web_backend && python main.py

# 终端2  
cd web_frontend && npm run dev
```

## 📊 关键结果

- **算法**: Double DQN （优于Standard DQN 1.1%）
- **完成率**: 31.4%
- **车辆数**: 4-5辆并行工作
- **测试覆盖率**: 92%

## 📚 更多信息

- 项目主README: ../README.md
- 实验详细文档: ../experiments/README_RIGOROUS_EXPERIMENT.md
- 源代码: https://github.com/Dictatora0/CampusFleet-AI

---

**最后更新**: 2025-12-04
