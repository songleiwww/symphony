# -*- coding: utf-8 -*-
# 使用正确的编码连接数据库
import sqlite3
import time

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# 使用 check_same_thread=False 和 uri=True
conn = sqlite3.connect(db_path, isolation_level=None)
conn.text_factory = str
cursor = conn.cursor()

# 先设置编码
cursor.execute("PRAGMA encoding='UTF-8'")

# 查看表结构
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='官属角色表'")
result = cursor.fetchone()
if result:
    print("Schema:")
    print(result[0])

# 尝试插入测试
now = time.strftime('%Y-%m-%d %H:%M:%S')

# 测试插入 - 使用原始列名
test_data = ('test_001', '测试官名', '男', '测试职', '测试职能', '测试专长', 'glm-4.7', '火山引擎', 1, '正常', now, now)

# 尝试获取列名
cursor.execute("PRAGMA table_info(官属角色表)")
cols_info = cursor.fetchall()
print("\nColumn info:")
for col in cols_info:
    print(f"  {col[1]}")

conn.close()
