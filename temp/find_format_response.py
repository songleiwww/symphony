import os
import sqlite3

# 搜索formatResponseUsageLine函数
search_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony'
target_func = 'formatResponseUsageLine'
found = []

for root, dirs, files in os.walk(search_path):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if target_func in content:
                        found.append(filepath)
                        print(f"找到 {target_func} 在: {filepath}")
            except Exception as e:
                continue

print(f"\n共找到 {len(found)} 个文件包含该函数")

# 查看模型使用统计表
print("\n查询模型使用统计表 (模型使用统计):")
db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%模型使用%'")
tables = cursor.fetchall()
for t in tables:
    print(f"\n表: {t[0]}")
    cursor.execute(f"PRAGMA table_info(`{t[0]}`)")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"字段: {cols}")
    
    # 查询ark-code-latest相关记录
    cursor.execute(f"SELECT * FROM `{t[0]}` WHERE 模型ID = 'ark-code-latest'")
    rows = cursor.fetchall()
    print(f"ark-code-latest 记录数: {len(rows)}")
    for row in rows:
        print(f"  {row}")

conn.close()
