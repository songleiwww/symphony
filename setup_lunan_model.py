# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【序境系统配置陆念昭模型】")
print("="*60)

# 1. 更新模型配置表中的ark-code-latest
print("\n【1. 更新模型配置表】")
c.execute("UPDATE 模型配置表 SET 备注='陆念昭专用' WHERE 模型标识符='ark-code-latest'")
print("  ✅ ark-code-latest 标记为陆念昭专用")

# 2. 更新官署角色表
print("\n【2. 更新官署角色表】")
c.execute("UPDATE 官署角色表 SET 模型标识符='ark-code-latest', 服务商='火山引擎' WHERE 角色名称='少府监'")
print("  ✅ 少府监绑定 ark-code-latest")

# 3. 添加规则到序境系统总则
print("\n【3. 添加陆念昭模型规则】")
c.execute('''INSERT INTO 序境系统总则 (规则名称, 规则配置, 规则说明) VALUES (?, ?, ?)''',
    ('陆念昭模型规则',
     '官职=少府监;模型=ark-code-latest;服务商=火山引擎;API=https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
     '陆念昭(少府监)必须使用ark-code-latest模型'))

conn.commit()

# 4. 验证
print("\n【4. 验证】")
c.execute("SELECT 角色名称, 模型标识符, 服务商 FROM 官署角色表 WHERE 角色名称='少府监'")
role = c.fetchone()
print(f"  少府监: {role[1]} ({role[2]})")

c.execute("SELECT COUNT(*) FROM 序境系统总则")
rule_count = c.fetchone()[0]
print(f"  序境总则: {rule_count}条")

conn.close()

print("\n" + "="*60)
print("【配置完成】")
print("="*60)
print("""
陆念昭模型配置：
- 官职: 少府监
- 模型: ark-code-latest
- 服务商: 火山引擎
- API: https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions
""")
