# Add model borrowing and fixing rule
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Find rules table
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]

rules_table = None
for t in tables:
    if '规则' in t:
        rules_table = t
        break

if rules_table:
    new_rule_id = "rule_080"
    new_rule_name = "模型借用与自愈原则"
    new_rule_content = "当模型配置表模型不可用时：1.可以借用宿主可用模型临时使用；2.必须将借用模型配置到自己的模型配置表；3.借用后必须调试确保可用；4.不可长期依赖宿主模型；5.最终必须使用序境系统自身模型池。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 080 added: 模型借用与自愈原则')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
