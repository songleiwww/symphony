# -*- coding: utf-8 -*-
"""
序境系统 - 10人组合评估冗余清理与冲突梳理
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
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 800},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=60)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"
    return None

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
print("【10人组合评估：冗余清理+冲突梳理】")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"调度: {len(models)}人\n")

# 评估任务
task = """请评估序境内核的冗余清理和冲突梳理方案：

【当前问题】
1. 调度器13个：core/scheduler.py, dispatcher/legacy/* 等
2. 接管功能5个：takeover_skill.py, takeover_skill_new.py 等
3. 记忆系统5个：memory_cache.py(过时), memory_system_v2.py 等

【整合建议】
1. 调度器：保留core/scheduler.py，归档dispatcher/legacy/*
2. 接管功能：保留takeover_skill.py，删除重复
3. 记忆系统：统一到memory/working_memory.py

请评估这个方案，给出：
1. 同意/不同意及其理由
2. 补充建议
3. 风险评估

简洁回答。"""

results = []
for i, m in enumerate(models[:10]):
    print(f"[{i+1}/{len(models)}] {m['provider']}-{m['name']} 评估中...")
    content = call_model(m, task)
    results.append({"provider": m['provider'], "name": m['name'], "content": content})
    print(f"  → 完成")

print("\n" + "="*60)
print("【评估汇总】")
print("="*60)

agreed = 0
disagreed = 0

for r in results:
    print(f"\n【{r['provider']}】{r['name']}:")
    content = r['content'][:400] if r['content'] else "无响应"
    print(content)
    
    if content and ("同意" in content or "可行" in content or "合理" in content):
        agreed += 1
    elif content and ("不同意" in content or "风险" in content):
        disagreed += 1
    print("-"*40)

print("\n" + "="*60)
print("【评估结论】")
print("="*60)
print(f"同意: {agreed}/10")
print(f"反对: {disagreed}/10")

# 生成最终建议
print("\n" + "="*60)
print("【最终建议】")
print("="*60)

if agreed > disagreed:
    print("✅ 多数同意，执行清理整合")
    print("""
建议执行步骤：
1. 备份当前内核
2. 归档dispatcher/legacy/*到backup/
3. 删除重复的takeover文件
4. 统一记忆系统入口
5. 验证功能正常
""")
else:
    print("⚠️ 多数反对，需重新评估方案")

print("\n" + "="*60)
print("【陆念昭】评估完成，请大人指示是否执行清理！")
print("="*60)
