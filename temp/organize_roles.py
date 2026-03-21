# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('='*60)
print('[OK] 官署角色梳理')
print('='*60)

# 1. 当前官署角色分类
print('\n[1] 当前官署角色分类')
c.execute('SELECT 所属官署, COUNT(*) FROM 官署角色表 GROUP BY 所属官署')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}人')

# 2. 检查模型配置表中的服务商
print('\n[2] 模型服务商')
c.execute('SELECT DISTINCT 服务商 FROM 模型配置表')
providers = [r[0] for r in c.fetchall()]
print(f'  {providers}')

# 3. 根据服务商映射官署
print('\n[3] 服务商->官署映射')
provider_to_office = {
    '智谱': '司礼监',
    '火山引擎': '工部',
    '硅基流动': '钦天监',
    '英伟达': '兵部',
    '魔力方舟': '吏部',
    '魔搭': '中书省',
}

for p, o in provider_to_office.items():
    c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 服务商 = ?', (p,))
    count = c.fetchone()[0]
    print(f'  {p} -> {o}: {count}模型')

# 4. 统计离线模型（已标记不删除）
print('\n[4] 离线模型统计')
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态 = ? GROUP BY 服务商', ('offline',))
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}个（已标记离线）')

conn.close()

print('\n[OK] 离线模型已标记，不删除')
