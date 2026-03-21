# -*- coding: utf-8 -*-
import sqlite3
import requests
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取硅基流动API配置
c.execute("SELECT API地址, API密钥 FROM 模型配置表 WHERE 服务商='硅基流动' LIMIT 1")
row = c.fetchone()
if row:
    api_url = row[0]
    api_key = row[1]
    if '/chat/completions' not in api_url:
        api_url = api_url.rstrip('/') + '/chat/completions'
    
    print("="*60)
    print("【硅基流动模型在线检测】")
    print(f"API: {api_url}")
    print("-"*60)
    
    # 获取所有硅基流动模型
    c.execute("SELECT id, 模型名称, 模型标识符 FROM 模型配置表 WHERE 服务商='硅基流动'")
    models = c.fetchall()
    print(f"总模型: {len(models)}个")
    
    online_count = 0
    for mid, mname, identifier in models:
        print(f"\n测试: {mname}", end=" ", flush=True)
        time.sleep(0.5)
        try:
            resp = requests.post(api_url, json={"model": identifier, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                              headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=15)
            if resp.status_code == 200:
                print("✅")
                c.execute("UPDATE 模型配置表 SET 在线状态='online' WHERE id=?", (mid,))
                online_count += 1
            else:
                print(f"❌ {resp.status_code}")
                c.execute("UPDATE 模型配置表 SET 在线状态='offline' WHERE id=?", (mid,))
        except Exception as e:
            print(f"❌ 错误")
            c.execute("UPDATE 模型配置表 SET 在线状态='offline' WHERE id=?", (mid,))
    
    print(f"\n在线: {online_count}/{len(models)}")
    conn.commit()

conn.close()
print("【完成】")
