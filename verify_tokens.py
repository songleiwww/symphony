#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确Token验证脚本 - 验证真实Token消耗
"""
import requests
import json
import time
from datetime import datetime

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# 简单测试 - 不设置max_tokens限制
print("="*60)
print("精确Token验证测试")
print("="*60)
print()

# 测试两个模型，不设置max_tokens限制
test_models = [
    {
        'name': '林思远',
        'model': 'meta/llama-3.1-405b-instruct',
        'task': '请用一句话介绍你自己。'
    },
    {
        'name': '王明远',
        'model': 'mistralai/mistral-large-3-675b-instruct-2512',
        'task': '请用一句话介绍你自己。'
    }
]

for test in test_models:
    print(f"测试模型: {test['name']} - {test['model']}")
    
    # 不设置max_tokens
    data = {
        'model': test['model'],
        'messages': [{'role': 'user', 'content': test['task']}]
    }
    
    try:
        r = requests.post(URL, headers=HEADERS, json=data, timeout=60)
        if r.status_code == 200:
            result = r.json()
            
            # 打印完整的usage信息
            usage = result.get('usage', {})
            print(f"  完整usage信息: {json.dumps(usage, indent=2)}")
            
            # 获取响应内容长度
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"  响应内容长度: {len(content)} 字符")
            print(f"  响应内容: {content[:100]}...")
            
    except Exception as e:
        print(f"  错误: {str(e)[:50]}")
    
    print()

print("="*60)
print("验证完成")
print("="*60)
