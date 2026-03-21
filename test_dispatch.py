# -*- coding: utf-8 -*-
"""
序境系统 - 调度引擎协调能力测试
陆念昭调度多个模型协同完成复杂任务
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import requests
import sqlite3
import io
import sys
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
dispatcher = DynamicDispatcher(db_path)

def call_model(model, prompt):
    """调用模型"""
    url = model['url']
    if "/chat/completions" not in url:
        url = url.rstrip("/") + "/chat/completions"
    
    payload = {
        "model": model['name'],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    
    headers = {"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}
    
    start = time.time()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        elapsed = time.time() - start
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'], elapsed, resp.status_code
    except Exception as e:
        return f"错误: {e}", time.time() - start, 0
    return None, time.time() - start, resp.status_code

print("="*60)
print("【陆念昭调度】调度引擎协调能力测试")
print("="*60)

# 选择不同服务商的模型
providers = {}
for m in dispatcher.models:
    p = m.get('provider', 'unknown')
    if p not in providers:
        providers[p] = m
    if len(providers) >= 4:
        break

print(f"\n【陆念昭】: 令！四员就位，协同完成调研任务！\n")

# 任务：每人负责一个方面
tasks = [
    ("智囊博士", "分析AI Agent自进化技术的最新趋势"),
    ("工部尚书", "评估模块化架构的优劣势"),
    ("翰林学士", "总结MCP协议的应用场景"),
    ("枢密使", "提出安全治理方案"),
]

team = []
for i, (role, task) in enumerate(tasks):
    model = list(providers.values())[i % len(providers)]
    team.append({"role": role, "task": task, "model": model})
    print(f"【{role}】使用 {model['name']} ({model['provider']})")
    print(f"  任务: {task}")

print("\n" + "-"*60)
print("【协同执行】")
print("-"*60)

results = []
for member in team:
    print(f"\n{member['role']} 工作中...")
    content, elapsed, code = call_model(member['model'], member['task'])
    results.append({
        "role": member['role'],
        "model": member['model']['name'],
        "time": elapsed,
        "status": code,
        "content": content[:150] if content else "无响应"
    })
    print(f"  → {member['model']['name']} | {elapsed:.1f}秒 | {code}")

print("\n" + "="*60)
print("【汇总报告】")
print("="*60)

for r in results:
    print(f"\n【{r['role']}】({r['model']})")
    print(f"  {r['content']}")

total_time = sum(r['time'] for r in results)
success = sum(1 for r in results if r['status'] == 200)

print(f"\n【统计】")
print(f"  参与模型: {len(results)}个")
print(f"  成功: {success}/{len(results)}")
print(f"  总耗时: {total_time:.1f}秒")

print("\n" + "="*60)
print("【陆念昭】: 调度引擎协调能力测试完成！")
print("="*60)
