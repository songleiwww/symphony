# -*- coding: utf-8 -*-
import sqlite3
import codecs

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# Use codecs to read file
conn = sqlite3.connect(db_path)

# Set text_factory to handle encoding
def decode_text(b):
    if isinstance(b, str):
        return b
    # Try multiple encodings
    for enc in ['utf-8', 'gbk', 'gb2312', 'utf-16']:
        try:
            return b.decode(enc)
        except:
            continue
    return b.decode('utf-8', errors='replace')

conn.text_factory = decode_text
cur = conn.cursor()

# Get table with 64 rows, 5 cols
for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 64:
        cur.execute(f'PRAGMA table_info("{t[0]}")')
        cols = cur.fetchall()
        if len(cols) == 5:
            # Get first rule to check encoding
            cur.execute(f'SELECT * FROM "{t[0]}" WHERE id=1')
            r = cur.fetchone()
            print(f'Table: {t[0]}')
            print(f'Rule 1: {r}')
            
            # Get all
            cur.execute(f'SELECT * FROM "{t[0]}" ORDER BY id')
            rules = cur.fetchall()
            
            # Write to file
            with open(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\rules_output.txt', 'w', encoding='utf-8') as f:
                for r in rules:
                    f.write(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}\n')
            
            print(f'Total: {len(rules)} rules saved')
            break

conn.close()
