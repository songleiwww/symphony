import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

# 查询模型配置表（最后一个是模型配置表？不，看输出："模型配置表"应该是编码问题，看"模型配置表"中文字符乱码，找到表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%模型%'")
tables = cursor.fetchall()
print("模型相关表:")
for t in tables:
    print(f"  {t[0]}")
    cursor.execute(f"PRAGMA table_info('{t[0]}')")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"  列: {cols}")

# 查询模型配置表中的数据
print("\n模型配置表数据:")
for t in tables:
    table_name = t[0]
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")

conn.close()
