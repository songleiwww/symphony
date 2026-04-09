#!/usr/bin/env python3
import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('SELECT id, name, model_id, provider_name FROM model_config WHERE provider_name = "minimax" OR provider_name like "%minimax%"')
rows = cursor.fetchall()

print(f'Found {len(rows)} MiniMax models in database:')
for row in rows:
    print(f'  id={row[0]}, name={row[1]}, model_id={row[2]}, provider={row[3]}')

conn.close()
