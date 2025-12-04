测试指南
========

本项目具有完整的测试覆盖，包括单元测试、集成测试和性能测试。

运行测试
--------

运行所有测试::

    pytest tests/ -v

运行特定模块测试::

    pytest tests/test_logger.py -v

生成覆盖率报告::

    pytest tests/ --cov=core --cov-report=html

测试结构
--------

测试文件组织::

    tests/
    ├── conftest.py              # 测试配置和fixtures
    ├── test_logger.py           # 日志系统测试
    ├── test_exceptions.py       # 异常测试
    ├── test_config.py           # 配置管理测试
    ├── test_decorators.py       # 装饰器测试
    ├── test_grid.py             # 网格环境测试
    ├── test_order_agent.py      # 订单智能体测试
    ├── test_data_logger.py      # 数据记录器测试
    ├── test_car_agent.py        # 车辆智能体测试
    ├── test_pathfinding.py      # 路径规划测试
    └── test_scheduler.py        # 调度器测试

测试覆盖率
----------

当前测试覆盖率统计:

- **核心模块**: 94%
- **智能体模块**: 85%
- **环境模块**: 88%
- **分析模块**: 90%
- **总体覆盖率**: 91%

编写测试
--------

使用pytest框架编写测试::

    import pytest
    from module import MyClass

    class TestMyClass:
        @pytest.fixture
        def instance(self):
            return MyClass()

        def test_method(self, instance):
            result = instance.method()
            assert result == expected_value

最佳实践
--------

1. **每个功能一个测试**: 每个测试应该只测试一个功能点
2. **使用fixtures**: 复用测试数据和设置
3. **参数化测试**: 使用 ``@pytest.mark.parametrize`` 测试多个输入
4. **测试边界情况**: 包括正常情况和异常情况
5. **清晰的断言**: 使用有意义的断言消息

Mock 使用
---------

使用 unittest.mock 进行对象模拟::

    from unittest.mock import Mock, patch

    def test_with_mock():
        mock_obj = Mock()
        mock_obj.method.return_value = "mocked"
        
        result = function_using_obj(mock_obj)
        
        assert result == "mocked"
        mock_obj.method.assert_called_once()

持续集成
--------

项目配置了 GitHub Actions 自动运行测试:

- **develop 分支**: 快速测试 (Python 3.10, 3.11)
- **main 分支**: 完整测试 (Python 3.8-3.11)
- **PR 检查**: 自动运行测试和代码质量检查
