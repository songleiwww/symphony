# Add API key usage rule
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Find rules table
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('Tables:', tables)

rules_table = None
for t in tables:
    if '规则' in t:
        rules_table = t
        break

if rules_table:
    new_rule_id = "rule_079"
    new_rule_name = "API密钥使用规则"
    new_rule_content = "使用模型配置表里的模型时：1.必须使用模型配置表中记录的API密钥；2.不可使用宿主的API密钥；3.模型配置表包含API地址和密钥；4.调用时从模型配置表读取对应模型的API配置；5.确保使用正确的服务商API。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print('[OK] Rule 079 added: API密钥使用规则')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
