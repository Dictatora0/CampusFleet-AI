"""
Root conftest.py - 确保项目根目录在 Python 路径中
这个文件放在项目根目录，会被所有测试自动加载
"""

import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径（如果还没有）
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Python path configured: {project_root}")
