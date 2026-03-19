# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== Debug问题检查 ===\n')

# 1. 官署角色表
print('1. 官署角色表')
cur.execute('SELECT COUNT(*) FROM "官署角色表"')
print(f'   总记录: {cur.fetchone()[0]}')

# 2. 未绑定模型的官署角色
cur.execute('SELECT COUNT(*) FROM "官署角色表" WHERE "模型配置ID" IS NULL OR "模型配置ID" = ""')
print(f'   未绑定模型: {cur.fetchone()[0]}')

# 3. 模型配置表
print('\n2. 模型配置表')
cur.execute('SELECT COUNT(*) FROM "模型配置表"')
print(f'   总记录: {cur.fetchone()[0]}')

# 4. 序境系统总则
print('\n3. 序境系统总则')
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
print(f'   总规则: {cur.fetchone()[0]}')

# 5. 记忆表
print('\n4. 记忆表')
cur.execute('SELECT COUNT(*) FROM "记忆表"')
print(f'   总记录: {cur.fetchone()[0]}')

# 6. 调度历史表
print('\n5. 调度历史表')
cur.execute('SELECT COUNT(*) FROM "调度历史表"')
print(f'   总记录: {cur.fetchone()[0]}')

# 7. 查找可能的重复记录
print('\n6. 检查重复')
cur.execute('SELECT "规则名称", COUNT(*) FROM "序境系统总则" GROUP BY "规则名称" HAVING COUNT(*) > 1')
dups = cur.fetchall()
print(f'   规则重复: {len(dups)}')

conn.close()
