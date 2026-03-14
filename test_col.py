# -*- coding: utf-8 -*-
import sqlite3
import time

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 先查看当前数据
cursor.execute('SELECT id, 模型名称, 模型服务商 FROM 官属角色表 LIMIT 3')
print('当前数据:')
for row in cursor.fetchall():
    print(f'  {row}')

# 用位置来插入: id=0, 官名=1, 性别=2, 职=3, 职能=4, 专长=5, 模型名称=6, 模型服务商=7, 角色等级=8
now = time.strftime('%Y-%m-%d %H:%M:%S')

officials = [
    ('shaofu_001', '少府监', '男', '监', '总领百工伎巧', '统筹管理', 'glm-4.7', '火山引擎', 1),
    ('shaofu_002', '少府少监', '男', '少监', '辅佐监务', '监督协调', 'glm-4.7', '火山引擎', 2),
]

# 使用UPDATE或INSERT
for o in officials:
    # 先尝试更新
    cursor.execute('UPDATE 官属角色表 SET 职=? WHERE id=?', (o[3], o[0]))
    if cursor.rowcount == 0:
        # 如果没有更新，则插入
        cursor.execute('''
            INSERT INTO 官属角色表 (id, 官名, 性别, 职, 职能, 专长, 模型名称, 模型服务商, 角色等级, 状态, 创建时间, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*o, '正常', now, now))

conn.commit()

# 验证
cursor.execute('SELECT id, 官名, 职, 模型名称 FROM 官属角色表')
print('\n更新后:')
for row in cursor.fetchall():
    print(f'  {row}')

conn.close()
