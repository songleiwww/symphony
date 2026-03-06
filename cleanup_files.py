#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony 清理脚本 - 删除测试和调试文件
"""

import os
from pathlib import Path

# Symphony目录
SYM_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")

# 需要删除的文件模式
DELETE_PATTERNS = [
    # 测试文件
    "test_*.py",
    "*_test.py",
    "debug_*.py",
    "*_debug.py",
    
    # 开发/改进文件
    "development.py",
    "improvement*.py",
    "workshop.py",
    "*_workshop.py",
    "*_improvement*.py",
    
    # 示例文件
    "example*.py",
    "demo_*.py",
    "weather_*.py",
    
    # 调试版本文件
    "*_v0*.py",
    "*_phase*.py",
    "*_team.py",
    
    # 临时测试
    "basic_test.py",
    "full_test.py",
    "simple_test.py",
    "quick_test.py",
    "deep_test*.py",
    "async_test*.py",
    
    # 清理脚本
    "cleanup*.py",
    "release*.py",
    "prepare_*.py",
    
    # 旧版本
    "v0*.py",
    "*_final.py",
    "*_real.py",  # 可能需要保留
]

# 明确要保留的核心文件
KEEP_FILES = {
    "brainstorm_panel_v2.py",
    "real_model_caller.py",
    "openclaw_config_loader.py",
    "symphony_core.py",
    "symphony_skill_wrapper.py",
    "model_manager.py",
    "skill_manager.py",
    "config.py",
    "main.py",
    "adapter_fix.py",
    "optimize_symphony.py",
    "symphony_debug.py",
    "adapter_development.py",
    "symphony_optimize_meeting.py",
}

def should_delete(filename):
    """判断文件是否应该删除"""
    name = filename.name
    
    # 保留核心文件
    if name in KEEP_FILES:
        return False
    
    # 检查删除模式
    for pattern in DELETE_PATTERNS:
        import fnmatch
        if fnmatch.fnmatch(name, pattern):
            return True
    
    return False

def main():
    print("=" * 60)
    print("Symphony 清理工具")
    print("=" * 60)
    print(f"目录: {SYM_PATH}")
    print()
    
    # 列出所有.py文件
    py_files = list(SYM_PATH.glob("*.py"))
    print(f"总Python文件数: {len(py_files)}")
    print()
    
    # 分类
    to_delete = []
    to_keep = []
    
    for f in py_files:
        if should_delete(f):
            to_delete.append(f)
        else:
            to_keep.append(f)
    
    print(f"将删除: {len(to_delete)} 个文件")
    print(f"将保留: {len(to_keep)} 个文件")
    print()
    
    # 显示删除列表
    print("=" * 60)
    print("将删除的文件:")
    print("=" * 60)
    for f in sorted(to_delete):
        print(f"  - {f.name}")
    
    print()
    
    # 显示保留列表
    print("=" * 60)
    print("将保留的文件:")
    print("=" * 60)
    for f in sorted(to_keep):
        print(f"  - {f.name}")
    
    print()
    
    # 执行删除（仅输出，不实际删除）
    print("=" * 60)
    print("提示: 此脚本仅列出文件，不执行删除")
    print("如需删除，请手动执行或修改代码")
    print("=" * 60)


if __name__ == "__main__":
    main()
