# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# 读取MEMORY.md中的规则
with open(r'C:\Users\Administrator\.openclaw\workspace\MEMORY.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取规则编号和规则名称
import re
rules = []
# 匹配 ### 6.1 xxx 或 ### 8.1 xxx 格式
for match in re.finditer(r'### (6\.1|8\.1) ([^\n]+)', content):
    rule_num = match.group(1)
    rule_name = match.group(2).strip()
    rules.append((rule_num, rule_name))

print("=== 需同步的新规则 ===\n")
for r in rules:
    print(f"{r[0]}: {r[1]}")

# 同步到数据库
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("\n=== 同步到数据库 ===\n")

# 检查是否已存在
for rule_num, rule_name in rules:
    c.execute("SELECT id FROM 序境系统总则 WHERE 规则编号=?", (rule_num,))
    exists = c.fetchone()
    
    if exists:
        # 更新
        c.execute("""
            UPDATE 序境系统总则 
            SET 规则说明=?, 更新时间=datetime('now')
            WHERE 规则编号=?
        """, (rule_name, rule_num))
        print(f"Updated: {rule_num} - {rule_name}")
    else:
        # 插入
        c.execute("""
            INSERT INTO 序境系统总则 (规则编号, 规则说明, 更新时间)
            VALUES (?, ?, datetime('now'))
        """, (rule_num, rule_name))
        print(f"Inserted: {rule_num} - {rule_name}")

conn.commit()

# 验证
print("\n=== 验证 ===\n")
c.execute("SELECT 规则编号, 规则说明 FROM 序境系统总则 WHERE 规则编号 LIKE '6.%' OR 规则编号 LIKE '8.%'")
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
print("\nDone!")
