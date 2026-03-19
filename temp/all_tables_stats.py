import sqlite3
from datetime import datetime, timedelta

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check all relevant tables
tables_to_check = ['任务表', '操作日志表', '故障记录表', 'self_evolution']

print("=== 各表数据统计 ===\n")

for table in tables_to_check:
    try:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        
        # Get column names
        c.execute(f"PRAGMA table_info({table})")
        cols = c.fetchall()
        col_names = [c[1] for c in cols]
        
        print(f"【{table}】- {count}条记录")
        print(f"  字段: {', '.join(col_names[:5])}")
        
        # Get recent records
        if count > 0:
            c.execute(f"SELECT * FROM {table} ORDER BY 1 DESC LIMIT 3")
            rows = c.fetchall()
            for row in rows[:2]:
                print(f"    {row[:3]}...")
        print()
    except Exception as e:
        print(f"【{table}】- 错误: {e}\n")

# Check 官署角色表
print("=== 官署角色表 ===")
c.execute("SELECT 官署, 角色名称, 模型 FROM 官署角色表 ORDER BY 官署")
roles = c.fetchall()
current_office = None
for r in roles:
    if r[0] != current_office:
        current_office = r[0]
        print(f"\n【{r[0]}】")
    print(f"  - {r[1]}: {r[2]}")

conn.close()
