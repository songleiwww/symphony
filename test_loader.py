#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OpenClaw配置加载器
演示如何使用加载器让交响自动读取真实配置
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Symphony - OpenClaw Config Loader Test")
print("=" * 70)

try:
    from openclaw_config_loader import (
        OpenClawConfigLoader,
        load_symphony_models
    )
    
    print("\n[1/4] Creating config loader...")
    loader = OpenClawConfigLoader()
    print("OK: Config loader created")
    
    print("\n[2/4] Loading model config...")
    models = loader.get_models()
    print(f"OK: Loaded {len(models)} models")
    
    print("\n[3/4] Displaying config summary...")
    loader.print_summary()
    
    print("\n[4/4] Testing model access...")
    # Get priority 1 model
    model1 = loader.get_model_by_priority(1)
    if model1:
        print(f"OK: Priority 1 model: {model1['alias']}")
        print(f"  Provider: {model1['provider']}")
        print(f"  API Key: {model1['api_key'][:10]}...")  # Show only first 10 chars
    
    # Get first model
    if models:
        first_model = models[0]
        print(f"\nFirst model available to Symphony:")
        print(f"  Name: {first_model['name']}")
        print(f"  Alias: {first_model['alias']}")
        print(f"  Provider: {first_model['provider']}")
        print(f"  Priority: {first_model['priority']}")
        print(f"  API Key configured: {'YES' if first_model['api_key'] else 'NO'}")
    
    print("\n" + "=" * 70)
    print("SUCCESS: Loader test passed!")
    print("=" * 70)
    print("\nUsage:")
    print("  from openclaw_config_loader import load_symphony_models")
    print("  MODEL_CHAIN = load_symphony_models()")
    print("\n  Symphony will now use real OpenClaw config automatically!")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
