# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (57 rows now after we tried to add)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count >= 50:
        table_name = t[0]
        
        # Find next available ID
        cur.execute(f'SELECT MAX(id) FROM "{table_name}"')
        max_id = cur.fetchone()[0]
        next_id = max_id + 1 if isinstance(max_id, int) else 58
        
        # Add rule: 模型配置表决定官署角色表数量
        new_rule = (next_id, '官署角色绑定规则', '模型配置表数量决定官署角色表数量(减去陆念昭)', '134模型=133角色(陆念昭除外),64角色未绑定需清理', '随时依据模型配置表更新官署角色绑定关系')
        
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print(f'Added rule {next_id}: 官署角色绑定规则')
        except Exception as e:
            print(f'Error: {e}')
        
        # Verify
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        print(f'Total: {cur.fetchone()[0]}')
        
        break

conn.close()
