# -*- coding: utf-8 -*-
import sqlite3
import json

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get column names
cur.execute("PRAGMA table_info(模型配置表)")
cols_info = cur.fetchall()
cols = [c[1] for c in cols_info]

# Get all models
cur.execute("SELECT * FROM 模型配置表")
rows = cur.fetchall()

# Convert to list of dicts
models = []
for row in rows:
    model = {}
    for i, col in enumerate(cols):
        model[col] = row[i]
    models.append(model)

# Save to JSON
output = {
    "更新时间": "2026-03-19 17:38",
    "总模型数": len(models),
    "在线模型": [m for m in models if m.get('在线状态') == 'online']
}

with open(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\model_status.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved {len(models)} models to JSON")
print(f"Online: {len(output['在线模型'])}")

# Count providers
from collections import Counter
providers = Counter()
for m in output['在线模型']:
    providers[m.get('服务商', 'Unknown')] += 1

print('\n=== Provider Stats ===')
for p, c in providers.most_common():
    print(f'{p}: {c}')

conn.close()
