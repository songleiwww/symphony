#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重试失败的专家
"""
import requests
import json
import time

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

failed_experts = [
    {'name': '赵心怡', 'model': 'z-ai/glm4.7', 'task': '请作为任务分类专家，分析交响系统模型调度问题，给出简洁的分类建议。'},
    {'name': '陈浩然', 'model': 'deepseek-ai/deepseek-v3.2', 'task': '请作为推理优化专家，分析交响系统模型调度优化方案，给出简洁建议。'},
    {'name': '王明远', 'model': 'mistralai/mistral-large-3-675b-instruct-2512', 'task': '请作为成本优化专家，分析交响系统模型调度优化方案。'}
]

results = []
total_tokens = 743

print('重试失败的专家...')

for exp in failed_experts:
    print(f'{exp["name"]} - {exp["model"]}')
    data = {
        'model': exp['model'],
        'messages': [{'role': 'user', 'content': exp['task']}],
        'max_tokens': 200,
        'temperature': 0.7
    }
    try:
        r = requests.post(URL, headers=HEADERS, json=data, timeout=90)
        if r.status_code == 200:
            result = r.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            results.append({'name': exp['name'], 'model': exp['model'], 'status': '成功', 'tokens': tokens, 'response': content[:300]})
            print(f'  成功! Token: {tokens}')
        else:
            print(f'  失败: {r.status_code}')
            results.append({'name': exp['name'], 'model': exp['model'], 'status': '失败', 'tokens': 0})
    except Exception as e:
        print(f'  异常: {str(e)[:50]}')
        results.append({'name': exp['name'], 'model': exp['model'], 'status': '异常', 'tokens': 0})

print(f'总Token: {total_tokens}')

with open('retry_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
