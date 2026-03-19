# Add Xujing System takeover rule
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Find rules table
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]

rules_table = None
for t in tables:
    if '规则' in t or 'ϵͳ' in t:
        rules_table = t
        break

if rules_table:
    new_rule_id = "rule_074"
    new_rule_name = "序境系统接管原则"
    new_rule_content = "处理事务必须：1.接管宿主使用序境系统处理；2.调用kernel_integration.py统一入口；3.不可直接使用默认模型绕过序境系统；4.必须通过序境调度器选择模型；5.每次调用记录到调度日志。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 074 added: 序境系统接管原则')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
