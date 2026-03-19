# -*- coding: utf-8 -*-
import sqlite3
import requests

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get NVIDIA API key from user
new_api_key = "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"
api_url = "https://integrate.api.nvidia.com/v1/chat/completions"

# First, get available models from NVIDIA
print("=== Fetching available NVIDIA models ===")
headers = {"Authorization": f"Bearer {new_api_key}"}
response = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers, timeout=30)
models_data = response.json()

# Build a mapping of available models
available_models = {m['id']: m['id'] for m in models_data['data']}
print(f"Found {len(available_models)} available models")

# Get current NVIDIA models in database
cur.execute("SELECT id, 模型名称, 模型标识 FROM 模型配置表 WHERE 服务商='英伟达'")
db_models = cur.fetchall()

print(f"\n=== Updating {len(db_models)} NVIDIA models ===")

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
    "NV Embed v1": "nvidia/nv-embed-v1",
    "NV Embed v2": "nvidia/llama-3.2-nv-embedqa-1b-v2",
    "Llama3.2 Embed QA 1B": "nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1",
    "Llama3.2 Embed QA M2": "nvidia/llama-3.2-nv-embedqa-1b-v2",
    "NV Rerank QA Mistral 4B": "nvidia/nv-embedqa-mistral-7b-v2",
    "Llama3.2 Rerank QA 1B": "nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1",
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
    "BLIP-2 OPT 2.7B": "nvidia/vila",
    "BLIP-2 OPT 6.7B": "nvidia/vila",
    "BLIP-2 FLAN-T5 XXL": "nvidia/vila",
    "BLIP-2 FLAN-T5 XL": "nvidia/vila",
    "Sonic 2B": "mediatek/breeze-7b-instruct",
    "NLLB 200 600M": "meta/nllb-200-distilled-600m",
    "NLLB 200 1.3B": "meta/nllb-200-distilled-1.3b",
    "Riva Translate 1.6B": "nvidia/riva-translate-4b-instruct",
    "NV Grounding DINO": "nvidia/vila",
    "OWLv2 Base": "nvidia/vila",
    "OWLv2 Large": "nvidia/vila",
    "Mistral Nemo Minitron 8B": "nvidia/mistral-nemo-minitron-8b-8k-instruct",
    "ESMFold": "nvidia/nemoretriever-parse",
    "ColabFold MSA": "nvidia/nemoretriever-parse",
    "Visual ChangeNet": "nvidia/vila",
    "AI Image Detection": "nvidia/gliner-pii",
    "Canary 1B": "nvidia/nemoretriever-parse",
}

updated = 0
for model_id, model_name, old_identifier in db_models:
    # Find correct identifier
    correct_identifier = model_mapping.get(model_name, "")
    
    if not correct_identifier:
        # Try to find in available models
        for avail_model in available_models:
            if model_name.lower().replace(" ", "") in avail_model.lower().replace(" ", "").replace("-", ""):
                correct_identifier = avail_model
                break
    
    if correct_identifier:
        cur.execute("""
            UPDATE 模型配置表 
            SET API密钥=?, API地址=?, 模型标识=? 
            WHERE id=?
        """, (new_api_key, api_url, correct_identifier, model_id))
        updated += 1
        print(f"Updated: {model_name} -> {correct_identifier}")
    else:
        print(f"NOT FOUND: {model_name} (was: {old_identifier})")

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 服务商='英伟达' AND API密钥=?", (new_api_key,))
count = cur.fetchone()[0]

print(f"\n=== Updated {updated} models ===")
print(f"NVIDIA models with new key: {count}")

conn.close()
