# Check model validity in Symphony
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get all models with their status
print('=== All Models in Symphony ===')
cur.execute('SELECT 模型名称, 模型标识符, 服务商, 运行状态 FROM 模型配置表')
for row in cur.fetchall():
    print(f'{row[3]} | {row[2]} | {row[0]} ({row[1]})')

print('\n=== Models by Status ===')
cur.execute('SELECT 运行状态, COUNT(*) FROM 模型配置表 GROUP BY 运行状态')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1]} models')

print('\n=== Zhixue Models (智谱) ===')
cur.execute('SELECT 模型名称, 模型标识符, 运行状态 FROM 模型配置表 WHERE 服务商 LIKE "%智谱%"')
for row in cur.fetchall():
    print(f'{row[2]} | {row[0]} ({row[1]})')

conn.close()
