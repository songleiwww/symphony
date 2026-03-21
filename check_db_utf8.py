
import sqlite3
import json
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

result = {
    "tables": {}
}

print("=== 数据库中的所有表 ===\n")
for table in tables:
    table_name = table[0]
    print(f"表名: {table_name}")
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    column_info = []
    print("字段:")
    for col in columns:
        col_dict = {
            "name": col[1],
            "type": col[2]
        }
        column_info.append(col_dict)
        print(f"  - {col[1]} ({col[2]})")
    
    # 获取行数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"记录数: {count}\n")
    
    # 显示前几条数据(如果有)
    sample_data = []
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print("前3条数据:")
        for row in rows:
            # 转换为可JSON序列化的格式
            row_data = []
            for item in row:
                if isinstance(item, bytes):
                    row_data.append("[BINARY]")
                else:
                    row_data.append(item)
            sample_data.append(row_data)
            print(f"  {row_data}")
    print("-" * 50)
    
    result["tables"][table_name] = {
        "columns": column_info,
        "count": count,
        "sample_data": sample_data
    }

conn.close()

# 保存结果到JSON文件
output_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\db_structure.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n数据库结构已保存到: {output_path}")

