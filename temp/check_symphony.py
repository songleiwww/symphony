# Check Symphony models
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get all providers with readable names
cur.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
print('=== Symphony Models by Provider ===')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1]} models')

# Get first model from each provider
print('\n=== Sample Models ===')
cur.execute('SELECT 模型名称, 模型标识符, 服务商 FROM 模型配置表 LIMIT 5')
for row in cur.fetchall():
    print(f'{row[2]}: {row[0]} ({row[1]})')

conn.close()
