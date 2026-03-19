# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the system rules table
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    if cur.fetchone()[0] >= 33:
        rule_table = t[0]
        break

if not rule_table:
    print('No rules table found')
    exit()

print(f'Found table: {rule_table}')

# Get column names
cur.execute(f'PRAGMA table_info("{rule_table}")')
cols = [c[1] for c in cur.fetchall()]
print(f'Columns: {cols}')

# Get all 33 rules
cur.execute(f'SELECT * FROM "{rule_table}" WHERE id <= 33 ORDER BY id')
rules = cur.fetchall()

# Check for potential conflicts
print('\n=== Checking for conflicts ===')

# Group by rule type
rule_names = {}
conflicts = []

for r in rules:
    rule_id = r[0]
    rule_name = r[1] if len(r) > 1 else ''
    rule_content = r[2] if len(r) > 2 else ''
    
    # Check for duplicate IDs
    if rule_id in rule_names:
        conflicts.append(f'ID {rule_id} appears multiple times')
    rule_names[rule_id] = (rule_name, rule_content)

# Print all rules for review
print('\n=== All 33 Rules ===')
for r in rules:
    print(f'\n--- ID {r[0]} ---')
    print(f'规则名称: {r[1]}')
    print(f'规则内容: {str(r[2])[:80]}...' if r[2] and len(str(r[2])) > 80 else f'规则内容: {r[2]}')

conn.close()
