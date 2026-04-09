# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db')
conn.text_factory = str
cur = conn.cursor()
cur.execute('SELECT provider_name, COUNT(*) FROM model_config GROUP BY provider_name ORDER BY COUNT(*) DESC')
print('Provider          Count')
print('-' * 30)
total = 0
for prov, cnt in cur.fetchall():
    print(f'{prov:20} {cnt:4}')
    total += cnt
print('-' * 30)
print(f'{"Total":20} {total:4}')
conn.close()

