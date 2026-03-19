import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=== 检查 fine_grain_templates 表 ===')
print()

# 检查表是否存在
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fine_grain_templates'")
if c.fetchone():
    print('表存在')
    
    # 检查字段
    print('\n字段结构:')
    c.execute('PRAGMA table_info(fine_grain_templates)')
    for row in c.fetchall():
        print(f'  {row[1]}: {row[2]}')
    
    # 检查数据
    print('\n数据量:')
    c.execute('SELECT COUNT(*) FROM fine_grain_templates')
    print(f'  {c.fetchone()[0]}条')
    
    # 查看数据样例
    print('\n数据样例:')
    c.execute('SELECT * FROM fine_grain_templates LIMIT 3')
    for row in c.fetchall():
        print(f'  {row}')
else:
    print('表不存在')

# 检查其他表
print('\n=== 所有表 ===')
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in c.fetchall()]
for t in tables:
    print(f'  {t}')

conn.close()
