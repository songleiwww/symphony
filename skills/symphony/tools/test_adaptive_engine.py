# -*- coding: utf-8 -*-
"""测试序境系统自适应引擎新能?""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Kernel.evolution_kernel import EvolutionKernel

print("=" * 60)
print("序境系统 v4.4.0 自适应引擎测试")
print("=" * 60)

# 初始化内?kernel = EvolutionKernel()
print(f"内核初始化状? {kernel is not None}")
print(f"自适应引擎可用: {kernel.active_adaptive_engine is not None}")

if kernel.active_adaptive_engine:
    print("\n引擎状?")
    status = kernel.get_adaptive_status()
    for k, v in status.items():
        if k != "config":
            print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("泛处理触发测?")
    
    test_cases = [
        "用序境帮我写一个Python冒泡排序函数",
        "我需要研究唐朝的科举制度",
        "明天要开产品评审会，帮我准备材料",
        "今天天气怎么样啊?,
        "我家猫跑丢了怎么?
    ]
    
    for test in test_cases:
        result = kernel.check_trigger(test)
        print(f"\n测试文本: {test}")
        print(f"  是否触发: {'?? if result['should_trigger'] else '??}")
        print(f"  置信? {result['confidence']:.2f}")
        print(f"  原因: {result['reason']}")
        if result['should_trigger']:
            print(f"  任务类别: {result['task_category']}")
            print(f"  优先? {result['priority']}")
    
    print("\n" + "=" * 60)
    print("?自适应引擎测试完成")

print("\n所有核心能力开发完成！")

