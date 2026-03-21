# -*- coding: utf-8 -*-
"""
序境系统 - 英伟达模型在线检测 第二批
从官网获取更多可用模型
"""
import sqlite3
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 英伟达官网模型列表（精选热门）
nvidia_models = [
    ("meta/llama-3.1-8b-instruct", "Llama 3.1 8B"),
    ("meta/llama-3.1-70b-instruct", "Llama 3.1 70B"),
    ("meta/llama-3.1-405b-instruct", "Llama 3.1 405B"),
    ("google/gemma-2-27b-it", "Gemma 2 27B"),
    ("microsoft/phi-3-mini-128k-instruct", "Phi-3 Mini 128K"),
    ("mistralai/mixtral-8x7b-instruct", "Mixtral 8x7B"),
    ("deepseek-ai/deepseek-r1-distill-qwen-14b", "DeepSeek R1 Qwen 14B"),
    ("nvidia/llama-3.1-nemotron-nano-8b-v1", "Nemotron Nano 8B"),
]

# 获取API配置
c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = c.fetchone()
api_url = row[0]
api_key = row[1]

if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'

print("="*60)
print("【陆念昭调度】英伟达模型在线检测 - 第二批")
print("="*60)
print(f"API: {api_url}")
print(f"测试模型: {len(nvidia_models)}个")
print("-"*60)

results = []
for model_id, model_name in nvidia_models:
    print(f"\n{model_name}")
    print(f"  ID: {model_id}")
    try:
        resp = requests.post(
            api_url,
            json={"model": model_id, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=25
        )
        status = resp.status_code
        if status == 200:
            print(f"  ✅ 在线")
            results.append((model_name, model_id, "online"))
        else:
            print(f"  ❌ {status}: {resp.text[:50]}")
            results.append((model_name, model_id, "offline"))
    except Exception as e:
        print(f"  ❌ 错误: {str(e)[:30]}")
        results.append((model_name, model_id, "offline"))

print("\n" + "="*60)
print("【汇总】")
print("="*60)

online_models = [r for r in results if r[2] == "online"]
for r in results:
    status = "✅" if r[2] == "online" else "❌"
    print(f"{status} {r[0]}")

print(f"\n在线: {len(online_models)}/{len(results)}")

# 添加在线模型到数据库
print("\n【添加到数据库】")
for name, model_id, status in online_models:
    c.execute("""INSERT OR REPLACE INTO 模型配置表 
        (模型名称, 模型标识符, 服务商, API地址, API密钥, 在线状态, 模型类型)
        VALUES (?, ?, '英伟达', ?, ?, 'online', '通义对话')""",
        (name, model_id, api_url, api_key))
    print(f"  + {name}")

conn.commit()
conn.close()

print("\n【完成】")
