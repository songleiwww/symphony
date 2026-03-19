import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get model usage statistics
c.execute("""
    SELECT 服务商, COUNT(*) as 模型数
    FROM 模型配置表
    GROUP BY 服务商
    ORDER BY 模型数 DESC
""")
providers = c.fetchall()

print("=== 模型服务商分布 ===\n")
for p in providers:
    print(f"{p[0]}: {p[1]}个模型")

print("\n=== 调度统计 ===")
# Check if there's a dispatch table
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%dispatch%'")
tables = c.fetchall()
print(f"调度相关表: {tables}")

conn.close()
