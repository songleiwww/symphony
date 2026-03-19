import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("所有表:")
for t in tables:
    print(f"  {t[0]}")

# 查询模型配置表
print("\n查询模型配置表:")
cursor.execute("SELECT * FROM `模型配置表`")
rows = cursor.fetchall()
print(f"共 {len(rows)} 行")
for row in rows:
    print(f"  {row}")

# 获取表结构
print("\n模型配置表结构:")
cursor.execute("PRAGMA table_info(`模型配置表`)")
cols = cursor.fetchall()
for c in cols:
    print(f"  {c[1]}: {c[2]}")

conn.close()
