# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('[更正规则]')

# 更正第136条
c.execute("UPDATE 序境系统总则 SET 规则配置 = '分析意图准确度 不严格卡字 理解用户本意' WHERE id = 136")

print('  第136条已更正为: 分析意图准确度，不严格卡字')

conn.commit()
conn.close()

print('\n[OK] 规则已更正')
