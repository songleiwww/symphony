#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"
API_KEY = "3b922877-3fbe-45d1-a298-53f2231c5224"
API_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_ID = "ep-20260329114326-l2f2s"
MODEL_NAME = "Doubao-ark-activity (活动专用)"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get current max id
cursor.execute("SELECT MAX(id) FROM model_config")
row = cursor.fetchone()
max_id = row[0] if row and row[0] else 0
print("Current max id: %d" % max_id)

now = "2026-03-31 19:34:00"

# Add the new model
max_id += 1

sql = """
INSERT INTO model_config VALUES ({}, '{}', '{}', 'chat reasoning code', 'volcano', 
'{}', '{}', '火山引擎活动专用模型，独立API Key，第二天重置用量，对话推理代码', 
'{}', '{}', 0, 'active', '火山活动免费额度', 16384, 'active', NULL, 
'volcano|{}|{}|{}');
""".format(max_id, MODEL_NAME, MODEL_ID, API_ENDPOINT, API_KEY, now, now, MODEL_ID, API_ENDPOINT, API_KEY)

try:
    cursor.execute(sql)
    conn.commit()
    print("SUCCESS: Added model id=%d" % max_id)
    print("  Model: %s (%s)" % (MODEL_NAME, MODEL_ID))
    print("  Endpoint: %s" % API_ENDPOINT)
except Exception as e:
    print("ERROR: %s" % e)

cursor.execute("SELECT COUNT(*) FROM model_config WHERE provider_name = 'volcano'")
cnt = cursor.fetchone()[0]
print("\nTotal volcano models now: %d" % cnt)

conn.close()
