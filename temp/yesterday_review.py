import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=== 2026-03-16 成功任务回顾 ===')

# Get all dispatch history from yesterday
c.execute("""
    SELECT task_id, role_id, model_name, score, success, timestamp 
    FROM 调度历史表 
    WHERE timestamp LIKE '2026-03-16%'
    ORDER BY id
""")
rows = c.fetchall()

print(f'总调度次数: {len(rows)}')
success_count = sum(1 for r in rows if r[4] == 1)
print(f'成功次数: {success_count}')

print('\n--- 详细记录 ---')
for row in rows:
    task_id, role_id, model_name, score, success, ts = row
    status = 'SUCCESS' if success else 'FAIL'
    print(f'{status} | {ts[11:19]} | {role_id} | {model_name[:30]}')

# Get role names
print('\n--- 角色说明 ---')
c.execute("SELECT id, 姓名, 官职 FROM 官署角色表 WHERE id IN ('role-1', 'role-10', 'role-11')")
for row in c.fetchall():
    print(f'{row[0]}: {row[1]}({row[2]})')

conn.close()
