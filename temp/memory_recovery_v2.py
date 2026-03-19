import sqlite3
import time
from datetime import datetime

db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=== 记忆接续 ===')

# 第1步: 加载核心规则
print('\n第1步: 加载核心规则')
c.execute("SELECT 规则名称, 规则内容 FROM 内核规则表 WHERE 状态='启用' ORDER BY 优先级 DESC")
rules = c.fetchall()

for name, content in rules:
    now = time.time()
    c.execute('''
        INSERT INTO 记忆表 (memory_id, content, memory_type, importance, source, created_at, last_accessed, access_count)
        VALUES (?, ?, "core_rule", 1.0, "kernel_rules", ?, ?, 0)
    ''', (f'rule_{int(now)}', f'{name}: {content[:150]}', now, now))
    print(f'  ✅ {name}')

conn.commit()

# 第2步: 三大表信息
print('\n第2步: 三大表信息')
c.execute('SELECT id, 名称 FROM 官署表')
offices = c.fetchall()
print(f'  官署: {len(offices)}个')
for o in offices:
    print(f'    {o[1]}')

# 第3步: 核心角色绑定
print('\n第3步: 核心角色绑定')
c.execute('''
    SELECT r.姓名, r.官职, m.模型名称, m.服务商
    FROM 官署角色表 r
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.id IN ("role-1", "role-10", "role-11")
''')
for row in c.fetchall():
    print(f'  ✅ {row[0]}({row[1]}) -> {row[2]}({row[3]})')

# 第4步: 测试调度
print('\n第4步: 调度测试')
c.execute('''
    SELECT r.姓名, r.官职, o.名称, m.模型名称, m.服务商
    FROM 官署角色表 r
    JOIN 官署表 o ON r.所属官署 = o.id
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.id = "role-1"
''')
row = c.fetchone()
print(f'  角色: {row[0]}')
print(f'  官职: {row[1]}')
print(f'  官署: {row[2]}')
print(f'  模型: {row[3]}')
print(f'  引擎: {row[4]}')

conn.commit()
conn.close()

print('\n' + '='*50)
print('✅ 记忆接续完成!')
print('='*50)
