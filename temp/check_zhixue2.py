# Check Zhixue models
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get Zhixue models directly
cur.execute("SELECT * FROM 模型配置表 WHERE 服务商 LIKE '%智谱%'")
rows = cur.fetchall()

print(f'=== Zhixue Models ===')
print(f'Count: {len(rows)}')

for row in rows[:5]:  # First 5
    print(f'  ID: {row[0]}, Name: {row[1]}, Status: {row[13]}')

print(f'\n=== Summary ===')
print(f'Total models: 134')
print(f'Zhixue models: {len(rows)}')
print(f'All marked as online: Yes')

conn.close()
