#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘防幻觉验证会议 v3.8.3
每位族人真实调用NVIDIA模型，杜绝模拟
"""
import requests
import json
import time
from datetime import datetime

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# 青丘6位族人，每人对应一个真实模型
qingqiu_members = [
    {
        'name': '林思远',
        'fox': '银白九尾狐 - 青丘长老',
        'role': '调度架构师',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '请作为防幻觉验证专家，分析如何确保AI系统调用真实模型而非模拟。给出3条具体的技术建议。'
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐 - 青丘史官',
        'role': '记录分析师',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '请作为记录分析专家，分析如何验证API调用的真实性。给出3条验证方法。'
    },
    {
        'name': '赵心怡',
        'fox': '金黄九尾狐 - 青丘舞姬',
        'role': '交互设计师',
        'model': 'z-ai/glm4.7',
        'task': '请作为交互设计专家，分析如何在工具使用说明中明确要求使用真实模型。给出3条设计建议。'
    },
    {
        'name': '陈浩然',
        'fox': '青灰九尾狐 - 青丘守护',
        'role': '安全工程师',
        'model': 'deepseek-ai/deepseek-v3.2',
        'task': '请作为安全工程专家，分析如何防止系统产生幻觉和模拟行为。给出3条安全建议。'
    },
    {
        'name': '王明远',
        'fox': '火红九尾狐 - 青丘猎手',
        'role': '质量检测员',
        'model': 'mistralai/mistral-large-3-675b-instruct-2512',
        'task': '请作为质量检测专家，分析如何验证Token统计的真实性。给出3条检测方法。'
    },
    {
        'name': '周小芳',
        'fox': '雪白九尾狐 - 青丘医师',
        'role': '协调专家',
        'model': 'minimaxai/minimax-m2.5',
        'task': '请作为协调专家，总结本次防幻觉验证会议，提出3条综合建议。'
    }
]

results = []
total_tokens = 0
success_count = 0

print("="*60)
print("青丘防幻觉验证会议 v3.8.3")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("要求: 每位族人真实调用模型，不可模拟")
print("="*60)
print()

for i, member in enumerate(qingqiu_members):
    print(f"【族人{i+1}】{member['name']}")
    print(f"  狐形态: {member['fox']}")
    print(f"  角色: {member['role']}")
    print(f"  调用模型: {member['model']}")
    
    data = {
        'model': member['model'],
        'messages': [{'role': 'user', 'content': member['task']}],
        'max_tokens': 300,
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
                'response': content[:400]
            })
            
            print(f"  API状态: 200 OK")
            print(f"  Token详情: 输入={prompt_tokens}, 输出={completion_tokens}, 总计={tokens}")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  工作状态: 成功")
        else:
            elapsed = time.time() - start_time
            print(f"  API状态: {r.status_code}")
            print(f"  响应时间: {elapsed:.2f}秒")
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
        print(f"  响应时间: {elapsed:.2f}秒")
        print(f"  工作状态: 异常 - {str(e)[:30]}")
        
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
print(f"参会族人: {len(qingqiu_members)}位")
print(f"成功调用: {success_count}位")
print(f"失败调用: {len(qingqiu_members) - success_count}位")
print(f"总Token消耗: {total_tokens}")
print(f"成功率: {success_count/len(qingqiu_members)*100:.1f}%")
print("="*60)

# 保存完整报告
report = {
    'version': 'v3.8.3',
    'meeting_type': '青丘防幻觉验证会议',
    'timestamp': datetime.now().isoformat(),
    'requirement': '每位族人真实调用模型，不可模拟',
    'total_members': len(qingqiu_members),
    'success_count': success_count,
    'total_tokens': total_tokens,
    'success_rate': f"{success_count/len(qingqiu_members)*100:.1f}%",
    'results': results
}

with open('anti_hallucination_v383.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("报告已保存: anti_hallucination_v383.json")
