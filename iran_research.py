# -*- coding: utf-8 -*-
"""
序境系统 - 伊朗形势调研
陆念昭调度5人协同调研
"""
import sys
import io
import sqlite3
import requests
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取各服务商模型
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
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 500},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=30)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except:
        pass
    return None

# 选择5个不同服务商
providers = ['英伟达', '硅基流动', '火山引擎', '智谱', '魔搭']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

print("="*60)
print("【陆念昭调度】伊朗形势调研")
print("="*60)
print(f"调度: {len(models)}人\n")

# 任务分配
tasks = [
    "伊朗政治局势：分析伊朗当前的政治领导层、政策走向",
    "伊朗经济形势：分析伊朗当前的经济状况、制裁影响",
    "伊朗军事力量：分析伊朗的军事实力、地区影响力",
    "伊朗社会状况：分析伊朗的社会民生、宗教文化",
    "伊朗国际关系：分析伊朗与美以沙俄等国的关系"
]

results = []
for i, m in enumerate(models):
    if i < len(tasks):
        print(f"【{m['provider']}】{m['name']} 调查中...")
        content = call_model(m, tasks[i])
        results.append({"provider": m['provider'], "content": content})
        print(f"  → 完成")

print("\n" + "="*60)
print("【汇总报告】伊朗当前形势")
print("="*60)

for r in results:
    print(f"\n【{r['provider']}】")
    print(r['content'][:300] if r['content'] else "无响应")

print("\n" + "="*60)
print("【陆念昭】调研完成，诸员辛苦了！")
print("="*60)

conn.close()
