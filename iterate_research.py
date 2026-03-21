# -*- coding: utf-8 -*-
"""
序境系统 - 10人研讨：如何保证迭代不丢失功能+安全清理冗余
"""
import sys
import io
import sqlite3
import requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def get_model(provider):
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? AND 在线状态='online' LIMIT 1", (provider,))
    r = c.fetchone()
    if r:
        return {"name": r[0], "identifier": r[1], "url": r[2], "key": r[3], "provider": provider}
    return None

def call_model(model, prompt):
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 600},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=40)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"
    return None

# 获取10个不同模型
providers = ['英伟达', '硅基流动', '火山引擎', '智谱', '魔搭', '魔力方舟']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)
    if len(models) >= 10:
        break

# 如果不够，从同服务商多取
if len(models) < 10:
    for p in providers:
        c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? AND 在线状态='online' LIMIT 3", (p,))
        for r in c.fetchall():
            if len(models) >= 10:
                break
            models.append({"name": r[0], "identifier": r[1], "url": r[2], "key": r[3], "provider": p})

conn.close()

print("="*60)
print("【陆念昭调度】10人研讨：迭代保功能+安全清理")
print("="*60)
print(f"调度: {len(models)}人\n")

# 研讨问题
topic = """请作为专家研讨以下问题（简洁回答要点）：

问题1：软件迭代时，如何保证原有有益功能不丢失？
问题2：清理代码冗余时，如何确保无风险？

请给出具体可执行的方法论。"""

results = []
for i, m in enumerate(models[:10]):
    print(f"[{i+1}/{len(models)}] {m['provider']}-{m['name']} 研讨中...")
    content = call_model(m, topic)
    results.append({"provider": m['provider'], "name": m['name'], "content": content})
    print(f"  → 完成")

print("\n" + "="*60)
print("【研讨汇总】")
print("="*60)

for r in results:
    print(f"\n【{r['provider']}】{r['name']}:")
    print(r['content'][:400] if r['content'] else "无响应")
    print("-"*40)

print("\n" + "="*60)
print("【陆念昭】研讨结束，请大人审阅！")
print("="*60)
