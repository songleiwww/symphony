# Add self-check and recovery rule
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
    new_rule_id = "rule_076"
    new_rule_name = "模型自检与恢复机制"
    new_rule_content = "当未使用模型配置表里的模型而使用宿主模型时：1.必须自检配置；2.尽力恢复配置表里的模型上线；3.测试各服务商模型可用性；4.如模型离线需排查原因并修复；5.优先使用序境系统自身模型池。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 076 added: 模型自检与恢复机制')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
