import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get all NVIDIA models with nvidia/ namespace
c.execute("""
    SELECT id, 模型名称, 模型标识符 
    FROM 模型配置表 
    WHERE 服务商 = '英伟达' 
    AND 模型标识符 LIKE 'nvidia/%'
    ORDER BY id
""")
rows = c.fetchall()

print("=== 英伟达 nvidia/ 命名空间模型 ===\n")
for row in rows:
    print(f"ID {row[0]}: {row[1]} = {row[2]}")

conn.close()
