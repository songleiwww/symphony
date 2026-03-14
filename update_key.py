# -*- coding: utf-8 -*-
import sqlite3

# 从记忆中找到的火山引擎Key
# 3b922877-3fbe-45d1-a298-53f2231c52e7
KEY = "3b922877-3fbe-45d1-a298-53f2231c52e7"

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看当前的key
print("更新前的模型配置:")
cursor.execute('SELECT 模型名称, key FROM 模型配置表 WHERE 模型名称 LIKE "%ark%" OR 模型名称 LIKE "%Doubao%"')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print()

# 更新key (模糊匹配)
cursor.execute('UPDATE 模型配置表 SET key = ? WHERE key LIKE "%3b922877%" OR key LIKE "%3b922877%"', (KEY,))
print(f'已更新 {cursor.rowcount} 行')

# 也更新那些key为空或无效的
cursor.execute('UPDATE 模型配置表 SET key = ? WHERE 服务商 = "火山引擎" AND (key IS NULL OR key = "")', (KEY,))
print(f'火山引擎更新: {cursor.rowcount} 行')

conn.commit()

# 验证更新
print("\n更新后的模型配置:")
cursor.execute('SELECT 模型名称, key FROM 模型配置表 WHERE 模型名称 LIKE "%ark%" OR 模型名称 LIKE "%Doubao%" LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1][:30]}...' if row[1] and len(row[1]) > 30 else f'  {row[0]}: {row[1]}')

conn.close()
