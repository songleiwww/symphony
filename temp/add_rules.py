# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 添加新规则
# 先检查当前最大ID
c.execute("SELECT MAX(id) FROM 序境系统总则")
max_id = c.fetchone()[0] or 0
print(f"Current max ID: {max_id}")

# 新规则列表
new_rules = [
    (28, "6.1", "模型配置完整读取原则", "每次配置模型要完全读取配置所有字段，本行记录的所有信息进行分析再决定处理解决方案", "完整读取: 必须读取本行记录的所有字段; 分析要求: 在决定解决方案前分析整行所有信息; 禁止行为: 禁止仅凭单个字段就做出判断"),
    (29, "8.1", "API密钥问题排查规则", "相同服务商正确模型配置的key修复不正确的，如果一个模型key正确就排查其他原因", "同服务商密钥溯源: 同一服务商的多个模型共享同一API密钥; 正确密钥判定: 用该服务商任意一个模型测试API，成功返回200即证明密钥有效")
]

print("\n=== Syncing New Rules ===\n")

for rule_id, rule_num, rule_title, rule_desc, strategy in new_rules:
    c.execute("""
        INSERT INTO 序境系统总则 (id, 规则编号, 规则说明, 更新时间, 相关策略)
        VALUES (?, ?, ?, datetime('now'), ?)
    """, (rule_id, rule_num, rule_title + " - " + rule_desc, strategy))
    print(f"Inserted: {rule_num} - {rule_title}")

conn.commit()

# 验证
print("\n=== Verification ===\n")
c.execute("SELECT id, 规则编号, 规则说明 FROM 序境系统总则 WHERE id >= 28")
for row in c.fetchall():
    print(f"ID: {row[0]}, Num: {row[1]}, Desc: {row[2][:30]}...")

conn.close()
print("\nDone!")
