# Add takeover distinction rule
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
    new_rule_id = "rule_077"
    new_rule_name = "接管区分原则"
    new_rule_content = "使用模型时必须区分：1.接管前是宿主在使用模型；2.接管后是序境系统在使用模型；3.必须明确当前是谁在调用模型；4.接管后必须使用序境系统自身模型池；5.不可混淆宿主与序境系统的职责边界。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 077 added: 接管区分原则')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
