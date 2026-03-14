#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 添加项目根目录
PROJECT_DIR = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
sys.path.insert(0, PROJECT_DIR)

# 测试内核加载
print("=" * 60)
print("测试序境系统内核...")
print("=" * 60)

try:
    # 导入内核
    from kernel.kernel_loader import get_kernel
    kernel = get_kernel()
    print(f"✅ 内核加载成功")
    print(f"   官属数量: {len(kernel.roles)}")
    print(f"   模型数量: {len(kernel.models)}")
except Exception as e:
    print(f"❌ 内核加载失败: {e}")
    import traceback
    traceback.print_exc()
