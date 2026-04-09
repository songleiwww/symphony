# -*- coding: utf-8 -*-
"""序境调度能力评估脚本"""

import sys
import time
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

from Kernel.evolution_kernel import EvolutionKernel
from Kernel.intelligent_strategy_scheduler import (
    IntelligentStrategyScheduler, 
    TaskInfo, 
    TaskComplexity,
    StrategyType
)

def evaluate_scheduler():
    print("=" * 60)
    print("序境系统调度能力评估报告")
    print("=" * 60)
    
    # 初始化内?    k = EvolutionKernel()
    
    print("\n?. 基础设施?)
    print(f"  调度器类? {type(k.scheduler).__name__}")
    print(f"  Federation模型总数: {len(k.federation.models)}")
    active = len([m for m in k.federation.models.values() if m.status == 'online'])
    print(f"  活跃模型? {active}")
    
    print("\n?. 模型分布?)
    providers = {}
    for m in k.federation.models.values():
        p = m.provider
        providers[p] = providers.get(p, 0) + 1
    for p, c in sorted(providers.items(), key=lambda x: -x[1]):
        print(f"  {p}: {c}")
    
    print("\n?. 调度策略?)
    scheduler = k.scheduler
    print(f"  支持的策?")
    for st in StrategyType:
        print(f"    - {st.name}: {st.value}")
    
    # 测试不同复杂度任?    test_cases = [
        ("简单任?, "你好", TaskComplexity.SIMPLE),
        ("中等任务", "请写一段Python代码实现快速排序算法，包含详细的注?, TaskComplexity.MEDIUM),
        ("复杂任务", "请分析以下代码的性能瓶颈，并提出优化方案：首先读取一个大文件，然后进行数据清洗，接着进行统计分析，最后生成报?, TaskComplexity.COMPLEX),
    ]
    
    print("\n?. 调度测试?)
    results = []
    for name, prompt, complexity in test_cases:
        task = TaskInfo.create(
            id=f"eval_{name}",
            prompt=prompt,
            task_type="general",
            complexity=complexity
        )
        
        start = time.time()
        result = scheduler.schedule(task, None)
        elapsed = time.time() - start
        
        models_selected = len(result.selected_models)
        strategy = result.metrics.get('strategy', 'N/A') if result.success else 'ERROR'
        
        print(f"\n  [{name}]")
        print(f"    复杂? {complexity.name}")
        print(f"    策略: {strategy}")
        print(f"    选中模型: {models_selected}")
        print(f"    执行时间: {elapsed*1000:.1f}ms")
        print(f"    状? {'?成功' if result.success else '?失败'}")
        
        if result.selected_models:
            print(f"    模型列表:")
            for m in result.selected_models[:3]:
                print(f"      - {m.provider}/{m.name}")
            if len(result.selected_models) > 3:
                print(f"      ... 等{models_selected}?)
        
        results.append({
            'name': name,
            'complexity': complexity,
            'success': result.success,
            'models': models_selected,
            'time': elapsed * 1000,
            'strategy': strategy
        })
    
    print("\n?. 并发调度测试?)
    tasks = [
        TaskInfo.create(id=f"batch_{i}", prompt=f"测试任务{i}", task_type="general", 
                       complexity=TaskComplexity.SIMPLE)
        for i in range(10)
    ]
    
    start = time.time()
    batch_results = scheduler.batch_schedule(tasks)
    elapsed = time.time() - start
    
    success_count = sum(1 for r in batch_results if r.success)
    print(f"  批量任务: 10?)
    print(f"  成功: {success_count}")
    print(f"  总耗时: {elapsed*1000:.1f}ms")
    print(f"  平均: {elapsed*100:.1f}ms/任务")
    
    print("\n?. 调度统计?)
    stats = scheduler.get_stats()
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  成功任务: {stats['successful_tasks']}")
    print(f"  成功? {stats['success_rate']*100:.1f}%")
    print(f"  缓存命中: {stats['cache']['overall']['hits']}")
    print(f"  缓存未命? {stats['cache']['overall']['misses']}")
    print(f"  L1命中: {stats['cache']['l1']['hits']}")
    print(f"  L2命中: {stats['cache']['l2']['hits']}")
    print(f"  L3命中: {stats['cache']['l3']['hits']}")
    
    print("\n?. 评估结论?)
    
    # 评分维度
    score_model_count = min(active / 50, 1.0) * 25  # 50+模型满分
    score_provider = min(len(providers) / 5, 1.0) * 15  # 5+provider满分
    score_success = results[0]['success'] and results[1]['success'] and results[2]['success'] if results else False
    score_success = 30 if score_success else 0
    score_perf = max(0, 30 - (elapsed * 100))  # 性能扣分
    
    total_score = score_model_count + score_provider + score_success + score_perf
    
    print(f"  模型丰富? {score_model_count:.1f}/25")
    print(f"  服务商多样? {score_provider:.1f}/15")
    print(f"  调度成功? {score_success:.1f}/30")
    print(f"  调度性能: {score_perf:.1f}/30")
    print(f"  ──────────────────")
    print(f"  总分: {total_score:.1f}/100")
    
    if total_score >= 80:
        print(f"  评级: 优秀 - 调度能力强大")
    elif total_score >= 60:
        print(f"  评级: 良好 - 调度能力正常")
    else:
        print(f"  评级: 需改进 - 调度能力有提升空?)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    evaluate_scheduler()

