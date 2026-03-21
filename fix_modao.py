# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 把魔搭所有模型设为offline（API Key无效）
c.execute("UPDATE 模型配置表 SET 在线状态='offline' WHERE 服务商='魔搭'")
print(f"已更新魔搭模型状态为offline")

# 验证
c.execute("SELECT 服务商, 在线状态, COUNT(*) FROM 模型配置表 WHERE 服务商='魔搭' GROUP BY 服务商, 在线状态")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]} = {r[2]}")

c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态='online'")
print(f"\n在线总数: {c.fetchone()[0]}")

conn.commit()
conn.close()
print("【完成】")
