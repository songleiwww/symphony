# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取所有表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite%'")
tables = [t[0] for t in c.fetchall()]

for table in tables:
    c.execute(f"SELECT COUNT(*) FROM \"{table}\"")
    count = c.fetchone()[0]
    print(f"{table}: {count}")

# 特别检查模型配置表和官署角色表
print("\n=== 关键表 ===")
for table in tables:
    if '模型' in table and '配置' in table:
        c.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        print(f"模型配置表: {c.fetchone()[0]}")
    if '官署' in table and '角色' in table:
        c.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        print(f"官署角色表: {c.fetchone()[0]}")
