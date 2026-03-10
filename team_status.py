#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境全员述职脚本 - 硅基流动API版"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 使用硅基流动API
API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 6位核心成员，使用不同模型
members = [
    {'name': '沈清弦', 'model': 'Qwen/Qwen2.5-7B-Instruct', 'role': '枢密使 - 架构设计', 'task': '你是序境枢密使沈清弦，请用30字简述当前工作进度'},
    {'name': '苏云渺', 'model': 'Qwen/Qwen2.5-14B-Instruct', 'role': '工部尚书 - 代码开发', 'task': '你是序境工部尚书苏云渺，请用30字简述当前工作进度'},
    {'name': '顾清歌', 'model': 'THUDM/glm-4-9b-chat', 'role': '翰林学士 - 知识博学', 'task': '你是序境翰林学士顾清歌，请用30字简述当前工作进度'},
    {'name': '沈星衍', 'model': 'deepseek-ai/DeepSeek-V2-Chat', 'role': '智囊博士 - 智慧谋士', 'task': '你是序境智囊博士沈星衍，请用30字简述当前工作进度'},
    {'name': '叶轻尘', 'model': '01ai/Yi-1.5-9B-Chat', 'role': '行走使 - 轻量高效', 'task': '你是序境行走使叶轻尘，请用30字简述当前工作进度'},
    {'name': '林码', 'model': 'Qwen/Qwen2.5-72B-Instruct', 'role': '营造司正 - 代码实现', 'task': '你是序境营造司正林码，请用30字简述当前工作进度'},
]

results = []
total_tokens = 0

print('=== 序境全员述职开始 ===\n')

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
        else:
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'], 'response': str(result), 'tokens': 0, 'status': 'FAIL'})
            print('[FAIL] %s | %s' % (m['name'], str(result)[:50]))
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'model': m['model'], 'response': str(e), 'tokens': 0, 'status': 'FAIL'})
        print('[ERROR] %s | %s' % (m['name'], str(e)[:50]))

print('\n=== 述职汇总 ===')
for r in results:
    status_icon = '[OK]' if r['status'] == 'OK' else '[FAIL]'
    print('%s %s | %s' % (status_icon, r['name'], r['response'][:60]))

print('\n总消耗: %d tokens' % total_tokens)

# 保存结果
with open('team_status_report.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n报告已保存: team_status_report.json')
