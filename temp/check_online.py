# Check online models
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get models by status
print('=== Models by Status ===')
cur.execute('SELECT 运行状态, COUNT(*) FROM 模型配置表 GROUP BY 运行状态')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1]}')

# Get online models
print('\n=== Online Models ===')
cur.execute('SELECT id, 模型名称, 模型标识符, 服务商 FROM 模型配置表 WHERE 运行状态 = "online"')
for row in cur.fetchall():
    print(f'{row[3]}: {row[1]} ({row[2]})')

# Get Zhixue models
print('\n=== Zhixue (智谱) Models ===')
cur.execute('SELECT id, 模型名称, 模型标识符, 服务商, 运行状态 FROM 模型配置表 WHERE 服务商 LIKE "%智谱%"')
for row in cur.fetchall():
    print(f'{row[4]} | {row[1]} ({row[2]})')

conn.close()
