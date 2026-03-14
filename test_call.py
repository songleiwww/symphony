#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统测试 - 实际模型调用
"""
import sys
import os
import importlib.util

project_dir = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
os.chdir(project_dir)
sys.path.insert(0, project_dir)

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Symphony Model Call Test")
print("=" * 60)

# Load modules
spec = importlib.util.spec_from_file_location("model_call_manager", "core/model_call_manager.py")
model_call_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model_call_manager)
mm = model_call_manager.get_model_manager()

# Test model call
print("\n[Test] Calling GLM-4.7 via 火山引擎...")

success, content, meta = mm.call_model(
    "glm-4.7",
    "你好，请用一句话介绍你自己"
)

if success:
    print(f"  Success!")
    print(f"  Response: {content[:200]}...")
    print(f"  Duration: {meta.get('duration', 0):.2f}s")
    print(f"  Tokens: {meta.get('token_usage', 0)}")
else:
    print(f"  Failed: {content}")

print("\n" + "=" * 60)
