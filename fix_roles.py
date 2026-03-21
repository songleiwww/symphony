# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 删除多余的最后一个角色
c.execute("DELETE FROM 官署角色表 WHERE id = 'role-425'")
conn.commit()
print('已删除 role-425')

# 验证
c.execute('SELECT COUNT(*) FROM 官署角色表')
role_count = c.fetchone()[0]
print(f'官署角色表: {role_count}个')

c.execute('SELECT COUNT(*) FROM 模型配置表')
model_count = c.fetchone()[0]
print(f'模型配置表: {model_count}个')

print(f'\n✅ 对齐完成！差异: {abs(role_count - model_count)}')
