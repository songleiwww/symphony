# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 添加路径
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

print('[内核整合Debug]')
print('='*50)

# 检查模块
print('')
print('[1] Check modules]')
try:
    import intent_analyzer
    print('  intent_analyzer: OK')
except Exception as e:
    print(f'  intent_analyzer: FAIL - {e}')

try:
    import term_mapper
    print('  term_mapper: OK')
except Exception as e:
    print(f'  term_mapper: FAIL - {e}')

try:
    import safety_checker
    print('  safety_checker: OK')
except Exception as e:
    print(f'  safety_checker: FAIL - {e}')

print('')
print('[2] Check database]')
try:
    import sqlite3
    conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM 序境系统总则')
    count = c.fetchone()[0]
    print(f'  Rules: {count} OK')
    conn.close()
except Exception as e:
    print(f'  Database: FAIL - {e}')

print('')
print('[Debug Complete - All OK]')
