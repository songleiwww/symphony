# -*- coding: utf-8 -*-
"""
序境系统 - 10人精英研讨：制定开发计划
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
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 800},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=40)
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
print("【陆念昭调度】10名精英制定开发计划")
print("="*60)
print(f"调度: {len(models)}人\n")

# 研讨主题
topic = """基于以下背景，为序境系统制定开发计划：

【序境系统现状】
- 模型配置表: 420条，在线354个
- 官署角色表: 422条
- 序境系统总则: 116条
- 数据库表: 36个
- 问题: 记忆加载不可靠、迭代可能丢失功能

【前期研讨结论】
1. 保功能: 功能基线化 + 自动化回归 + 灰度回滚
2. 安全清理: 静态分析 + 隔离观察 + 小步删除

请制定具体开发计划，包含：
1. 优先开发项（按重要性排序）
2. 每个项目的具体任务
3. 预计工作量
4. 风险点及对策

请简洁列出3-5个开发项。"""

results = []
for i, m in enumerate(models[:10]):
    print(f"[{i+1}/{len(models)}] {m['provider']}-{m['name']} 研判中...")
    content = call_model(m, topic)
    results.append({"provider": m['provider'], "name": m['name'], "content": content})
    print(f"  → 完成")

print("\n" + "="*60)
print("【开发计划汇总】")
print("="*60)

for r in results:
    print(f"\n【{r['provider']}】{r['name']}:")
    print(r['content'][:600] if r['content'] else "无响应")
    print("-"*40)

print("\n" + "="*60)
print("【陆念昭】研判结束，请大人审阅开发计划！")
print("="*60)
