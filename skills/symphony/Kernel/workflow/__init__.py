# -*- coding: utf-8 -*-
"""
FineGrainedWorkflow - 细粒度工作流引擎
========================================

核心概念：
- 每步可验证：思考/执行/验证 分离
- Token 预算控制：防止过量输出
- 结果归一化：多步 → 统一输出

使用示例：
    from Kernel.workflow import FineGrainedWorkflow, WorkflowBuilder
    
    # 创建代码生成工作流
    wf = WorkflowBuilder.code_generation_workflow("写一个快速排序")
    result = wf.execute()
"""

__all__ = [
    'FineGrainedWorkflow',
    'WorkflowBuilder',
    'WorkflowStep',
    'WorkflowResult',
    'StepStatus'
]

from .fine_grained_workflow import (
    FineGrainedWorkflow,
    WorkflowBuilder,
    WorkflowStep,
    WorkflowResult,
    StepStatus
)
