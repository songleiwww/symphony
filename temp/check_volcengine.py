import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 列出所有火山引擎模型
c.execute('SELECT id, 模型名称, 服务商, API密钥, 是否在线 FROM 模型配置表 WHERE 服务商=?', ('火山引擎',))
print('=== 火山引擎模型 ===')
rows = c.fetchall()
for row in rows:
    key = row[3] if row[3] else '无'
    print(f'ID:{row[0]} {row[1]}')
    print(f'  Key:{key[:25]}...' if len(key) > 25 else f'  Key:{key}')
    print(f'  状态:{row[4]}')
    print()

conn.close()
