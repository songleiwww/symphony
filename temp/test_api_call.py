#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import requests

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# Get API config
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT id, 模型名称, 模型标识符, 服务商, API地址, API密钥 FROM 模型配置表 WHERE id = 56")
row = c.fetchone()
conn.close()

if row:
    model_config = {
        "id": row[0],
        "name": row[1],
        "api_id": row[2],
        "provider": row[3],
        "api_url": row[4],
        "api_key": row[5]
    }
    
    print(f"Model: {model_config['name']}")
    print(f"API URL: {model_config['api_url']}")
    print(f"API Key: {model_config['api_key'][:30]}...")
    
    # Test API call
    url = model_config['api_url']
    api_key = model_config['api_key']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_config["api_id"],
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    
    print("\nCalling API...")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"Success! Response: {result['choices'][0]['message']['content'][:100]}")
        else:
            print(f"Error: {resp.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
