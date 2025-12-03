"""
自定义异常类模块
"""


class CampusFleetException(Exception):
    """CampusFleet AI 基础异常类"""

    pass


class SimulationError(CampusFleetException):
    """仿真运行错误"""

    pass


class PathfindingError(CampusFleetException):
    """路径规划错误"""

    pass


class SchedulingError(CampusFleetException):
    """调度错误"""

    pass


class OrderError(CampusFleetException):
    """订单处理错误"""

    pass


class CarAgentError(CampusFleetException):
    """车辆智能体错误"""

    pass


class ConfigurationError(CampusFleetException):
    """配置错误"""

    pass


class ValidationError(CampusFleetException):
    """数据验证错误"""

    pass


class ResourceError(CampusFleetException):
    """资源不足错误"""

    pass
