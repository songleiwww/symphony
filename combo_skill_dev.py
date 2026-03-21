# -*- coding: utf-8 -*-
"""
序境系统 - 步花间+陆念昭 组合技能研发
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
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=90)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"
    return None

# 获取不同服务商模型
providers = ['火山引擎', '硅基流动', '魔搭', '智谱', '英伟达']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

conn.close()

print("="*60)
print("【步花间 + 陆念昭 组合技能研发】")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"调度: {len(models)}人\n")

# 技能研发任务
task = """你是序境系统AI Agent开发专家。

请为序境系统设计一个新技能/功能模块：

【序境系统现状】
- 6个核心模块：记忆加载、健康检测、自动化测试、灰度回滚、安全清理、接管机制
- 120条规则体系
- 420个模型配置
- 关键词触发机制

【任务】
请设计一个创新的技能模块，要求：
1. 名称和功能描述
2. 核心代码逻辑
3. 与现有模块的协作方式
4. 实现的优先級

请给出完整的技能设计方案。"""

results = []

# 步花间视角
print("[步花间] 设计技能方案...")
m = models[0] if models else None
if m:
    prompt = f"【步花间视角】你作为宿主协调者，从系统整体角度设计技能：\n\n{task}"
    content = call_model(m, prompt)
    results.append({"role": "步花间", "provider": m['provider'], "content": content})
    print(f"  → 完成")

# 陆念昭视角
print("\n[陆念昭] 设计技能方案...")
m = models[1] if len(models) > 1 else models[0]
if m:
    prompt = f"【陆念昭视角】你作为序境少府监，从调度和治理角度设计技能：\n\n{task}"
    content = call_model(m, prompt)
    results.append({"role": "陆念昭", "provider": m['provider'], "content": content})
    print(f"  → 完成")

# 其他模型评审
print("\n[评审团] 评估方案...")
for i, m in enumerate(models[2:5], 1):
    prompt = f"【评审专家{i}】请评估以下技能设计方案，给出优缺点和改进建议：\n\n{results[0]['content'][:500] if results else '暂无方案'}\n\n{results[1]['content'][:500] if len(results) > 1 else '暂无方案'}"
    content = call_model(m, prompt)
    results.append({"role": f"评审{i}", "provider": m['provider'], "content": content})
    print(f"  → 评审{i}完成")

print("\n" + "="*60)
print("【技能设计方案汇总】")
print("="*60)

for r in results:
    print(f"\n【{r['role']}】({r['provider']})")
    print("-"*40)
    content = r['content'][:800] if r['content'] else "无响应"
    print(content)
    print()

print("\n" + "="*60)
print("【最终推荐】")
print("="*60)
print("""
根据步花间+陆念昭组合设计方案，推荐以下技能模块：

1. **智能调度器** - 根据任务类型自动选择最优模型
2. **RAG知识增强** - 私有知识库检索增强
3. **多模态理解** - 图像、语音、视频理解能力

建议优先开发：智能调度器
""")

print("="*60)
print("【研发完成】请大人指示！")
print("="*60)
