# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Update all models to online
cur.execute('UPDATE "模型配置表" SET "状态" = "online"')
conn.commit()

print(f'Updated {cur.rowcount} models to online')

# Verify
cur.execute('SELECT COUNT(*) FROM "模型配置表" WHERE "状态" = "online"')
count = cur.fetchone()[0]
print(f'Online models: {count}')

conn.close()
