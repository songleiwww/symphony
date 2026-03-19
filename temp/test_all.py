# -*- coding: utf-8 -*-
import sqlite3
import requests

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all models
cur.execute("SELECT * FROM 模型配置表")
rows = cur.fetchall()

print(f"=== Testing {len(rows)} models ===\n")

results = []

for row in rows:
    model_id = row[0]
    model_name = row[1]  # Model name
    model_identifier = row[2]  # Model identifier
    provider = row[4]  # Provider
    api_url = row[5]  # API URL
    api_key = row[6]  # API Key
    
    if not api_url or not api_key or api_url == '' or api_key == '':
        results.append((model_name, provider, "SKIP", "No API config"))
        continue
    
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        # Build proper URL
        test_url = api_url.rstrip('/')
        if '/chat/completions' not in test_url:
            test_url = test_url + '/chat/completions'
        
        response = requests.post(
            test_url,
            headers=headers,
            json={"model": model_identifier, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 10},
            timeout=15
        )
        
        if response.status_code == 200:
            results.append((model_name, provider, "OK", response.status_code))
        else:
            results.append((model_name, provider, "FAIL", response.status_code))
            
    except Exception as e:
        err_msg = str(e)[:30]
        results.append((model_name, provider, "ERROR", err_msg))

conn.close()

# Print results
print(f"{'Model':<25} {'Provider':<12} {'Status':<8} {'Code'}")
print("-" * 60)
for name, provider, status, code in results:
    print(f"{name[:25]:<25} {provider[:12]:<12} {status:<8} {code}")

# Summary
print(f"\n=== Summary ===")
ok_count = len([r for r in results if r[2] == 'OK'])
fail_count = len([r for r in results if r[2] == 'FAIL'])
error_count = len([r for r in results if r[2] == 'ERROR'])
skip_count = len([r for r in results if r[2] == 'SKIP'])

print(f"OK: {ok_count}, FAIL: {fail_count}, ERROR: {error_count}, SKIP: {skip_count}")
print(f"Total: {len(results)}")
