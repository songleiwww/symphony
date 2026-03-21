# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查找所有备份表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%_old%' OR name LIKE '%_auto%' OR name LIKE '%_backup%')")
backups = c.fetchall()

print("="*60)
print("【模型备份表位置】")
print("="*60)
print(f"\n数据库: {db_path}")
print(f"\n备份表数量: {len(backups)}个\n")

for t in backups:
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = c.fetchone()[0]
    print(f"  {t[0]}: {count}条")

conn.close()
