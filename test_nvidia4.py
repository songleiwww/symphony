# -*- coding: utf-8 -*-
"""
序境系统 - 英伟达模型在线检测 第四批
仔细测试
"""
import sqlite3
import requests
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 第四批模型（更多选择）
nvidia_models = [
    ("nvidia/llama3-chatqa-1.5-8b", "Llama3 ChatQA 1.5 8B"),
    ("mistralai/codestral-22b-instruct-v0.1", "Codestral 22B"),
    ("mistralai/mistral-small-24b-instruct", "Mistral Small 24B"),
    ("mistralai/mistral-nemotron", "Mistral Nemotron"),
    ("google/codegemma-1.1-7b", "CodeGemma 1.1 7B"),
    ("microsoft/phi-3.5-mini", "Phi-3.5 Mini"),
    ("microsoft/phi-3-small-128k-instruct", "Phi-3 Small 128K"),
    ("deepseek-ai/deepseek-v3.1", "DeepSeek V3.1"),
]

c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = c.fetchone()
api_url = row[0]
api_key = row[1]
if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'

print("="*60)
print("【第四批】英伟达模型在线检测")
print("-"*60)

results = []
for model_id, model_name in nvidia_models:
    print(f"\n测试: {model_name}", end=" ", flush=True)
    time.sleep(1)  # 别太快
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
