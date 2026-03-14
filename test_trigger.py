# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试触发系统
from trigger_system import analyze_intent, get_auto_help

test_messages = [
    '交响调度3个模型',
    '帮我开发一个功能', 
    '不知道选哪个好',
    '删除所有文件',
    '今天天气怎么样',
    '学习AI知识',
    '请问如何配置',
]

print('='*60)
print('Symphony Trigger System Test')
print('='*60)

for msg in test_messages:
    result = get_auto_help(msg)
    print(f'\nInput: {msg}')
    print(f'  Mode: {result["mode"]}')
    print(f'  Multi-Model: {result["multi_model"]}')
    print(f'  Reason: {result["reason"]}')
    print(f'  Priority: {result["priority"]}')
