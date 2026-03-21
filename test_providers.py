# -*- coding: utf-8 -*-
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

# 硅基流动
c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商='硅基流动' LIMIT 3")
print("【硅基流动】")
for r in c.fetchall():
    name, mid, url, key = r
    url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 50}, 
                          headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, timeout=20)
        print(f"  {name}: {resp.status_code}")
    except Exception as e:
        print(f"  {name}: 错误 {e}")

# 魔搭
c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商='魔搭' LIMIT 3")
print("\n【魔搭】")
for r in c.fetchall():
    name, mid, url, key = r
    url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 50}, 
                          headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, timeout=20)
        print(f"  {name}: {resp.status_code}")
    except Exception as e:
        print(f"  {name}: 错误 {e}")

conn.close()
