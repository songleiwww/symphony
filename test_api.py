#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""序境全员述职脚本 - 调试版"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
API_KEY = '3b922877-3fbe-45d1-a298-53f2231c5224'

# 测试单个成员
member = {'name': '沈清弦', 'model': 'ark-code-latest', 'task': '你好，请回复"收到"'}

headers = {'Authorization': API_KEY, 'Content-Type': 'application/json'}
data = {
    'model': member['model'],
    'messages': [{'role': 'user', 'content': member['task']}],
    'max_tokens': 100
}

print('Testing API...')
print('URL:', API_URL)
print('Model:', member['model'])

try:
    r = requests.post(API_URL, headers=headers, json=data, timeout=30)
    print('Status:', r.status_code)
    print('Response:', r.text[:500])
except Exception as e:
    print('Error:', str(e))
