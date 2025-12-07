"""
配置管理模块
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class SimulationConfig:
    """仿真配置"""

    grid_size: int = 15
    num_cars: int = 3
    max_steps: int = 1000
    fps: int = 2
    enable_logging: bool = True
    log_level: str = "INFO"

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.grid_size < 5 or self.grid_size > 100:
            raise ValueError(f"grid_size must be between 5 and 100, got {self.grid_size}")
        if self.num_cars < 1 or self.num_cars > 50:
            raise ValueError(f"num_cars must be between 1 and 50, got {self.num_cars}")
        if self.max_steps < 1:
            raise ValueError(f"max_steps must be positive, got {self.max_steps}")
        return True


@dataclass
class CarConfig:
    """车辆配置"""

    max_battery: int = 100
    battery_consumption_rate: float = 1.0
    charging_rate: float = 5.0
    low_battery_threshold: int = 20
    critical_battery_threshold: int = 10
    max_capacity: int = 3  # VRP 最大订单容量

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.max_battery <= 0:
            raise ValueError("max_battery must be positive")
        if self.battery_consumption_rate <= 0:
            raise ValueError("battery_consumption_rate must be positive")
        if self.charging_rate <= 0:
            raise ValueError("charging_rate must be positive")
        return True


@dataclass
class RLConfig:
    """强化学习配置"""

    # DQN 配置
    dqn_learning_rate: float = 1e-3
    dqn_gamma: float = 0.95
    dqn_epsilon_start: float = 0.9
    dqn_epsilon_end: float = 0.01
    dqn_epsilon_decay: int = 10000
    dqn_memory_size: int = 50000
    dqn_batch_size: int = 64

    # PPO 配置
    ppo_learning_rate: float = 3e-4
    ppo_gamma: float = 0.99
    ppo_gae_lambda: float = 0.95
    ppo_clip_ratio: float = 0.2
    ppo_entropy_coef: float = 0.01
    ppo_value_coef: float = 0.5
    ppo_update_epochs: int = 10

    # 训练配置
    max_episodes: int = 1000
    eval_interval: int = 50
    save_interval: int = 100
    early_stop_threshold: float = 0.90
    patience: int = 200

    # 环境配置
    env_max_steps: int = 200
    env_max_orders_per_episode: int = 15

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.dqn_learning_rate <= 0 or self.ppo_learning_rate <= 0:
            raise ValueError("Learning rates must be positive")
        if not (0 < self.dqn_gamma < 1) or not (0 < self.ppo_gamma < 1):
            raise ValueError("Gamma must be between 0 and 1")
        return True


@dataclass
class WebConfig:
    """Web 服务配置"""

    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    workers: int = 1
    cors_origins: list = field(default_factory=lambda: ["*"])

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.port < 1024 or self.port > 65535:
            raise ValueError(f"port must be between 1024 and 65535, got {self.port}")
        if self.workers < 1:
            raise ValueError("workers must be at least 1")
        return True


@dataclass
class DemoConfig:
    """演示/测试配置"""

    small_grid_size: int = 8
    small_num_cars: int = 2
    test_num_orders: int = 10

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.test_num_orders < 1:
            raise ValueError("test_num_orders must be positive")
        return True


@dataclass
class VisualizationConfig:
    """可视化配置"""

    cell_size: int = 40
    fps: int = 10

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.cell_size < 10 or self.cell_size > 100:
            raise ValueError("cell_size must be between 10 and 100")
        if self.fps < 1 or self.fps > 60:
            raise ValueError("fps must be between 1 and 60")
        return True


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.simulation = SimulationConfig()
        self.car = CarConfig()
        self.rl = RLConfig()
        self.web = WebConfig()
        self.demo = DemoConfig()
        self.visualization = VisualizationConfig()

    def load_from_file(self, config_file: str):
        """从 JSON 文件加载配置"""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # 更新配置
        if "simulation" in config_data:
            self.simulation = SimulationConfig(**config_data["simulation"])
        if "car" in config_data:
            self.car = CarConfig(**config_data["car"])
        if "rl" in config_data:
            self.rl = RLConfig(**config_data["rl"])
        if "web" in config_data:
            self.web = WebConfig(**config_data["web"])
        if "demo" in config_data:
            self.demo = DemoConfig(**config_data["demo"])
        if "visualization" in config_data:
            self.visualization = VisualizationConfig(**config_data["visualization"])

        # 验证所有配置
        self.validate_all()

    def save_to_file(self, config_file: str):
        """保存配置到 JSON 文件"""
        config_data = {
            "simulation": self.simulation.__dict__,
            "car": self.car.__dict__,
            "rl": self.rl.__dict__,
            "web": self.web.__dict__,
            "demo": self.demo.__dict__,
            "visualization": self.visualization.__dict__,
        }

        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def validate_all(self):
        """验证所有配置"""
        self.simulation.validate()
        self.car.validate()
        self.rl.validate()
        self.web.validate()
        self.demo.validate()
        self.visualization.validate()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "simulation": self.simulation.__dict__,
            "car": self.car.__dict__,
            "rl": self.rl.__dict__,
            "web": self.web.__dict__,
            "demo": self.demo.__dict__,
            "visualization": self.visualization.__dict__,
        }


# 全局配置实例
config = ConfigManager()
