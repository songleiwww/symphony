# -*- coding: utf-8 -*-
"""
序境系统 - 魔搭模型在线检测 第二批
"""
import sqlite3
import requests
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取魔搭API配置
c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='魔搭' LIMIT 1")
row = c.fetchone()
api_url = row[0]
api_key = row[1]
if '/chat/completions' not in api_url:
    api_url = api_url.rstrip('/') + '/chat/completions'

# 第二批测试模型（从官网热门模型）
models_to_test = [
    ("iic/mossmoon-7b-sft", "MOSS Moon 7B SFT"),
    ("iic/mossmoon-7b-chat", "MOSS Moon 7B Chat"),
    ("iic/llama3-8b-instruct", "Llama3 8B Instruct"),
    ("iic/llama3-70b-instruct", "Llama3 70B Instruct"),
    ("iic/qwen-14b-chat", "Qwen 14B Chat"),
    ("iic/qwen-72b-chat", "Qwen 72B Chat"),
    ("iic/qwen1.5-72b-chat", "Qwen1.5 72B Chat"),
    ("iic/qwen1.5-110b-chat", "Qwen1.5 110B Chat"),
    ("iic/Salesforce-codegen25-7b-multi", "CodeGen25 7B Multi"),
    ("iic/bunny-llama3-8b-v1.5", "Bunny Llama3 8B"),
    ("iic/Paraformer3-Speech", "Paraformer3 Speech"),
    ("iic/speech_paraformer-large-vad", "Paraformer VAD"),
    ("iic/speech_paraformer-asr", "Paraformer ASR"),
    ("iic/SenseVoiceSmall", "SenseVoice Small"),
    ("iic/cosyvoice2-0.5B", "CosyVoice2 0.5B"),
    ("iic/Amphion", "Amphion"),
]

print("="*60)
print("【魔搭模型在线检测 - 第二批】")
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

# 添加在线模型
for name, identifier, status in results:
    if status == "online":
        c.execute("""INSERT OR REPLACE INTO 模型配置表 
            (模型名称, 模型标识符, 服务商, API地址, API密钥, 在线状态, 模型类型)
            VALUES (?, ?, '魔搭', ?, ?, 'online', '通义对话')""",
            (name, identifier, api_url, api_key))

conn.commit()
conn.close()
print("【完成】")
