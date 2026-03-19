# Check model config
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT id, 模型名称, 模型标识符, 服务商 FROM 模型配置表 WHERE 服务商 LIKE "%MiniMax%" OR 服务商 LIKE "%mini%" LIMIT 5')
rows = cur.fetchall()
print('MiniMax models:')
for r in rows:
    print(r)

# Check default model
print('\n---')
cur.execute('SELECT 规则内容 FROM 系统规则表 WHERE 规则名称 LIKE "%默认%" OR 规则名称 LIKE "%主模型%"')
print(cur.fetchall())
conn.close()
