# Add external config borrowing rule
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
    new_rule_id = "rule_075"
    new_rule_name = "外部配置借用汇报机制"
    new_rule_content = "使用外部/合作伙伴配置时：1.必须明确汇报使用了外部配置；2.必须说明配置来源和所属；3.借用配置需记录借还日志；4.使用外部配置时需礼貌感谢；5.不可将外部配置误认为是序境系统自身配置。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 075 added: 外部配置借用汇报机制')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
