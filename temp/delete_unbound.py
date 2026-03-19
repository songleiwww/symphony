# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find unbound roles
cur.execute('SELECT id, 姓名, 官职 FROM "官署角色表" WHERE 模型配置表_ID IS NULL')
unbound = cur.fetchall()

print(f'=== Unbound Roles: {len(unbound)} ===')
for r in unbound:
    print(f'  {r[0]}: {r[1]} - {r[2]}')

# Delete unbound roles
if unbound:
    ids = [r[0] for r in unbound]
    placeholders = ','.join(['?'] * len(ids))
    cur.execute(f'DELETE FROM "官署角色表" WHERE id IN ({placeholders})', ids)
    deleted = cur.rowcount
    conn.commit()
    print(f'\n=== Deleted {deleted} unbound roles ===')

# Verify
cur.execute('SELECT COUNT(*) FROM "官署角色表"')
total = cur.fetchone()[0]
print(f'官署角色表 now has {total} roles')

# Also check model binding
cur.execute('SELECT COUNT(*) FROM "官署角色表" WHERE 模型配置表_ID IS NOT NULL')
bound = cur.fetchone()[0]
print(f'Bound to models: {bound}')

conn.close()
