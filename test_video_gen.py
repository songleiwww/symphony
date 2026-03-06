#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()

print('=== 交响视频生成测试 ===')
print()

# 提交视频生成任务
prompt = '一只可爱的小猫在草地上奔跑，阳光明媚'
print(f'Prompt: {prompt}')
print()

result = panel.generate_video(prompt)

print(f'成功: {result.success}')
print(f'模型: {result.model_name}')
print(f'异步: {result.is_async}')
print(f'Task ID: {result.task_id}')
print(f'延迟: {result.latency:.1f}s')
print(f'错误: {result.error}')
print()

if result.task_id and not result.task_id.startswith('async_'):
    print('=== 查询任务状态 ===')
    status = panel.query_video_task(result.task_id)
    print(f'Task ID: {status.task_id}')
    print(f'状态: {status.status}')
    print(f'进度: {status.progress}%')
    print(f'URL: {status.url}')
    print(f'错误: {status.error}')
