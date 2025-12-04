开发指南
========

本指南帮助开发者快速开始贡献代码。

开发环境设置
------------

1. 克隆仓库::

    git checkout develop

2. 创建虚拟环境::

    python -m venv venv
    source venv/bin/activate  # Windows: venv\\Scripts\\activate

3. 安装依赖::

    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pip install -r requirements-test.txt

4. 安装开发工具::

    ./setup_dev_tools.sh

代码规范
--------

格式化工具
~~~~~~~~~~

- **Black**: 代码格式化 (行长度: 100)
- **isort**: 导入语句排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查

运行格式化::

    ./quick_format.sh

或手动运行::

    black core/ tests/ --line-length 100
    isort core/ tests/ --profile black
    flake8 core/ --max-line-length=100

Pre-commit Hooks
~~~~~~~~~~~~~~~~

安装 pre-commit hooks::

    pre-commit install

每次提交时自动运行检查。

提交规范
--------

使用 Conventional Commits 格式:

.. code-block:: text

    <type>(<scope>): <subject>

    <body>

    <footer>

类型 (type):

- ``feat``: 新功能
- ``fix``: Bug 修复
- ``docs``: 文档更新
- ``style``: 代码格式调整
- ``refactor``: 代码重构
- ``test``: 测试相关
- ``chore``: 构建/工具更新

示例::

    feat(agents): add new scheduling algorithm

    Implement priority-based scheduling for orders

    Closes #123

分支策略
--------

主分支
~~~~~~

- ``main``: 生产分支，严格保护
- ``develop``: 开发分支，日常开发

功能分支
~~~~~~~~

从 ``develop`` 创建::

    git checkout develop
    git checkout -b feature/my-feature

命名规范:

- ``feature/``: 新功能
- ``bugfix/``: Bug 修复
- ``hotfix/``: 紧急修复
- ``refactor/``: 代码重构

工作流程
--------

1. **创建功能分支**::

    git checkout develop
    git pull origin develop
    git checkout -b feature/my-feature

2. **开发和测试**::

    # 编写代码
    # 运行测试
    pytest tests/
    
    # 格式化代码
    ./quick_format.sh

3. **提交代码**::

    git add .
    git commit -m "feat: add my feature"

4. **推送并创建 PR**::

    git push origin feature/my-feature
    # 在 GitHub 上创建 Pull Request

5. **等待 CI 和 Code Review**

6. **合并后删除分支**::

    git branch -d feature/my-feature

添加新模块
----------

1. **创建模块文件**::

    mkdir my_module
    touch my_module/__init__.py
    touch my_module/my_class.py

2. **编写代码** (包含文档字符串)

3. **添加类型注解**::

    def my_function(arg1: int, arg2: str) -> bool:
        """
        函数描述
        
        Args:
            arg1: 参数1描述
            arg2: 参数2描述
        
        Returns:
            返回值描述
        """
        return True

4. **编写测试**::

    # tests/test_my_module.py
    import pytest
    from my_module import MyClass

    class TestMyClass:
        def test_method(self):
            obj = MyClass()
            assert obj.method() == expected

5. **更新文档**:

   在 ``docs/source/api/`` 添加模块文档

性能优化
--------

分析工具
~~~~~~~~

使用 ``@performance_monitor`` 装饰器::

    from core.decorators import performance_monitor

    @performance_monitor
    def my_slow_function():
        # 代码
        pass

基准测试::

    pytest tests/benchmarks/ --benchmark-only

优化建议
~~~~~~~~

1. 使用适当的数据结构
2. 避免不必要的循环
3. 缓存重复计算
4. 使用生成器处理大数据
5. 并行化独立任务

调试技巧
--------

使用日志::

    from core.logger import LoggerManager

    logger = LoggerManager.get_logger(__name__)
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告")
    logger.error("错误")

使用 pdb 调试器::

    import pdb
    pdb.set_trace()  # 设置断点

常见问题
--------

Q: 如何运行单个测试?
~~~~~~~~~~~~~~~~~~~~

A: 使用 pytest 的 ``-k`` 参数::

    pytest tests/ -k "test_function_name"

Q: 如何生成文档?
~~~~~~~~~~~~~~~~

A: 运行 sphinx-build::

    cd docs
    make html

Q: CI 失败了怎么办?
~~~~~~~~~~~~~~~~~~

A: 

1. 检查 GitHub Actions 日志
2. 在本地运行相同的检查
3. 修复问题后重新推送

贡献指南
--------

1. Fork 项目
2. 创建功能分支
3. 提交代码 (遵循规范)
4. 推送到你的 fork
5. 创建 Pull Request

我们欢迎:

- Bug 修复
- 新功能
- 文档改进
- 性能优化
- 测试补充

资源链接
--------

- `GitHub 仓库 <https://github.com/Dictatora0/CampusFleet-AI>`_
- `问题跟踪 <https://github.com/Dictatora0/CampusFleet-AI/issues>`_
- `CI/CD 状态 <https://github.com/Dictatora0/CampusFleet-AI/actions>`_
