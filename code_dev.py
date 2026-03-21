# -*- coding: utf-8 -*-
"""
序境系统 - 10位代码专家迭代开发
记录模型贡献度和Token消耗
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

def call_model_with_stats(model, prompt):
    """调用模型并返回Token消耗"""
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    start_time = datetime.now()
    
    try:
        resp = requests.post(url, json={
            "model": model['identifier'],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        }, headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=60)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if resp.status_code == 200:
            data = resp.json()
            usage = data.get('usage', {})
            
            return {
                'success': True,
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0),
                'content': data['choices'][0]['message']['content'],
                'elapsed': elapsed,
                'provider': model['provider'],
                'name': model['name']
            }
        else:
            return {'success': False, 'error': resp.status_code, 'elapsed': elapsed, 'provider': model['provider'], 'name': model['name']}
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        return {'success': False, 'error': str(e), 'elapsed': elapsed, 'provider': model['provider'], 'name': model['name']}

# 获取10个不同模型
providers = ['英伟达', '硅基流动', '火山引擎', '智谱', '魔搭', '魔力方舟']
models = []
seen = set()
for p in providers:
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? AND 在线状态='online'", (p,))
    for r in c.fetchall():
        key = (p, r[0])
        if key not in seen and len(models) < 10:
            seen.add(key)
            models.append({"name": r[0], "identifier": r[1], "url": r[2], "key": r[3], "provider": p})

conn.close()

print("="*60)
print("【陆念昭调度】10位代码专家迭代开发")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"调度: {len(models)}人\n")

# 开发任务
task = """请为序境系统编写一个简单的Python模块：模型健康检查器。

要求：
1. 检查模型配置表中的模型在线状态
2. 尝试调用每个模型API
3. 记录在线/离线状态

请直接输出代码（不超过50行），不要解释。"""

results = []
total_prompt = 0
total_completion = 0
total_elapsed = 0
success_count = 0

for i, m in enumerate(models[:10]):
    print(f"[{i+1}/{len(models)}] {m['provider']}-{m['name']} 开发中...")
    result = call_model_with_stats(m, task)
    results.append(result)
    
    if result['success']:
        success_count += 1
        total_prompt += result['prompt_tokens']
        total_completion += result['completion_tokens']
        total_elapsed += result['elapsed']
        print(f"  ✅ 消耗: {result['prompt_tokens']}+{result['completion_tokens']}={result['total_tokens']} tokens, {result['elapsed']:.1f}s")
    else:
        print(f"  ❌ {result.get('error')}")

print("\n" + "="*60)
print("【开发贡献度报告】")
print("="*60)

print(f"\n{'排名':<4} {'服务商':<8} {'模型':<20} {'Token消耗':<12} {'状态'}")
print("-"*60)

sorted_results = sorted([r for r in results if r.get('success')], 
                       key=lambda x: x.get('total_tokens', 0), reverse=True)

for i, r in enumerate(sorted_results):
    print(f"{i+1:<4} {r['provider']:<8} {r['name'][:18]:<20} {r['total_tokens']:<12} ✅")

for r in [r for r in results if not r.get('success')]:
    print(f"{'--':<4} {r['provider']:<8} {r['name'][:18]:<20} {'--':<12} ❌")

print("\n" + "="*60)
print("【Token消耗汇总】")
print("="*60)

print(f"成功开发: {success_count}/10")
print(f"总输入Token: {total_prompt}")
print(f"总输出Token: {total_completion}")
print(f"总计Token: {total_prompt + total_completion}")
print(f"总耗时: {total_elapsed:.1f}秒")

print("\n" + "="*60)
print("【陆念昭】开发完成，请大人审阅！")
print("="*60)
