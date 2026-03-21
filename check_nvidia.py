# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查英伟达模型字段
c.execute("SELECT 模型名称, 模型标识符, 服务商, API地址, 在线状态 FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 10")

print("="*80)
print("【英伟达模型字段检查】")
print("="*80)

for r in c.fetchall():
    print(f"\n模型名称: {r[0]}")
    print(f"  模型标识符: {r[1]}")
    print(f"  服务商: {r[2]}")
    print(f"  API地址: {r[3]}")
    print(f"  在线状态: {r[4]}")

# 检查总数
c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 服务商='英伟达'")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 服务商='英伟达' AND 在线状态='online'")
online = c.fetchone()[0]

print("\n" + "="*80)
print(f"英伟达总计: {total}个, 在线: {online}个")
print("="*80)

conn.close()
