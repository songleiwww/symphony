#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度优化序境系统 - 使用6矩阵"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from adaptive_matrix import AdaptiveMatrixSystem
from dispatcher import Dispatcher

# 初始化
matrix = AdaptiveMatrixSystem()
dispatcher = Dispatcher()

# 深度优化任务
task = """
基于今日预学习成果，优化序境系统：

【预学习数据】
- 6矩阵: 2759 tokens, 100%成功率
- 7-10矩阵: 70-80%成功率
- 11-17矩阵: 企业级++++

【优化方向】
1. SKILL.md格式规范
2. 安全机制加固
3. 缓存机制优化
4. 部署流程简化

请给出系统优化方案。
"""

print('=== 6矩阵深度优化序境系统 ===')
print('执行深度分析...')

# 获取6级矩阵任务
tasks = matrix.get_tasks_for_level(6)
print(f'获取到 {len(tasks)} 个任务')

# 执行优化
for t in tasks[:3]:
    print(f'执行: {str(t)[:50]}...')

result = dispatcher.dispatch(task)

print('\n=== 深度优化结果 ===')
print(result)
print('\n=== 完成 ===')
