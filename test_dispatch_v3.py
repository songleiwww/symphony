# -*- coding: utf-8 -*-
"""
序境系统 - 调度引擎协调能力测试 v3
使用模型标识符
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

import requests
import sqlite3
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取各服务商模型
def get_model(provider):
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? LIMIT 1", (provider,))
    r = c.fetchone()
    if r:
        return {"name": r[0], "identifier": r[1], "url": r[2], "key": r[3], "provider": provider}
    return None

def call_model(model, prompt):
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    payload = {
        "model": model['identifier'],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }
    headers = {"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'], resp.status_code
        else:
            return f"{resp.status_code}", resp.status_code
    except Exception as e:
        return f"错误", 0

print("="*60)
print("【陆念昭调度】调度引擎协调能力测试 v3")
print("="*60)

# 选择4个不同服务商
providers = ['英伟达', '火山引擎', '硅基流动', '魔搭']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)
        print(f"【{p}】{m['name']} -> {m['identifier']}")

print("\n" + "-"*60)

tasks = [
    "分析AI Agent自进化技术的最新趋势",
    "评估模块化架构的优劣势",
    "总结MCP协议的应用场景",
    "提出安全治理方案"
]

results = []
for i, m in enumerate(models):
    print(f"\n{m['provider']} 工作中...")
    content, code = call_model(m, tasks[i])
    results.append({"provider": m['provider'], "name": m['name'], "code": code, "content": content[:150] if content else "无"})
    print(f"  → {code}")

print("\n" + "="*60)
print("【结果】")
print("="*60)
success = sum(1 for r in results if r['code'] == 200)
for r in results:
    print(f"{r['provider']} ({r['name']}): {r['code']}")
print(f"\n成功: {success}/{len(results)}")

conn.close()
