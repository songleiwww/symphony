# -*- coding: utf-8 -*-
"""
序境系统 - 修复调度引擎API调用 v2
使用模型标识符修复API调用
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
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取模型时使用模型标识符
c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 服务商 IN ('硅基流动', '魔搭', '英伟达') LIMIT 5")
models_data = c.fetchall()
conn.close()

def call_with_identifier(model_name, model_id, api_url, api_key, provider, prompt):
    """使用模型标识符调用"""
    url = api_url
    # 确保URL正确
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    payload = {
        "model": model_id,  # 使用标识符
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'], resp.status_code
        else:
            return f"{resp.status_code}: {resp.text[:80]}", resp.status_code
    except Exception as e:
        return f"错误: {e}", 0

print("="*60)
print("【修复测试v2】使用模型标识符")
print("="*60)

for md in models_data:
    model_name, model_id, api_url, api_key, provider = md
    print(f"\n【{provider}】{model_name}")
    print(f"  标识符: {model_id}")
    content, code = call_with_identifier(model_name, model_id, api_url, api_key, provider, "你好")
    print(f"  状态: {code}")
    if content:
        print(f"  回复: {content[:100]}")

print("\n" + "="*60)
