import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# Find the model config table
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
model_table = None
for t in tables:
    if '模型' in t and '配置' in t:
        model_table = t
        break

# Get all NVIDIA models
c.execute(f"SELECT * FROM '{model_table}'")
rows = c.fetchall()

# Column indices
IDX_ID = 0
IDX_NAME = 1
IDX_MODEL_ID = 2
IDX_PROVIDER = 4
IDX_API_URL = 5

# Filter NVIDIA models
nvidia_rows = [r for r in rows if r[IDX_PROVIDER] == '英伟达']

print("=== 英伟达模型API配置分析 ===\n")

# Group by API URL
api_groups = {}
for row in nvidia_rows:
    model_id = row[IDX_ID]
    model_name = row[IDX_NAME]
    model_id_raw = row[IDX_MODEL_ID]
    api_url = row[IDX_API_URL]
    
    if api_url not in api_groups:
        api_groups[api_url] = []
    api_groups[api_url].append({'name': model_name, 'id': model_id, 'model_id': model_id_raw})

print(f"发现 {len(api_groups)} 种不同的API配置:\n")

for idx, (api_url, models) in enumerate(api_groups.items(), 1):
    print(f"--- 配置组 {idx} ---")
    print(f"API地址: {api_url}")
    print(f"模型数量: {len(models)}")
    print("模型列表:")
    for m in models:
        print(f"  - {m['id']}: {m['name']} (ID: {m['model_id']})")
    print()

conn.close()
