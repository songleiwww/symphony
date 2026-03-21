# -*- coding: utf-8 -*-
"""
序境系统 - 英伟达模型在线检测 第九批
"""
import sqlite3
import requests
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 第九批
nvidia_models = [
    ("google/shieldgemma-9b", "ShieldGemma 9B"),
    ("google/gemma-3-1b-it", "Gemma 3 1B"),
    ("google/codegemma-7b", "CodeGemma 7B"),
    ("mistralai/mixtral-8x7b-instruct", "Mixtral 8x7B v2"),
    ("mistralai/mistral-large-instruct", "Mistral Large Instruct"),
    ("deepseek-ai/deepseek-r1-distill-qwen-32b", "DeepSeek R1 Qwen 32B v2"),
    ("deepseek-ai/deepseek-r1-distill-llama-8b", "DeepSeek R1 Llama 8B v2"),
    ("abacusai/dracarys-llama-3.1-70b-instruct", "Dracarys Llama 3.1 70B"),
]

c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = c.fetchone()
api_url = row[0]
api_key = row[1]
if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'

print("="*60)
print("【第九批】英伟达模型在线检测")
print("-"*60)

results = []
for model_id, model_name in nvidia_models:
    print(f"\n测试: {model_name}", end=" ", flush=True)
    time.sleep(1)
    try:
        resp = requests.post(api_url, json={"model": model_id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                          headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=25)
        if resp.status_code == 200:
            print("✅")
            results.append((model_name, model_id, "online"))
        else:
            print(f"❌ {resp.status_code}")
            results.append((model_name, model_id, "offline"))
    except Exception as e:
        print(f"❌ 错误")
        results.append((model_name, model_id, "offline"))

online = sum(1 for r in results if r[2] == "online")
print(f"\n在线: {online}/{len(results)}")

for name, model_id, status in results:
    if status == "online":
        c.execute("""INSERT OR REPLACE INTO 模型配置表 (模型名称, 模型标识符, 服务商, API地址, API密钥, 在线状态, 模型类型)
            VALUES (?, ?, '英伟达', ?, ?, 'online', '通义对话')""", (name, model_id, api_url, api_key))

conn.commit()
conn.close()
print("【完成】")
