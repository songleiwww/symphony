# Add self-check rule
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
    # Insert new rule about self-check
    new_rule_id = "rule_071"
    new_rule_name = "自检机制"
    new_rule_content = "每次执行任务后必须自检：1.是否幻觉执行（编造不存在的数据）；2.是否绕过序境系统总则；3.是否欺骗执行（汇报不实信息）；4.是否虚假执行（未真实调用模型）。如有违反，必须主动承认错误并解释原因，禁止隐瞒。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 071 added: 自检机制')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
