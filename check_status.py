# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT 服务商, 在线状态, COUNT(*) FROM 模型配置表 GROUP BY 服务商, 在线状态 ORDER BY 服务商, 在线状态")
print("="*60)
print("【各服务商在线状态】")
print("="*60)
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]} = {r[2]}")

c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态='online'")
print(f"\n在线总数: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态='offline'")
print(f"离线总数: {c.fetchone()[0]}")

conn.close()
