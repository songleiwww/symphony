# -*- coding: utf-8 -*-
"""Quick test for model API"""
import sys
import sqlite3
import requests
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db"

def test_model():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 模型名称, 模型标识符, 服务商, API地址, API密钥 FROM 模型配置表 WHERE 在线状态="online" LIMIT 1')
    row = c.fetchone()
    conn.close()
    
    if not row:
        print("No online models found")
        return
    
    name, identifier, provider, api_url, api_key = row
    print(f"Testing: {name} ({provider})")
    
    url = api_url
    if "/chat/completions" not in url:
        url = url.rstrip("/") + "/chat/completions"
    
    try:
        resp = requests.post(url, json={
            "model": identifier,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }, headers={"Authorization": f"Bearer {api_key}"}, timeout=15)
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS: Model is online!")
        else:
            print(f"FAILED: {resp.text[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_model()
