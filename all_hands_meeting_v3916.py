#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘全员讨论大会 v3.9.16
研究任务连贯性和OpenClaw限制问题
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

# 6位青丘全员
experts = [
    {
        'name': '林思远',
        'fox': '银白九尾狐 - 青丘长老',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''作为青丘长老，请分析OpenClaw系统的限制问题：

1. OpenClaw有什么限制？
   - 超时限制
   - Token限制
   - 并发限制
   - 其他限制

2. 这些限制如何影响任务连贯性？

3. 建议的解决方案是什么？

请简明扼要回答（约200字）。'''
    },
    {
        'name': '张晓明',
        'fox': '墨黑九尾狐 - 青丘史官',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''作为青丘史官，请记录和分析任务连贯性问题：

1. 历史上出现过哪些任务中断问题？

2. 任务卡死的常见原因是什么？

3. 如何确保任务完成不中断？

请简明扼要回答（约200字）。'''
    },
    {
        'name': '赵心怡',
        'fox': '金黄九尾狐 - 青丘舞姬',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''作为青丘舞姬，请从用户体验角度分析：

1. 用户对任务连贯性的期望是什么？

2. 任务中断对用户的影响？

3. 如何提升用户体验？

请简明扼要回答（约200字）。'''
    },
    {
        'name': '陈浩然',
        'fox': '青灰九尾狐 - 青丘守护',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''作为青丘守护，请从安全角度分析：

1. 任务连贯性的安全风险是什么？

2. 如何防止任务被恶意中断？

3. 安全恢复机制建议？

请简明扼要回答（约200字）。'''
    },
    {
        'name': '王明远',
        'fox': '火红九尾狐 - 青丘猎手',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''作为青丘猎手，请从执行角度分析：

1. 如何快速检测任务卡死？

2. 如何快速恢复任务？

3. 最佳实践建议？

请简明扼要回答（约200字）。'''
    },
    {
        'name': '周小芳',
        'fox': '雪白九尾狐 - 青丘医师',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''作为青丘医师，请从修复角度分析：

1. 如何诊断任务问题？

2. 如何治愈任务中断？

3. 预防措施建议？

请简明扼要回答（约200字）。'''
    }
]

results = []
total_tokens = 0

print("="*60)
print("青丘全员讨论大会 v3.9.16")
print("研究任务连贯性和OpenClaw限制问题")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

for i, expert in enumerate(experts):
    print(f"【{i+1}/6】{expert['name']}({expert['fox'].split('-')[0].strip()})...", end=" ", flush=True)
    
    try:
        r = requests.post(URL, headers=HEADERS, json={
            'model': expert['model'],
            'messages': [{'role': 'user', 'content': expert['task']}],
            'max_tokens': 300
        }, timeout=60)
        
        if r.status_code == 200:
            data = r.json()
            tokens = data.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens
            print(f"成功 Token:{tokens}")
            results.append({'name': expert['name'], 'status': '成功', 'tokens': tokens})
        else:
            print(f"失败:{r.status_code}")
            results.append({'name': expert['name'], 'status': '失败'})
    except Exception as e:
        print(f"异常:{str(e)[:20]}")
        results.append({'name': expert['name'], 'status': '异常'})

print()
print("="*60)
print(f"大会完成 Token:{total_tokens}")
print("="*60)

# 保存
with open('all_hands_meeting_v3916.json', 'w', encoding='utf-8') as f:
    json.dump({
        'version': 'v3.9.16',
        'topic': '全员讨论大会-任务连贯性研究',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'total_tokens': total_tokens
    }, f, ensure_ascii=False, indent=2)

print("已保存: all_hands_meeting_v3916.json")
