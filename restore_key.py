# -*- coding: utf-8 -*-
import sqlite3

# 恢复火山引擎Key
KEY = "3b922877-3fbe-45d1-a298-53f2231c5224"

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 恢复Key
cursor.execute('UPDATE 模型配置表 SET key = ? WHERE 服务商 = "火山引擎"', (KEY,))
print(f'火山引擎Key已恢复: {cursor.rowcount} 行')

conn.commit()
conn.close()
