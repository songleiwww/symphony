# -*- coding: utf-8 -*-
import sqlite3
import requests

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 查看魔搭和硅基流动模型
print("=== Models in Other Providers ===\n")

# 魔搭
c.execute('SELECT 模型名称, API地址 FROM 模型配置表 WHERE 服务商="魔搭" AND 在线状态="online"')
print("--- 魔搭 ---")
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}")

# 硅基流动
c.execute('SELECT 模型名称, API地址 FROM 模型配置表 WHERE 服务商="硅基流动" AND 在线状态="online"')
print("\n--- 硅基流动 ---")
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()

# Test 硅基流动 API
print("\n=== Testing 硅基流动 ===\n")
url = "https://api.siliconflow.cn/v1/chat/completions"
api_key = "sk-dtjcmhtmwptzuvwctnpfxpqqfxlzzzijptzwq"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "Qwen/Qwen2.5-72B-Instruct",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 30
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
    else:
        print(f"Error: {response.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
