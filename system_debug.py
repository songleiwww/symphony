# -*- coding: utf-8 -*-
"""
序境系统 - 多人协同Debug
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
print("【多人协同Debug】")
print("="*60)
print(f"调度: {len(models)}人\n")

# Debug任务
debug_tasks = [
    ("调度器专家", "检查core/scheduler.py和dispatcher/调度器是否正常工作，找出可能的问题"),
    ("记忆系统专家", "检查memory/working_memory.py和记忆加载模块是否正常"),
    ("接管功能专家", "检查skills/takeover_skill.py接管功能是否正常"),
    ("健康检测专家", "检查health_check.py健康检测是否正常工作"),
    ("数据库专家", "检查symphony.db数据库表结构和关系是否正常"),
]

results = []

for i, (role, task) in enumerate(debug_tasks):
    if i >= len(models):
        break
    
    m = models[i]
    print(f"[{i+1}/{len(debug_tasks)}] {m['provider']}-{m['name']} 担任{role}...")
    
    prompt = f"""你是一位专业的{role}。

请Debug序境系统：
1. 检查相关模块
2. 找出潜在问题
3. 给出修复建议

{task}"""
    
    content = call_model(m, prompt)
    results.append({"role": role, "provider": m['provider'], "content": content})
    print(f"  → 完成")

print("\n" + "="*60)
print("【Debug汇总】")
print("="*60)

issues = []
for r in results:
    print(f"\n【{r['role']}】({r['provider']})")
    print("-"*40)
    content = r['content'][:500] if r['content'] else "无响应"
    print(content)
    
    if content and ("问题" in content or "错误" in content or "bug" in content.lower()):
        issues.append(r['role'])

print("\n" + "="*60)
print("【发现问题】")
print("="*60)

if issues:
    print(f"发现{len(issues)}个问题:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("未发现明显问题")

print("\n" + "="*60)
print("【陆念昭】Debug完成，请大人指示！")
print("="*60)
