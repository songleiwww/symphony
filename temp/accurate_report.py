# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
from datetime import datetime, timedelta

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('='*60)
print('[精确Tokens统计 - 从数据库读取]')
print('='*60)

# 检查是否有Token使用记录表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%token%'")
token_tables = c.fetchall()

if token_tables:
    print(f'\n[Token记录表: {token_tables}]')
    for t in token_tables:
        c.execute(f'SELECT COUNT(*) FROM {t[0]}')
        count = c.fetchone()[0]
        print(f'  {t[0]}: {count}条记录')
else:
    print('\n[无专门Token记录表]')

# 检查序境系统总则中的汇报记录
c.execute("SELECT 规则名称, 规则配置 FROM 序境系统总则 WHERE 规则名称 LIKE '%汇报%' OR 规则名称 LIKE '%tokens%' OR 规则名称 LIKE '%调度%'")
print('\n[调度汇报记录]')
reports = c.fetchall()
for r in reports[:10]:
    print(f'  {r[0]}: {r[1][:50] if r[1] else ""}...')

# 检查模型配置表中的评分（间接反映使用情况）
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
print('\n[各服务商模型数]')
providers = {}
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}个')
    providers[r[0]] = r[1]

# 今日日期范围
today = datetime.now().strftime('%Y-%m-%d')
print(f'\n[今日] {today}')

# 检查是否有调用记录（通过检查相关表）
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
all_tables = [t[0] for t in c.fetchall()]
print(f'\n[数据库所有表]')
for t in all_tables[:20]:
    print(f'  {t}')

conn.close()

print('\n[注意] 精确Tokens需要从API调用日志中提取')
