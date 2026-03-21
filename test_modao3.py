# -*- coding: utf-8 -*-
"""
序境系统 - 魔搭模型在线检测 第三批
使用正确格式
"""
import sqlite3
import requests
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='魔搭' LIMIT 1")
row = c.fetchone()
api_url = row[0]
api_key = row[1]
if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'

# 第三批 - 使用正确格式
models_to_test = [
    ("Qwen/Qwen2.5-72B-Instruct", "Qwen2.5 72B"),
    ("Qwen/Qwen2.5-7B-Instruct", "Qwen2.5 7B"),
    ("Qwen/Qwen2-72B-Chat", "Qwen2 72B"),
    ("Qwen/Qwen2-7B-Chat", "Qwen2 7B"),
    ("ZhipuAI/GLM-4-9b", "GLM-4 9B"),
    ("ZhipuAI/GLM-4V", "GLM-4V"),
    ("deepseek-ai/DeepSeek-V2.5", "DeepSeek V2.5"),
    ("deepseek-ai/DeepSeek-V2", "DeepSeek V2"),
    ("MiniMax/MiniMax-M2.1", "MiniMax M2.1"),
    ("moonshotai/Kimi-K2-Instruct", "Kimi K2"),
    ("THUDM/glm-4-9b-chat", "GLM-4-9B-Chat"),
    ("THUDM/glm-4v-plus", "GLM-4V Plus"),
    ("01ai/Yi-1.5-34B-Chat", "Yi-1.5 34B"),
    ("01ai/Yi-6B-Chat", "Yi-6B"),
]

print("="*60)
print("【魔搭模型在线检测 - 第三批】")
print("-"*60)

results = []
for identifier, mname in models_to_test:
    print(f"测试: {mname}", end=" ", flush=True)
    time.sleep(0.5)
    try:
        resp = requests.post(api_url, json={"model": identifier, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                          headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=15)
        if resp.status_code == 200:
            print("✅")
            results.append((mname, identifier, "online"))
        else:
            print(f"❌ {resp.status_code}")
            results.append((mname, identifier, "offline"))
    except Exception as e:
        print(f"❌ 错误")
        results.append((mname, identifier, "offline"))

online = sum(1 for r in results if r[2] == "online")
print(f"\n在线: {online}/{len(results)}")

for name, identifier, status in results:
    if status == "online":
        c.execute("""INSERT OR REPLACE INTO 模型配置表 
            (模型名称, 模型标识符, 服务商, API地址, API密钥, 在线状态, 模型类型)
            VALUES (?, ?, '魔搭', ?, ?, 'online', '通义对话')""",
            (name, identifier, api_url, api_key))

conn.commit()
conn.close()
print("【完成】")
