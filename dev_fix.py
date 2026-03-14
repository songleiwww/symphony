#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境系统性Debug修复 - 8人并行"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 读取Debug结果
with open('debug_results.json', 'r', encoding='utf-8') as f:
    debug_results = json.load(f)

# 8人修复任务
fix_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦，负责修复架构问题。

Debug发现的问题：
%s

请给出架构修复方案JSON（60字以内）
''' % debug_results[0]['response'][:500]
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺，负责修复代码问题。

Debug发现的问题：
%s

请给出代码修复方案JSON（60字以内）
''' % debug_results[1]['response'][:500]
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌，负责修复规则问题。

Debug发现的问题：
%s

请给出规则修复方案JSON（60字以内）
''' % debug_results[2]['response'][:500]
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'task': '''你是序境智囊博士沈星衍，负责修复策略问题。

Debug发现的问题：
%s

请给出策略修复方案JSON（60字以内）
''' % debug_results[3]['response'][:500]
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘，负责修复性能问题。

Debug发现的问题：
%s

请给出性能修复方案JSON（60字以内）
''' % debug_results[4]['response'][:500]
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码，负责修复工程问题。

Debug发现的问题：
%s

请给出工程修复方案JSON（60字以内）
''' % debug_results[5]['response'][:500]
    },
    {
        'name': '顾至尊',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '首辅大学士',
        'task': '''你是序境首辅大学士顾至尊，负责修复整体问题。

Debug发现的问题：
%s

请给出整体修复方案JSON（60字以内）
''' % debug_results[6]['response'][:500]
    },
    {
        'name': '陆念昭',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '少府监',
        'task': '''你是序境少府监陆念昭，负责修复调度问题。

Debug发现的问题：
%s

请给出调度修复方案JSON（60字以内）
''' % debug_results[7]['response'][:500]
    },
]

results = []
total_tokens = 0

print('=== 序境系统性Debug修复 ===')
print('任务：根据Debug结果修复问题\n')

for m in fix_tasks:
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': m['model'],
        'messages': [{'role': 'user', 'content': m['task']}],
        'max_tokens': 200,
        'temperature': 0.7
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=60)
        result = r.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '无响应')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'].split('/')[-1], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['role'], tokens))
        else:
            results.append({'name': m['name'], 'role': m['role'], 'response': str(result), 'status': 'FAIL'})
            print('[FAIL] %s' % m['name'])
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'response': str(e), 'status': 'FAIL'})
        print('[ERROR] %s' % m['name'])
    time.sleep(0.5)

print('\n=== 修复方案汇总 ===')
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s:' % (r['name'], r['role']))
        print(r['response'][:150])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存修复结果
with open('fix_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n修复方案已保存: fix_results.json')
