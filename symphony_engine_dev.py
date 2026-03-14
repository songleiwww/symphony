#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响调度引擎 - 连续流程开发
1. 分析用户工作难度
2. 确定需要调度的模型数量
3. 调度交响引擎工作
"""
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print("=" * 70)
print("交响调度引擎 - 连续流程开发")
print("=" * 70)

# Task 1: 分析工作流程设计
print("\n[模型1] 工作流程架构师 - 设计连续流程...")
r1 = panel.call_model(
    prompt="""设计一个交响调度引擎的连续流程系统。

需求：
1. 分析用户工作难度 - 评估任务复杂度(简单/中等/复杂)
2. 确定模型数量 - 根据难度分配(1-6个模型)
3. 调度引擎工作 - 自动选择合适的模型进行协作

设计要点：
- 难度评估维度：任务类型、上下文长度、所需专业知识、时效性
- 模型分配策略：简单1个、中等2-3个、复杂4-6个
- 调度逻辑：主模型 + 辅助模型 + 备用模型

用Python设计这个系统的核心类和方法。""",
    model_id="deepseek-ai/DeepSeek-R1-0528",
    max_tokens=2000
)
print(f"  状态: {'成功' if r1.success else '失败'}, Tokens: {r1.tokens}")

# Task 2: 实现难度评估器
print("\n[模型2] 难度评估专家 - 实现评估器...")
r2 = panel.call_model(
    prompt="""设计任务难度评估器和模型调度器。

1. TaskDifficultyAnalyzer 类：
- analyze(task_description, context_length, domain) -> difficulty_level
- 评估维度：复杂度、专业性、时间敏感性
- 返回：简单/中等/复杂/紧急

2. ModelDispatcher 类：
- dispatch(difficulty_level, available_models) -> model_list
- 根据难度选择模型数量和类型
- 支持优先级排序和备用模型

3. SymphonyCoordinator 类：
- coordinate(task) -> 调用流程
- 分析 -> 调度 -> 执行 -> 汇总

用Python实现完整的代码。""",
    model_id="deepseek-ai/deepseek-v3.2",
    max_tokens=2000
)
print(f"  状态: {'成功' if r2.success else '失败'}, Tokens: {r2.tokens}")

# Task 3: 集成与测试
print("\n[模型3] 集成测试专家 - 集成方案...")
r3 = panel.call_model(
    prompt="""设计交响调度引擎的集成方案。

现有：
- BrainstormPanel (多模型调度)
- 限流追踪器
- 错误处理器
- 配置管理器

需求：
1. 将难度评估器集成到调度流程
2. 实现自动模型数量决策
3. 支持工作流程状态追踪
4. 提供完整的API接口

设计SymphonyEngine类，包含：
- analyze_task(task) -> analysis_result
- dispatch_models(analysis) -> model_list
- execute_workflow(models, task) -> result
- get_workflow_status() -> status

写出完整的Python代码实现。""",
    model_id="deepseek-ai/DeepSeek-R1-0528",
    max_tokens=2000
)
print(f"  状态: {'成功' if r3.success else '失败'}, Tokens: {r3.tokens}")

# Summary
print("\n" + "=" * 70)
print("开发完成总结")
print("=" * 70)

total_tokens = sum(r.tokens for r in [r1, r2, r3] if r.success)
print(f"\n总Tokens: {total_tokens}")

for i, (name, r) in enumerate([("流程设计", r1), ("评估器", r2), ("集成方案", r3)], 1):
    print(f"\n[{i}] {name}")
    print("-" * 50)
    if r.success:
        print(r.response[:1500])
        if len(r.response) > 1500:
            print("... [truncated]")
    else:
        print(f"Failed: {r.error}")