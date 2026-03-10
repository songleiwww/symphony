#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境全员述职脚本 - 补全2人(最终版)"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 补全2人 - 使用确认可用的模型
members = [
    {'name': '沈星衍', 'model': 'THUDM/glm-4-32k', 'role': '智囊博士 - 智慧谋士', 'task': '你是序境智囊博士沈星衍，请用30字简述当前工作进度'},
    {'name': '叶轻尘', 'model': 'Qwen/Qwen2.5-7B-Instruct', 'role': '行走使 - 轻量高效', 'task': '你是序境行走使叶轻尘，请用30字简述当前工作进度'},
]

results = []
total_tokens = 258

print('=== 补全述职(最终版) ===\n')

for m in members:
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': m['model'],
        'messages': [{'role': 'user', 'content': m['task']}],
        'max_tokens': 100,
        'temperature': 0.7
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=30)
        result = r.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '无响应')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['model'].split('/')[-1], tokens))
            print('    回复: %s' % content[:50])
        else:
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'], 'response': str(result), 'tokens': 0, 'status': 'FAIL'})
            print('[FAIL] %s | %s' % (m['name'], str(result)[:50]))
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'model': m['model'], 'response': str(e), 'tokens': 0, 'status': 'FAIL'})
        print('[ERROR] %s | %s' % (m['name'], str(e)[:50]))

print('\n总消耗: %d tokens' % total_tokens)
