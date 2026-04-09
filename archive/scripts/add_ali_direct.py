#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"
API_KEY = "sk-fee678dbf4d84f9a910356821c95c0d5"
API_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Get current max id
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT MAX(id) FROM model_config")
row = cursor.fetchone()
max_id = row[0] if row and row[0] else 0
print("Current max id: %d" % max_id)

now = "2026-03-31 19:20:00"

# Add each model directly with string formatting
models_added = 0

# 1
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'qvq-max-2025-03-25', 'qvq-max-2025-03-25', 'vision multimodal', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qvq-max-2025-03-25|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: qvq-max-2025-03-25" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 2
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen-Math-Turbo', 'qwen-math-turbo', 'math reasoning', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 999970 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen-math-turbo|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen-Math-Turbo" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 3
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen3-VL-235B-A22B-Thinking', 'qwen3-vl-235b-a22b-thinking', 'vision reasoning multimodal', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 998112 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen3-vl-235b-a22b-thinking|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen3-VL-235B-A22B-Thinking" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 4
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen-Coder-Turbo-0919', 'qwen-coder-turbo-0919', 'code generation', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen-coder-turbo-0919|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen-Coder-Turbo-0919" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 5
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen2.5-Math-7B-Instruct', 'qwen2.5-math-7b-instruct', 'math reasoning', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen2.5-math-7b-instruct|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen2.5-Math-7B-Instruct" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 6
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen-VL-Plus-2025-05-07', 'qwen-vl-plus-2025-05-07', 'vision multimodal', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen-vl-plus-2025-05-07|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen-VL-Plus-2025-05-07" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 7
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen2.5-VL-72B-Instruct', 'qwen2.5-vl-72b-instruct', 'vision multimodal chat', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen2.5-vl-72b-instruct|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen2.5-VL-72B-Instruct" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 8
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen3-VL-32B-Thinking', 'qwen3-vl-32b-thinking', 'vision reasoning multimodal', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen3-vl-32b-thinking|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen3-VL-32B-Thinking" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 9
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'Qwen-Plus-2025-07-28', 'qwen-plus-2025-07-28', 'chat reasoning code', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|qwen-plus-2025-07-28|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: Qwen-Plus-2025-07-28" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

# 10
max_id += 1
sql = """
INSERT INTO model_config VALUES ({}, 'DeepSeek-R1-Distill-Qwen-7B', 'deepseek-r1-distill-qwen-7b', 'reasoning thinking', 'ali_bailian', 
'{}', '{}', '阿里云百炼免费额度 1000000 tokens 过期 2026/05/29 免费额度用完即停', 
'{}', '{}', 0, 'active', '免费额度 用完即停', 8192, 'active', NULL, 
'ali_bailian|deepseek-r1-distill-qwen-7b|{}|{}');
""".format(max_id, API_ENDPOINT, API_KEY, now, now, API_ENDPOINT, API_KEY)
try:
    cursor.execute(sql)
    print("Added id %d: DeepSeek-R1-Distill-Qwen-7B" % max_id)
    models_added += 1
except Exception as e:
    print("Error: %s" % e)

conn.commit()
cursor.execute("SELECT COUNT(*) FROM model_config WHERE provider_name = 'ali_bailian'")
cnt = cursor.fetchone()[0]
print("\n=====")
print("Total added: %d/%d models" % (models_added, 10))
print("Total ali_bailian models in database: %d" % cnt)
conn.close()
