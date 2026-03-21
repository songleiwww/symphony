# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('【整改任务分配】')
print('='*60)

# 任务1：扩展AI资讯源
print('\n【任务1】扩展AI资讯抓取源')
print('  执行者：顾清歌（翰林学士）')
print('  增加：腾讯AI、网易AI、机器之心备用源')

# 任务2：识别离线模型
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c = conn.cursor()
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态 = ? GROUP BY 服务商', ('offline',))
print('\n【任务2】离线模型分布')
for row in c.fetchall():
    print(f'    {row[0]}: {row[1]}个')

c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = ?', ('offline',))
total = c.fetchone()[0]
print(f'  总计：{total}个')

# 列出可清理的离线模型
c.execute('SELECT id, 模型名称, 服务商 FROM 模型配置表 WHERE 在线状态 = ? AND \"本行记录锁定\" != ? LIMIT 10', ('offline', '是'))
print('\n  可清理模型（前10条）：')
for row in c.fetchall():
    print(f'    ID:{row[0]} {row[1]} ({row[2]})')

conn.close()

print('\n【待用户确认】是否清理这10条离线模型？')
