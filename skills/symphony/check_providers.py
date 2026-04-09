import sqlite3
import requests

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
print("Providers:", [(p["code"], p["name"]) for p in providers])
print("First provider API key length:", len(providers[0]["api_key"]) if providers[0]["api_key"] else 0)
print("First provider base_url:", providers[0]["base_url"])

# Try to call aliyun directly with a chat model
provider = providers[0]
url = f"{provider['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
print("URL:", url)

payload = {
    "model": "deepseek-v3",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 50,
    "temperature": 0.7,
    "stream": False
}
headers = {"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print("Status:", response.status_code)
    print("Response:", response.text[:500])
except Exception as e:
    print("Error:", e)
