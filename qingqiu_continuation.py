#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘族群会议 v3.8.2 - 工作接续问题专题
赵心怡API异常，其他专家接续工作
"""
import requests
import json
import time

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# 青丘族群成员继续完成任务
qingqiu_members = [
    {
        'name': '林思远',
        'fox': '银白九尾狐 - 青丘长老',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '请作为青丘长老林思远，接续赵心怡的任务分类工作。分析交响系统模型调度问题的任务分类，给出完整的分类方案。'
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐 - 青丘史官',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '请作为青丘史官张晓明，记录本次会议的工作接续过程，并分析任务分类的细节。'
    },
    {
        'name': '陈浩然',
        'fox': '青灰九尾狐 - 青丘守护',
        'model': 'deepseek-ai/deepseek-v3.2',
        'task': '请作为青丘守护陈浩然，分析模型调度中的问题，提供优化建议。'
    }
]

results = []
total_tokens = 1225

print("="*60)
print("青丘族群会议 - 工作接续专题")
print("="*60)
print()

for member in qingqiu_members:
    print(f"青丘族人: {member['name']}")
    print(f"  狐形态: {member['fox']}")
    
    data = {
        'model': member['model'],
        'messages': [{'role': 'user', 'content': member['task']}],
        'max_tokens': 300,
        'temperature': 0.7
    }
    
    try:
        r = requests.post(URL, headers=HEADERS, json=data, timeout=90)
        if r.status_code == 200:
            result = r.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            
            results.append({
                'name': member['name'],
                'fox_form': member['fox'],
                'model': member['model'],
                'status': '成功',
                'tokens': tokens,
                'response': content[:400]
            })
            print(f"  状态: 成功 - Token: {tokens}")
        else:
            print(f"  状态: 失败 - {r.status_code}")
            results.append({
                'name': member['name'],
                'fox_form': member['fox'],
                'model': member['model'],
                'status': '失败',
                'tokens': 0
            })
    except Exception as e:
        print(f"  状态: 异常 - {str(e)[:30]}")
        results.append({
            'name': member['name'],
            'fox_form': member['fox'],
            'model': member['model'],
            'status': '异常',
            'tokens': 0
        })
    print()

print("="*60)
print(f"接续工作Token消耗: {total_tokens}")
print("="*60)

with open('qingqiu_continuation.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
