"""
测试配置管理模块
"""

import json
import os
import tempfile

import pytest

from core.config import CarConfig, ConfigManager, RLConfig, SimulationConfig, WebConfig


class TestSimulationConfig:
    """测试仿真配置"""

    def test_default_values(self):
        """测试默认值"""
        config = SimulationConfig()
        assert config.grid_size == 15
        assert config.num_cars == 3
        assert config.max_steps == 1000
        assert config.fps == 2
        assert config.enable_logging is True
        assert config.log_level == "INFO"

    def test_custom_values(self):
        """测试自定义值"""
        config = SimulationConfig(grid_size=20, num_cars=5, max_steps=2000)
        assert config.grid_size == 20
        assert config.num_cars == 5
        assert config.max_steps == 2000

    def test_validation_success(self):
        """测试验证成功"""
        config = SimulationConfig(grid_size=10, num_cars=5)
        assert config.validate() is True

    def test_validation_grid_size_too_small(self):
        """测试网格大小过小"""
        config = SimulationConfig(grid_size=3)
        with pytest.raises(ValueError, match="grid_size"):
            config.validate()

    def test_validation_grid_size_too_large(self):
        """测试网格大小过大"""
        config = SimulationConfig(grid_size=150)
        with pytest.raises(ValueError, match="grid_size"):
            config.validate()

    def test_validation_num_cars_invalid(self):
        """测试车辆数量无效"""
        config = SimulationConfig(num_cars=0)
        with pytest.raises(ValueError, match="num_cars"):
            config.validate()


class TestCarConfig:
    """测试车辆配置"""

    def test_default_values(self):
        """测试默认值"""
        config = CarConfig()
        assert config.max_battery == 100
        assert config.battery_consumption_rate == 1.0
        assert config.charging_rate == 5.0
        assert config.low_battery_threshold == 20
        assert config.critical_battery_threshold == 10
        assert config.max_capacity == 3

    def test_validation_success(self):
        """测试验证成功"""
        config = CarConfig()
        assert config.validate() is True

    def test_validation_negative_battery(self):
        """测试负电量"""
        config = CarConfig(max_battery=-10)
        with pytest.raises(ValueError, match="max_battery"):
            config.validate()


class TestRLConfig:
    """测试强化学习配置"""

    def test_default_values(self):
        """测试默认值"""
        config = RLConfig()
        assert config.dqn_learning_rate == 1e-3
        assert config.ppo_learning_rate == 3e-4
        assert config.max_episodes == 1000

    def test_validation_success(self):
        """测试验证成功"""
        config = RLConfig()
        assert config.validate() is True

    def test_validation_invalid_learning_rate(self):
        """测试无效学习率"""
        config = RLConfig(dqn_learning_rate=-0.001)
        with pytest.raises(ValueError, match="Learning rates"):
            config.validate()


class TestWebConfig:
    """测试Web配置"""

    def test_default_values(self):
        """测试默认值"""
        config = WebConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8001
        assert config.reload is False
        assert config.workers == 1

    def test_validation_success(self):
        """测试验证成功"""
        config = WebConfig()
        assert config.validate() is True

    def test_validation_invalid_port(self):
        """测试无效端口"""
        config = WebConfig(port=100)
        with pytest.raises(ValueError, match="port"):
            config.validate()


class TestConfigManager:
    """测试配置管理器"""

    def test_initialization(self):
        """测试初始化"""
        manager = ConfigManager()
        assert manager.simulation is not None
        assert manager.car is not None
        assert manager.rl is not None
        assert manager.web is not None

    def test_to_dict(self):
        """测试转换为字典"""
        manager = ConfigManager()
        config_dict = manager.to_dict()

        assert "simulation" in config_dict
        assert "car" in config_dict
        assert "rl" in config_dict
        assert "web" in config_dict

    def test_save_and_load(self):
        """测试保存和加载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.json")

            # 创建并修改配置
            manager1 = ConfigManager()
            manager1.simulation.grid_size = 25
            manager1.car.max_battery = 150

            # 保存配置
            manager1.save_to_file(config_file)
            assert os.path.exists(config_file)

            # 加载配置
            manager2 = ConfigManager()
            manager2.load_from_file(config_file)

            # 验证配置
            assert manager2.simulation.grid_size == 25
            assert manager2.car.max_battery == 150

    def test_validate_all(self):
        """测试验证所有配置"""
        manager = ConfigManager()
        # 默认配置应该都有效
        manager.validate_all()  # 不应该抛出异常

    def test_validate_all_with_invalid_config(self):
        """测试验证无效配置"""
        manager = ConfigManager()
        manager.simulation.grid_size = 200  # 超出范围

        with pytest.raises(ValueError):
            manager.validate_all()

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        manager = ConfigManager()
        with pytest.raises(FileNotFoundError):
            manager.load_from_file("nonexistent_config.json")

    def test_load_invalid_json(self):
        """测试加载无效JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "invalid.json")
            with open(config_file, "w") as f:
                f.write("{ invalid json }")

            manager = ConfigManager()
            with pytest.raises(json.JSONDecodeError):
                manager.load_from_file(config_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
