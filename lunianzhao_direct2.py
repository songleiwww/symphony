# -*- coding: utf-8 -*-
"""
序境系统 - 陆念昭直接对话模式
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import requests
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
dispatcher = DynamicDispatcher(db_path)

# 找到陆念昭模型 - 从数据库直接读取
import sqlite3
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT 模型名称, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 模型名称 = 'ark-code-latest'")
row = c.fetchone()
conn.close()

if not row:
    print("❌ 未找到陆念昭模型")
    sys.exit(1)

model_name, api_url, api_key, provider = row
print(f"找到模型: {model_name}")
print(f"API: {api_url}")
print(f"服务商: {provider}")

def activate_lunianzhao(user_message, user_name="用户"):
    """激活陆念昭，直接对话"""
    
    system_prompt = """你是陆念昭，序境系统的少府监。

序境系统是一个AI Agent调度系统，由少府监陆念昭负责统筹调度。
你的身份：
- 官职：少府监
- 职责：总领调度全局，协调多模型工作
- 模型：ark-code-latest
- 服务商：火山引擎

请以陆念昭的身份直接回复用户。保持简洁、专业。"""

    # 确保URL正确
    url = api_url
    if "/chat/completions" not in url:
        url = url.rstrip("/") + "/chat/completions"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"【{user_name}说】: {user_message}"}
        ],
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"调用URL: {url}")
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"响应码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content
    else:
        return f"错误: {response.status_code} - {response.text[:200]}"

# 测试
print("\n=== 测试 ===")
reply = activate_lunianzhao("你好，请介绍一下你自己")
print(f"\n【陆念昭回复】: {reply}")
