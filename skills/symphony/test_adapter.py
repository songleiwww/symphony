import sqlite3
import requests
import json

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
PRIORITY_ORDER = ["aliyun", "minimax", "zhipu", "nvidia"]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT provider_code, provider_name, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
providers = []
for row in cursor.fetchall():
    providers.append({"code": row[0], "name": row[1], "base_url": row[2].rstrip("/"), "api_key": row[3]})
conn.close()

providers = sorted(providers, key=lambda p: PRIORITY_ORDER.index(p["code"]))
provider = providers[0]  # aliyun

# Get a chat model
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT model_id, model_name, context_window FROM model_config WHERE provider = 'aliyun' AND is_enabled = 1 AND model_type = 'chat' LIMIT 1")
row = cursor.fetchone()
conn.close()

model = {"model_id": row[0], "model_name": row[1], "context_window": row[2]}
print(f"Using model: {model}")

url = f"{provider['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
payload = {"model": model["model_id"], "messages": [{"role": "user", "content": "Say 'OK' in one word"}], "max_tokens": 20}
headers = {"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"}

response = requests.post(url, headers=headers, json=payload, timeout=30)
result = response.json()
print("Status: OK")
print("Content:", result["choices"][0]["message"]["content"])

# Save to file
with open(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\test_result.json", "w", encoding="utf-8") as f:
    json.dump({"status": "success", "model": model["model_id"], "response": result["choices"][0]["message"]["content"]}, f, ensure_ascii=False, indent=2)
print("Result saved to test_result.json")
