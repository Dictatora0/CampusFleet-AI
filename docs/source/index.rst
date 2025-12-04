CampusFleet AI 文档
==================

CampusFleet AI 是一个智能校园配送多智能体系统，采用先进的AI技术实现自主配送车辆的调度和路径规划。

.. toctree::
   :maxdepth: 2
   :caption: 目录:

   introduction
   api/index
   guides/testing
   guides/development

快速开始
--------

安装依赖::

    pip install -r requirements.txt
    pip install -r requirements-test.txt

运行测试::

    pytest tests/ -v

主要特性
--------

* 🚗 **多智能体系统**: 支持多个自主配送车辆协同工作
* 🗺️ **路径规划**: 高效的A*算法和MAPF（Multi-Agent Path Finding）
* 📊 **数据分析**: 完整的仿真数据记录和可视化
* 🧪 **完整测试**: 94%+ 代码覆盖率
* 🏗️ **企业级架构**: 统一日志、异常处理、配置管理

技术栈
------

- Python 3.8+
- Pytest (测试框架)
- Pygame (可视化)
- NumPy (数值计算)

索引和表格
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
