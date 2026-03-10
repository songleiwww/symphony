#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境进化方向研讨 - 少府监核心会议"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 6位核心成员研讨任务
discussion_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦。

请分析序境系统当前最需要进化的方向，从以下维度思考：
1. 架构层面：系统结构是否合理
2. 能力层面：哪些能力还缺失
3. 性能层面：响应速度、并发能力
4. 生态层面：与OpenClaw/Skill的集成

请用50字以内，指出最关键的1-2个进化方向。
'''
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺。

请从代码工程角度分析序境最需要进化的方向：
1. 代码质量：可维护性、可扩展性
2. 开发效率：开发体验、调试能力
3. 测试覆盖：单元测试、集成测试
4. 文档完善：API文档、使用指南

请用50字以内，指出最关键的1-2个进化方向。
'''
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌。

请从知识管理角度分析序境最需要进化的方向：
1. 记忆系统：短期/长期记忆
2. 知识库：领域知识积累
3. 学习能力：持续学习新知识
4. 上下文：多轮对话连贯性

请用50字以内，指出最关键的1-2个进化方向。
'''
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'task': '''你是序境智囊博士沈星衍。

请从智能化角度分析序境最需要进化的方向：
1. 意图理解：更精准理解用户意图
2. 主动感知：主动发现用户需求
3. 个性化：适应用户习惯偏好
4. 推理能力：复杂问题处理

请用50字以内，指出最关键的1-2个进化方向。
'''
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘。

请从执行效率角度分析序境最需要进化的方向：
1. 响应速度：更快响应用户
2. 并发处理：多任务并行能力
3. 资源优化：降低资源消耗
4. 故障恢复：异常处理能力

请用50字以内，指出最关键的1-2个进化方向。
'''
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码。

请从工程实现角度分析序境最需要进化的方向：
1. 模块化：代码解耦程度
2. 标准化：接口规范程度
3. 自动化：部署、监控、运维
4. 兼容性：多平台支持

请用50字以内，指出最关键的1-2个进化方向。
'''
    },
]

results = []
total_tokens = 0

print('=== 序境进化方向研讨 ===')
print('主题：分析最需要进化的方向\n')

for m in discussion_tasks:
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': m['model'],
        'messages': [{'role': 'user', 'content': m['task']}],
        'max_tokens': 150,
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
            results.append({'name': m['name'], 'role': m['role'], 'response': str(result), 'status': 'FAIL'})
            print('[FAIL] %s' % m['name'])
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'response': str(e), 'status': 'FAIL'})
        print('[ERROR] %s' % m['name'])
    time.sleep(0.5)

print('\n=== 进化方向汇总 ===')
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s:' % (r['name'], r['role']))
        print(r['response'])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存研讨成果
with open('evolution_discussion.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n研讨成果已保存: evolution_discussion.json')
