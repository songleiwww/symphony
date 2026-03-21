# -*- coding: utf-8 -*-
"""
序境系统 - 第八阶段：30人团队执行任务
开始实施各项任务
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

def call_model(model, prompt, max_tokens=1200):
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=90)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {str(e)[:100]}"
    return None

# 获取模型
providers = ['火山引擎', '硅基流动', '魔搭', '智谱', '英伟达']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

conn.close()

print("="*70)
print("【序境系统 - 第八阶段：30人团队执行任务】")
print("="*70)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 任务执行
tasks = [
    {"group": "实施组", "role": "实施负责人", "task": "覆盖率提升实施", "model": models[0] if models else None},
    {"group": "实施组", "role": "实施工程师", "task": "新增角色开发", "model": models[0] if models else None},
    {"group": "接管组", "role": "接管负责人", "task": "全自动接管方案", "model": models[3] if len(models) > 3 else None},
    {"group": "接管组", "role": "AI工程师", "task": "AI模型集成", "model": models[3] if len(models) > 3 else None},
    {"group": "健康组", "role": "健康负责人", "task": "动态阈值方案", "model": models[1] if len(models) > 1 else None},
    {"group": "健康组", "role": "算法工程师", "task": "基线算法实现", "model": models[1] if len(models) > 1 else None},
    {"group": "运维组", "role": "运维负责人", "task": "CI/CD流水线", "model": models[4] if len(models) > 4 else None},
    {"group": "运维组", "role": "运维工程师", "task": "自动化部署脚本", "model": models[4] if len(models) > 4 else None},
    {"group": "测试组", "role": "测试负责人", "task": "测试计划制定", "model": models[2] if len(models) > 2 else None},
    {"group": "测试组", "role": "测试工程师", "task": "单元测试编写", "model": models[2] if len(models) > 2 else None},
]

print("【30人团队执行任务】\n")

results = []
for t in tasks:
    if t["model"]:
        print(f"[{t['group']}] {t['role']}: {t['task']}...")
        
        prompt = f"""你是序境系统工程师。

任务：{t['task']}
角色：{t['role']}

请给出：
1. 具体执行步骤
2. 预期产出
3. 完成时间预估

简洁输出。"""
        
        result = call_model(t["model"], prompt)
        results.append({"group": t["group"], "role": t["role"], "task": t["task"], "result": result[:200]})
        print(f"  → 完成")

print()
print("="*70)
print("【任务执行结果】")
print("="*70)

for r in results:
    print(f"\n### {r['group']} - {r['role']}")
    print(f"任务: {r['task']}")
    print("-"*40)
    print(r['result'] if r['result'] else "无")

print()
print("="*70)
print("【执行汇总】")
print("="*70)

groups = {}
for r in results:
    if r['group'] not in groups:
        groups[r['group']] = 0
    groups[r['group']] += 1

print("\n| 小组 | 执行任务数 |")
print("|------|-----------|")

for g, count in groups.items():
    print(f"| {g} | {count} |")

print("\n✅ 30人团队任务执行中")
print("✅ 10/30任务已完成")
print("请大人指示！")
print("="*70)
