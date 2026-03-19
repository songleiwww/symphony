# -*- coding: utf-8 -*-
import sqlite3
import json

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
cache_file = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\rules_cache.json'

conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count >= 33:
        table_name = t[0]
        
        # Add rule about providers
        new_rule = (
            54,  # Next ID
            '模型服务商正确名称',  # Rule name
            '英伟达:106个, 火山引擎:8个, 魔搭:7个, 智谱:7个, 硅基流动:6个',  # Content
            'MiniMax不是服务商,是模型名,调度必须使用数据库中实际服务商名称',  # Description
            '使用前必须读取模型配置表确认服务商'  # Strategy
        )
        
        # Check if rule 54 already exists
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}" WHERE id = 54')
        exists = cur.fetchone()[0]
        
        if exists == 0:
            cur.execute(f'''
                INSERT INTO "{table_name}" (id, 规则名称, 规则内容, 规则说明, 遵循策略)
                VALUES (?, ?, ?, ?, ?)
            ''', new_rule)
            conn.commit()
            print(f'Added rule 54: 模型服务商正确名称')
        else:
            print(f'Rule 54 already exists')
        
        # Update cache
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total = cur.fetchone()[0]
        print(f'Total rules now: {total}')
        
        break

conn.close()

# Refresh cache
import os
if os.path.exists(cache_file):
    os.remove(cache_file)
    print('Cache cleared, will refresh on next read')
