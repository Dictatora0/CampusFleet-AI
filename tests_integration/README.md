# 集成测试目录

本目录包含系统级集成测试脚本。

## 文件说明

- **test_system.py** - 基础系统功能测试
- **test_gui.py** - 图形界面集成测试
- **test_improvements.py** - 系统改进验证测试
- **test_mapf.py** - MAPF 算法集成测试
- **test_vrp.py** - VRP 算法集成测试
- **test_rl_system.py** - 强化学习系统完整测试

## 使用方法

```bash
# 运行基础系统测试
python tests_integration/test_system.py

# 运行 RL 系统测试
python tests_integration/test_rl_system.py

# 运行所有集成测试
pytest tests_integration/
```

## 测试说明

- 集成测试验证多个模块协同工作
- 单元测试位于 `tests/` 目录
- 运行测试前确保安装所有依赖
