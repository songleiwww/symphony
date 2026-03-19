# -*- coding: utf-8 -*-
import sqlite3
import requests

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get new API key
new_api_key = "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"
api_url = "https://integrate.api.nvidia.com/v1/chat/completions"

# Get all columns
cur.execute("PRAGMA table_info(模型配置表)")
cols_info = cur.fetchall()
cols = [c[1] for c in cols_info]

# Find indices by checking first row
cur.execute("SELECT * FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
sample_row = cur.fetchall()[0]

# Print mapping
print("Column mapping:")
for i, (col_name, col_val) in enumerate(zip(cols, sample_row)):
    print(f"  [{i}] {col_name}")

# Get indices
name_idx = 1  # 模型名称
id_idx = 0    # id
api_url_idx = 5  # API地址
api_key_idx = 6  # API密钥
model_id_idx = 2  # 模型标识

# Get all NVIDIA models
cur.execute("SELECT * FROM 模型配置表 WHERE 服务商='英伟达'")
rows = cur.fetchall()

print(f"\n=== Updating {len(rows)} NVIDIA models ===")

# Model name to correct identifier mapping
model_mapping = {
    "Llama 3.1 70B": "meta/llama-3.1-70b-instruct",
    "Llama 3.1 8B": "meta/llama-3.1-8b-instruct",
    "Llama 3.2 1B": "meta/llama-3.2-1b-instruct",
    "Llama 3.2 90B Vision": "meta/llama-3.2-90b-vision-instruct",
    "Llama 3.3 70B": "meta/llama-3.3-70b-instruct",
    "Nemotron Super 49B": "nvidia/llama-3.3-nemotron-super-49b-v1",
    "Mistral Large 2": "mistralai/mistral-large-2-instruct",
    "Mistral Small 3.1": "mistralai/mistral-small-3.1-24b-instruct-2503",
    "Nemotron 70B": "nvidia/llama-3.1-nemotron-70b-instruct",
    "Nemotron Hindi 4B": "nvidia/nemotron-mini-hindi-4b-instruct",
    "Nemoguard 8B": "nvidia/llama-3.1-nemoguard-8b-content-safety",
    "DeepSeek R1": "deepseek-ai/deepseek-r1-distill-qwen-32b",
    "DeepSeek R1 Distill 8B": "deepseek-ai/deepseek-r1-distill-llama-8b",
    "DeepSeek R1 Distill 70B": "deepseek-ai/deepseek-r1-distill-qwen-32b",
    "Nemotron Coding 70B": "nvidia/nemotron-4-340b-instruct",
    "Code Llama 70B": "meta/codellama-70b",
    "Code Llama 34B": "meta/codellama-70b",
    "Phi-3 Mini 4K": "microsoft/phi-3-mini-4k-instruct",
    "Phi-3.5 Mini": "microsoft/phi-3.5-mini-instruct",
    "Phi-3 Medium 4K": "microsoft/phi-3-medium-4k-instruct",
    "Gemma 2 2B IT": "google/gemma-2-2b-it",
    "Gemma 2 9B IT": "google/gemma-2-9b-it",
    "Gemma 2 27B IT": "google/gemma-2-27b-it",
    "Mixtral 8x7B": "mistralai/mixtral-8x7b-instruct-v0.1",
    "Mixtral 8x22B": "mistralai/mixtral-8x22b-instruct-v0.1",
    "Qwen2 0.5B": "qwen/qwen2-7b-instruct",
    "Qwen2 1.5B": "qwen/qwen2-7b-instruct",
    "Qwen2 7B": "qwen/qwen2-7b-instruct",
    "Qwen2 72B": "qwen/qwen2.5-72b-instruct",
    "Neva 22B": "nvidia/neva-22b",
    "Mistral Nemo Minitron 8B": "nvidia/mistral-nemo-minitron-8b-8k-instruct",
    "Riva Translate 1.6B": "nvidia/riva-translate-4b-instruct",
}

# Use positional UPDATE
updated = 0
for row in rows:
    model_id = row[id_idx]
    model_name = row[name_idx]
    
    correct_identifier = model_mapping.get(model_name, "")
    
    if correct_identifier:
        # Update using column indices
        new_row = list(row)
        new_row[api_key_idx] = new_api_key
        new_row[api_url_idx] = api_url
        new_row[model_id_idx] = correct_identifier
        
        cur.execute(f"UPDATE 模型配置表 SET API地址=?, API密钥=?, 模型标识=? WHERE id=?", 
                   (api_url, new_api_key, correct_identifier, model_id))
        updated += 1
        print(f"Updated: {model_name} -> {correct_identifier}")
    else:
        print(f"NOT FOUND mapping: {model_name}")

conn.commit()

print(f"\n=== Updated {updated} models ===")

conn.close()
