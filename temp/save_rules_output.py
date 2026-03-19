# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Read rules
cur.execute('SELECT * FROM "序境系统总则" ORDER BY id')
rules = cur.fetchall()

# Write to file with UTF-8
with open(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\rules_output.txt', 'w', encoding='utf-8') as f:
    f.write('=== 序境系统总则 ===\n\n')
    for r in rules:
        f.write(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}\n')

print(f'Written {len(rules)} rules to file')
conn.close()
