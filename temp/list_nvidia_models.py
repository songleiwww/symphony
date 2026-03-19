# -*- coding: utf-8 -*-
import sqlite3
import requests

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get first NVIDIA model
cur.execute("SELECT * FROM 模型配置表 WHERE 服务商='英伟达' LIMIT 1")
row = cur.fetchone()

api_key = row[6]

# Get available models
print("=== Getting available models from NGC ===")

headers = {"Authorization": f"Bearer {api_key}"}

# Try to get model list
urls_to_try = [
    "https://ngc.nvidia.com/v1/models",
    "https://ngc.nvidia.com/api/v1/models",
    "https://integrate.api.nvidia.com/v1/models",
]

for url in urls_to_try:
    print(f"\nTesting: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Success! Content-Type: {response.headers.get('Content-Type')}")
            # Check if JSON
            if 'json' in response.headers.get('Content-Type', ''):
                data = response.json()
                print(f"  Models: {data}")
            else:
                print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")

conn.close()
