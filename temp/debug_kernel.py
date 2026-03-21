# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('[内核整合Debug]')
print('='*50)

# 检查模块
print('')
print('[1] Check modules]')
modules_ok = True
try:
    import intent_analyzer
    print('  intent_analyzer: OK')
except Exception as e:
    print(f'  intent_analyzer: FAIL - {e}')
    modules_ok = False

try:
    import term_mapper
    print('  term_mapper: OK')
except Exception as e:
    print(f'  term_mapper: FAIL - {e}')
    modules_ok = False

try:
    import safety_checker
    print('  safety_checker: OK')
except Exception as e:
    print(f'  safety_checker: FAIL - {e}')
    modules_ok = False

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
print('[3] Check offices]')
try:
    import sqlite3
    conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM 官署角色表 WHERE 所属官署 = '少府监'")
    count = c.fetchone()[0]
    print(f'  Shaofu: {count} OK')
    conn.close()
except Exception as e:
    print(f'  Offices: FAIL - {e}')

print('')
print('[Debug Complete]')
