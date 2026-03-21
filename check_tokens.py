# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查模型执行结果表
c.execute("SELECT * FROM 模型执行结果表")
rows = c.fetchall()

print("【模型执行记录】")
for r in rows[:10]:
    print(r)

# 检查是否有专门的token记录表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%token%'")
token_tables = c.fetchall()
print("\n【Token相关表】")
for t in token_tables:
    print(f"  - {t[0]}")
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"    {c.fetchone()[0]}条")

conn.close()
