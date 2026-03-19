#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""优化序境系统调度脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dispatcher import Dispatcher

# 初始化调度器
dispatcher = Dispatcher()

print('=== 调度多人使用矩阵优化序境系统 ===')
print()

# 4个优化方向
tasks = [
    "SKILL.md格式规范化 - 分析skills目录下的SKILL.md格式问题",
    "安全机制加固 - 分析调度器安全机制现状",
    "缓存机制优化 - 分析内存和磁盘缓存优化方案",
    "部署流程简化 - 分析部署脚本简化方案"
]

results = []
for i, task in enumerate(tasks, 1):
    print(f'执行优化任务 {i}/4: {task[:30]}...')
    result = dispatcher.dispatch(task)
    results.append({
        'id': i,
        'task': task,
        'result': result
    })
    print(f'  -> 完成')

print()
print('=== 优化结果汇总 ===')
for r in results:
    print(f'{r["id"]}. {r["task"][:40]}')
    if r['result']:
        print(f'   {str(r["result"])[:100]}')

print()
print('=== 调度完成 ===')
