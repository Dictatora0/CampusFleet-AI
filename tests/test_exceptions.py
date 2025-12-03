"""
测试自定义异常模块
"""

import pytest

from core.exceptions import (
    CampusFleetException,
    CarAgentError,
    ConfigurationError,
    OrderError,
    PathfindingError,
    ResourceError,
    SchedulingError,
    SimulationError,
    ValidationError,
)


class TestExceptionHierarchy:
    """测试异常继承层次"""

    def test_base_exception(self):
        """测试基础异常类"""
        exc = CampusFleetException("测试错误")
        assert str(exc) == "测试错误"
        assert isinstance(exc, Exception)

    def test_simulation_error(self):
        """测试仿真错误"""
        exc = SimulationError("仿真错误")
        assert isinstance(exc, CampusFleetException)
        assert isinstance(exc, Exception)

    def test_pathfinding_error(self):
        """测试路径规划错误"""
        exc = PathfindingError("路径规划错误")
        assert isinstance(exc, CampusFleetException)

    def test_scheduling_error(self):
        """测试调度错误"""
        exc = SchedulingError("调度错误")
        assert isinstance(exc, CampusFleetException)

    def test_order_error(self):
        """测试订单错误"""
        exc = OrderError("订单错误")
        assert isinstance(exc, CampusFleetException)

    def test_car_agent_error(self):
        """测试车辆智能体错误"""
        exc = CarAgentError("车辆错误")
        assert isinstance(exc, CampusFleetException)

    def test_configuration_error(self):
        """测试配置错误"""
        exc = ConfigurationError("配置错误")
        assert isinstance(exc, CampusFleetException)

    def test_validation_error(self):
        """测试验证错误"""
        exc = ValidationError("验证错误")
        assert isinstance(exc, CampusFleetException)

    def test_resource_error(self):
        """测试资源错误"""
        exc = ResourceError("资源错误")
        assert isinstance(exc, CampusFleetException)


class TestExceptionRaising:
    """测试异常抛出和捕获"""

    def test_raise_and_catch_specific(self):
        """测试抛出和捕获特定异常"""
        with pytest.raises(SimulationError) as exc_info:
            raise SimulationError("测试仿真错误")

        assert "测试仿真错误" in str(exc_info.value)

    def test_raise_and_catch_base(self):
        """测试用基类捕获子类异常"""
        with pytest.raises(CampusFleetException):
            raise PathfindingError("路径错误")

    def test_exception_with_details(self):
        """测试带详细信息的异常"""
        error_msg = "无法找到从 (0,0) 到 (10,10) 的路径"
        with pytest.raises(PathfindingError) as exc_info:
            raise PathfindingError(error_msg)

        assert error_msg in str(exc_info.value)

    def test_multiple_exception_types(self):
        """测试多种异常类型"""
        exceptions = [
            (SimulationError, "仿真错误"),
            (PathfindingError, "路径错误"),
            (SchedulingError, "调度错误"),
            (OrderError, "订单错误"),
            (CarAgentError, "车辆错误"),
            (ConfigurationError, "配置错误"),
            (ValidationError, "验证错误"),
            (ResourceError, "资源错误"),
        ]

        for exc_class, msg in exceptions:
            with pytest.raises(exc_class) as exc_info:
                raise exc_class(msg)
            assert msg in str(exc_info.value)


class TestExceptionInContext:
    """测试在实际场景中使用异常"""

    def test_error_handling_pattern(self):
        """测试错误处理模式"""

        def risky_operation():
            raise PathfindingError("无法找到路径")

        try:
            risky_operation()
            assert False, "应该抛出异常"
        except PathfindingError as e:
            assert "无法找到路径" in str(e)
        except CampusFleetException:
            assert False, "应该捕获更具体的异常"

    def test_exception_chaining(self):
        """测试异常链"""
        try:
            try:
                raise ValueError("原始错误")
            except ValueError as e:
                raise ConfigurationError("配置加载失败") from e
        except ConfigurationError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
