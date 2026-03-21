# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【序境系统配置陆念昭模型】")
print("="*60)

# 列出表
print("\n【表列表】")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for t in tables:
    print(f"  - {t[0]}")

# 查看模型配置表结构
print("\n【模型配置表字段】")
c.execute("PRAGMA table_info(模型配置表)")
for col in c.fetchall():
    print(f"  {col}")

# 查看官署角色表
print("\n【官署角色表字段】")
c.execute("PRAGMA table_info(官署角色表)")
for col in c.fetchall():
    print(f"  {col}")

conn.close()
