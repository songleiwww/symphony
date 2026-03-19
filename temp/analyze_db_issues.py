# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== 数据库问题分析 ===\n')

# 1. 记忆表空值检查
print('1. 记忆表空值检查')
cur.execute('SELECT * FROM "记忆表" WHERE memory_id IS NULL OR memory_id = ""')
null_rows = cur.fetchall()
print(f'   空值记录: {len(null_rows)}条')
if null_rows:
    for r in null_rows[:3]:
        print(f'   - {r}')

# 2. 记忆表过期检查
print('\n2. 记忆表过期检查')
cur.execute('SELECT COUNT(*) FROM "记忆表" WHERE expires_at IS NOT NULL AND expires_at < 1773930000')
expired = cur.fetchone()[0]
print(f'   过期记录: {expired}条')

# 3. 调度历史分析
print('\n3. 调度历史分析')
cur.execute('SELECT model_name, COUNT(*) as cnt FROM "调度历史表" GROUP BY model_name ORDER BY cnt DESC LIMIT 5')
model_usage = cur.fetchall()
print(f'   模型使用统计:')
for m in model_usage:
    print(f'   - {m[0]}: {m[1]}次')

# 4. 序境系统总则规则检查
print('\n4. 序境系统总则规则检查')
cur.execute('SELECT * FROM "序境系统总则" WHERE id >= 65')
new_rules = cur.fetchall()
print(f'   新增规则(65+): {len(new_rules)}条')
for r in new_rules:
    print(f'   - {r[0]}: {r[1]}')

# 5. 模型配置表在线状态
print('\n5. 模型配置表在线状态')
cur.execute('SELECT 状态, COUNT(*) FROM "模型配置表" GROUP BY 状态')
status_counts = cur.fetchall()
for s in status_counts:
    print(f'   - {s[0]}: {s[1]}个')

# 6. 官署角色绑定检查
print('\n6. 官署角色绑定检查')
cur.execute('SELECT COUNT(*) FROM "官署角色表" WHERE "模型配置ID" IS NULL OR "模型配置ID" = ""')
unbound = cur.fetchone()[0]
print(f'   未绑定模型的官署角色: {unbound}个')

# 7. 调度历史角色分布
print('\n7. 调度历史角色分布')
cur.execute('SELECT role_id, COUNT(*) FROM "调度历史表" GROUP BY role_id ORDER BY COUNT(*) DESC LIMIT 5')
role_usage = cur.fetchall()
for r in role_usage:
    print(f'   - {r[0]}: {r[1]}次')

conn.close()
