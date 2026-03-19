# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Delete old rules
try:
    cur.execute('DELETE FROM "序境系统总则"')
    print('Deleted old rules')
except Exception as e:
    print(f'Delete error: {e}')

# Read SQL file and extract INSERT statements
import re

with open(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\序境系统总则.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract INSERT statements
inserts = re.findall(r"INSERT INTO \"序境系统总则\" VALUES \((.*?)\);", content)

# Insert each rule
for insert in inserts:
    # Parse the values
    parts = [p.strip().strip("'\"") for p in insert.split(',')]
    if len(parts) >= 5:
        rule_id = int(parts[0])
        rule_name = parts[1]
        rule_config = parts[2]
        rule_desc = parts[3]
        rule_action = parts[4]
        
        sql = 'INSERT INTO "序境系统总则" VALUES (?, ?, ?, ?, ?)'
        try:
            cur.execute(sql, (rule_id, rule_name, rule_config, rule_desc, rule_action))
        except Exception as e:
            print(f'Error inserting rule {rule_id}: {e}')

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
count = cur.fetchone()[0]
print(f'Inserted {count} rules')

conn.close()
