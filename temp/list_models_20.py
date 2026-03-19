import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Get all models with valid API
c.execute("SELECT id, 模型名称, 模型标识符, 服务商, API地址 FROM 模型配置表 WHERE API地址 IS NOT NULL AND API密钥 IS NOT NULL LIMIT 20")
print('=== 可用模型(1-20) ===')
print('ID | 模型名 | 标识符 | 服务商')
print('-' * 80)
for row in c.fetchall():
    print(f'{row[0]:2} | {row[1][:20]:20} | {row[2][:25]:25} | {row[3]}')

# Get 陆念昭 binding
print('\n=== 陆念昭绑定 ===')
c.execute("SELECT r.id, r.姓名, r.官职, m.模型名称, m.服务商 FROM 官署角色表 r JOIN 模型配置表 m ON r.模型配置表_ID = m.id WHERE r.id = 'role-1'")
for row in c.fetchall():
    print(f'角色: {row[1]}({row[2]})')
    print(f'模型: {row[3]} - {row[4]}')

conn.close()
