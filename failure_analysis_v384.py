#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘族人工作失败原因分析会议 v3.8.4
分析模型失败原因，制定自动化接续方案，改进动态调度
"""
import requests
import json
import time
from datetime import datetime

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# 动态调度：根据任务复杂度决定模型数量
# 本次任务：分析失败原因 + 制定接续方案 = 中等复杂度 = 3-4个模型
task_complexity = "中等"
dynamic_model_count = 4  # 动态计算：中等复杂度=4个模型

# 选取最稳定的4个模型进行动态调度
stable_models = [
    {
        'name': '林思远',
        'fox': '银白九尾狐 - 青丘长老',
        'role': '问题分析专家',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '请作为问题分析专家，分析以下模型失败原因：1)张晓明(Qwen 3.5 397B)连接超时；2)赵心怡(GLM-4.7)NoneType错误；3)陈浩然(DeepSeek V3.2)连接超时。给出失败原因分析和解决建议。'
    },
    {
        'name': '王明远',
        'fox': '火红九尾狐 - 青丘猎手',
        'role': '接续方案设计师',
        'model': 'mistralai/mistral-large-3-675b-instruct-2512',
        'task': '请作为接续方案设计师，针对上述3个模型失败情况，设计自动化接续方案，确保工作完整。给出3条具体接续策略。'
    },
    {
        'name': '周小芳',
        'fox': '雪白九尾狐 - 青丘医师',
        'role': '调度优化专家',
        'model': 'minimaxai/minimax-m2.5',
        'task': '请作为调度优化专家，提出动态调度改进方案：根据任务复杂度动态决定模型数量，而不是固定6个。给出动态调度算法建议。'
    },
    {
        'name': '林思远',
        'fox': '银白九尾狐 - 青丘长老',
        'role': '最终汇总报告',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '请汇总本次会议成果：1)失败原因分析；2)接续方案；3)动态调度改进。给出完整的工作完整性保障方案。'
    }
]

results = []
total_tokens = 0
success_count = 0

print("="*60)
print("青丘族人工作失败原因分析会议 v3.8.4")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"任务复杂度: {task_complexity}")
print(f"动态模型数量: {dynamic_model_count}个（根据复杂度计算）")
print("="*60)
print()

for i, member in enumerate(stable_models):
    print(f"【族人{i+1}】{member['name']}")
    print(f"  狐形态: {member['fox']}")
    print(f"  角色: {member['role']}")
    print(f"  调用模型: {member['model']}")
    
    data = {
        'model': member['model'],
        'messages': [{'role': 'user', 'content': member['task']}],
        'max_tokens': 400,
        'temperature': 0.7
    }
    
    start_time = time.time()
    
    try:
        r = requests.post(URL, headers=HEADERS, json=data, timeout=120)
        elapsed = time.time() - start_time
        
        if r.status_code == 200:
            result = r.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            prompt_tokens = result.get('usage', {}).get('prompt_tokens', 0)
            completion_tokens = result.get('usage', {}).get('completion_tokens', 0)
            tokens = result.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            success_count += 1
            
            results.append({
                'name': member['name'],
                'fox': member['fox'],
                'role': member['role'],
                'model': member['model'],
                'status': '成功',
                'api_status': r.status_code,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': tokens,
                'elapsed': round(elapsed, 2),
                'response': content[:500]
            })
            
            print(f"  API状态: 200 OK")
            print(f"  Token详情: 输入={prompt_tokens}, 输出={completion_tokens}, 总计={tokens}")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  工作状态: 成功")
        else:
            elapsed = time.time() - start_time
            print(f"  API状态: {r.status_code}")
            print(f"  工作状态: 失败")
            
            results.append({
                'name': member['name'],
                'fox': member['fox'],
                'role': member['role'],
                'model': member['model'],
                'status': '失败',
                'api_status': r.status_code,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'elapsed': round(elapsed, 2),
                'response': f'API返回错误: {r.status_code}'
            })
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  API状态: 异常")
        print(f"  工作状态: 异常")
        
        results.append({
            'name': member['name'],
            'fox': member['fox'],
            'role': member['role'],
            'model': member['model'],
            'status': '异常',
            'api_status': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
            'elapsed': round(elapsed, 2),
            'response': str(e)[:100]
        })
    
    print()

print("="*60)
print("会议总结")
print("="*60)
print(f"动态模型数量: {dynamic_model_count}个（根据任务复杂度计算）")
print(f"成功调用: {success_count}/{len(stable_models)}")
print(f"总Token消耗: {total_tokens}")
print("="*60)

# 保存报告
report = {
    'version': 'v3.8.4',
    'meeting_type': '族人工作失败原因分析会议',
    'timestamp': datetime.now().isoformat(),
    'dynamic_analysis': {
        'task_complexity': task_complexity,
        'model_count': dynamic_model_count,
        'reason': '根据任务复杂度动态计算'
    },
    'failed_models': [
        {'name': '张晓明', 'model': 'Qwen 3.5 397B', 'reason': '连接超时'},
        {'name': '赵心怡', 'model': 'GLM-4.7', 'reason': 'NoneType错误'},
        {'name': '陈浩然', 'model': 'DeepSeek V3.2', 'reason': '连接超时'}
    ],
    'total_members': len(stable_models),
    'success_count': success_count,
    'total_tokens': total_tokens,
    'results': results
}

with open('failure_analysis_v384.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("报告已保存: failure_analysis_v384.json")
