# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('='*50)
print('[少府监完整配置]')
print('='*50)

# 少府监及下属
c.execute("SELECT 官职, 姓名, 职责 FROM 官署角色表 WHERE 所属官署 = '少府监' ORDER BY id")
roles = c.fetchall()
print('\n【少府监本监】')
for r in roles:
    print(f'  {r[0]}: {r[1]} ({r[2]})')

# 下属机构
subsidiaries = ['中尚署', '左尚署', '右尚署', '掌冶署']
for sub in subsidiaries:
    c.execute('SELECT 官职, 姓名, 职责 FROM 官署角色表 WHERE 所属官署 = ? ORDER BY id', (sub,))
    roles = c.fetchall()
    if roles:
        print(f'\n【{sub}】')
        for r in roles:
            print(f'  {r[0]}: {r[1]} ({r[2]})')

# 少府监相关规则
print('\n【序境系统总则】')
c.execute("SELECT id, 规则名称 FROM 序境系统总则 WHERE 规则名称 LIKE '%少府监%' OR 规则名称 LIKE '%唐制%' OR 规则名称 LIKE '%机构%'")
for r in c.fetchall():
    print(f'  第{r[0]}条: {r[1]}')

conn.close()
