#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境多人开发任务 - 真实模型调度"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 开发任务 - 6个成员并行开发
dev_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦，负责架构设计。
请为序境系统设计"主被动关键词执行功能"，要求：
1. 被动触发：识别"交响"/"序境"/"symphony"自动响应
2. 主动感知：分析用户意图，主动提供帮助
3. 输出架构设计文档（100字以内）
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺，负责代码开发。
请设计"人员响应模块"的Python代码结构，要求：
1. 识别消息中提及的成员姓名
2. 自动调度对应模型响应
3. 输出代码框架（100字以内）
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌，负责知识库。
请设计"主动帮助系统"的规则引擎，要求：
1. 检测用户困难关键词
2. 主动提供解决方案
3. 输出规则设计（100字以内）
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘，负责轻量任务。
请设计"关键词触发器"的正则表达式，要求：
1. 匹配"交响"/"序境"/"symphony"
2. 匹配人员姓名（沈清弦/苏云渺等）
3. 输出正则规则（80字以内）
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码，负责代码实现。
请设计"模型调度器"的调度策略，要求：
1. 根据任务类型选择模型
2. 实现故障转移机制
3. 输出调度逻辑（100字以内）
'''
    },
    {
        'name': '顾至尊',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '首辅大学士',
        'task': '''你是序境首辅大学士顾至尊，负责整体协调。
请设计"序境开发"的整合方案，要求：
1. 汇总各模块设计
2. 确定开发优先级
3. 输出整合计划（100字以内）
'''
    },
]

results = []
total_tokens = 0

print('=== 序境多人开发开始 ===\n')
print('任务：主被动关键词执行 + 人员响应 + 主动帮助\n')

for m in dev_tasks:
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': m['model'],
        'messages': [{'role': 'user', 'content': m['task']}],
        'max_tokens': 300,
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
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'].split('/')[-1], 'response': str(result), 'tokens': 0, 'status': 'FAIL'})
            print('[FAIL] %s | %s' % (m['name'], str(result)[:50]))
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'model': m['model'].split('/')[-1], 'response': str(e), 'tokens': 0, 'status': 'FAIL'})
        print('[ERROR] %s | %s' % (m['name'], str(e)[:50]))
    time.sleep(0.5)  # 避免限流

print('\n=== 开发成果汇总 ===')
for r in results:
    status = '[OK]' if r['status'] == 'OK' else '[FAIL]'
    print('\n%s %s (%s):' % (status, r['name'], r['role']))
    print(r['response'][:200])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存开发成果
with open('dev_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n开发成果已保存: dev_results.json')
