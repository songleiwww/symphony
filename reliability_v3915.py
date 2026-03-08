#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘可靠性解决方案 v3.9.15 - 简化版
解决真实性和连贯性问题
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

# 3位专家（简化版）
experts = [
    {
        'name': '林思远',
        'role': '真实性验证',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '''请简述如何确保交响系统使用真实模型调用，防止模拟和幻觉。给出3个核心类的Python代码（约50行）：
1. RealCallVerifier - 验证真实调用
2. HallucinationDetector - 检测幻觉
3. ResponseValidator - 验证响应'''
    },
    {
        'name': '张晓明',
        'role': '任务连贯性',
        'model': 'qwen/qwen3.5-397b-a17b',
        'task': '''请简述如何保证任务不卡死、不停滞。给出3个核心类的Python代码（约50行）：
1. TaskContinuityManager - 连贯性管理
2. DeadlockDetector - 死锁检测
3. TimeoutHandler - 超时处理'''
    },
    {
        'name': '赵心怡',
        'role': '状态追踪',
        'model': 'minimaxai/minimax-m2.5',
        'task': '''请简述如何追踪任务状态。给出3个核心类的Python代码（约50行）：
1. StateTracker - 状态追踪
2. ProgressMonitor - 进度监控
3. RecoveryManager - 恢复管理'''
    }
]

results = []
total_tokens = 0

print("="*60)
print("青丘可靠性解决方案 v3.9.15")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

for i, expert in enumerate(experts):
    print(f"【{expert['name']}】{expert['role']}...", end=" ", flush=True)
    
    try:
        r = requests.post(URL, headers=HEADERS, json={
            'model': expert['model'],
            'messages': [{'role': 'user', 'content': expert['task']}],
            'max_tokens': 500  # 限制输出
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
print(f"完成 Token:{total_tokens}")

# 保存
with open('reliability_v3915.json', 'w', encoding='utf-8') as f:
    json.dump({'version': 'v3.9.15', 'results': results, 'tokens': total_tokens}, f, ensure_ascii=False)

print("已保存: reliability_v3915.json")
