# -*- coding: utf-8 -*-
"""
序境系统 - 全系统整合
调度多人协同整合
"""
import sys
import io
import sqlite3
import requests
from datetime import datetime
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
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=60)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"
    return None

# 获取各领域专家
providers = ['火山引擎', '硅基流动', '魔搭', '智谱', '英伟达']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

conn.close()

print("="*60)
print("【全系统整合】选调人员协同")
print("="*60)
print(f"调度: {len(models)}人\n")

# 整合任务
tasks = [
    ("架构师", "设计序境系统整体架构方案，包含模块划分、接口设计、数据流"),
    ("测试工程师", "设计自动化测试方案，覆盖核心功能"),
    ("运维工程师", "设计监控告警方案，确保系统稳定运行"),
    ("安全工程师", "设计安全加固方案，防护措施"),
    ("性能工程师", "设计性能优化方案，提升响应速度"),
]

results = []

for i, (role, task) in enumerate(tasks):
    if i >= len(models):
        break
    
    m = models[i]
    print(f"[{i+1}/{len(tasks)}] {m['provider']}-{m['name']} 担任{role}...")
    
    prompt = f"""你是一位专业的{role}。
    
请为序境系统设计{role}方案。

要求：
1. 针对序境系统现状（420模型、6个核心功能）
2. 简洁实用
3. 输出具体可执行的内容

{task}"""
    
    content = call_model(m, prompt)
    results.append({"role": role, "provider": m['provider'], "content": content})
    print(f"  → 完成")

print("\n" + "="*60)
print("【整合方案汇总】")
print("="*60)

for r in results:
    print(f"\n【{r['role']}】({r['provider']})")
    print("-"*40)
    print(r['content'][:500] if r['content'] else "无响应")
    print()

print("\n" + "="*60)
print("【陆念昭】整合方案已生成，请大人审阅！")
print("="*60)
