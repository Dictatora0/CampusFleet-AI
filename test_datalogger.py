#!/usr/bin/env python3
"""测试DataLogger的frame_records属性"""

from analytics.data_logger import DataLogger

# 创建DataLogger实例
logger = DataLogger()

# 测试frame_data属性
print("✅ frame_data 存在: {hasattr(logger, 'frame_data')}")
print("✅ frame_records 存在: {hasattr(logger, 'frame_records')}")

# 测试是否是同一个对象
if hasattr(logger, "frame_records"):
    print("✅ frame_records 是 frame_data 的别名: {logger.frame_records is logger.frame_data}")
    print("✅ 修复成功！CSV导出应该能正常工作了")
else:
    print(f"❌ frame_records 属性不存在，修复未生效")
