# -*- coding: utf-8 -*-
import sqlite3
import time

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

now = time.strftime('%Y-%m-%d %H:%M:%S')

# 修复陆念昭的数据 - 使用正确的字段顺序
# 位置: 0=id, 1=官名, 2=性别, 3=职位, 4=职能, 5=专长, 6=模型, 7=服务商, 8=等级
cursor.execute('''
    UPDATE 官属角色表 
    SET 官名=?, 职位=?, 职能=?, 专长=?, 更新时间=?
    WHERE id=?
''', ('陆念昭', '少府监', '统筹调度、任务分发、文档归档', '史官/记录官', now, 'evolve_002'))

conn.commit()

# 验证
cursor.execute('SELECT * FROM 官属角色表 WHERE id="evolve_002"')
r = cursor.fetchone()
print('Updated 陆念昭:')
print('  ID:', r[0])
print('  官名:', r[1])
print('  职位:', r[3])
print('  职能:', r[4])
print('  专长:', r[5])
print('  模型:', r[6])
print('  服务商:', r[7])
print('  等级:', r[8])

conn.close()
print('\nDone!')
