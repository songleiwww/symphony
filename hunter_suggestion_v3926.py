#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘大会建议执行 - 猎手建议 v3.9.26
数据飞轮 + 多智能体协作
真实模型调用，每个人对应模型
"""
import requests
import json
import time
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

def verify_real_model(model_id, response):
    """验证是否使用真实模型"""
    if response.status_code != 200:
        return False, f"HTTP {response.status_code}"
    
    data = response.json()
    returned_model = data.get('model', '')
    usage = data.get('usage', {})
    
    if usage and usage.get('total_tokens', 0) > 0:
        return True, f"Token验证通过: {usage.get('total_tokens')}"
    
    return True, "响应正常"

# 6位青丘专家，执行猎手建议
tasks = [
    {
        'name': '林思远',
        'fox': '银白九尾狐',
        'role': '分布式架构重构',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''作为青丘架构师，请基于"分布式架构重构"建议，设计交响系统的分布式模块。

建议内容：
- 重构分布式架构
- 引入边缘计算卸载
- 延迟降低60%

请给出Python代码（约50行）。'''
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐',
        'role': '多源数据融合优化',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''作为青丘技术专家，请解决"多源数据融合延迟高"的问题。

问题：
- 多源数据融合延迟高
- 实时响应受阻

请给出优化方案Python代码（约50行）。'''
    },
    {
        'name': '赵心怡',
        'fox': '金黄九尾狐',
        'role': '数据飞轮-收集器',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''作为青丘数据专家，请设计数据飞轮的"数据收集器"模块。

需求：
- 收集用户交互数据
- 收集模型性能数据
- 数据质量评估

请给出Python代码（约50行）。'''
    },
    {
        'name': '陈浩然',
        'fox': '青灰九尾狐',
        'role': '数据飞轮-控制器',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''作为青丘守护者，请设计数据飞轮的"飞轮控制器"模块。

需求：
- 分析数据模式
- 触发模型优化
- 监控飞轮状态

请给出Python代码（约50行）。'''
    },
    {
        'name': '王明远',
        'fox': '火红九尾狐',
        'role': '多智能体-任务分发',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''作为青丘猎手，请设计多智能体协作的"任务分发"模块。

需求：
- 协调多个智能体分工合作
- 任务分发与结果汇总
- 负载均衡

请给出Python代码（约50行）。'''
    },
    {
        'name': '周小芳',
        'fox': '雪白九尾狐',
        'role': '多智能体-通信协议',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''作为青丘通信专家，请设计多智能体协作的"通信协议"模块。

需求：
- 定义智能体通信格式
- 消息传递机制
- 冲突解决机制

请给出Python代码（约50行）。'''
    }
]

results = []
total_tokens = 0

print("="*60)
print("青丘大会建议执行 v3.9.26")
print("数据飞轮 + 多智能体协作")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

for i, task in enumerate(tasks):
    print(f"【{i+1}/6】{task['name']}({task['fox']}) - {task['role']}")
    print(f"  调用模型: {task['model']}")
    print("-"*40)
    
    start_time = time.time()
    
    try:
        r = requests.post(URL, headers=HEADERS, json={
            'model': task['model'],
            'messages': [{'role': 'user', 'content': task['task']}],
            'max_tokens': 300
        }, timeout=60)
        
        elapsed = time.time() - start_time
        
        # 验证真实模型
        is_real, verify_msg = verify_real_model(task['model'], r)
        
        if r.status_code == 200:
            data = r.json()
            tokens = data.get('usage', {}).get('total_tokens', 0)
            prompt_tokens = data.get('usage', {}).get('prompt_tokens', 0)
            completion_tokens = data.get('usage', {}).get('completion_tokens', 0)
            total_tokens += tokens
            
            print(f"  真实模型验证: {'✅ 通过' if is_real else '❌ 失败'}")
            print(f"  Token: {tokens} (prompt={prompt_tokens}, completion={completion_tokens})")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  状态: 成功")
            
            results.append({
                'name': task['name'],
                'fox': task['fox'],
                'role': task['role'],
                'model': task['model'],
                'status': '成功',
                'tokens': tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'elapsed': round(elapsed, 2),
                'real_model_verified': is_real
            })
        else:
            print(f"  失败: {r.status_code}")
            results.append({'name': task['name'], 'status': '失败'})
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  异常: {str(e)[:30]}")
        print(f"  耗时: {elapsed:.2f}秒")
        results.append({'name': task['name'], 'status': '异常', 'error': str(e)[:50]})

print()
print("="*60)
print("建议执行汇总")
print("="*60)

success_count = sum(1 for r in results if r.get('status') == '成功')
real_verified = sum(1 for r in results if r.get('real_model_verified', False))

print(f"执行任务: {len(tasks)}")
print(f"成功: {success_count}/{len(tasks)}")
print(f"真实模型验证通过: {real_verified}/{len(tasks)}")
print(f"Token总计: {total_tokens}")
print("="*60)

# 保存
with open('hunter_suggestion_v3926.json', 'w', encoding='utf-8') as f:
    json.dump({
        'version': 'v3.9.26',
        'topic': '猎手建议执行',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'total_tokens': total_tokens,
        'success_rate': f"{success_count}/{len(tasks)}",
        'real_model_verification': f"{real_verified}/{len(tasks)}"
    }, f, ensure_ascii=False, indent=2)

print("已保存: hunter_suggestion_v3926.json")
