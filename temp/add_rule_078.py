# Add own models usage rule
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
    new_rule_id = "rule_078"
    new_rule_name = "序境模型专用原则"
    new_rule_content = "必须使用序境系统自身模型池：1.只有使用自己的模型才能验证是否在真正多模型协作；2.使用宿主模型无法验证序境系统调度能力；3.调度多个模型时必须从模型配置表选择；4.每次调度需记录使用的模型来源；5.禁止依赖宿主模型进行模型协作演示。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 078 added: 序境模型专用原则')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
