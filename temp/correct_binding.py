import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=' * 70)
print('正确绑定关系 - 从官署表获取名称')
print('=' * 70)

# 正确的三表关联查询
print('\n【正确绑定样例】')
print('-' * 50)
c.execute('''
    SELECT 
        r.姓名,
        r.官职,
        o.名称 as 官署名称,
        r.所属官署 as 官署ID,
        m.模型名称,
        m.服务商 as 引擎
    FROM 官署角色表 r
    JOIN 官署表 o ON r.所属官署 = o.id
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.状态 = "正常"
    LIMIT 20
''')

print('角色      官职        所属官署    官署ID       模型                     引擎')
print('-' * 80)
for row in c.fetchall():
    print(f'{row[0]:<10} {row[1]:<12} {row[2]:<10} {row[3]:<12} {row[4][:22]:<25} {row[5]:<10}')

# 按官署统计
print('\n【按官署分组统计】')
print('-' * 50)
c.execute('''
    SELECT 
        o.名称 as 官署名称,
        COUNT(r.id) as 人数
    FROM 官署角色表 r
    JOIN 官署表 o ON r.所属官署 = o.id
    GROUP BY o.名称
    ORDER BY 人数 DESC
''')

for row in c.fetchall():
    print(f'  {row[0]}: {row[1]}人')

conn.close()
