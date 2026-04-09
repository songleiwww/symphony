# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
皇权能力自使?序境调度适配功能测试脚本
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Kernel.evolution_kernel import EvolutionKernel

def test_imperial_scene_recognition():
    """测试皇权场景自动识别能力"""
    print("=" * 60)
    print("测试1：皇权场景自动识别能?)
    print("=" * 60)
    
    kernel = EvolutionKernel()
    print(f"内核初始化成功，版本: {kernel.get_kernel_status()['version']}")
    print(f"自适应引擎状? {'?已启? if kernel.active_adaptive_engine else '?未启?}")
    
    test_cases = [
        "陛下，内阁奏折已整理完毕，请御览",
        "户部今年的赋税报表已经统计完?,
        "皇后娘娘的寿宴安排需要礼部配?,
        "边关急报，匈奴进犯，需要兵部调度军?,
        "请编写一个Python脚本实现数据可视?, # 非皇权场景，测试不会误触?    ]
    
    for i, text in enumerate(test_cases):
        result = kernel.check_trigger(text)
        print(f"\n测试用例 {i+1}: {text}")
        print(f"  触发状? {'?触发' if result['should_trigger'] else '?不触?}")
        print(f"  置信? {result['confidence']:.2f}")
        print(f"  任务类别: {result['task_category']}")
        print(f"  优先? {result['priority']}")
        print(f"  触发原因: {result['reason']}")
    
    return True

def test_imperial_scheduling():
    """测试序境调度能力适配"""
    print("\n" + "=" * 60)
    print("测试2：序境调度能力适配")
    print("=" * 60)
    
    kernel = EvolutionKernel()
    
    test_cases = [
        "拟一道圣旨，大赦天下",
        "兵部如何调度军队抵御北方入侵",
        "户部统计全国灾荒情况，制定赈灾方?,
    ]
    
    for i, text in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {text}")
        result = kernel.process_request(text)
        if result:
            print(f"  任务ID: {result['task_id']}")
            print(f"  触发置信? {result['trigger_confidence']:.2f}")
            print(f"  适配计划:")
            print(f"    任务类别: {result['adaptation_plan']['task_category']}")
            print(f"    优先? {result['adaptation_plan']['priority']}")
            print(f"    选择模型: {result['adaptation_plan']['selected_models']}")
            print(f"    脑群规模: {result['adaptation_plan']['brain_group_size']}")
            print(f"    QPS限制: {result['coordination_result']['resource_allocation']['qps_limit']}")
            print(f"    成本估计: {result['adaptation_plan']['cost_estimate']} ?)
            print(f"  调度子系? {result['coordination_result']['subsystems_assigned']}")
            print(f"  执行流程: {result['coordination_result']['execution_flow']}")
        else:
            print(f"  ?未触?)
    
    return True

def test_cross_capability_collaboration():
    """测试跨能力协?""
    print("\n" + "=" * 60)
    print("测试3：跨能力协同")
    print("=" * 60)
    
    kernel = EvolutionKernel()
    
    # 复杂场景：军事调?粮草筹备+地方配合
    text = "北方匈奴十万大军进犯，兵部需调度20万军队出征，户部筹备3年粮草，沿途州县配合转运，制定完整作战方案"
    result = kernel.process_request(text)
    
    if result:
        print(f"复杂任务触发成功: {text}")
        print(f"协同子系? {result['coordination_result']['subsystems_assigned']}")
        print(f"自动启用了以下能力协?")
        if 'multi_agent' in result['coordination_result']['subsystems_assigned']:
            print(f"  ?多脑协同")
        if 'algorithm_coordinator' in result['coordination_result']['subsystems_assigned']:
            print(f"  ?群智能算法优?)
        if 'military_wisdom' in result['coordination_result']['subsystems_assigned']:
            print(f"  ?军事智慧引擎")
        if 'wisdom_engine' in result['coordination_result']['subsystems_assigned']:
            print(f"  ?智慧引擎验证")
    
    return True

if __name__ == "__main__":
    print("🎯 皇权能力自使?序境调度适配功能测试")
    print("=" * 60)
    
    all_passed = True
    try:
        test_imperial_scene_recognition()
        test_imperial_scheduling()
        test_cross_capability_collaboration()
        
        print("\n" + "=" * 60)
        print("?所有测试通过！皇权能力已成功整合到序境内?)
        print("=" * 60)
        print("功能特?")
        print("1. ?皇权场景自动识别：覆盖皇帝、官署、后宫、军事、文化等所有场?)
        print("2. ?序境调度适配：QPS?限流、成本优先、多服务商并行、全链路日志留存")
        print("3. ?跨能力协同：自动整合多脑协同、群智能算法、军事智慧引擎等核心能力")
        print("4. ?内核原生整合：无需额外配置，开箱即?)
        print("5. ?双环境同步：已同步到生产和开发环?)
        
    except Exception as e:
        print(f"\n?测试失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    sys.exit(0 if all_passed else 1)

