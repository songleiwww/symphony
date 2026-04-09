#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"
API_KEY = "sk-fee678dbf4d84f9a910356821c95c0d5"
API_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Models provided
MODELS = [
    ("qvq-max-2025-03-25", "qvq-max-2025-03-25", "vision multimodal", "1000000", "2026/05/29"),
    ("qwen-math-turbo", "qwen-math-turbo", "math reasoning", "999970", "2026/05/29"),
    ("qwen3-vl-235b-a22b-thinking", "qwen3-vl-235b-a22b-thinking", "vision reasoning multimodal", "998112", "2026/05/29"),
    ("qwen-coder-turbo-0919", "qwen-coder-turbo-0919", "code generation", "1000000", "2026/05/29"),
    ("qwen2.5-math-7b-instruct", "qwen2.5-math-7b-instruct", "math reasoning", "1000000", "2026/05/29"),
    ("qwen-vl-plus-2025-05-07", "qwen-vl-plus-2025-05-07", "vision multimodal", "1000000", "2026/05/29"),
    ("qwen2.5-vl-72b-instruct", "qwen2.5-vl-72b-instruct", "vision multimodal chat", "1000000", "2026/05/29"),
    ("qwen3-vl-32b-thinking", "qwen3-vl-32b-thinking", "vision reasoning multimodal", "1000000", "2026/05/29"),
    ("qwen-plus-2025-07-28", "qwen-plus-2025-07-28", "chat reasoning code", "1000000", "2026/05/29"),
    ("deepseek-r1-distill-qwen-7b", "deepseek-r1-distill-qwen-7b", "reasoning thinking", "1000000", "2026/05/29"),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get max id
cursor.execute("SELECT MAX(id) FROM model_config")
row = cursor.fetchone()
max_id = row[0] if row and row[0] else 0
print("Current max id: %d" % max_id)

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
added = 0

for name, model_id, model_type, remaining, expires in MODELS:
    max_id += 1
    # 17 columns exactly
    sql = """
    INSERT INTO model_config (
        id, name, model_id, model_type, provider_name,
        api_address, api_key, usage_rule, created_at, updated_at,
        locked, status, payment_type, max_tokens, sync_status,
        last_sync, combo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    usage_rule = "阿里云百炼免费额度 %s tokens, 过期 %s, 免费额度用完即停, %s" % (remaining, expires, model_type)
    combo = "ali_bailian|%s|%s|%s" % (model_id, API_ENDPOINT, API_KEY)

    params = (
        max_id,
        name,
        model_id,
        model_type,
        "ali_bailian",
        API_ENDPOINT,
        API_KEY,
        usage_rule,
        now_str,
        now_str,
        0,
        "active",
        "免费额度 用完即停",
        8192,
        "active",
        None,
        combo,
    )
    # 17 params matches 17 columns
    try:
        cursor.execute(sql, params)
        added += 1
        print("Added %d: %s (%s)" % (max_id, name, model_id))
    except Exception as e:
        print("ERROR adding %d: %s" % (max_id, e))

conn.commit()

print("\n")
print("Done. Added %d out of %d models" % (added, len(MODELS)))

cursor.execute("SELECT COUNT(*) FROM model_config WHERE provider_name = 'ali_bailian'")
cnt = cursor.fetchone()[0]
print("Total ali_bailian models now: %d" % cnt)

conn.close()
