# Check Zhixue models
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get column names
cur.execute('PRAGMA table_info(模型配置表)')
cols = [c[1] for c in cur.fetchall()]

# Find index of provider column
provider_idx = None
status_idx = None
for i, c in enumerate(cols):
    if '服务商' in c:
        provider_idx = i
    if '状态' in c:
        status_idx = i

print(f'Provider column index: {provider_idx}')
print(f'Status column index: {status_idx}')

# Get Zhixue models
cur.execute('SELECT * FROM 模型配置表')
all_rows = cur.fetchall()

zhixue_count = 0
zhixue_online = 0
for row in all_rows:
    provider = row[provider_idx] if provider_idx else ''
    status = row[status_idx] if status_idx else ''
    if '智谱' in provider:
        zhixue_count += 1
        if 'online' in status:
            zhixue_online += 1
        print(f'  {status} | {row[1]} ({provider})')

print(f'\n=== Summary ===')
print(f'Total Zhixue models: {zhixue_count}')
print(f'Zhixue online: {zhixue_online}')

conn.close()
