#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v4.0开发测试 - 使用交响调度器 (Smart Orchestrator)
验证交响能否真正并行调用多个模型
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from smart_orchestrator import SmartOrchestrator, OrchestrationStrategy

# 测试任务
TEST_PROMPTS = [
    "你好，请用一句话介绍你自己",
    "请告诉我你最擅长什么领域",
    "请用一句话评价Python编程语言"
]

def main():
    print("=" * 60)
    print("🎼 交响调度器测试 - 真实API调用")
    print("=" * 60)
    
    # 初始化调度器
    orchestrator = SmartOrchestrator()
    print(f"\n📋 已加载 {len(orchestrator.models)} 个模型")
    
    # 选择3个不同提供商的模型进行测试
    test_models = []
    providers_seen = set()
    
    for model in orchestrator.models:
        if model["provider"] not in providers_seen:
            test_models.append(model)
            providers_seen.add(model["provider"])
            if len(test_models) >= 3:
                break
    
    print(f"\n📦 选择测试模型:")
    for m in test_models:
        print(f"  - {m['provider']}/{m['model_id']}")
    
    # 并行调用测试
    print("\n" + "=" * 60)
    print("🚀 开始并行调用测试...")
    print("=" * 60)
    
    from smart_orchestrator import call_model
    
    import concurrent.futures
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_model = {
            executor.submit(call_model, m, p): (m, p)
            for m, p in zip(test_models, TEST_PROMPTS)
        }
        
        for future in concurrent.futures.as_completed(future_to_model):
            m, p = future_to_model[future]
            try:
                result = future.result()
                results.append(result)
                
                status = "✅" if result["success"] else "❌"
                print(f"\n{status} {m['provider']}/{m['model_id']}")
                print(f"   耗时: {result.get('elapsed', 0):.2f}s")
                
                if result["success"]:
                    print(f"   响应: {result['response'][:100]}...")
                    print(f"   Token: {result.get('total_tokens', 0)}")
                else:
                    print(f"   错误: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                print(f"\n❌ {m['provider']}/{m['model_id']} - Exception: {e}")
    
    # 统计
    success = sum(1 for r in results if r.get("success"))
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {success}/{len(results)} 成功")
    print("=" * 60)
    
    return success > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
