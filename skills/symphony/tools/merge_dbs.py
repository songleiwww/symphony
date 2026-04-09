# -*- coding: utf-8 -*-
"""
合并旧库 symphony.db ?symphony_working.db
把旧库有、新库没有的模型补进?"""
import sqlite3, shutil, os
from datetime import datetime

OLD_DB = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db'
NEW_DB = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db'
BACKUP_DIR = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\backup'

# Provider 名称映射（旧?-> 新库?PROVIDER_MAP = {
    'aliyun': 'ali_bailian',
    'zhipuai': 'zhipu',
    'minimax': 'minimax',
    'nvidia': 'nvidia',
    'volcano': 'volcano',
}

def get_old_models(db_path):
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute('SELECT model_id, provider, model_name, base_url, api_key, status, cost_per_1k_tokens, priority FROM model_config')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_new_model_keys(db_path):
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute('SELECT model_id, provider_name FROM model_config')
    keys = set()
    for r in cur.fetchall():
        keys.add((str(r[0]), str(r[1])))
    conn.close()
    return keys

def get_new_max_id(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT MAX(CAST(id AS INTEGER)) FROM model_config')
    max_id = cur.fetchone()[0] or 0
    conn.close()
    return max_id

def merge():
    print('=== 开始合并数据库 ===')
    
    # 备份新库
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'symphony_working_pre_merge_{ts}.db')
    shutil.copy2(NEW_DB, backup_path)
    print(f'备份新库: {os.path.basename(backup_path)}')

    old_rows = get_old_models(OLD_DB)
    new_keys = get_new_model_keys(NEW_DB)
    next_id = get_new_max_id(NEW_DB) + 1

    print(f'旧库模型: {len(old_rows)}')
    print(f'新库已有key? {len(new_keys)}')

    conn = sqlite3.connect(NEW_DB)
    cur = conn.cursor()

    added = 0
    skipped = 0
    errors = []

    for row in old_rows:
        model_id, provider, model_name, base_url, api_key, status, cost, priority = row
        model_id = str(model_id).strip()
        provider = str(provider).strip()
        model_name = str(model_name).strip()
        base_url = str(base_url).strip() if base_url else ''
        api_key = str(api_key).strip() if api_key else ''
        
        # 映射 provider 名称
        mapped_provider = PROVIDER_MAP.get(provider, provider)
        key = (model_id, mapped_provider)
        
        if key in new_keys:
            skipped += 1
            continue

        next_id += 1
        combo = f'{mapped_provider}|{model_id}|{base_url}|'

        try:
            cur.execute("""
                INSERT INTO model_config
                (id, name, model_id, model_type, provider_name, api_address, api_key,
                 usage_rule, status, payment_type, max_tokens, combo, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                next_id,
                model_name,
                model_id,
                'chat',
                mapped_provider,
                base_url,
                api_key,
                'free' if cost == 0 else 'paid',
                status or 'active',
                'free' if cost == 0 else 'paid',
                4096,
                combo,
                'synced_from_old'
            ))
            added += 1
            print(f'  + [{mapped_provider}] {model_name} ({model_id})')
        except Exception as e:
            errors.append(f'Error adding {model_id}: {e}')

    conn.commit()
    conn.close()

    print(f'\n=== 合并完成 ===')
    print(f'新增: {added} ?)
    print(f'跳过(已存?: {skipped} ?)
    if errors:
        print(f'错误: {len(errors)} ?)
        for e in errors[:5]:
            print(f'  {e}')

if __name__ == '__main__':
    merge()

