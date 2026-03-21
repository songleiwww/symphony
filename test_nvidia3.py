# -*- coding: utf-8 -*-
"""
序境系统 - 英伟达模型在线检测 第三批
"""
import sqlite3
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 第三批模型
nvidia_models = [
    ("mistralai/mistral-7b-instruct-v0.3", "Mistral 7B v0.3"),
    ("mistralai/mixtral-8x22b-instruct", "Mixtral 8x22B"),
    ("microsoft/phi-4-mini-flash-reasoning", "Phi-4 Mini Flash"),
    ("deepseek-ai/deepseek-r1-distill-qwen-7b", "DeepSeek R1 Qwen 7B"),
    ("deepseek-ai/deepseek-r1-distill-llama-8b", "DeepSeek R1 Llama 8B"),
    ("ai21labs/jamba-1.5-mini-instruct", "Jamba 1.5 Mini"),
    ("baichuan-inc/baichuan2-13b-chat", "Baichuan 2 13B"),
    ("nvidia/llama3-chatqa-1.5-8b", "Llama3 ChatQA 8B"),
]

c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = c.fetchone()
api_url = row[0]
api_key = row[1]
if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'

print("="*60)
print("【第三批】英伟达模型在线检测")
print("-"*60)

results = []
for model_id, model_name in nvidia_models:
    try:
        resp = requests.post(api_url, json={"model": model_id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                          headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=25)
        if resp.status_code == 200:
            print(f"✅ {model_name}")
            results.append((model_name, model_id, "online"))
        else:
            print(f"❌ {model_name}: {resp.status_code}")
            results.append((model_name, model_id, "offline"))
    except Exception as e:
        print(f"❌ {model_name}: 错误")
        results.append((model_name, model_id, "offline"))

online = sum(1 for r in results if r[2] == "online")
print(f"\n在线: {online}/{len(results)}")

# 添加在线的
for name, model_id, status in results:
    if status == "online":
        c.execute("""INSERT OR REPLACE INTO 模型配置表 (模型名称, 模型标识符, 服务商, API地址, API密钥, 在线状态, 模型类型)
            VALUES (?, ?, '英伟达', ?, ?, 'online', '通义对话')""", (name, model_id, api_url, api_key))

conn.commit()
conn.close()
print("【完成】")
