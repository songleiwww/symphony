#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境少府监协作能力完善 - 8人并行"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 8人协作能力完善任务
tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦，负责协作架构设计。

请为少府监设计协作能力提升方案：
1. 成员间通信机制
2. 任务协调流程
3. 信息共享方式
4. 冲突解决机制

输出JSON（60字以内）
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺，负责心情愉悦系统。

请设计让成员工作愉快的方案：
1. 成就系统
2. 激励反馈
3. 休息提醒
4. 赞美机制

输出JSON（60字以内）
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌，负责文化氛围建设。

请设计少府监文化氛围方案：
1. 口号/愿景
2. 仪式感设计
3. 成员认可
4. 团队精神

输出JSON（60字以内）
'''
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'task': '''你是序境智囊博士沈星衍，负责智能协调。

请设计智能协调方案：
1. 任务自动分配
2. 负载均衡提醒
3. 能力匹配
4. 优先级调度

输出JSON（60字以内）
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘，负责联络机制。

请设计成员联络方案：
1. 实时通信
2. 状态同步
3. 消息传递
4. 紧急联络

输出JSON（60字以内）
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码，负责协作环境建设。

请设计协作环境方案：
1. 工作空间
2. 资源共享
3. 协作工具
4. 效率提升

输出JSON（60字以内）
'''
    },
    {
        'name': '顾至尊',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '首辅大学士',
        'task': '''你是序境首辅大学士顾至尊，负责统筹协调。

请设计繁荣发展方案：
1. 成长机制
2. 晋升通道
3. 贡献奖励
4. 团队凝聚

输出JSON（60字以内）
'''
    },
    {
        'name': '陆念昭',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '少府监',
        'task': '''你是序境少府监陆念昭，负责最终整合。

请综合以下7位成员的方案，设计完整协作系统：
1. 通信机制+心情愉悦
2. 文化氛围+智能协调
3. 联络机制+协作环境
4. 繁荣发展

输出JSON（80字以内）
'''
    },
]

results = []
total_tokens = 0

print('=== 少府监协作能力完善 ===')
print('主题：协作+心情愉悦+繁荣发展\n')

for m in tasks:
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
            results.append({'name': m['name'], 'role': m['role'], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['role'], tokens))
        else:
            results.append({'name': m['name'], 'status': 'FAIL'})
            print('[FAIL] %s' % m['name'])
    except Exception as e:
        print('[ERROR] %s' % m['name'])
    time.sleep(0.5)

print('\n=== 协作方案汇总 ===')
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s:' % (r['name'], r['role']))
        print(r['response'][:120])

print('\n\n总消耗: %d tokens' % total_tokens)

with open('collaboration.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n方案已保存: collaboration.json')
