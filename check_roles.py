# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取官署角色表结构
c.execute("PRAGMA table_info(官署角色表)")
print("官署角色表字段:")
for col in c.fetchall():
    print(f"  {col[1]} ({col[2]})")

# 查看前5条和后5条
c.execute("SELECT * FROM 官署角色表 ORDER BY id LIMIT 5")
print("\n前5条:")
for row in c.fetchall():
    print(f"  {row}")

c.execute("SELECT * FROM 官署角色表 ORDER BY id DESC LIMIT 5")
print("\n后5条:")
for row in c.fetchall():
    print(f"  {row}")

# 获取官署分布
c.execute("SELECT 官署, COUNT(*) as cnt FROM 官署角色表 GROUP BY 官署 ORDER BY cnt DESC")
print("\n官署分布:")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}个")
