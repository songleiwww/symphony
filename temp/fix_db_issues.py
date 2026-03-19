# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== 修复数据库问题 ===\n')

# 1. 删除记忆表空值记录
print('1. 删除记忆表空值记录')
cur.execute('DELETE FROM "记忆表" WHERE memory_id IS NULL OR memory_id = ""')
deleted = cur.rowcount
print(f'   已删除: {deleted}条')

# 2. 删除记忆表过期记录
print('\n2. 删除记忆表过期记录')
import time
current_time = time.time()
cur.execute('DELETE FROM "记忆表" WHERE expires_at IS NOT NULL AND expires_at < ?', (current_time,))
deleted2 = cur.rowcount
print(f'   已删除: {deleted2}条')

# 3. 删除记忆表中重复的内核规则
print('\n3. 删除记忆表中重复的内核规则')
cur.execute('DELETE FROM "记忆表" WHERE memory_type = "core_rule"')
deleted3 = cur.rowcount
print(f'   已删除: {deleted3}条')

conn.commit()

# 验证
print('\n=== 验证修复结果 ===')
cur.execute('SELECT COUNT(*) FROM "记忆表"')
count = cur.fetchone()[0]
print(f'记忆表剩余记录: {count}条')

cur.execute('SELECT COUNT(*) FROM "记忆表" WHERE memory_id IS NULL OR memory_id = ""')
null_count = cur.fetchone()[0]
print(f'空值记录: {null_count}条')

conn.close()
print('\n✅ 修复完成！')
