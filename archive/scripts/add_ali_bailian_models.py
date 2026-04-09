#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add all provided Alibaba Cloud DashScope (阿里云百炼) models to Symphony database
"""

import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"
API_KEY = "sk-fee678dbf4d84f9a910356821c95c0d5"
API_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Models provided by user
MODELS = [
    {
        "name": "QvQ-Plus 20250728",
        "model_id": "qwen-plus-2025-07-28",
        "model_type": "chat reasoning code",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "QvQ-VL-Plus 20250507",
        "model_id": "qwen-vl-plus-2025-05-07",
        "model_type": "vision multimodal chat",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "Qwen3-VL-235B-A22B-Thinking",
        "model_id": "qwen3-vl-235b-a22b-thinking",
        "model_type": "vision reasoning multimodal",
        "remaining": "998,112",
        "expires": "2026/05/29",
    },
    {
        "name": "Qwen3-VL-32B-Thinking",
        "model_id": "qwen3-vl-32b-thinking",
        "model_type": "vision reasoning multimodal",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "Qwen2.5-VL-72B-Instruct",
        "model_id": "qwen2.5-vl-72b-instruct",
        "model_type": "vision multimodal chat",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "Qwen-Coder-Turbo-0919",
        "model_id": "qwen-coder-turbo-0919",
        "model_type": "code generation",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "Qwen2.5-Math-7B-Instruct",
        "model_id": "qwen2.5-math-7b-instruct",
        "model_type": "math reasoning",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "DeepSeek-R1-Distill-Qwen-7B",
        "model_id": "deepseek-r1-distill-qwen-7b",
        "model_type": "reasoning thinking",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "qvq-max-2025-03-25",
        "model_id": "qvq-max-2025-03-25",
        "model_type": "vision multimodal",
        "remaining": "1,000,000",
        "expires": "2026/05/29",
    },
    {
        "name": "Qwen-Math-Turbo",
        "model_id": "qwen-math-turbo",
        "model_type": "math reasoning",
        "remaining": "999,970",
        "expires": "2026/05/29",
    },
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get current max id
    cursor.execute("SELECT MAX(id) FROM model_config")
    max_id = cursor.fetchone()[0] or 0
    print(f"Current max id: {max_id}")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    added = 0

    for model in MODELS:
        max_id += 1
        new_id = max_id

        usage_rule = (f"阿里云百炼免费额度 {model['remaining']} tokens, "
                     f"过期 {model['expires']}, 免费额度用完即停, {model['model_type']}")

        combo = f"ali_bailian|{model['model_id']}|{API_ENDPOINT}|{API_KEY}"

        sql = """
        INSERT INTO model_config VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """

        params = (
            new_id,
            model["name"],
            model["model_id"],
            model["model_type"],
            "ali_bailian",
            API_ENDPOINT,
            API_KEY,
            usage_rule,
            now_str,
            now_str,
            0,  # locked
            "active",
            "免费额度 用完即停",
            8192,  # max_tokens
            "active",
            None,  # last_sync
            combo,
        )

        try:
            cursor.execute(sql, params)
            added += 1
            print(f"  Added: {new_id} - {model['name']} ({model['model_id']})")
        except Exception as e:
            print(f"  FAILED {new_id}: {e}")

    conn.commit()

    print(f"\n📊 Done: Added {added} models successfully")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM model_config WHERE provider_name = 'ali_bailian'")
    count = cursor.fetchone()[0]
    print(f"Total ali_bailian models in DB: {count}")

    conn.close()

if __name__ == "__main__":
    main()
