# -*- coding: utf-8 -*-
import sqlite3
import json
import os
from datetime import datetime

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
cache_file = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\rules_cache.json'

def read_rules_from_db():
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()
    
    # Find the rules table
    cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cur.fetchall()
    
    rule_table = None
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
        if cur.fetchone()[0] == 57:
            rule_table = t[0]
            break
    
    if not rule_table:
        conn.close()
        return None
    
    # Get all rules
    cur.execute(f'SELECT * FROM "{rule_table}" WHERE id <= 33 ORDER BY id')
    rules = cur.fetchall()
    
    # Get column names
    cur.execute(f'PRAGMA table_info("{rule_table}")')
    cols = [c[1] for c in cur.fetchall()]
    
    conn.close()
    
    return {
        'table': rule_table,
        'columns': cols,
        'rules': rules,
        'timestamp': datetime.now().isoformat()
    }

def get_cached_rules():
    """Get rules from cache or DB"""
    # Check if cache exists and is fresh (within 5 minutes)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # Check if cache is fresh (5 minutes)
            cache_time = datetime.fromisoformat(cache['timestamp'])
            now = datetime.now()
            if (now - cache_time).seconds < 300:  # 5 minutes
                print(f'Using cache from {cache["timestamp"]}')
                return cache
        except:
            pass
    
    # Read from DB and cache
    rules = read_rules_from_db()
    if rules:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        print(f'Read from DB and cached at {rules["timestamp"]}')
    
    return rules

# Test
result = get_cached_rules()
if result:
    print(f'\n=== 已读取总则 ===')
    print(f'表: {result["table"]}')
    print(f'规则数: {len(result["rules"])}')
    print(f'缓存时间: {result["timestamp"]}')
