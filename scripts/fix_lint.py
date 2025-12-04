#!/usr/bin/env python3
"""
自动修复常见的 flake8 linting 问题
"""
from pathlib import Path


def remove_unused_imports(file_path: Path, unused_imports: list):
    """删除未使用的导入"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for line in lines:
        skip = False
        for unused in unused_imports:
            # 匹配整行导入
            if unused in line and ("import" in line or "from" in line):
                # 检查是否是单独一行的导入
                if line.strip().startswith("import") or line.strip().startswith("from"):
                    skip = True
                    modified = True
                    break

        if not skip:
            new_lines.append(line)

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✓ {file_path}: 删除未使用的导入")


def fix_fstring_placeholders(file_path: Path, line_numbers: list):
    """修复 f-string 缺少占位符"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    for line_num in line_numbers:
        idx = line_num - 1
        if idx < len(lines):
            line = lines[idx]
            # 将 f"..." 改为 "..."
            if line.count('f"') > 0 or line.count("f'") > 0:
                # 只在没有 {} 的情况下移除 f
                if "{" not in line:
                    lines[idx] = line.replace('f"', '"').replace("f'", "'")
                    modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✓ {file_path}: 修复 f-string")


def fix_bare_except(file_path: Path, line_numbers: list):
    """修复裸 except"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    for line_num in line_numbers:
        idx = line_num - 1
        if idx < len(lines):
            line = lines[idx]
            if "except:" in line:
                lines[idx] = line.replace("except:", "except Exception:")
                modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✓ {file_path}: 修复裸 except")


def remove_unused_variables(file_path: Path, variables: dict):
    """删除未使用的变量（用 _ 替换）"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    for var_name, line_num in variables.items():
        idx = line_num - 1
        if idx < len(lines):
            line = lines[idx]
            # 将 var = ... 改为 _ = ...
            if f"{var_name} =" in line:
                lines[idx] = line.replace(f"{var_name} =", "_ =")
                modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✓ {file_path}: 移除未使用的变量")


# 主要修复列表
fixes = {
    # 未使用的导入
    "agents/scheduler_agent.py": {
        "unused_imports": ["typing.Optional"],
        "fstring_lines": [563, 620],
    },
    "algorithms/mapf_planner.py": {
        "unused_imports": ["collections.defaultdict", "typing.NamedTuple"]
    },
    "algorithms/vrp_solver.py": {"unused_imports": ["random"]},
    "analytics/visualization.py": {"unused_imports": ["typing.List"]},
    "core/config.py": {"unused_imports": ["typing.Optional"]},
    "core/context.py": {"fstring_lines": [363]},
    "core/decorators.py": {"unused_imports": ["typing.Any"]},
    "core/logger.py": {"unused_imports": ["datetime.datetime"]},
    "core/simulation.py": {"unused_imports": ["typing.Optional"]},
    "demos/demo_gui.py": {"bare_except_lines": [116]},
    "visualization/pygame_viewer.py": {
        "unused_imports": ["typing.Dict", "typing.List"],
        "fstring_lines": [130],
        "unused_vars": {"bolt_points": 206, "alpha": 462},
    },
    "rl_agents/dqn_agent.py": {"unused_imports": ["typing.Tuple"], "unused_vars": {"loss": 449}},
    "rl_agents/ppo_agent.py": {
        "unused_imports": ["typing.Optional", "torch.distributions.MultivariateNormal"],
        "unused_vars": {"states": 362, "actions": 363, "old_log_probs": 364},
    },
}


def main():
    root = Path("/Users/lifulin/Desktop/CampusFleet AI")

    for file_rel, fix_data in fixes.items():
        file_path = root / file_rel
        if not file_path.exists():
            print(f"✗ {file_path}: 文件不存在")
            continue

        if "unused_imports" in fix_data:
            remove_unused_imports(file_path, fix_data["unused_imports"])

        if "fstring_lines" in fix_data:
            fix_fstring_placeholders(file_path, fix_data["fstring_lines"])

        if "bare_except_lines" in fix_data:
            fix_bare_except(file_path, fix_data["bare_except_lines"])

        if "unused_vars" in fix_data:
            remove_unused_variables(file_path, fix_data["unused_vars"])

    print("\n✅ 批量修复完成！")
    print("建议运行: flake8 . --max-line-length=100 来验证修复")


if __name__ == "__main__":
    main()
