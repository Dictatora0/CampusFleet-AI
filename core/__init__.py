"""核心模块初始化"""

# 基础模块 - 无依赖，可直接导入
from .config import CarConfig, ConfigManager, RLConfig, SimulationConfig, WebConfig, config
from .decorators import (
    cache_result,
    log_calls,
    monitor_performance,
    performance_monitor,
    retry,
    timer,
    validate_args,
)
from .exceptions import (
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
from .logger import LoggerManager, get_logger


# 延迟导入 - 避免循环依赖
# 使用时才导入 SimulationContext 和 Simulation
def _lazy_import_simulation():
    """延迟导入仿真相关模块"""
    from .context import SimulationContext
    from .simulation import Simulation, run_simulation

    return SimulationContext, Simulation, run_simulation


# 提供便捷的访问方式
def get_simulation_context(*args, **kwargs):
    """获取 SimulationContext 实例"""
    SimulationContext, _, _ = _lazy_import_simulation()
    return SimulationContext(*args, **kwargs)


def get_simulation(*args, **kwargs):
    """获取 Simulation 实例"""
    _, Simulation, _ = _lazy_import_simulation()
    return Simulation(*args, **kwargs)


# 为了向后兼容，在 __getattr__ 中处理延迟导入
def __getattr__(name):
    if name in ("SimulationContext", "Simulation", "run_simulation"):
        SimulationContext, Simulation, run_simulation = _lazy_import_simulation()
        if name == "SimulationContext":
            return SimulationContext
        elif name == "Simulation":
            return Simulation
        elif name == "run_simulation":
            return run_simulation
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # 核心类
    "SimulationContext",
    "Simulation",
    "run_simulation",
    # 日志
    "get_logger",
    "LoggerManager",
    # 配置
    "config",
    "ConfigManager",
    "SimulationConfig",
    "CarConfig",
    "RLConfig",
    "WebConfig",
    # 异常
    "CampusFleetException",
    "SimulationError",
    "PathfindingError",
    "SchedulingError",
    "OrderError",
    "CarAgentError",
    "ConfigurationError",
    "ValidationError",
    "ResourceError",
    # 装饰器
    "timer",
    "retry",
    "cache_result",
    "validate_args",
    "log_calls",
    "monitor_performance",
    "performance_monitor",
]
