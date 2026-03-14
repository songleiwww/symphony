#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响系统真实API调用验证
每位专家进行实际API调用，验证真实性
"""
import requests
import json
import time

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

experts = [
    {'name': '林思远', 'model': 'meta/llama-3.1-405b-instruct', 
     'task': '请作为调度架构师，分析交响系统的模型调度问题，给出简洁的技术建议。'},
    {'name': '张晓明', 'model': 'qwen/qwen3.5-397b-a17b', 
     'task': '请作为负载均衡专家，分析模型并发的负载问题，给出简洁的技术建议。'},
    {'name': '赵心怡', 'model': 'z-ai/glm4.7', 
     'task': '请作为任务分类专家，分析用户输入的任务类型，给出简洁的分类结果。'},
    {'name': '陈浩然', 'model': 'deepseek-ai/deepseek-v3.2', 
     'task': '请作为推理优化专家，分析模型推理优化方案，给出简洁的技术建议。'},
    {'name': '王明远', 'model': 'mistralai/mistral-large-3-675b-instruct-2512', 
     'task': '请作为成本优化专家，分析模型调度的成本问题，注意我们没有购买流量，请基于实际情况分析。'},
    {'name': '周小芳', 'model': 'minimaxai/minimax-m2.5', 
     'task': '请作为智能路由专家，分析模型路由策略，给出简洁的技术建议。'}
]

results = []
total_tokens = 0

print('='*60)
print('Symphony v3.8.1 真实API调用验证')
print('='*60)
print()

for i, exp in enumerate(experts):
    print(f'专家{i+1}: {exp["name"]}')
    print(f'  模型: {exp["model"]}')
    
    data = {
        'model': exp['model'],
        'messages': [{'role': 'user', 'content': exp['task']}],
        'max_tokens': 200,
        'temperature': 0.7
    }
    
    try:
        start = time.time()
        r = requests.post(URL, headers=HEADERS, json=data, timeout=60)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            
            results.append({
                'name': exp['name'],
                'model': exp['model'],
                'status': '成功',
                'response': content[:500],
                'tokens': tokens,
                'time': round(elapsed, 1),
                'api_status': r.status_code
            })
            print(f'  状态: 成功')
            print(f'  Token: {tokens}')
            print(f'  时间: {elapsed:.1f}秒')
        else:
            print(f'  状态: 失败 - {r.status_code}')
            results.append({
                'name': exp['name'],
                'model': exp['model'],
                'status': '失败',
                'response': f'API错误: {r.status_code}',
                'tokens': 0,
                'time': round(elapsed, 1),
                'api_status': r.status_code
            })
    except Exception as e:
        print(f'  状态: 异常')
        results.append({
            'name': exp['name'],
            'model': exp['model'],
            'status': '异常',
            'response': str(e)[:100],
            'tokens': 0,
            'time': 0,
            'api_status': 0
        })
    
    print()

print('='*60)
print(f'总Token消耗: {total_tokens}')
print('='*60)

# 保存结果
with open('real_api_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('结果已保存')
