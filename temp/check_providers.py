# Check all providers
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get all providers
cur.execute('SELECT DISTINCT 服务商 FROM 模型配置表')
providers = cur.fetchall()
print('All providers:')
for p in providers:
    print(f'  - {p[0]}')

# Get model count by provider
print('\n---')
cur.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
counts = cur.fetchall()
for c in counts:
    print(f'{c[0]}: {c[1]} models')

conn.close()
