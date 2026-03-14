# -*- coding: utf-8 -*-
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT 模型名称, url FROM 模型配置表 WHERE 服务商="火山引擎" LIMIT 3')
print("火山引擎模型配置:")
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}')
conn.close()
