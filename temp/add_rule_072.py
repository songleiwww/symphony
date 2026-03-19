# Add error memory clearing rule
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
    # Insert new rule about error memory clearing
    new_rule_id = "rule_072"
    new_rule_name = "错误记忆清除机制"
    new_rule_content = "被用户指出错误后：1.必须将错误记忆标记为不可用；2.清除错误记忆使其不可回忆；3.禁止使用错误记忆进行任何风险汇报和操作；4.更新正确信息到MEMORY.md；5.如有疑虑先查询数据库确认。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 072 added: 错误记忆清除机制')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
