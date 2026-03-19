# Compare Symphony models with working host models
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get all Symphony models
cur.execute('SELECT id, 模型名称, 模型标识符, 服务商 FROM 模型配置表')
symphony_models = {}
for row in cur.fetchall():
    key = row[2]  # model identifier
    symphony_models[key] = {'name': row[1], 'provider': row[3]}

print('=== Symphony Models ===')
for k, v in list(symphony_models.items())[:10]:
    print(f'{v["provider"]}: {k}')

# Check if host models exist in Symphony
host_models = ['ark-code-latest', 'doubao-seed-2.0-code', 'glm-4.7', 'kimi-k2.5', 'deepseek-v3.2']
print('\n=== Checking Host Models in Symphony ===')
for m in host_models:
    if m in symphony_models:
        print(f'✅ {m} exists in Symphony')
    else:
        print(f'❌ {m} NOT in Symphony')

conn.close()
