#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证真实模型调用
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*60)
print("验证真实模型调用")
print("="*60)

# 导入真实调用器
from real_model_caller import RealModelCaller

caller = RealModelCaller()

print(f"\n已加载模型数: {len(caller.models)}")

print("\n模型列表:")
for i, m in enumerate(caller.models[:5], 1):
    print(f"  {i}. {m['alias']} ({m['provider']})")
    print(f"     ID: {m['model_id']}")
    print(f"     API: {m['base_url']}")

print("\n" + "="*60)
print("测试真实API调用...")
print("="*60)

# 测试调用
result = caller.call(prompt="你好，请回复'测试成功'", priority=1)

print(f"\n调用结果:")
print(f"  成功: {result.success}")
print(f"  模型: {result.model_alias}")
print(f"  提供商: {result.provider}")
print(f"  响应: {result.response[:200] if result.response else '无'}")
print(f"  错误: {result.error if result.error else '无'}")
print(f"  耗时: {result.latency:.2f}s")
print(f"  Tokens: {result.total_tokens}")

if result.success:
    print("\n✅ 真实模型调用成功！")
else:
    print("\n❌ 调用失败")
