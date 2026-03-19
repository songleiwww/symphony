# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== 调度历史统计 ===\n')

# 最近10条调度
cur.execute('SELECT "调度时间", "使用模型", "服务商", "角色名称" FROM "调度历史表" ORDER BY "调度时间" DESC LIMIT 10')
rows = cur.fetchall()

print('最近调度记录：')
for r in rows:
    print(f'  {r[3]} | {r[2]} | {r[1]}')

print('\n=== 模型使用统计 ===')
cur.execute('SELECT "使用模型", COUNT(*) as cnt FROM "调度历史表" GROUP BY "使用模型" ORDER BY cnt DESC')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}次')

print('\n=== 服务商使用统计 ===')
cur.execute('SELECT "服务商", COUNT(*) as cnt FROM "调度历史表" GROUP BY "服务商" ORDER BY cnt DESC')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}次')

conn.close()
