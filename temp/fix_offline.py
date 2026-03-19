# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 将英伟达和智谱模型标记为需要修复
# 先查看当前状态
print("=== Current Online Models ===\n")

c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态="online" GROUP BY 服务商')
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n=== Updating NVIDIA models to offline (need fix) ===\n")

# 更新英伟达模型状态
c.execute('UPDATE 模型配置表 SET 在线状态="offline" WHERE 服务商="英伟达"')
print(f"Updated {c.rowcount} NVIDIA models")

conn.commit()

# 查看更新后
print("\n=== After Update ===\n")
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态="online" GROUP BY 服务商')
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
print("\nDone!")
