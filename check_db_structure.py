
import sqlite3
import json

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== 数据库中的所有表 ===\n")
for table in tables:
    table_name = table[0]
    print(f"表名: {table_name}")
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("字段:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 获取行数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"记录数: {count}\n")
    
    # 显示前几条数据(如果有)
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print("前3条数据:")
        for row in rows:
            print(f"  {row}")
    print("-" * 50)

conn.close()

