
import sqlite3
import json
from pathlib import Path
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 数据库路径
db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("Xujing System - Su Yunmiao Phase 1")
print("=" * 80)

# 1. 查看所有表
print("\nDatabase Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# 2. 查看模型配置表结构
print("\nModel Config Table Structure:")
try:
    cursor.execute("PRAGMA table_info(模型配置表);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"  Error: {e}")

# 3. 查询模型配置表数据
print("\nModel Config Table Data (first 20):")
model_config_data = []
try:
    cursor.execute("SELECT * FROM 模型配置表;")
    rows = cursor.fetchall()
    # 获取列名
    cursor.execute("PRAGMA table_info(模型配置表);")
    col_names = [col[1] for col in cursor.fetchall()]
    
    for row in rows:
        row_dict = dict(zip(col_names, row))
        model_config_data.append(row_dict)
    
    for i, row_dict in enumerate(model_config_data[:20]):
        print(f"\n  [{i+1}]")
        for k, v in row_dict.items():
            print(f"    {k}: {v}")
            
    print(f"\n  ... total {len(model_config_data)} models")
except Exception as e:
    print(f"  Error: {e}")

# 4. 统计各服务商模型状态
print("\nModel Status Statistics:")
stats_result = {}
try:
    cursor.execute("""
        SELECT 服务商, 在线状态, COUNT(*) as 数量 
        FROM 模型配置表 
        GROUP BY 服务商, 在线状态
        ORDER BY 服务商, 在线状态;
    """)
    stats = cursor.fetchall()
    for stat in stats:
        provider = stat[0]
        status = stat[1]
        count = stat[2]
        if provider not in stats_result:
            stats_result[provider] = {}
        stats_result[provider][status] = count
        print(f"  Provider: {provider}, Status: {status}, Count: {count}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
print("\n" + "=" * 80)

# 保存结果到JSON
output_data = {
    "已完成": [],
    "进行中": ["任务1：统一抽象层设计", "任务2：模型治理模块"],
    "API配置": "数据库: symphony.db",
    "模型数据": model_config_data,
    "统计数据": stats_result
}

output_file = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\su_yunmiao_phase1_result.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\nResults saved to: {output_file}")

