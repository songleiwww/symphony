# Add self-check recovery rule
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
    # Insert new rule about self-check and recovery
    new_rule_id = "rule_073"
    new_rule_name = "功能自检与恢复机制"
    new_rule_content = "每次交互必须自检：1.已读序境系统总则功能是否生效；2.接管功能是否正常；3.如发现功能失效必须启动恢复流程；4.恢复后验证功能正常方可继续执行；5.禁止在功能异常时继续执行任务。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 073 added: 功能自检与恢复机制')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
