#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境应急部门述职 - 顾清歌"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 顾清歌述职任务
task = {
    'name': '顾清歌',
    'model': 'THUDM/glm-4-9b-chat',
    'role': '翰林学士（应急部门主管）',
    'task': '''你是序境翰林学士顾清歌，担任应急管理部门主管。

请以古代官员述职的口吻，写一份述职报告，内容包括：
1. 应急部门的职责范围
2. 近期处理的事件
3. 应急响应能力
4. 存在的问题
5. 改进计划

用80字以内，以JSON格式输出。
'''
}

headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
data = {
    'model': task['model'],
    'messages': [{'role': 'user', 'content': task['task']}],
    'max_tokens': 300,
    'temperature': 0.7
}

print('=== 序境应急管理部门述职 ===\n')
print('述职官员：顾清歌（翰林学士）')
print('部门：应急管理司\n')

try:
    r = requests.post(API_URL, headers=headers, json=data, timeout=60)
    result = r.json()
    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0]['message'].get('content', '')
        tokens = result.get('usage', {}).get('total_tokens', 0)
        
        print('[述职报告]')
        print(content)
        print('\n消耗: %d tokens' % tokens)
    else:
        print('[FAIL]', str(result))
except Exception as e:
    print('[ERROR]', str(e))
