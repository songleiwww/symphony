# -*- coding: utf-8 -*-
"""
序境系统 - 综合Debug任务
陆念昭调度多模型进行系统诊断
"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')

from dynamic_dispatcher import DynamicDispatcher
import requests
import json
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
dispatcher = DynamicDispatcher(db_path)

# 陆念昭角色
lunianzhao_model = None
for m in dispatcher.models:
    if 'ark-code-latest' in m.get('name', '').lower():
        lunianzhao_model = m
        break

def call_model(model, prompt):
    """调用模型"""
    url = model['url']
    if "/chat/completions" not in url:
        url = url.rstrip("/") + "/chat/completions"
    
    payload = {
        "model": model['name'],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800
    }
    
    headers = {"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"
    return None

# 调试任务清单
debug_tasks = [
    ("模型配置表", "检查模型配置表数量、字段完整性"),
    ("官署角色表", "检查官署角色表数量是否与模型配置表对齐"),
    ("序境系统总则", "检查序境系统总则条数"),
    ("在线状态", "检查各服务商模型在线状态"),
]

print("="*50)
print("陆念昭调度：序境系统综合Debug")
print("="*50)

# 陆念昭发号施令
print("\n【陆念昭】: 令！诸员就位，对序境系统进行全面诊断！\n")

# 调度多个模型同时debug
results = []
for i, (task_name, task_desc) in enumerate(debug_tasks):
    print(f"【任务{i+1}】{task_name}: {task_desc}")
    
    # 选择不同服务商的模型
    provider_model = None
    for m in dispatcher.models:
        if m['provider'] not in [r.get('provider') for r in results[:i]]:
            provider_model = m
            break
    
    if not provider_model:
        provider_model = dispatcher.models[i % len(dispatcher.models)]
    
    result = call_model(provider_model, f"请检查序境系统{task_name}：{task_desc}。返回检查结果。")
    results.append({"task": task_name, "model": provider_model['name'], "result": result})
    print(f"  → {provider_model['name']}: {result[:100] if result else '无响应'}...")

print("\n" + "="*50)
print("【Debug汇总】")
print("="*50)
for r in results:
    print(f"\n{r['task']} ({r['model']}):")
    print(f"  {r['result'][:200] if r['result'] else '无响应'}")

print("\n【陆念昭】: 诸员辛苦了，Debug完成。")
