"""
Pytest 配置文件 - 提供全局的 fixtures 和配置
"""

import sys
from pathlib import Path

import pytest

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录路径"""
    return project_root


@pytest.fixture
def sample_grid_5x5():
    """创建一个5x5的测试网格"""
    return [
        [".", ".", ".", ".", "."],
        [".", "#", "#", "#", "."],
        [".", ".", ".", "#", "."],
        [".", "#", ".", ".", "."],
        [".", ".", ".", ".", "."],
    ]


@pytest.fixture
def sample_grid_10x10():
    """创建一个10x10的测试网格"""
    grid = []
    for i in range(10):
        row = []
        for j in range(10):
            # 创建一些随机障碍物
            if (i, j) in [(2, 2), (2, 3), (3, 2), (7, 7)]:
                row.append("#")
            else:
                row.append(".")
        grid.append(row)
    return grid
