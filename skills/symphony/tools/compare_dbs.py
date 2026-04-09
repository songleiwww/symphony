# -*- coding: utf-8 -*-
import sqlite3

old_db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db'
new_db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db'

def get_old_models(db_path):
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute('SELECT model_id, provider, model_name, base_url FROM model_config')
    rows = cur.fetchall()
    conn.close()
    # key: model_id|provider
    return {(str(r[0]), str(r[1])): r for r in rows}

def get_new_models(db_path):
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute('SELECT model_id, provider_name, name, api_address FROM model_config')
    rows = cur.fetchall()
    conn.close()
    return {(str(r[0]), str(r[1])): r for r in rows}

old_models = get_old_models(old_db)
new_models = get_new_models(new_db)

old_keys = set(old_models.keys())
new_keys = set(new_models.keys())

missing = old_keys - new_keys
extra = new_keys - old_keys

print(f'旧库 symphony.db:      {len(old_models)} 个模?)
print(f'新库 symphony_working.db: {len(new_models)} 个模?)
print(f'丢失: {len(missing)} ?)
print(f'新增: {len(extra)} ?)

if missing:
    print(f'\n=== 丢失?{len(missing)} 个模?===')
    for k in sorted(missing, key=lambda x: x[1]):
        r = old_models[k]
        print(f'  [{r[1]}] {r[0]} - {r[2]} | {r[3]}')

if extra:
    print(f'\n=== 新库多出?{len(extra)} 个模?===')
    for k in sorted(extra, key=lambda x: x[1]):
        r = new_models[k]
        print(f'  [{r[1]}] {r[0]} - {r[2]}')

