# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== All Models in Config ===\n')

# Get all model config
cur.execute('SELECT "模型名称", "服务商", "状态" FROM "模型配置表"')
rows = cur.fetchall()

# Group by provider
providers = {}
for r in rows:
    model_name = r[0]
    provider = r[1]
    status = r[2]
    if provider not in providers:
        providers[provider] = {"count": 0, "online": 0, "offline": 0, "models": []}
    providers[provider]["count"] += 1
    if status == "online":
        providers[provider]["online"] += 1
    else:
        providers[provider]["offline"] += 1
    if len(providers[provider]["models"]) < 5:
        providers[provider]["models"].append(model_name)

print('Provider Statistics:')
for p, info in providers.items():
    print(f'\n{p}:')
    print(f'  Total: {info["count"]}, Online: {info["online"]}, Offline: {info["offline"]}')
    print(f'  Sample models: {", ".join(info["models"])}')

conn.close()
