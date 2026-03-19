# Check volcano models in Symphony
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get all models with status
cur.execute('SELECT 模型标识符, 服务商, 运行状态 FROM 模型配置表')
print('=== All Models ===')
for row in cur.fetchall():
    print(f'{row[1]} | {row[0]} | {row[2]}')

conn.close()
