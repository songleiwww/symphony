# -*- coding: utf-8 -*-
"""
序境系统 - 修复调度引擎API调用
修复各服务商API地址问题
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import requests
import sqlite3
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
dispatcher = DynamicDispatcher(db_path)

def call_model_fixed(model, prompt):
    """修复后的模型调用"""
    url = model.get('url', '')
    provider = model.get('provider', '')
    model_name = model.get('name', '')
    
    # 根据服务商修复URL
    if '英伟达' in provider:
        # 英伟达：使用正确的模型ID
        if 'llama' in model_name.lower():
            model_id = 'meta/llama-3.2-1b-instruct'
        else:
            model_id = model_name
        url = 'https://integrate.api.nvidia.com/v1/chat/completions'
    elif '硅基流动' in provider:
        # 硅基流动：添加/chat/completions
        url = url.rstrip('/') + '/chat/completions'
    elif '魔搭' in provider:
        # 魔搭：添加/chat/completions
        url = url.rstrip('/') + '/chat/completions'
    else:
        # 火山引擎等确保有/chat/completions
        if '/chat/completions' not in url:
            url = url.rstrip('/') + '/chat/completions'
    
    payload = {
        "model": model_id if 'model_id' in dir() else model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }
    
    headers = {
        "Authorization": f"Bearer {model.get('key', '')}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'], resp.status_code
        else:
            return f"状态{resp.status_code}: {resp.text[:100]}", resp.status_code
    except Exception as e:
        return f"错误: {e}", 0

# 测试各服务商
print("="*60)
print("【修复测试】各服务商API调用")
print("="*60)

test_models = []
for m in dispatcher.models:
    p = m.get('provider', '')
    if p not in [x.get('provider') for x in test_models]:
        test_models.append(m)
    if len(test_models) >= 4:
        break

for m in test_models:
    print(f"\n【{m['provider']}】{m['name']}")
    content, code = call_model_fixed(m, "你好，请回复")
    print(f"  状态: {code}")
    print(f"  回复: {content[:100] if content else '无'}")

print("\n" + "="*60)
print("【修复完成】")
print("="*60)
