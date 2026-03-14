# -*- coding: utf-8 -*-
# 获取数据库表结构
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get table schema
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='官属角色表'")
result = c.fetchone()
if result:
    print("CREATE TABLE statement:")
    print(result[0])

conn.close()
