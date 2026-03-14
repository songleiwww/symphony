# -*- coding: utf-8 -*-
"""
检查官名vs官职 - 使用ID映射
"""
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 使用位置获取数据
cursor.execute('SELECT * FROM 官属角色表')
rows = cursor.fetchall()

# ID到官名的映射（从插入时的数据）
id_to_name = {
    'evolve_001': '沈清弦',
    'evolve_002': '陆念昭', 
    'evolve_003': '苏云渺',
    'evolve_004': '顾清歌',
    'evolve_005': '顾至尊',
    'evolve_006': '沈星衍',
    'evolve_007': '叶轻尘',
    'evolve_008': '林码',
}

# 位置说明:
# 0=id, 1=官名(name), 2=性别, 3=职位(position), 4=职能, 5=专长, 6=模型, 7=服务商, 8=等级

print("=" * 60)
print("官名 vs 官职 对照表")
print("=" * 60)
print()
print(f"{'ID':<15} {'官名':<10} {'官职':<10} {'等级':<5}")
print("-" * 40)

for r in rows[:10]:
    pid = r[0]
    # 官名 (position 1) - 这是姓名
    # 官职 (position 3) - 这是职位
    pname = id_to_name.get(pid, r[1])  # 尝试用已知映射
    pjob = r[3]  # 职位
    plevel = r[8]  # 等级
    
    print(f"{pid:<15} {pname:<10} {pjob:<10} {plevel:<5}")

conn.close()
