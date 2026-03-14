#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境系统性Debug除错 - 8人并行"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 读取当前symphony.py代码
with open('symphony.py', 'r', encoding='utf-8') as f:
    symphony_code = f.read()[:3000]  # 限制长度

# 8人Debug任务
debug_tasks = [
    {
        'name': '沈清弦',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '枢密使',
        'task': '''你是序境枢密使沈清弦，负责架构审查。

请审查以下symphony.py代码，找出架构问题：
1. 模块耦合度
2. 设计模式问题
3. 潜在死锁风险
4. 内存泄漏风险

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '苏云渺',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '工部尚书',
        'task': '''你是序境工部尚书苏云渺，负责代码质量审查。

请审查以下symphony.py代码，找出代码问题：
1. 语法错误
2. 类型错误
3. 逻辑错误
4. 未处理异常

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '顾清歌',
        'model': 'THUDM/glm-4-9b-chat',
        'role': '翰林学士',
        'task': '''你是序境翰林学士顾清歌，负责规则审查。

请审查以下symphony.py代码，找出规则问题：
1. 告警规则缺陷
2. 边界条件遗漏
3. 配置错误
4. 默认值问题

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '沈星衍',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '智囊博士',
        'task': '''你是序境智囊博士沈星衍，负责策略审查。

请审查以下symphony.py代码，找出策略问题：
1. 调度策略漏洞
2. 优先级问题
3. 超时处理
4. 降级策略

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '叶轻尘',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '行走使',
        'task': '''你是序境行走使叶轻尘，负责性能审查。

请审查以下symphony.py代码，找出性能问题：
1. 资源占用
2. 响应延迟
3. 并发瓶颈
4. 缓存效率

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '林码',
        'model': 'Qwen/Qwen2.5-72B-Instruct',
        'role': '营造司正',
        'task': '''你是序境营造司正林码，负责工程审查。

请审查以下symphony.py代码，找出工程问题：
1. 接口规范性
2. 扩展性问题
3. 兼容性
4. 可测试性

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '顾至尊',
        'model': 'Qwen/Qwen2.5-14B-Instruct',
        'role': '首辅大学士',
        'task': '''你是序境首辅大学士顾至尊，负责统筹审查。

请审查以下symphony.py代码，找出整体问题：
1. 功能完整性
2. 无效功能
3. 冗余代码
4. 缺失功能

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
    {
        'name': '陆念昭',
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'role': '少府监',
        'task': '''你是序境少府监陆念昭，负责调度审查。

请审查以下symphony.py代码，找出调度问题：
1. 任务队列
2. 负载均衡
3. 故障转移
4. 状态管理

代码片段：
%s

输出问题JSON（50字以内）
''' % symphony_code
    },
]

results = []
total_tokens = 0

print('=== 序境系统性Debug除错 ===')
print('任务：全面排查功能失控、无效功能\n')

for m in debug_tasks:
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
            results.append({'name': m['name'], 'role': m['role'], 'model': m['model'].split('/')[-1], 'response': content, 'tokens': tokens, 'status': 'OK'})
            print('[OK] %s | %s | %d tokens' % (m['name'], m['role'], tokens))
        else:
            results.append({'name': m['name'], 'role': m['role'], 'response': str(result), 'status': 'FAIL'})
            print('[FAIL] %s' % m['name'])
    except Exception as e:
        results.append({'name': m['name'], 'role': m['role'], 'response': str(e), 'status': 'FAIL'})
        print('[ERROR] %s' % m['name'])
    time.sleep(0.5)

print('\n=== Debug问题汇总 ===')
issues_found = []
for r in results:
    if r['status'] == 'OK':
        print('\n【%s】%s:' % (r['name'], r['role']))
        print(r['response'][:150])
        issues_found.append(r['response'])

print('\n\n总消耗: %d tokens' % total_tokens)

# 保存Debug结果
with open('debug_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\nDebug结果已保存: debug_results.json')
