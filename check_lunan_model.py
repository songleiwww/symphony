# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【查找陆念昭模型配置】")
print("="*50)

# 查找陆念昭配置的模型
c.execute("SELECT 模型名称, 模型标识符, API地址, 服务商 FROM 模型配置表 WHERE 备注 LIKE ? OR 模型标识符 LIKE ?", 
          ("%陆念昭%", "%ark-code%"))
results = c.fetchall()

print("\n陆念昭可用模型:")
for r in results:
    print(f"  - {r[0]} ({r[3]})")
    print(f"    标识符: {r[1]}")
    print(f"    API: {r[2][:60]}...")
    print()

# 查找官署角色表中陆念昭绑定
c.execute("SELECT 角色名称, 模型标识符, 服务商 FROM 官署角色表 WHERE 角色名称 LIKE '%陆念昭%' OR 角色名称 LIKE '%少府监%'")
roles = c.fetchall()

print("\n官署角色绑定:")
for r in roles:
    print(f"  - {r[0]}: {r[1]} ({r[2]})")

conn.close()
