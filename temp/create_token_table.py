# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
from datetime import datetime

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('[创建Token使用记录表]')

# 创建Token使用记录表
c.execute('''
CREATE TABLE IF NOT EXISTS Token使用记录表 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    model_name TEXT NOT NULL,
    provider TEXT,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success'
)
''')

print('[表结构]')
c.execute("PRAGMA table_info(Token使用记录表)")
for col in c.fetchall():
    print(f'  {col[1]}: {col[2]}')

# 添加第146条规则
c.execute('SELECT MAX(id) FROM 序境系统总则')
max_id = c.fetchone()[0]

rule = (max_id+1, 'Token使用记录规则', 
     '每次模型调用后记录prompt_tokens、completion_tokens、total_tokens到Token使用记录表',
     'Token记录')

c.execute('''
    INSERT INTO 序境系统总则 (id, 规则名称, 规则配置, 规则说明)
    VALUES (?, ?, ?, ?)
''', rule)
print(f'\n[+第{max_id+1}条] Token使用记录规则')

conn.commit()
conn.close()

print('\n[OK] Token使用记录机制已建立')
