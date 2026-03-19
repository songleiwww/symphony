import sqlite3
import requests

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# Find the model config table
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
model_table = None
for t in tables:
    if '模型' in t and '配置' in t:
        model_table = t
        break

# Get all NVIDIA models - using index
c.execute(f"SELECT * FROM '{model_table}'")
rows = c.fetchall()

# Column indices
IDX_ID = 0
IDX_NAME = 1
IDX_MODEL_ID = 2
IDX_PROVIDER = 4
IDX_API_URL = 5
IDX_API_KEY = 6

# Filter NVIDIA models
nvidia_rows = [r for r in rows if r[IDX_PROVIDER] == '英伟达']

print("=== 英伟达模型逐一核查 ===\n")

results = []
for row in nvidia_rows:
    model_id = row[IDX_ID]
    model_name = row[IDX_NAME]
    model_id_raw = row[IDX_MODEL_ID]
    api_url = row[IDX_API_URL]
    api_key = row[IDX_API_KEY]
    
    # Test API
    status = "?"
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': model_id_raw, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}
        
        # Try the base URL first
        base_url = api_url.split('/chat/completions')[0] if '/chat/completions' in api_url else api_url
        
        resp = requests.post(f'{base_url}/chat/completions', headers=headers, json=data, timeout=15)
        
        if resp.status_code == 200:
            status = "[OK]"
        elif resp.status_code == 404:
            # Try alternative endpoints
            alt_endpoints = [
                f'{base_url}/v1/chat/completions',
                'https://integrate.api.nvidia.com/v1/chat/completions',
            ]
            found = False
            for alt_url in alt_endpoints:
                try:
                    resp2 = requests.post(alt_url, headers=headers, json=data, timeout=15)
                    if resp2.status_code == 200:
                        status = "[OK]"
                        found = True
                        break
                    else:
                        status = f"[E{resp2.status_code}]"
                except:
                    status = "[E]"
            if not found:
                status = "[E404]"
        else:
            status = f"[E{resp.status_code}]"
            
    except requests.exceptions.Timeout:
        status = "[TIMEOUT]"
    except Exception as e:
        status = f"[ERROR]"
    
    print(f"{model_id:>3}. {model_name[:35]:<35} {status}")
    results.append({'id': model_id, 'name': model_name, 'status': status})

# Summary
print("\n=== 汇总 ===")
ok_count = sum(1 for r in results if '[OK]' in r['status'])
print(f"可用: {ok_count}")
print(f"不可用: {len(results) - ok_count}")

conn.close()
