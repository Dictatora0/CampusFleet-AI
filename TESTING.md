# 测试指南

本项目使用 `pytest` 框架进行自动化测试。测试套件包括单元测试和集成测试，覆盖系统的关键组件。

## 安装测试依赖

```bash
pip install -r requirements.txt
```

这将安装：

- `pytest>=6.0.0` - 测试框架
- `pytest-cov>=2.10.0` - 测试覆盖率工具
- `scipy>=1.5.0` - 匈牙利算法支持

## 运行测试

### 运行所有测试

```bash
# 简单运行
pytest

# 详细输出
pytest -v

# 显示打印输出
pytest -v -s
```

### 运行特定测试文件

```bash
# 测试路径规划模块
pytest tests/test_pathfinding.py -v

# 测试车辆智能体
pytest tests/test_car_agent.py -v

# 测试调度器
pytest tests/test_scheduler.py -v

# 集成测试
pytest test_system.py -v
```

### 运行特定测试类或函数

```bash
# 运行特定测试类
pytest tests/test_pathfinding.py::TestAStarAlgorithm -v

# 运行特定测试函数
pytest tests/test_car_agent.py::TestCarAgentInitialization::test_basic_initialization -v
```

### 使用标记过滤测试

```bash
# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行路径规划相关测试
pytest -m pathfinding
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest --cov=. --cov-report=html

# 查看报告
open htmlcov/index.html  # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

### 生成终端覆盖率报告

```bash
pytest --cov=. --cov-report=term-missing
```

## 测试结构

```
CampusFleet AI/
├── tests/                      # 单元测试目录
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_pathfinding.py    # 路径规划测试
│   ├── test_car_agent.py      # 车辆智能体测试
│   └── test_scheduler.py      # 调度器测试
├── test_system.py             # 集成测试
└── pytest.ini                 # Pytest 配置
```

## 测试内容

### 1. 路径规划测试 (`test_pathfinding.py`)

- **基本功能**: 初始化、位置验证、邻居查找
- **A\*算法**: 简单路径、障碍物绕行、无路径情况
- **BFS 算法**: 基本路径规划
- **边界情况**: 空网格、单格网格、全障碍物

### 2. 车辆智能体测试 (`test_car_agent.py`)

- **初始化**: 基本参数、默认值
- **状态转换**: 空闲 → 取货 → 配送 → 完成
- **移动逻辑**: 路径规划、避障、距离跟踪
- **任务执行**: 任务分配、完整配送流程
- **碰撞处理**: 优先级判断、避让策略

### 3. 调度器测试 (`test_scheduler.py`)

- **策略测试**: 贪心、负载均衡、匈牙利算法
- **分配逻辑**: 单订单、多订单、订单多于车辆
- **边界情况**: 无空闲车、空订单列表
- **跟踪功能**: 分配历史、统计计数

### 4. 集成测试 (`test_system.py`)

- **模块导入**: 验证所有模块可正确导入
- **环境模块**: 地图创建、路径规划
- **智能体模块**: 车辆、订单、调度器创建
- **仿真系统**: 上下文创建、订单添加、仿真执行
- **完整工作流**: 多订单处理、车辆协同

## 编写新测试

### 测试文件命名

- 测试文件名以 `test_` 开头
- 测试类名以 `Test` 开头
- 测试函数名以 `test_` 开头

### 使用 Fixtures

```python
import pytest

@pytest.fixture
def my_fixture():
    """提供测试数据"""
    return some_test_data

def test_something(my_fixture):
    """使用 fixture 的测试"""
    assert my_fixture is not None
```

### 断言最佳实践

```python
# 好的断言 - 带有错误信息
assert result == expected, f"期望 {expected}，得到 {result}"

# 好的断言 - 明确的条件
assert len(items) > 0, "列表不应该为空"

# 避免 - 没有错误信息
assert result == expected
```

## 持续集成

测试套件设计用于 CI/CD 环境：

```yaml
# .github/workflows/test.yml 示例
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.8"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest -v --cov=. --cov-report=xml
```

## 故障排查

### 导入错误

如果遇到 `ModuleNotFoundError`：

```bash
# 确保在项目根目录运行测试
cd /path/to/CampusFleet-AI
pytest
```

### scipy 未安装

如果看到匈牙利算法回退警告：

```bash
pip install scipy>=1.5.0
```

### 测试失败

1. 查看详细输出: `pytest -v`
2. 查看完整回溯: `pytest --tb=long`
3. 停在第一个失败: `pytest -x`
4. 显示打印语句: `pytest -s`

## 性能测试

虽然当前测试套件专注于功能正确性，但可以添加性能测试：

```python
import time

def test_performance():
    """测试性能"""
    start = time.time()
    # 执行操作
    elapsed = time.time() - start
    assert elapsed < 1.0, f"操作耗时 {elapsed}s，超过1秒"
```

## 贡献指南

添加新功能时，请：

1. 为新功能编写测试
2. 确保所有现有测试通过
3. 保持测试覆盖率 > 80%
4. 更新本文档

---

更多信息请参考：

- [Pytest 文档](https://docs.pytest.org/)
- [项目 README](README.md)
