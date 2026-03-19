import sqlite3
import time

db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

now = time.time()

# 更新正确的API Key到数据库
c.execute('''
    UPDATE 模型配置表 
    SET API密钥 = '3b922877-3fbe-45d1-a298-53f2231c5224'
    WHERE 服务商 = '火山引擎'
''')

# 重置火山引擎模型健康状态
c.execute('''
    UPDATE 模型健康表 
    SET 健康状态 = '正常', 连续失败 = 0, 更新时间 = ?
    WHERE 模型ID IN (SELECT id FROM 模型配置表 WHERE 服务商 = '火山引擎')
''', (now,))

conn.commit()

# 验证
c.execute('SELECT COUNT(*) FROM 模型健康表 WHERE 健康状态 = ? AND 模型ID IN (SELECT id FROM 模型配置表 WHERE 服务商 = ?)', ('正常', '火山引擎'))
count = c.fetchone()[0]
print(f'火山引擎健康状态已重置: {count}个模型')

# 更新官署角色的模型配置
c.execute("UPDATE 官署角色表 SET 模型配置表_ID = 56 WHERE id = 'role-1'")

conn.commit()
print('OK')

conn.close()
