# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查重复的模型标识符
print("="*60)
print("【检查重复模型标识符】")
print("="*60)

c.execute("""
    SELECT 模型标识符, COUNT(*) as cnt, GROUP_CONCAT(模型名称) as names
    FROM 模型配置表 
    WHERE 模型标识符 IS NOT NULL AND 模型标识符 != ''
    GROUP BY 模型标识符 
    HAVING cnt > 1
    ORDER BY cnt DESC
""")

duplicates = c.fetchall()
print(f"\n重复的模型标识符: {len(duplicates)}个")
for d in duplicates:
    print(f"  {d[0]}: {d[1]}个")
    print(f"    {d[2]}")

# 总计
c.execute("SELECT COUNT(*) FROM 模型配置表")
total = c.fetchone()[0]
print(f"\n数据库总模型数: {total}")
print(f"调度器加载: 294个")
print(f"差异: {total - 294}个")

conn.close()
