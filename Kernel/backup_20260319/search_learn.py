#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dispatcher import Dispatcher

d = Dispatcher()

# 调度官员进行搜索学习
tasks = [
    '搜索学习 AI Agent自动进化 最新进展 2026',
    '搜索学习 MCP协议 中文 2026 发展',
    '搜索学习 大模型自进化 技术 论文 2026'
]

print('=== 调度少府监官员进行预学习 ===')
for i, task in enumerate(tasks, 1):
    print('任务', i, ':', task)
    result = d.dispatch(task)
    if result.get('assigned_roles'):
        role = result.get('assigned_roles')[0]
        print('  分配:', role.get('姓名'), '-', role.get('model'))
    print()
