#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单真实模型调用测试
"""

import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pathlib import Path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from real_model_caller import RealModelCaller

print("=" * 80)
print("🎯 简单真实模型调用测试")
print("=" * 80)

# 初始化
caller = RealModelCaller()

# 测试1: ark-code-latest
print("\n[1] 调用 ark-code-latest (优先级1)...")
result1 = caller.call_model("你好，请介绍一下你自己。", priority=1)
print(f"   成功: {result1.success}")
if result1.success:
    print(f"   响应: {result1.response}")
    print(f"   Token: {result1.total_tokens}")
    print(f"   延迟: {result1.latency:.2f}秒")

# 测试2: deepseek-v3.2
print("\n[2] 调用 deepseek-v3.2 (优先级2)...")
result2 = caller.call_model("你好，请用一句话介绍Symphony项目。", priority=2)
print(f"   成功: {result2.success}")
if result2.success:
    print(f"   响应: {result2.response}")
    print(f"   Token: {result2.total_tokens}")
    print(f"   延迟: {result2.latency:.2f}秒")

print("\n" + "=" * 80)
print("✅ 测试完成！")
print("=" * 80)
